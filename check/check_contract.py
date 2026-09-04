#!/usr/bin/env python3
"""계약 준수 게이트: 각자 만들어 온 스킬을 통합 점검 전에 거른다.

사용: python3 check/check_contract.py <팩 경로> [--run-check]

종료 코드로 분기한다:
  0 = 🟢 GREEN  계약 준수. --run-check를 주면 곧바로 점검기(run_check.py)를 실행한다.
  1 = 🟡 YELLOW 이름 표기 어긋남. 교정안을 REMEDIATION.md로 쓴다 (기계가 제안, 사람이 반영).
  2 = 🔴 RED    팀 결정이 필요한 충돌. 결정 요청 목록을 출력한다. 자동 교정하지 않는다.

RED가 하나라도 있으면 YELLOW 교정안을 만들지 않는다. 이름부터 고쳐도 소용없기 때문이다(제거 우선).
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import TABLE_RE, find_skills, halt_list, has_halt, next_of, norm, parse_contract, parse_skill

GREEN, YELLOW, RED = 0, 1, 2
findings = []  # (level, 항목, 설명, 교정안 or None)


def finding(level, item, desc, fix=None):
    findings.append((level, item, desc, fix))


def main(pack_dir, run_harness=False):
    pack = Path(pack_dir)
    contract_path = pack / "CONTRACT.md"
    c = parse_contract(contract_path)
    if c is None:
        print(f"🔴 CONTRACT.md(또는 그 안의 ```contract 블록)가 없음: {pack}\n")
        print("   이름을 대조하려면 계약이 하나 필요합니다. templates/CONTRACT.md를 복사해 채우세요.")
        print("   인터뷰(askflow)의 데이터 정의·시나리오·연동 답이 그대로 이 자리에 들어갑니다.")
        return RED

    skills = {}
    for p in find_skills(pack):
        meta, body = parse_skill(p)
        if meta is None:
            finding(RED, p.parent.name, "frontmatter 없음. 계약 대조 불가")
            continue
        skills[meta.get("name", p.parent.name)] = (meta, body, p)
    if not skills:
        print("🔴 스킬을 찾지 못함 (skills/<사분면>/<이름>/SKILL.md)")
        return RED

    t_canon = {norm(t): t for t in c["tables"]}
    p_canon = {norm(x): x for x in c["payloads"]}

    # 1. 표 이름 대조 (frontmatter + 본문)
    for name, (meta, body, path) in skills.items():
        for field in ("reads", "writes"):
            for t in meta.get(field) or []:
                if t in c["tables"]:
                    continue
                if norm(t) in t_canon:
                    finding(YELLOW, name, f"{field}의 표 이름이 계약과 표기가 다름: {t}",
                            (str(path), t, t_canon[norm(t)]))
                else:
                    finding(RED, name, f"{field}에 계약에 없는 표: {t}. 팀이 계약에 추가할지 결정 필요")
        for t in set(TABLE_RE.findall(body)):
            if t not in c["tables"] and norm(t) in t_canon:
                finding(YELLOW, name, f"본문의 표 이름 표기가 다름: {t}", (str(path), t, t_canon[norm(t)]))

    # 2. 단일 기록자 (정규화해서 비교한다. 표기 차이에 가려진 충돌을 잡는다)
    for t, names in c.get("duplicate_writers", {}).items():  # 계약 자체가 한 표에 기록자를 둘 적은 경우
        finding(RED, t, f"계약의 writers에 기록자가 {len(names)}명: {names}. 팀이 한 명으로 정해야 함")
    writers = {}
    for name, (meta, _, _) in skills.items():
        for t in meta.get("writes") or []:
            writers.setdefault(norm(t), []).append(name)
    for nt, ws in writers.items():
        canon = t_canon.get(nt, nt)
        declared = c["writers"].get(canon)
        if len(ws) > 1:
            finding(RED, canon, f"기록자가 {len(ws)}명: {ws}. 계약상 기록자는 "
                                f"{declared or '미지정'}. 팀이 한 명으로 정해야 함")
        elif declared and ws[0] != declared:
            finding(RED, canon, f"계약상 기록자는 {declared}인데 {ws[0]}가 씀. 담당 재확인 필요")

    # 3. 페이로드 이름 대조
    for name, (meta, _, path) in skills.items():
        for field in ("inputs", "outputs"):
            for v in meta.get(field) or []:
                if v in c["payloads"]:
                    continue
                if norm(v) in p_canon:
                    finding(YELLOW, name, f"{field}의 이름 표기가 다름: {v}", (str(path), v, p_canon[norm(v)]))
                else:
                    finding(RED, name, f"{field}에 계약에 없는 이름: {v}. 팀이 페이로드를 정의해야 함")

    # 4. 흐름 (직선·갈림길 모두 허용)
    edges, nodes_in_chain = set(), set()
    for path in c["chain"]:
        nodes_in_chain.update(path)
        edges.update(zip(path, path[1:]))
    for s in [s for s in skills if s not in nodes_in_chain]:
        finding(RED, s, "계약 흐름에 없는 스킬. 어디에 넣을지 팀이 결정 필요")
    for s in [s for s in nodes_in_chain if s not in skills]:
        finding(RED, s, "계약에 있으나 제출되지 않은 스킬. 담당자 확인 필요")
    for a, b in edges:
        if a in skills and b in skills:
            actual = next_of(skills[a][0])
            if b in actual:
                continue
            lvl = YELLOW if any(norm(x) == norm(b) for x in actual) else RED
            finding(lvl, a, f"next가 계약과 다름: {actual or '(없음)'} (계약: {b})",
                    (str(skills[a][2]), f"next: {skills[a][0].get('next')}", f"next: {b}") if lvl == YELLOW else None)

    # 5. 임계값 (자유 서술도 잡는다)
    if c["threshold"]:
        want = re.sub(r"[^\d]", "", c["threshold"])
        for name, (_, body, _) in skills.items():
            nums = set(re.findall(r"(\d+)\s*%", body))
            wrong = nums - {want}
            if wrong:
                finding(RED, name, f"임계값이 계약({c['threshold']})과 다름: {sorted(wrong)}%. "
                                   f"어느 값이 맞는지 팀이 정해야 함")
            elif nums and not re.search(r"±\s*" + want, body):
                finding(YELLOW, name, f"임계값 표기가 계약 형식(±{want}%)과 다름")

    # 6. 정지 지점 (체인 끝뿐 아니라 중간 지점도 검사한다)
    for h in halt_list(c):
        if h in skills:
            meta, body, _ = skills[h]
            if meta.get("writes"):
                finding(RED, h, f"정지 지점인데 표에 기록함: {meta['writes']}. 자동 발송 위험")
            if not has_halt(body):
                finding(RED, h, "정지 지점인데 본문에 확인 요청·정지 문구가 없음. "
                                "체인 중간 지점이면 점검기 L4가 못 보는 자리이므로 여기서 반드시 잡는다")
        else:
            finding(RED, h, "halt_at에 있으나 제출되지 않은 스킬")

    reds = [f for f in findings if f[0] == RED]
    yellows = [f for f in findings if f[0] == YELLOW]
    print(f"계약: {contract_path}")
    print(f"제출 스킬 {len(skills)}개: {sorted(skills)}\n")
    if reds:
        print(f"🔴 팀 결정 필요 {len(reds)}건")
        for _, item, desc, _ in reds:
            print(f"  - [{item}] {desc}")
    if yellows:
        print(f"\n🟡 표기 교정 가능 {len(yellows)}건")
        for _, item, desc, _ in yellows:
            print(f"  - [{item}] {desc}")
    if not reds and not yellows:
        print("🟢 계약 준수. 위반 없음")

    print("\n" + "=" * 55)
    if reds:
        code = RED
        print(f"🔴 RED. 팀이 {len(reds)}건을 결정한 뒤 재검사하세요. 자동 교정하지 않습니다.")
        print("     (이름부터 고쳐도 소용없으므로 YELLOW 교정안도 만들지 않습니다)")
    elif yellows:
        code = YELLOW
        rem = pack / "REMEDIATION.md"
        lines = ["# 계약 표기 교정안", "", "기계가 제안하는 치환입니다. **확인 후 반영**하고 재검사하세요.", ""]
        for _, item, desc, fix in yellows:
            lines.append(f"- **{item}**: {desc}")
            if fix:
                lines.append(f"  - `{fix[0]}`: `{fix[1]}` → `{fix[2]}`")
        rem.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"🟡 YELLOW. 교정안을 {rem}에 썼습니다. 반영 후 재검사하세요.")
    else:
        code = GREEN
        print("🟢 GREEN. 계약 준수. 통합 점검기로 진행합니다.")

    if run_harness:
        if code == GREEN:
            print("\n" + "─" * 55 + "\n→ 통합 점검기 실행\n")
            r = subprocess.run([sys.executable, str(Path(__file__).parent / "run_check.py"), str(pack)])
            return r.returncode
        print("→ 계약 미준수이므로 점검기를 실행하지 않습니다.")
    return code


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.exit(main(args[0] if args else ".", "--run-check" in sys.argv))
