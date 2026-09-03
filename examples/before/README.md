# before — 통폐합 전, 팀원 3명이 각자 만들어 온 스킬

같은 팀(주간 회의 준비)의 세 사람이 서로 상의 없이 만든 스킬 5개다. 계약도 기획서도 없다.
`intake` → `askflow` → `skillmerge` → `weave` → `mergechk`를 거친 결과가 [`../after/`](../after/)다.

```bash
python3 check/similarity.py examples/before
```

를 돌리면 `회의록요약`(팀원A)과 `미팅노트정리`(팀원B)가 **동일 → 합침 후보**로 뜬다. 입력·출력·읽는 표가 같고(표기만 `회의록목록.csv` vs `회의록_목록.csv`), 판단기준도 같다.
`액션아이템추출 → 안건정리`는 **인접 → 체인**으로 뜬다. 합치지 않고 `weave`가 잇는다.
