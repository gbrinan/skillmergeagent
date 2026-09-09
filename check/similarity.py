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


# ── 임계값. 값마다 근거가 되는 실측 쌍이 check/labels.json에 있고, check/calibrate.py가 여유를 보고한다.
#    상수를 바꾸려면 먼저 labels.json에 반대 사례를 더한다. 근거 없는 상수는 두지 않는다.
IO_SAME = 0.6   # 입력끼리·출력끼리 겹침 평균. 동일 쌍(회의록요약↔미팅노트정리)은 1.0, 체인 쌍(액션아이템추출↔안건정리)은 0.25,
                # Jcurve 13개 팩의 비동일 최대 0.17. 0.6은 "다섯 중 셋이 같다"는 뜻이고 양쪽 사이의 빈 구간에 있다.
TAB_SAME = 0.5  # 읽고 쓰는 표 겹침. 홀로는 가르지 못한다: retry-request↔quote-parse는 표가 전부 같아도(1.0) 다른 일이다.
                # io와 함께 써야만 뜻이 있다. 동일 쌍 1.0, 동명이인 쌍 0.67.
TXT_SAME = 0.3  # io·표가 같을 때 동일과 동명이인을 가르는 본문 키워드 겹침. 동일 쌍 0.41, 동명이인 쌍(휴가신청검토↔휴가승인심사) 0.24.
                # 여유가 0.17뿐이다. 실측 쌍이 둘밖에 없으니 가설로 두고, 실제 팀 팩에서 어긋나면 labels.json에 더하고 다시 잰다.
COPY_COVERAGE = 0.9  # 입출력 필드가 없는 스킬(공개 카탈로그)끼리의 동일 판정. 같은 문장이 작은 쪽 본문의 이 비율 이상을 덮어야 한다.
                # NVIDIA 351개 실측: 진짜 중복(nvidia-skill-finder 두 곳)은 1.00, 한 틀로 쓴 다른 스킬(physical-ai 두 DAG)은 0.77.
                # 처음엔 키워드 겹침 0.8로 봤는데 그 쌍이 0.87로 동일에 잡혔다. 키워드는 틀을 못 가르고 문장 덮임이 가른다.
TXT_READ = 0.5  # 분류 없이 "사람이 읽고 판단"으로 올리는 키워드 겹침. NVIDIA 6만 쌍의 무관 분포는 중앙값 0.13, 99분위 0.39.
                # Jcurve의 내용의맥락파악↔워딩(0.89)·공유대상자목록정리↔메일발송(0.55)이 여기 걸렸고 사람이 보니 다른 일이었다.
SHARED_MIN = 3  # 이 줄 수 이상 같은 문장을 공유하면 공통 문단으로 본다. 1~2줄은 관용구(시작 조건 문장)가 겹친 것이었다(Jcurve 실측)
BOILER_MIN_SKILLS, BOILER_RATIO = 5, 0.3  # 이만큼 많은 스킬에 있는 줄은 리포 공통 틀이다. 두 스킬의 공통이 아니다 (k-skill 123개 스텁 실측)
STUB_MAX_LINES = 3  # 틀을 뺀 뒤 남는 문장이 이보다 적으면 본문이 없는 스텁이다
# 점수 가중치는 표 정렬과 --min 표시 컷에만 쓴다. 분류 규칙은 점수를 보지 않는다.
# 순서(io > text > table)는 위의 근거를 따른다: io가 "같은 일"의 정의고, 표 겹침은 홀로 뜻이 없다.
W_IO, W_TAB, W_TXT = 0.45, 0.25, 0.30


def jaccard(a, b):
    if not a and not b:
        return None
    return len(a & b) / len(a | b)


def load(dirs):
    skills = []
    for d in dirs:
        for p in sorted(Path(d).rglob("*.md")):
            if p.name.lower() != "skill.md" or "archive" in p.parts or "evals" in p.parts:
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
    score = W_IO * io_v + W_TAB * tab_v + W_TXT * txt
    cover = shared / max(1, min(len(a["lines"]), len(b["lines"])))  # 같은 문장이 작은 쪽 본문을 얼마나 덮는가
    subset = (a["in"] and a["out"] and b["in"] and b["out"] and
              ((a["in"] <= b["in"] and a["out"] <= b["out"]) or (b["in"] <= a["in"] and b["out"] <= a["out"])))
    if a["stub"] or b["stub"]:
        kind = "스텁(본문 없음) → 판단 보류"  # 본문이 다른 곳에 있다. SKILL.md만으로는 같은 일인지 알 수 없다
    elif io_v >= IO_SAME and tab_v >= TAB_SAME:
        kind = "동일 → 합침 후보" if txt >= TXT_SAME else "동명이인 → 합치지 않음(판단기준 다름, 갈림길 검토)"
    elif not a["has_io"] and not b["has_io"] and cover >= COPY_COVERAGE:
        kind = f"동일(같은 문장이 본문의 {int(cover*100)}%) → 합침 후보"  # 입출력 필드가 없는 스킬은 문장 덮임으로만 판정한다
    elif shared >= SHARED_MIN:
        # 다른 일을 하는데 같은 문단을 들고 있다. 합치는 게 아니라 그 문단을 한 곳으로 뽑는다
        kind = f"공통부분 → 참조 추출(같은 문장 {shared}줄)" + (" +인접" if chain else "")
    elif chain:
        kind = "인접 → 체인(weave)"  # 출력이 입력으로 이어지면 같은 일이 아니라 앞뒤 일이다
    elif subset and tab_v >= 0.5:
        kind = "포함 → 흡수 후보"
    elif txt >= TXT_READ:
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
