#!/usr/bin/env python3
"""유사 스킬 감사: 통폐합(skillmerge)과 체인(weave)의 후보를 기계적으로 뽑는다.

사용: python3 check/similarity.py <폴더> [<폴더> ...] [--min 0.4] [--all]

여러 팀원의 폴더를 한꺼번에 넣어도 된다. 각 폴더 아래의 SKILL.md/skill.md를 전부 읽어 쌍마다 세 축을 잰다:
  io     입력·출력 이름 겹침 (Jaccard, 표기 정규화)
  table  읽고 쓰는 표 겹침
  text   판단기준·본문 키워드 겹침 (한국어 2글자 이상 어절 + 영단어)
  shared  같은 문장(12자 이상)을 몇 줄 공유하는가. 설정·보일러플레이트가 복사된 흔적
그리고 분류를 제안한다: 동일(합침) · 포함(흡수) · 동명이인(합치지 않음, 갈림길) · 공통부분(합치지 않고 공통 문단을 참조 파일로) · 인접(체인) · 무관.
분류는 제안이지 판정이 아니다. 합칠지는 팀이 정하고, 합침은 승인 뒤에만 한다.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import norm, parse_skill

STOP = {"있다", "없다", "한다", "된다", "하는", "위해", "대한", "경우", "그대로", "않는다", "않는", "이다",
        "the", "and", "for", "with", "that", "this", "from", "not", "are", "is", "to", "of", "in"}


def tokens(body):
    body = re.sub(r"```.*?```", " ", body, flags=re.S)
    toks = set()
    for w in re.findall(r"[가-힣]{2,}|[A-Za-z]{3,}", body):
        w = w.lower()
        if w in STOP:
            continue
        toks.add(w)
        if re.match(r"[가-힣]", w) and len(w) > 2:  # 조사 붙은 어절도 잡히도록 2글자 조각을 더한다
            toks.update(w[i:i + 2] for i in range(len(w) - 1))
    return toks


def lines_of(body):
    """본문의 문장 단위 집합. 불릿·번호를 떼고 12자 이상만 센다. 제목은 뺀다."""
    out = set()
    for raw in re.sub(r"```.*?```", " ", body, flags=re.S).splitlines():
        line = re.sub(r"^\s*(?:[-*]|\d+\.)\s*", "", raw).strip()
        if len(line) >= 12 and not line.startswith("#") and re.search(r"[A-Za-z가-힣0-9]{3}", line):  # 표 괘선 같은 기호 줄은 문장이 아니다
            out.add(line)
    return out


SHARED_MIN = 3  # 이 줄 수 이상 같은 문장을 공유하면 공통 문단으로 본다
BOILER_MIN_SKILLS, BOILER_RATIO = 5, 0.3  # 이만큼 많은 스킬에 있는 줄은 리포 공통 틀이다. 두 스킬의 공통이 아니다
STUB_MAX_LINES = 3  # 틀을 뺀 뒤 남는 문장이 이보다 적으면 본문이 없는 스텁이다


def jaccard(a, b):
    if not a and not b:
        return None
    return len(a & b) / len(a | b)


def load(dirs):
    skills = []
    for d in dirs:
        for p in sorted(Path(d).rglob("*.md")):
            if p.name.lower() != "skill.md" or "archive" in p.parts:
                continue
            meta, body = parse_skill(p)
            if meta is None:
                continue
            f = lambda k: {norm(x) for x in (meta.get(k) or [])}
            skills.append({"name": meta.get("name", p.parent.name), "path": str(p),
                           "in": f("inputs"), "out": f("outputs"), "tab": f("reads") | f("writes"),
                           "writes": f("writes"), "text": tokens(body), "lines": lines_of(body),
                           "has_io": bool(meta.get("inputs") or meta.get("outputs"))})
    # 리포 공통 틀: 많은 스킬이 똑같이 가진 줄(생성된 스텁, 공통 머리말)은 두 스킬의 공통이 아니다
    if len(skills) >= BOILER_MIN_SKILLS:
        df = {}
        for s in skills:
            for line in s["lines"]:
                df[line] = df.get(line, 0) + 1
        boiler = {line for line, n in df.items() if n >= BOILER_MIN_SKILLS and n / len(skills) >= BOILER_RATIO}
        for s in skills:
            s["lines"] = s["lines"] - boiler
            s["stub"] = len(s["lines"]) < STUB_MAX_LINES
        load.boiler = boiler
    else:
        load.boiler = set()
    for s in skills:
        s.setdefault("stub", len(s["lines"]) < STUB_MAX_LINES)
    return skills


def classify(a, b):
    io_a, io_b = a["in"] | a["out"], b["in"] | b["out"]
    # 입력끼리·출력끼리 따로 잰다. 합쳐서 재면 A의 출력이 B의 입력인 체인 쌍이 '같은 일'로 보인다.
    j_in, j_out = jaccard(a["in"], b["in"]), jaccard(a["out"], b["out"])
    parts = [x for x in (j_in, j_out) if x is not None]
    io = sum(parts) / len(parts) if parts else None
    tab = jaccard(a["tab"], b["tab"])
    txt = jaccard(a["text"], b["text"]) or 0.0
    chain = bool(a["out"] & b["in"]) or bool(b["out"] & a["in"])
    shared = len(a["lines"] & b["lines"])
    io_v = io if io is not None else 0.0
    tab_v = tab if tab is not None else io_v
    score = 0.45 * io_v + 0.25 * tab_v + 0.30 * txt
    subset = (a["in"] and a["out"] and b["in"] and b["out"] and
              ((a["in"] <= b["in"] and a["out"] <= b["out"]) or (b["in"] <= a["in"] and b["out"] <= a["out"])))
    if a["stub"] or b["stub"]:
        kind = "스텁(본문 없음) → 판단 보류"  # 본문이 다른 곳에 있다. SKILL.md만으로는 같은 일인지 알 수 없다
    elif io_v >= 0.6 and tab_v >= 0.5:
        kind = "동일 → 합침 후보" if txt >= 0.3 else "동명이인 → 합치지 않음(판단기준 다름, 갈림길 검토)"
    elif not a["has_io"] and not b["has_io"] and txt >= 0.8:
        kind = "동일(본문이 거의 같음) → 합침 후보"  # 입출력 필드가 없는 스킬은 본문으로만 판정한다
    elif shared >= SHARED_MIN:
        # 다른 일을 하는데 같은 문단을 들고 있다. 합치는 게 아니라 그 문단을 한 곳으로 뽑는다
        kind = f"공통부분 → 참조 추출(같은 문장 {shared}줄)" + (" +인접" if chain else "")
    elif chain:
        kind = "인접 → 체인(weave)"  # 출력이 입력으로 이어지면 같은 일이 아니라 앞뒤 일이다
    elif subset and tab_v >= 0.5:
        kind = "포함 → 흡수 후보"
    elif txt >= 0.5:
        kind = "본문 유사 → 사람이 읽고 판단"
    else:
        kind = "무관"
    return score, io, tab, txt, kind


def fmt(v):
    return "-" if v is None else f"{v:.2f}"


def main(argv):
    dirs = [a for a in argv if not a.startswith("--")]
    minimum = 0.4
    if "--min" in argv:
        minimum = float(argv[argv.index("--min") + 1])
        dirs = [d for d in dirs if d != argv[argv.index("--min") + 1]]
    show_all = "--all" in argv
    skills = load(dirs or ["."])
    if len(skills) < 2:
        print("스킬이 2개 미만이라 대조할 쌍이 없습니다")
        return 0
    rows = []
    for i in range(len(skills)):
        for j in range(i + 1, len(skills)):
            score, io, tab, txt, kind = classify(skills[i], skills[j])
            if show_all or kind.startswith(("동일", "포함", "동명", "공통", "인접")) or score >= minimum:
                rows.append((score, skills[i]["name"], skills[j]["name"], io, tab, txt, kind))
    rows = [r for r in rows if not r[6].startswith("스텁")]
    rows.sort(key=lambda r: -r[0])
    stubs = [s["name"] for s in skills if s["stub"]]
    print(f"스킬 {len(skills)}개, 후보 쌍 {len(rows)}개 (점수 ≥ {minimum} 또는 분류가 있는 쌍)")
    if load.boiler:
        print(f"리포 공통 틀 {len(load.boiler)}줄은 공통 문단 계산에서 뺐다 (스킬 {BOILER_MIN_SKILLS}개 이상, {int(BOILER_RATIO*100)}% 이상이 같은 줄)")
    if stubs:
        print(f"스텁(틀을 빼면 본문이 {STUB_MAX_LINES}줄 미만) {len(stubs)}개는 판단 보류: " + ", ".join(stubs[:6]) + (" …" if len(stubs) > 6 else ""))
    print()
    print("| 점수 | A | B | io | table | text | 분류(제안) |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for score, a, b, io, tab, txt, kind in rows:
        print(f"| {score:.2f} | {a} | {b} | {fmt(io)} | {fmt(tab)} | {txt:.2f} | {kind} |")
    merges = [r for r in rows if r[6].startswith(("동일", "포함"))]
    shared = [r for r in rows if r[6].startswith("공통")]
    print()
    if merges:
        print(f"→ 합침·흡수 후보 {len(merges)}쌍. 계획을 보고하고 승인 뒤에만 합칩니다(skillmerge).")
    else:
        print("→ 합침 후보 없음. 빈 결과는 유효합니다. 통폐합을 정당화하려고 유사도를 부풀리지 않습니다.")
    if shared:
        print(f"→ 공통 문단 {len(shared)}쌍. 합치지 않고 그 문단을 참조 파일 하나로 뽑아 두 스킬이 가리키게 합니다.")
        if len(shared) >= 20:  # 쌍이 많으면 한 가족이 한 틀을 나눠 쓰는 것이다. 쌍이 아니라 가족 단위로 보인다
            parent = {}
            def find(x):
                while parent.setdefault(x, x) != x:
                    parent[x] = parent[parent[x]]; x = parent[x]
                return x
            for _, a, b, *_r in shared:
                parent[find(a)] = find(b)
            fam = {}
            for _, a, b, *_r in shared:
                fam.setdefault(find(a), set()).update((a, b))
            fams = sorted(fam.values(), key=len, reverse=True)
            print(f"   가족 {len(fams)}개로 묶입니다. 가족마다 참조 파일 하나면 됩니다:")
            for f in fams[:5]:
                names = sorted(f)
                print(f"   · {len(names)}개: " + ", ".join(names[:4]) + (" …" if len(names) > 4 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
