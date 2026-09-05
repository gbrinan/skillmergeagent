#!/usr/bin/env python3
"""흐름 추정: 스킬 더미가 어떤 워크플로우를 만들 수 있는지, 스킬 본문이 서로를 부르는 문장에서 읽어낸다.

사용: python3 check/flow.py <폴더> [<폴더>...] [--json] [--labels check/flow_labels.json]

frontmatter의 `next`가 없어도 된다. 공개 스킬 692개 중 `next`를 쓰는 것은 0개였고,
그 대신 본문이 "그다음 X를 쓴다", "REQUIRED SUB-SKILL: X"처럼 서로를 부른다(superpowers 14개 중 7개, NVIDIA 350개 중 250개).
간선마다 근거 문장을 원문 그대로 단다. 근거 없는 간선은 만들지 않는다. 추정 간선은 사람이 확인하기 전에는 계약의 chain이 되지 않는다.

관계 종류 (뭉개지 않는다. 순서와 선행지식은 다른 것이다):
  선언     frontmatter next            확정
  입출력   A.outputs ∩ B.inputs         확정
  순서     "그다음·then·after·먼저"      추정 → 확인표 C 후보
  하위스킬 "호출·invoke·use the X skill" 추정 → 체인이 아니라 A 안에서 B를 부름
  선행지식 "REQUIRED BACKGROUND·먼저 알아야" 추정 → 체인이 아니라 읽을 순서
  언급     그 밖의 이름 부름             간선 아님. 보고만
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_skills, norm, parse_skill  # noqa: E402

# 관계 신호. 위에서부터 먼저 맞는 것이 이긴다. superpowers 10쌍(flow_labels.json)이 근거다.
CUES = [
    ("선행지식", re.compile(r"required background|must understand|prerequisite|before (using|reading) this|선행|먼저 알아|알아야", re.I)),
    ("하위스킬", re.compile(r"required sub-?skill|\binvoke\b|\bcall(s|ing)?\b|use (the )?[`'\"]?[\w:-]+[`'\"]? skill|호출|불러|사용한다|스킬을 쓴다|스킬로 받", re.I)),
    ("순서", re.compile(r"\b(then|next|after|afterwards|followed by|proceed to|hand ?off|first)\b|→|->|그다음|다음 (단계|스킬)|이후|뒤에|넘긴|넘겨|이어서|끝나면|되면", re.I)),
]
# 폴더에 없는 스킬을 부르는 꼴. 이름을 모르니 문장 꼴로 잡는다. 한글 "X로 넘긴다"·"X 스킬", 영어 "use the X skill"·"pack:X"
TARGET_SHAPES = [
    re.compile(r"([가-힣][\w가-힣-]{1,}?)(?:으로|로)\s+(?:넘긴|넘겨|보낸|이어)"),  # 비탐욕: "견적발송으로"에서 "견적발송". 두 글자는 아래서 거른다
    re.compile(r"([가-힣][\w가-힣-]{2,}) 스킬(?:을|로|이|은)"),
    re.compile(r"(?:use|invoke) (?:the )?[`'\"]?([A-Za-z][\w-]{2,})[`'\"]? skill", re.I),
    # 팩 접두어 "superpowers:X". 접두어는 4자 이상. XML 이름공간(w:author, a:buChar, p:sldIdLst)이 여기 걸렸다(.claude 실측)
    re.compile(r"(?<![\w/<`])[a-z][\w-]{3,}:([a-z][\w-]{2,})(?![\w-]*[>`])"),
]
KO_STOP = {"해당", "모든", "다른", "이전", "이후", "각각", "다음", "위의", "아래"}
EXAMPLE_LIST = re.compile(r"(examples?|e\.g\.|such as|good:|bad:|✅|❌|예:|예시|같은 스킬|와 달리|처럼)", re.I)  # 나열·서식 예시는 관계가 아니다


def load(dirs):
    skills = {}
    for d in dirs:
        for p in find_skills(d) or sorted(Path(d).rglob("SKILL.md")):
            meta, body = parse_skill(p)
            if meta is None:
                continue
            name = str(meta.get("name") or p.parent.name)
            skills[name] = {"path": str(p), "meta": meta, "text": body + "\n" + str(meta.get("description") or ""),
                            "in": {norm(x) for x in (meta.get("inputs") or [])},
                            "out": {norm(x) for x in (meta.get("outputs") or [])},
                            "next": [s.strip() for s in re.split(r"[|,]", str(meta.get("next") or "")) if s.strip() and s.strip().lower() != "null"]}
    return skills


def name_pattern(names):
    # 한글 이름은 조사가 붙으므로(견적산출로) 뒤 경계를 요구하지 않는다. 긴 이름부터 맞춘다
    parts = []
    for n in sorted(names, key=len, reverse=True):
        if len(n) < 3:
            continue
        e = re.escape(n)
        parts.append(e if re.search(r"[가-힣]", n) else e + r"(?![\w-])")
    return re.compile(r"(?<![\w-])(" + "|".join(parts) + r")") if parts else None


def infer(skills):
    edges = []  # (src, dst, kind, evidence)
    seen = set()
    pat = name_pattern(skills)
    for n, s in skills.items():
        for t in s["next"]:
            edges.append((n, t, "선언", "frontmatter next"))
            seen.add((n, t))
        for m, o in skills.items():
            if m != n and s["out"] & o["in"] and (n, m) not in seen:
                edges.append((n, m, "입출력", f"outputs∩inputs = {sorted(s['out'] & o['in'])}"))
                seen.add((n, m))
    if pat is None:
        return edges
    for n, s in skills.items():
        for line in re.split(r"(?<=[.!?。])\s+|\n", re.sub(r"```.*?```", " ", s["text"], flags=re.S)):
            hits = {h for h in pat.findall(line) if h != n}
            if not hits:
                continue
            kind = "언급"
            if not EXAMPLE_LIST.search(line):
                for k, cue in CUES:
                    if cue.search(line):
                        kind = k
                        break
            for h in hits:
                key = (n, h, kind)
                if key in seen or (n, h) in seen and kind != "언급":
                    continue
                seen.add(key)
                edges.append((n, h, kind, line.strip()[:110]))
    return edges


def missing_targets(skills):
    """본문이 부르는데 폴더에 없는 이름. 증거 문장을 단다. 일반 명사가 섞일 수 있어 보고만 한다."""
    known = set(skills)
    out = {}
    for n, s in skills.items():
        for line in re.sub(r"```.*?```", " ", s["text"], flags=re.S).splitlines():
            if EXAMPLE_LIST.search(line):
                continue
            line = re.sub(r"`[^`]*`|<[^>]*>", " ", line)  # 코드 조각·태그 안의 이름은 스킬이 아니다
            for shape in TARGET_SHAPES:
                for m in shape.finditer(line):
                    t = m.group(1)
                    if t in known or t == n or t.lower() in ("this", "that", "the", "a", "an"):
                        continue
                    if re.search(r"[가-힣]", t) and (len(t) < 3 or t in KO_STOP):  # 두 글자 일반 명사(발송·다음)는 이름이 아니다
                        continue
                    out.setdefault(t, (n, line.strip()[:90]))
    return out


def report(skills, edges):
    # 체인에 드는 관계: 선언·입출력(확정), 순서·하위스킬(추정). 하위스킬은 "A 안에서 B를 부른다"이지만 워크플로우 덮임으로는 한 걸음이다.
    # 선행지식은 읽을 순서이지 실행 순서가 아니라 뺀다. superpowers의 REQUIRED SUB-SKILL이 곧 다음 걸음이었다.
    chain = [e for e in edges if e[2] in ("선언", "입출력", "순서", "하위스킬")]
    indeg, outdeg = {}, {}
    for a, b, _, _ in chain:
        outdeg[a] = outdeg.get(a, 0) + 1
        indeg[b] = indeg.get(b, 0) + 1
    known = set(skills)
    missing = {b: (a, ev) for a, b, k, ev in edges if b not in known and k != "언급"}
    for t, (src, ev) in missing_targets(skills).items():
        missing.setdefault(t, (src, ev))
    starts = [n for n in skills if outdeg.get(n) and not indeg.get(n)]
    ends = [n for n in skills if indeg.get(n) and not outdeg.get(n)]
    orphans = [n for n in skills if not indeg.get(n) and not outdeg.get(n)]
    # 군집: 체인·하위스킬·선행지식 간선으로 이어진 연결 요소
    parent = {}
    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, b, k, _ in edges:
        if k != "언급" and b in known:
            parent[find(a)] = find(b)
    groups = {}
    for n in skills:
        groups.setdefault(find(n), []).append(n)
    clusters = sorted(groups.values(), key=len, reverse=True)
    return {"chain": chain, "starts": starts, "ends": ends, "orphans": orphans, "missing": missing,
            "clusters": clusters, "edges": edges}


def main(argv):
    dirs = [a for a in argv if not a.startswith("--") and not a.endswith(".json")]
    labels = argv[argv.index("--labels") + 1] if "--labels" in argv else None
    skills = load(dirs or ["."])
    edges = infer(skills)
    r = report(skills, edges)
    if "--json" in argv:
        print(json.dumps({**r, "missing": {k: list(v) for k, v in r["missing"].items()}, "skills": sorted(skills)}, ensure_ascii=False, indent=2))
        return 0
    print(f"스킬 {len(skills)}개. 간선 {len(edges)}개 (언급 제외 {sum(1 for e in edges if e[2] != '언급')}개)\n")
    print("| 관계 | A | B | 근거 문장 |\n| --- | --- | --- | --- |")
    order = {"선언": 0, "입출력": 1, "순서": 2, "하위스킬": 3, "선행지식": 4, "언급": 5}
    for a, b, k, ev in sorted(edges, key=lambda e: (order[e[2]], e[0], e[1])):
        mark = " (추정)" if k in ("순서", "하위스킬", "선행지식") else ""
        ev = ev.replace("|", "\\|")
        print(f"| {k}{mark} | {a} | {b} | {ev} |")
    print()
    print(f"시작점: {', '.join(r['starts']) or '(없음)'}")
    print(f"끝점: {', '.join(r['ends']) or '(없음)'}")
    print(f"고아(어디에도 안 붙음): {', '.join(r['orphans']) or '(없음)'}")
    print("불려도 폴더에 없는 스킬: " + (", ".join(f"{t} ({src}: {ev[:40]}…)" for t, (src, ev) in sorted(r["missing"].items())) or "(없음)"))
    print(f"군집 {len(r['clusters'])}개: " + " / ".join(f"{len(c)}개({', '.join(c[:3])}{' …' if len(c) > 3 else ''})" for c in r["clusters"]))
    n_infer = sum(1 for e in r["chain"] if e[2] in ("순서", "하위스킬"))
    if n_infer:
        print(f"\n→ 순서·하위스킬 간선 {n_infer}개는 추정입니다. 확인표 C에 (추정)으로 올리고 사람이 확인하기 전에는 chain에 넣지 않습니다.")
    if not r["chain"] and len(skills) > 1:
        print("\n→ 순서 간선이 없습니다. 카탈로그(서로 부르지 않는 스킬 묶음)이거나, 순서가 파일 밖에 있습니다. askflow가 묻습니다.")
    if labels:
        return score(edges, labels)
    return 0


def score(edges, path):
    """이름표(기대 간선)와 대조해 정밀도·재현율을 보고한다. 자료가 없으면 건너뛴다."""
    want = json.loads(Path(path).read_text(encoding="utf-8"))
    got = {(a, b, k) for a, b, k, _ in edges if k != "언급"}
    exp = {(e["a"], e["b"], e["kind"]) for e in want["edges"]}
    tp = got & exp
    fp = got - exp
    fn = exp - got
    print(f"\n이름표 대조 ({path}): 맞음 {len(tp)} / 더 잡음 {len(fp)} / 놓침 {len(fn)}")
    for a, b, k in sorted(fp):
        print(f"  더 잡음: {a} → {b} ({k})")
    for a, b, k in sorted(fn):
        print(f"  놓침:   {a} → {b} ({k})")
    must = {(e["a"], e["b"], e["kind"]) for e in want["edges"] if e.get("must")}
    bad = must - got
    if bad:
        print(f"❌ 반드시 잡아야 할 간선 {len(bad)}개를 놓쳤습니다")
        return 1
    print("✅ 반드시 잡아야 할 간선은 전부 잡았습니다")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
