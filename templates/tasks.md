# Project: [프로젝트명]

## Goal

한 줄로 적는 최종 목표. 북극성 역할. 예: "팀원 5명이 각자 만든 스킬을 하나의 팀 에이전트로 묶고, 처음부터 끝까지 위임되는지 확인한다."

## Current Phase

🔄 Phase 1: 자료 파악

## Phases

### Phase 1: 자료 파악 (intake) 🔄

- [ ] 폴더의 스킬·프롬프트·설계도 전부 읽기
- [ ] 스킬 카드 인벤토리 + 확인표 A·B·C
- [ ] 의도 제안 확인받기

### Phase 2: 워크플로우 인터뷰 (askflow) ⏸️

- [ ] 확인표 통째 확인
- [ ] (없음) 칸만 질문: 팀 정체성 → 데이터 정의 → 결과 반영 → 연동 → 순서 빈틈
- [ ] agent-plan.md 8절 + CONTRACT.md

### Phase 3: 통폐합 (skillmerge) ⏸️

- [ ] 유사도 감사 (check/similarity.py)
- [ ] 합침·흡수·체인·유지 계획 보고 → 승인
- [ ] 합친 스킬 v0 작성, 폐기 스킬 archive/

### Phase 4: 워크플로우 엮기 (weave) ⏸️

- [ ] 맥락 군집 → 체인·갈림길·정지 지점
- [ ] 커버리지 표 (빠진 스킬 0)

### Phase 5: 점검·동작 테스트 (mergechk) ⏸️

- [ ] readchk → DECISIONS.md
- [ ] 계약 게이트 🟢 → L1~L4 통과
- [ ] 사람 판정: 실제 실행 1회, 오류 주입 1회

### Phase 6: 전달 ⏸️

- [ ] 스킬을 만들지 않은 팀원이 README만 보고 쓸 수 있는가
- [ ] 발표·공유 자료

## Key Questions

1. 팀이 실제로 쓰는 표와 칸 이름은?
2. 결과가 기록될 곳은?

## Decisions Made

| Decision | Rationale |
| --- | --- |
| (예) A와 B를 하나로 합침 | 입력·출력·표가 같고 판단기준이 동일 |

## Errors Encountered

| Error | Attempt | Resolution |
| --- | --- | --- |
| (예) 계약 게이트 🔴 기록자 중복 | 1 | 팀이 기록자를 compare-update로 결정 |

## Notes

- 진행할 때마다 Phase 상태를 갱신한다: ⏸️ 대기 → 🔄 진행 → ✅ 완료
- 중요한 결정 전에 이 파일을 다시 읽는다.
- 모든 오류를 기록한다. 같은 삽질을 막는다.
