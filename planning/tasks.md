# Project: skillmergeagent

## Goal

팀원들이 각자 만든 스킬을 파악 → 인터뷰 → 통폐합 → 워크플로우로 엮기 → 검증까지 이끄는, 회사에 묶이지 않는 스킬 스위트를 만든다. paperthin 규약(자기완결 SKILL.md, 사분면, 제거 우선)과 file-based planning(세 파일 메모리)을 따른다.

## Current Phase

✅ Phase 7: paperthin 점검 반영 (PR #1 두 번째 커밋)

## Phases

### Phase 1: 자료 파악 ✅

- [x] paperthin 전문 읽기 (README · CLAUDE.md · invocation · 스킬 28개 · 검증 스크립트 · CI)
- [x] Jcurve_SKI 읽기 (README · SKILL.md · DESIGN.md · 인터뷰 프롬프트 v1/v2 · 점검 기준 · check/ 스크립트 · 예시 팩 · 페르소나)
- [x] ahastudio file-based-planning-workflow 읽기

### Phase 2: 설계 ✅

- [x] 엔진(이 저장소)과 인스턴스(Jcurve_SKI)를 분리하기로 결정
- [x] 스킬 6개 이름·사분면·호출 방식 확정 (mesh/ 없음)
- [x] 팩 규격은 Jcurve_SKI의 계약 블록·frontmatter와 호환 유지

### Phase 3: 구현 ✅

- [x] skills/ 6개 (Goal · Workflow · Rules · Verification)
- [x] templates/ 9개
- [x] check/ 이식·일반화 (_common · check_contract · run_check · readchk) + similarity 신설
- [x] scripts/validate-skills.sh · plugin.json · CI

### Phase 4: 예시와 검증 ✅

- [x] examples/before (팀원 3명, 스킬 5개, 중복 1쌍) · examples/after (합치고 엮어 통과)
- [x] 유사도 감사가 중복 쌍을 잡고, 계약 게이트 🟢, L1~L4 전체 통과, readchk 미결 0

### Phase 5: 문서 ✅

- [x] README (지도 · 색인 · 흐름 · 산출물 · 세 파일 · 출처)
- [x] CLAUDE.md (철학 · 레이아웃 · 서식 · 규약 · 출하 체크)

### Phase 6: 전달 ✅

- [x] main 시드 + 기능 브랜치 push, PR

### Phase 7: paperthin 점검 반영 ✅

- [x] shower(README·skillmerge 냉독, 별도 세션) · hate(근본 반론 + 첫 못) · mandela(남이 만든 팩으로 독립 검증) · ssotize(규격 재진술 12곳) · dedash(em-dash 95개) · detool
- [x] hate의 첫 못 = 변이 테스트 5개 → 3개 잡음, 2개 못 잡음. `check/mutations.sh`로 CI에 고정
- [x] README·mergechk: "검증" → "구조·계약 판정 + 사람 판정 2개", 알려진 한계 명시
- [x] README 용어표 9개 · 설치 후 위치 · 프로필은 선택 · 호출 방식
- [x] skillmerge: 외부 참조 8개의 뜻과 "없으면" 지침, 판단기준 문장 통일, 스냅샷 단계(H1), archive 위치
- [x] readchk: 판단기준없음 갈래(한 갈래로 묶음) · `check_spec_sync.py`(H3) · CI 2단계 추가
- [x] dedash: em-dash 95개를 역할별로 치환(제목·정의는 콜론, 급전환은 마침표, 덧붙임은 괄호·쉼표). 코드 식별자·URL은 없었음
- [x] planning-with-files: 전환하지 않고 `planfiles`가 물러나는 규칙으로 공존 (아래 결정)
- [ ] 사용자 결정 대기: 공통부분 추출(H2)

## Key Questions

1. `skillmerge`를 model-invoked로 두는 것이 과잉 합침을 부르는가? → 실측 후 판단. 지금은 승인 게이트로 막는다.
2. 상류 산출물 어댑터(설계도 HTML → 팩)를 엔진에 둘 것인가? → 아니오. 형식이 회사마다 달라 프로필 저장소의 몫이다.

## Decisions Made

| Decision | Rationale |
| --- | --- |
| 엔진과 인스턴스를 두 저장소로 | 회사 고유 명사(브랜드 색·세션 번호·상류 도구 형식)가 엔진에 섞이면 다른 팀이 못 쓴다 |
| 스킬 6개, mesh/ 없음 | 소규모 팀의 다관점 검증은 동작 테스트의 상호 검증으로 대체 (제거 우선) |
| 절 제목은 영어(Goal/Workflow/Rules/Verification), 본문은 한국어 | 검증 스크립트와 다른 에이전트가 같은 뼈대를 인식 |
| check/ 스크립트를 Jcurve_SKI에서 복사해 일반화 | 링크로 공유하면 두 저장소 다 자기완결이 깨진다. 규격(계약 블록·frontmatter)은 호환 유지 |
| similarity는 입력끼리·출력끼리 따로 잰다 | 합쳐 재면 A의 출력이 B의 입력인 체인 쌍이 "같은 일"로 보였다 (실측) |
| 표 이름 정규식에서 공백 제거 | "이번 주 회의록이 회의록목록.csv" 같은 문장 조각이 표 이름으로 잡혔다 (실측) |
| 기계 판정을 "검증"이라 부르지 않는다 | 변이 테스트: 본문을 "아무것도 하지 않는다"로 바꿔도 통과. 기계는 구조·계약만 본다 |
| 판단기준 없음은 실패가 아니라 미결(readchk) | 규칙이 불릿으로만 있는 외부 팩(team-agent)에서 4/5 오탐. 막지 않고 보이게 두고 한 갈래로 묶었다 |
| 합치기 전 스냅샷(커밋 또는 archive/_snapshot) | Hermes Curator의 rollback에서 가져옴. 되돌릴 수 없으면 합치지 않는다 |
| 규격 정본은 `_common.py`, 복사본은 `check_spec_sync.py`가 지킨다 | paperthin check-catalog-sync와 같은 자리. 자기완결 복사를 링크로 바꾸지 않는다 |
| planning-with-files로 갈아타지 않고 `planfiles`가 물러나는 규칙을 둔다 | 그쪽은 파일명 고정·단독 소유 전제라 두 스킬이 같은 파일을 쓰면 덮어쓴다. 훅은 특정 호스트의 플러그인 설치에서만 붙어 이식성 이점이 없다. 우리 스킬을 없애면 세 파일 규칙의 집이 사라진다. 물러나는 규칙 한 줄이면 충돌 없이 어느 쪽 팀도 쓴다 |

## Errors Encountered

| Error | Attempt | Resolution |
| --- | --- | --- |
| similarity가 액션아이템추출↔안건정리를 "동명이인"으로 분류 | 1 | io 축을 in/in · out/out 평균으로 변경 → 인접(체인)으로 정정 |
| L3 용어 일관 검사에 문장 조각이 표 이름으로 등장 | 1 | TABLE_RE에서 공백 허용 제거 |
| has_criteria가 본문의 '판단기준' 단어만으로 통과 (M4 미검출) | 1 | 절 제목·→ 줄·조건문만 인정 |
| 절 제목만 인정하니 외부 팩에서 5/5 오탐 | 2 | 예외 절·조건문 인정 + 한 갈래로 묶음 → 1건 |
| 파이썬 패치 heredoc이 본문의 EOF·따옴표에 끊김 | 2 | 패치 스크립트를 파일로 써서 실행 |

## Notes

- 진행할 때마다 Phase 상태를 갱신한다: ⏸️ 대기 → 🔄 진행 → ✅ 완료
- 중요한 결정 전에 이 파일을 다시 읽는다.
- 모든 오류를 기록한다.
