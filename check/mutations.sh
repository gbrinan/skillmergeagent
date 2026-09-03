#!/usr/bin/env bash
# 변이 테스트 — 점검기가 "살아 있는 팩"과 "구조만 남은 팩"을 구별하는지 고정한다.
# examples/after를 복사해 의미만 부순 변이 5개를 넣고, 잡아야 할 것은 잡고(🔴 또는 미결)
# 못 잡는 것은 "알려진 한계"로 명시한다. 한계가 조용히 사라지거나 늘면 여기서 실패한다.
set -u
cd "$(dirname "$0")/.."
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
fail=0
gate() { python3 check/check_contract.py "$1" --run-check >/dev/null 2>&1; echo $?; }
forks() { python3 check/readchk.py "$1" 2>/dev/null | grep -oE "미결 [0-9]+건" | grep -oE "[0-9]+" || echo 0; }
expect() { # name actual expected
  if [ "$2" = "$3" ]; then echo "  ✅ $1 → $2"; else echo "  ❌ $1 → $2 (기대 $3)"; fail=1; fi; }

cp -r examples/after "$T/m0"
echo "M0 원본"; expect "gate exit" "$(gate $T/m0)" 0; expect "readchk 미결" "$(forks $T/m0)" 0

cp -r examples/after "$T/m2"; sed -i 's/^chain: .*/chain: 안건확정 -> 안건정리 -> 액션아이템추출 -> 회의록요약/' "$T/m2/CONTRACT.md"
echo "M2 체인 순서 뒤집기 (이름 그대로)"; expect "gate exit" "$(gate $T/m2)" 2

cp -r examples/after "$T/m3"; sed -i 's/^writes: \[\]$/writes: [주간안건.csv]/; s/확인 요청하고 멈춘다/그대로 발송한다/' "$T/m3/skills/depth/안건확정/SKILL.md"
echo "M3 정지 지점이 표에 기록 + 확인 문구 삭제"; expect "gate exit" "$(gate $T/m3)" 2

cp -r examples/after "$T/m5"; sed -i 's/^threshold: .*/threshold: ±15%/' "$T/m5/CONTRACT.md"
sed -i 's/^## 절차/단가가 ±50% 넘게 변하면 멈춘다.\n\n## 절차/' "$T/m5/skills/coil/안건정리/SKILL.md"
echo "M5 임계값이 문서마다 다름"; expect "gate exit" "$(gate $T/m5)" 2

cp -r examples/after "$T/m4"; python3 - "$T/m4" <<'EOF'
import re, sys
from pathlib import Path
p = Path(sys.argv[1]) / "skills/depth/회의록요약/SKILL.md"
p.write_text(re.sub(r"## 판단기준.*?(?=## 산출물)", "", p.read_text(), flags=re.S))
EOF
echo "M4 판단기준·예외 절 삭제 (규칙 문장이 하나도 안 남음)"; expect "gate exit (구조는 통과)" "$(gate $T/m4)" 0; expect "readchk 미결" "$(forks $T/m4)" 1

cp -r examples/after "$T/m1"; python3 - "$T/m1" <<'EOF'
import sys
from pathlib import Path
p = Path(sys.argv[1]) / "skills/depth/액션아이템추출/SKILL.md"
t = p.read_text(); fm = t.split("---")[1]
p.write_text("---" + fm + "---\n\n# 액션아이템추출\n\n## 절차\n1. 아무것도 하지 않는다. 그래도 액션아이템.csv 에 기록한다고 적어 둔다.\n")
EOF
echo "M1 본문을 '아무것도 하지 않는다'로 (알려진 한계 — 기계는 의미를 못 본다)"
expect "gate exit" "$(gate $T/m1)" 0; expect "readchk 미결 (판단기준 없음으로만 잡힘)" "$(forks $T/m1)" 1

echo
if [ "$fail" -eq 0 ]; then echo "✓ 변이 5개: 잡아야 할 3개는 🔴, 판단기준 삭제는 미결, 본문 무의미는 알려진 한계"; else echo "✗ 변이 회귀 실패"; exit 1; fi
