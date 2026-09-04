#!/usr/bin/env python3
"""스킬마다 evals/evals.json이 있고 시나리오가 3개 이상인지, 서식이 맞는지 본다. CI가 돌린다."""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_EVALS = 3  # Anthropic 스킬 지침: 스킬마다 평가 3개 이상


def main():
    skills = sorted(glob.glob(str(ROOT / "skills/*/*/SKILL.md")))
    bad = 0
    for s in skills:
        f = Path(s).parent / "evals" / "evals.json"
        if not f.is_file():
            print(f"❌ {f.relative_to(ROOT)} 없음"); bad += 1; continue
        d = json.loads(f.read_text(encoding="utf-8"))
        evals = d.get("evals", [])
        if len(evals) < MIN_EVALS:
            print(f"❌ {f.relative_to(ROOT)}: 시나리오 {len(evals)}개 (< {MIN_EVALS})"); bad += 1
        for e in evals:
            for k in ("id", "name", "prompt", "expected_output", "files", "expectations"):
                if k not in e:
                    print(f"❌ {f.relative_to(ROOT)} #{e.get('id')}: {k} 없음"); bad += 1
            for rel in e.get("files", []):
                if not (ROOT / rel).exists():
                    print(f"❌ {f.relative_to(ROOT)} #{e.get('id')}: 입력 {rel} 없음"); bad += 1
        if d.get("skill_name") != Path(s).parent.name:
            print(f"❌ {f.relative_to(ROOT)}: skill_name이 폴더와 다름"); bad += 1
    print(f"{'✅' if not bad else '❌'} 평가 파일 {len(skills)}개, 시나리오 {sum(len(json.loads((Path(s).parent/'evals'/'evals.json').read_text(encoding='utf-8')).get('evals', [])) for s in skills if (Path(s).parent/'evals'/'evals.json').is_file())}개")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
