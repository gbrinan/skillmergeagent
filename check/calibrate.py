#!/usr/bin/env python3
"""similarity.py의 임계값이 이름표 쌍(labels.json)을 옳게 가르는지 대조하고, 각 임계값의 여유를 보고한다.

사용: python3 check/calibrate.py [--labels check/labels.json]

임계값은 이 파일이 보고하는 여유에서 나온다. 상수를 바꾸려면 먼저 여기에 반대 사례를 더한다.
이름표 쌍이 하나라도 다르게 분류되면 1로 끝난다. 저장소 밖(external) 쌍은 자료가 없으면 건너뛴다.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import similarity as sim  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def coverage(a, b):
    shared = len(a["lines"] & b["lines"])
    return shared / max(1, min(len(a["lines"]), len(b["lines"])))


def main(argv):
    labels_path = ROOT / "check" / "labels.json"
    if "--labels" in argv:
        labels_path = Path(argv[argv.index("--labels") + 1])
    pairs = json.loads(labels_path.read_text(encoding="utf-8"))["pairs"]
    cache = {}
    rows, skipped, wrong = [], [], []
    for p in pairs:
        d = p["dir"] if p["dir"].startswith("/") else str(ROOT / p["dir"])
        if not Path(d).is_dir():
            skipped.append(p)
            continue
        if d not in cache:
            cache[d] = {s["name"]: s for s in sim.load([d])}
            # 같은 이름이 두 곳에 있는 경우(진짜 중복)를 위해 경로별로도 둔다
            cache[d + "#all"] = sim.load([d])
        allsk = cache[d + "#all"]
        cand_a = [s for s in allsk if s["name"] == p["a"]]
        cand_b = [s for s in allsk if s["name"] == p["b"] and s is not cand_a[0]] if cand_a else []
        if not cand_a or not cand_b:
            skipped.append(p)
            continue
        a, b = cand_a[0], cand_b[0]
        score, io, tab, txt, kind = sim.classify(a, b)
        got = kind.split(" ")[0].split("(")[0]
        ok = got.startswith(p["expect"])
        rows.append((ok, p, io, tab, txt, coverage(a, b), len(a["lines"] & b["lines"]), kind))
        if not ok:
            wrong.append((p, kind))

    print("| 결과 | 쌍 | 기대 | io | table | text | 문장 덮임 | 같은 줄 | 실제 분류 |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    f = sim.fmt
    for ok, p, io, tab, txt, cov, sh, kind in rows:
        print(f"| {'✅' if ok else '❌'} | {p['a']} ↔ {p['b']} | {p['expect']} | {f(io)} | {f(tab)} | {txt:.2f} | {cov:.2f} | {sh} | {kind} |")
    if skipped:
        print(f"\n건너뜀 {len(skipped)}쌍 (자료 없음): " + ", ".join(f"{p['a']}↔{p['b']}" for p in skipped))

    # 임계값의 여유: 각 규칙마다 가장 가까운 양성과 음성
    def near(pred, key):
        pos = [key(r) for r in rows if pred(r[1]["expect"]) and r[0]]
        neg = [key(r) for r in rows if not pred(r[1]["expect"])]
        return (min(pos) if pos else None), (max(neg) if neg else None)

    print("\n임계값의 여유 (규칙 → 가장 약한 양성 / 가장 강한 음성). 둘 사이에 상수가 있어야 한다:")
    same_io = lambda r: r[2] is not None and r[2] >= sim.IO_SAME and (r[3] if r[3] is not None else r[2]) >= sim.TAB_SAME
    pos = [r[2] for r in rows if r[1]["expect"] == "동일" and r[2] is not None]
    neg = [r[2] for r in rows if r[1]["expect"] not in ("동일", "동명이인") and r[2] is not None]  # 동명이인은 io가 같아야 하니 TXT_SAME이 가른다
    print(f"- IO_SAME={sim.IO_SAME}: 동일의 io 최소 {f(min(pos) if pos else None)} / 동일·동명이인이 아닌 쌍의 io 최대 {f(max(neg) if neg else None)}")
    pos = [r[4] for r in rows if r[1]['expect'] == '동일' and same_io(r)]
    neg = [r[4] for r in rows if r[1]['expect'] == '동명이인' and same_io(r)]
    print(f"- TXT_SAME={sim.TXT_SAME}: io·표가 같은 쌍에서 동일의 text 최소 {f(min(pos) if pos else None)} / 동명이인의 text 최대 {f(max(neg) if neg else None)}")
    pos = [r[5] for r in rows if r[1]['expect'] == '동일' and not same_io(r)]
    neg = [r[5] for r in rows if r[1]['expect'] != '동일']
    print(f"- COPY_COVERAGE={sim.COPY_COVERAGE}: 입출력 없는 동일의 덮임 최소 {f(min(pos) if pos else None)} / 그 밖의 덮임 최대 {f(max(neg) if neg else None)}")
    pos = [r[4] for r in rows if r[1]['expect'] == '본문']
    neg = [r[4] for r in rows if r[1]['expect'] == '무관']
    print(f"- TXT_READ={sim.TXT_READ}: '사람이 읽음'의 text 최소 {f(min(pos) if pos else None)} / 무관의 text 최대 {f(max(neg) if neg else None)}")
    if wrong:
        print(f"\n❌ 이름표와 다른 분류 {len(wrong)}쌍:")
        for p, kind in wrong:
            print(f"   {p['a']} ↔ {p['b']}: 기대 {p['expect']}, 실제 {kind}. 이유: {p['why']}")
        return 1
    print(f"\n✅ 이름표 {len(rows)}쌍 전부 기대대로 분류됨")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
