# Findings & Decisions

> **기술적 발견, 중요한 결정이 있을 때마다 이 파일을 즉시 갱신한다.**

## Requirements

- [ ] (예) 견적 메일을 파싱해 비교표를 갱신한다
- [ ] (예) 단가가 ±15% 넘게 변하면 멈추고 사람에게 확인한다

## Research Findings

### 자료 인벤토리 (intake)

| 스킬 | 담당 | 한 일 | 입력 | 출력 | 읽는 표 | 쓰는 표 | 다음 | 사람 여부 | 출처 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| (예) quote-parse | 팀원A | 견적 메일 파싱 | 견적메일 | 파싱결과 | 승인공급사목록.xlsx | (없음) | compare-update | 자동 | skills/depth/quote-parse/SKILL.md |

### 데이터 명세 (askflow)

| 표 이름 | 칸 이름 | 원본 위치(SSOT) | 읽기/쓰기 |
| --- | --- | --- | --- |
| (예) 견적비교표.xlsx | 공급사, 품목, 단가, 납기, 수신일 | 팀 공용 드라이브/구매/ | 쓰기(compare-update) |

## Technical Decisions

| Decision | Rationale |
| --- | --- |
| (예) 회의록요약·미팅노트정리를 하나로 | 입력·출력·표·판단기준 동일 (similarity 0.9) |

## Issues Encountered

### 1. (예) 계약 게이트 🟡 표기 변형

**문제**: `견적_비교표.xlsx` vs `견적비교표.xlsx`

**해결**: REMEDIATION.md 치환안 승인 후 반영

**결과**: 🟢

## Resources

- 기획서(SSOT): `agent-plan.md`
- 계약: `CONTRACT.md`
- 판정 기준: `docs/check-criteria.md`

## Learnings

### (날짜 시각) 제목

한 단락. 다음 세션이 이 절만 읽고도 같은 실수를 피할 수 있게.
