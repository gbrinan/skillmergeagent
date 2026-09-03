#!/usr/bin/env python3
"""통합 점검기 — 기계 판정 (L1~L3 + L4 일부).

사용:
  python3 check/run_check.py <팩 경로>   팀 에이전트 팩을 판정
  python3 check/run_check.py --self      이 저장소 자신을 판정 (README 구조도 ↔ 실제 폴더)

종료 코드 0 = 기계 판정 전체 통과. L4의 [사람 판정] 항목(실제 실행·오류 주입)은 별도 수행 필요.
기준은 docs/check-criteria.md.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import TABLE_RE, find_skills, has_halt, human_of, next_of, parse_contract, parse_skill

results = []


def check(layer, name, ok, detail=""):
    """ok=True 통과 · ok=False 실패 · ok=None 명시적으로 수용된 위험(⚠️, 실패로 세지 않음)."""
    results.append((layer, name, ok, detail))


def _topo(skills, nexts):
    order, seen = [], set()

    def walk(n):
        if n in seen:
            return
        seen.add(n)
        for m_ in nexts.get(n, []):
            if m_ in skills:
                walk(m_)
        order.append(n)
    for n in skills:
        walk(n)
    return list(reversed(order))


def main(pack_dir):
    pack = Path(pack_dir)

    # L1 구조
    for f in ["README.md", "agent-plan.md", "AGENTS.md"]:
        check("L1", f"필수 파일 {f}", (pack / f).is_file())
    check("L1", "skills/ 존재", (pack / "skills").is_dir())
    check("L1", "data/ 존재", (pack / "data").is_dir())
    plan_copies = [p for p in pack.rglob("agent-plan.md") if "archive" not in p.parts]
    check("L1", "agent-plan.md SSOT 유일성", len(plan_copies) == 1,
          f"{len(plan_copies)}개 발견" if len(plan_copies) != 1 else "")

    skills = {}
    for p in find_skills(pack):
        meta, body = parse_skill(p)
        check("L1", f"{p.parent.name}: frontmatter", meta is not None)
        if meta:
            missing = [k for k in ["name", "inputs", "outputs", "reads", "writes", "next"] if k not in meta]
            check("L1", f"{meta.get('name', p.parent.name)}: 헤더 필드 완비", not missing,
                  f"누락: {missing}" if missing else "")
            skills[meta.get("name", p.parent.name)] = (meta, body, p)
    check("L1", "스킬 1개 이상", len(skills) > 0)

    plan = (pack / "agent-plan.md").read_text(encoding="utf-8") if (pack / "agent-plan.md").is_file() else ""
    agent_md = (pack / "AGENTS.md").read_text(encoding="utf-8") if (pack / "AGENTS.md").is_file() else ""
    contract = parse_contract(pack / "CONTRACT.md") or {"tables": {}}

    # L2 맥락 반영 — 명세 안의 표 = 기획서에 적힌 표 + 계약 tables(확장자 없는 이름도 여기로)
    plan_tables = set(TABLE_RE.findall(plan)) | set(contract["tables"])
    for name, (meta, body, p) in skills.items():
        check("L2", f"{name}: 기획서에 언급", name in plan or name in agent_md,
              "agent-plan.md/AGENTS.md 어디에도 없음" if name not in plan + agent_md else "")
        used = set((meta.get("reads") or []) + (meta.get("writes") or []))
        outside = used - plan_tables
        check("L2", f"{name}: 데이터가 명세 안", not outside, f"명세 밖 표: {sorted(outside)}" if outside else "")
        check("L2", f"{name}: 본문 존재", len(body.strip()) > 50)

    # L3 충돌·일관성
    writers = {}
    for name, (meta, _, _) in skills.items():
        for t in meta.get("writes") or []:
            writers.setdefault(t, []).append(name)
    for t, ws in writers.items():
        check("L3", f"단일 기록자: {t}", len(ws) == 1, f"복수 기록자 {ws}" if len(ws) > 1 else "")

    nexts = {n: next_of(m) for n, (m, _, _) in skills.items()}
    targets = {t for vs in nexts.values() for t in vs}
    starts = [n for n in skills if n not in targets]
    reached, frontier = set(starts), list(starts)
    while frontier:
        cur = frontier.pop()
        for nxt in nexts.get(cur, []):
            if nxt in skills and nxt not in reached:
                reached.add(nxt)
                frontier.append(nxt)

    def has_cycle():
        state = {}

        def walk(n):
            if state.get(n) == 1:
                return True
            if state.get(n) == 2:
                return False
            state[n] = 1
            for m_ in nexts.get(n, []):
                if m_ in skills and walk(m_):
                    return True
            state[n] = 2
            return False
        return any(walk(n) for n in skills)

    check("L3", "흐름: 시작점 1개", len(starts) == 1, f"시작점 {starts}")
    check("L3", "흐름: 모든 스킬에 도달(고아 없음)", reached == set(skills), f"도달 못 함: {sorted(set(skills) - reached)}")
    check("L3", "흐름: 순환 없음", not has_cycle())
    dangling = [(a, t) for a, vs in nexts.items() for t in vs if t not in skills]
    check("L3", "흐름: next가 실재하는 스킬을 가리킴", not dangling, f"없는 스킬 지목: {dangling}" if dangling else "")
    for a, vs in nexts.items():
        for b in vs:
            if b not in skills:
                continue
            out, inp = set(skills[a][0].get("outputs") or []), set(skills[b][0].get("inputs") or [])
            check("L3", f"흐름 정합: {a}→{b}", bool(out & inp),
                  f"outputs {sorted(out)} ↛ inputs {sorted(inp)}" if not out & inp else "")

    # 산출물 유형 — 탈락 사유가 아니라 이름 붙이기. AI 태스크 수(다단계성)와 갈림길 유무(순서 가변성)를 본다.
    branching = any(len(v) > 1 for v in nexts.values())
    humans = {n: human_of(m) for n, (m, _, _) in skills.items()}
    ai_tasks = [n for n, h in humans.items() if h in ("자동", "증강")]
    human_only = [n for n, h in humans.items() if h == "사람고유"]
    known_human = any(humans.values())
    too_few = known_human and len(ai_tasks) < 3
    if too_few:
        pack_kind = f"팀 스킬팩 (AI 태스크 {len(ai_tasks)}개 — 다단계성 기준선 3개 미충족)"
        kind_note = [f"  · AI에 맡길 태스크(자동·증강)가 {len(ai_tasks)}개입니다. 에이전트가 대신할 일 자체가 적습니다.",
                     "    태스크를 더 쪼개 3개 이상으로 만들거나, 이대로 스킬 묶음으로 씁니다."]
    elif branching:
        pack_kind, kind_note = "팀 에이전트 (갈림길 있음)", []
    else:
        pack_kind = "팀 스킬팩 (순차 실행)"
        kind_note = ["  · 순서가 매번 같은 흐름입니다. 지금 만든 것은 스킬 묶음이고,",
                     "    갈림길이 생기는 순간 그대로 에이전트가 됩니다 — 부품은 이미 다 만들었습니다."]

    terminals = [n for n in skills if not nexts.get(n)]
    mid_human = [n for n in human_only if n not in terminals]
    chain = _topo(skills, nexts) if reached == set(skills) else []

    # 용어 일관: 표 이름 표기 변형
    all_text = plan + agent_md + "".join(b for _, b, _ in skills.values())
    names = set(TABLE_RE.findall(all_text))
    normalized = {}
    for n in names:
        normalized.setdefault(re.sub(r"[_\-]", "", n).lower(), set()).add(n)
    for key, variants in normalized.items():
        check("L3", f"용어 일관: {min(variants)}", len(variants) == 1, f"표기 변형 {sorted(variants)}" if len(variants) > 1 else "")

    # 규칙 일관: ±N% 임계값
    thresholds = {src: set(re.findall(r"±\s*(\d+)\s*%", txt))
                  for src, txt in [("agent-plan", plan), ("AGENTS", agent_md)] + [(n, b) for n, (_, b, _) in skills.items()]}
    declared = set().union(*thresholds.values())
    if declared:
        conflict = [s for s, v in thresholds.items() if v and v != declared]
        check("L3", "규칙 일관: 임계값 ±%", len(declared) == 1 and not conflict,
              f"발견된 값 {sorted(declared)}" if len(declared) > 1 else "")

    # L4 처음부터 끝까지 (기계 판정 부분)
    if chain:
        first_in = skills[chain[0]][0].get("inputs") or []
        plan_flat = plan.replace(" ", "")
        check("L4", "시작 입력이 시나리오와 일치", any(i.replace(" ", "") in plan_flat for i in first_in),
              f"기획서에 없는 입력 {first_in}")
        for t in terminals:
            t_meta, t_body, _ = skills[t]
            tag = f"끝점 {t}" if len(terminals) > 1 else "최종 단계"
            check("L4", f"{tag}: 출력이 시나리오 산출물",
                  any(o.replace(" ", "") in plan_flat for o in (t_meta.get("outputs") or [])),
                  f"기획서에 없는 출력 {t_meta.get('outputs')}")
            check("L4", f"{tag}: 자동 발송 없음", not t_meta.get("writes"), f"끝점이 직접 기록: {t_meta.get('writes')}")
            if has_halt(t_body):
                check("L4", f"{tag}: 휴먼인더루프 명시", True)
            else:
                dfile = pack / "DECISIONS.md"
                dtext = dfile.read_text(encoding="utf-8") if dfile.is_file() else ""
                acknowledged = "결정됨" in dtext and t in dtext and ("검수" in plan or "검수" in agent_md)
                check("L4", f"{tag}: 휴먼인더루프 명시", None if acknowledged else False,
                      "검수 지점 없음 — 팀이 위험으로 수용하고 DECISIONS.md에 기록함" if acknowledged else
                      "본문에 확인 요청·정지가 없음 (수용하려면 DECISIONS.md에 결정을 기록하십시오)")

    fails = [r for r in results if r[2] is False]
    accepted = [r for r in results if r[2] is None]
    for layer in ["L1", "L2", "L3", "L4"]:
        rows = [r for r in results if r[0] == layer]
        print(f"\n[{layer}] {sum(1 for r in rows if r[2])}/{len(rows)} 통과")
        for _, name, ok, detail in rows:
            mark = "✅" if ok is True else ("⚠️" if ok is None else "❌")
            print(f"  {mark} {name}" + (f" — {detail}" if detail and ok is not True else ""))
    print(f"\n{'=' * 50}")
    verdict = "전체 통과 ✅" if not fails else f"실패 {len(fails)}건 ❌"
    if accepted and not fails:
        verdict += f" (수용된 위험 {len(accepted)}건 ⚠️ — 사라지지 않습니다)"
    print(f"기계 판정: {verdict}")
    print(f"산출물 유형: {pack_kind}")
    for line in kind_note:
        print(line)
    if not known_human:
        print("  · 스킬에 human 필드(자동·증강·사람고유)가 없어 태스크 수 판정을 건너뛰었습니다.")
    if mid_human:
        print(f"  ⚠️ 사람고유 지점이 체인 중간에 있습니다: {mid_human}")
        print("     L4는 끝점만 검사하므로, CONTRACT.md의 halt_at에 이 이름을 반드시 넣으십시오.")
    print("주의: L4의 [사람 판정] 2개(실제 실행, 오류 주입)는 별도 수행 필요")
    return 1 if fails else 0


def self_check(repo_dir):
    """저장소 자신을 검사: README 구조도가 실재하는 최상위 폴더를 전부 안내하는가."""
    repo = Path(repo_dir)
    readme = repo / "README.md"
    if not readme.is_file():
        print("❌ README.md 없음")
        return 1
    text = readme.read_text(encoding="utf-8")
    actual = {p.name for p in repo.iterdir() if p.is_dir() and not p.name.startswith((".", "__"))}
    documented = set(re.findall(r"[│├└─\s]([\w.-]+)/", text))
    missing = sorted(actual - documented)
    check("SELF", "README가 모든 최상위 폴더를 안내", not missing, f"구조도에 없는 폴더: {missing}" if missing else "")
    rows = [r for r in results if r[0] == "SELF"]
    for _, name, ok, detail in rows:
        print(f"  {'✅' if ok else '❌'} {name}" + (f" — {detail}" if detail and not ok else ""))
    fails = [r for r in rows if not r[2]]
    print(f"저장소 자기 판정: {'통과 ✅' if not fails else f'실패 {len(fails)}건 ❌'}")
    return 1 if fails else 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "."
    if arg == "--self":
        sys.exit(self_check(Path(__file__).resolve().parent.parent))
    sys.exit(main(arg))
