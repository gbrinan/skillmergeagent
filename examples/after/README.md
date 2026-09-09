# 주간회의준비 에이전트

사용법 3줄:
1. 회의록목록.csv에 이번 주 회의록을 등록하면 흐름이 돈다.
2. 결과는 액션아이템.csv와 주간안건.csv, 그리고 팀장에게 갈 안건 초안으로 나온다.
3. 마지막 단계(안건확정)에서 팀장이 확인해야 끝난다. 회의 공지는 자동으로 나가지 않는다.

상세는 [agent-plan.md](agent-plan.md) 참조 (SSOT). 통폐합 전 상태는 [`../before/`](../before/).

```bash
python3 check/readchk.py examples/after
python3 check/check_contract.py examples/after --run-check
```
