# Project: skillmergeagent

## Goal

팀원들이 각자 만든 스킬을 파악 → 인터뷰 → 통폐합 → 워크플로우로 엮기 → 검증까지 이끄는, 회사에 묶이지 않는 스킬 스위트를 만든다. paperthin 규약(자기완결 SKILL.md, 사분면, 제거 우선)과 file-based planning(세 파일 메모리)을 따른다.

## Current Phase

✅ Phase 12: 생성 후 한 차례 정리하는 Stop 훅 (로컬 구현·CLI 검증 완료)

### Phase 12: 생성 후 refinement

- [x] 기존 정본·생성 경로와 Codex Stop 프로토콜 확인.
- [x] 세션별 명시적 대상 등록, 1회 재검토, 스냅샷·결과 상태 구현.
- [x] 정리 규칙 단일 문서와 생성 스킬 연결, 로컬 훅 설정.
- [x] CLI 경계·회귀 검사와 실제 파일 정리 시연, 한계 기록. 호스트 자동 재개·독립 모델 평가는 별도 미검증.

인수 조건: 등록된 생성물만 검토; 의미 충돌·고유 예외 보존; 중복은 정본 참조; 변경 없는 경우 no-op; 자동 반복 없음; 검토 미완료와 실행 미검증을 숨기지 않음.

### Phase 11: 최소 정보와 점진적 인터뷰

- [x] 기존 스킬·계약·평가를 읽고 설계 모드와 실행 팩의 경계를 확인.
- [x] intake·askflow·weave·mergechk와 기획서 서식을 수정: 누락/해당 없음/충돌 구분, 질문 한 개씩, 충분하면 즉시 산출.
- [x] README·규약·평가 시나리오 동기화. 합성 입력의 수동 문답과 기존 자동 검사 검증; 실제 고객 인터뷰·전체 모델 반복 평가는 미실시.
- [x] 결과·한계·다음 행동 기록. 원격 게시 및 전역 설치는 하지 않음.

인수 조건: 자료 0개로 시작 가능; 이미 아는 값 재질문 없음; 표 없는 업무에 표 생성 강요 없음; 예외·미결 보존; 단계별 입출력·담당·판단·정지·완료 기준을 갖춘 흐름 생성; 설계 완료와 실제 실행 검증 구분.

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

### Phase 8: 실측 1 (intake를 남이 만든 상류 산출물에) ✅

- [x] Jcurve_SKI `examples/upstream/`(와이어프레임 3개 + ATF 보고서)에 `intake`를 지시문 그대로 수행 → 카드 3장, 확인표 A·B·C, 의도 제안, 인터뷰 목록 6개. 결과는 그 저장소의 `examples/upstream/INTAKE.md`
- [x] 지시문이 비어 있던 자리 5곳을 `intake`에 추가(이름 우선순위, 여러 파일을 태스크 이름으로 잇기, 표가 아닌 저장 위치, 뜻 모르는 코드, 추정 연결 표시)
- [x] 실측 2: 공개 스킬 리포 6개(k-skill 123 · NVIDIA 351 · wshobson 183 · anthropics 20 · superpowers 14 · vercel 1)에 파서·유사도·readchk를 돌림. 깨진 곳 5개를 고침(아래 Errors)
- [ ] 실측 3: 실제 팀 폴더(SKILL.md가 있는 것)에 `intake` → `askflow`까지

### Phase 9: 공식 기준의 빈 곳 채우기 (평가 · 상수 근거) ✅

- [x] 스킬 6개에 `evals/evals.json`(skill-creator 서식) 시나리오 19개. 입력은 `examples/`와 `evals/files/` 고정 자료
- [x] 시나리오 19개를 스킬 있음으로, 핵심 3개 스킬의 10개는 스킬 없음(baseline)으로도 같은 모델(Sonnet)에서 실행하고 채점. 결과는 progress.md
- [x] `similarity.py` 상수마다 근거 쌍을 `check/labels.json`에, 여유 보고를 `check/calibrate.py`에. CI에 추가
- [x] 재도출에서 드러난 오류 1개 수정: 입출력 없는 스킬의 동일 판정을 키워드 겹침 0.8에서 문장 덮임 0.9로 (NVIDIA physical-ai 쌍 오탐)
- [x] `examples/homonym/` (동명이인 쌍) 추가. TXT_SAME의 음성 사례이자 CI 검사
- [ ] LICENSE 파일: package.json은 MIT라 하는데 파일이 없다. 사용자 결정 대기

### Phase 10: 흐름 추정 (규격 없이 본문에서 워크플로우 읽기) ✅

- [x] 실측: 공개 스킬이 서로 이름을 부르는가. superpowers 14개 중 7개, NVIDIA 350개 중 250개, wshobson 183개 중 41개, anthropics 0개(카탈로그)
- [x] `check/flow.py`: 선언·입출력(확정) / 순서·하위스킬·선행지식(추정) / 언급(간선 아님)을 근거 문장과 함께. 시작·끝·고아·군집·"불려도 폴더에 없는 스킬"
- [x] `check/flow_labels.json`: superpowers 11간선 이름표. 맞음 11 · 더 잡음 0 · 놓침 0
- [x] `examples/prose/`: next 없이 본문에만 순서가 적힌 다섯 스킬. CI 검사
- [x] intake(확인표 C를 추정으로 채움) · askflow(통째 확인, 없는 스킬은 하나씩) · weave(확인된 것만 chain)
- [x] 평가 2개(intake 4, weave 4) 실행. 5/5 · 5/5. 채점자 지적: `examples/prose/README.md`가 정답을 적어 두어 단정문 3개가 본문을 안 읽어도 만족된다. 고정 자료의 README는 검사 명세이지 평가 입력이 아니어야 한다
- [x] 실측 3a (읽기 전용): 사용자의 실제 `.claude/skills` 11개. 합침 후보 0, 간선 0(카탈로그), 번들 `/mnt/skills`와 바이트 동일한 복사본 7개 발견, `flow.py` 오탐 1건(XML 이름공간 `w:author`를 팩 접두어로) 수정
- [ ] 실측 3b: 인터뷰. 복사본 7개를 어떻게 할지, `session-start-hook`의 name 불일치는 사용자 결정

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
- [x] H2 공통부분 추출: similarity에 같은 문장 줄 수 축, skillmerge에 여섯 번째 분류(합치지 않고 shared/로 뽑기), examples/shared와 CI 회귀

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
| 유사도 상수는 `labels.json`의 이름표 쌍이 정한다 | Anthropic 지침의 "근거 없는 상수 금지". 상수를 바꾸려면 반대 사례부터 더한다. `calibrate.py`가 여유를 보고하고 CI가 돌린다 |
| 입출력 없는 스킬의 동일 판정은 문장 덮임(0.9)으로 | 키워드 겹침 0.8은 한 틀로 쓴 다른 스킬(덮임 0.77, 키워드 0.87)을 동일로 잡았다. 진짜 중복은 덮임 1.00 |
| 평가는 `skills/<사분면>/<이름>/evals/evals.json`에 | skill-creator가 찾는 자리. 고정 자료는 `evals/files/`에 두고 검증기·파서는 `evals/`를 건너뛴다 |
| 흐름은 규격이 아니라 본문에서 읽는다 | `next`를 쓰는 공개 스킬이 0개. 본문의 이름 부름이 진짜 신호였다. 규격은 입력이 아니라 출력이 된다 |
| 하위스킬 간선도 체인에 넣는다 | superpowers의 REQUIRED SUB-SKILL이 곧 다음 걸음이었다. 빼면 executing-plans가 고아가 된다. 선행지식만 뺀다 |
| 추정 간선은 사람이 확인하기 전에 chain에 넣지 않는다 | 오탐이 있다(예시 나열, 서식 예). 추정인 채로 계약에 들어가면 거짓 계약이다 |
| 공통부분은 합침이 아니라 추출 | 다른 일을 하는 두 스킬이 같은 문단(설정·보일러플레이트)을 들고 있으면 스킬이 아니라 문단을 한 곳으로 옮긴다. 하나의 사실은 한 곳에. 뽑은 뒤 남은 본문이 같아지면 그때 동일이다 |
| planning-with-files로 갈아타지 않고 `planfiles`가 물러나는 규칙을 둔다 | 그쪽은 파일명 고정·단독 소유 전제라 두 스킬이 같은 파일을 쓰면 덮어쓴다. 훅은 특정 호스트의 플러그인 설치에서만 붙어 이식성 이점이 없다. 우리 스킬을 없애면 세 파일 규칙의 집이 사라진다. 물러나는 규칙 한 줄이면 충돌 없이 어느 쪽 팀도 쓴다 |

## Errors Encountered

| Error | Attempt | Resolution |
| --- | --- | --- |
| similarity가 액션아이템추출↔안건정리를 "동명이인"으로 분류 | 1 | io 축을 in/in · out/out 평균으로 변경 → 인접(체인)으로 정정 |
| L3 용어 일관 검사에 문장 조각이 표 이름으로 등장 | 1 | TABLE_RE에서 공백 허용 제거 |
| has_criteria가 본문의 '판단기준' 단어만으로 통과 (M4 미검출) | 1 | 절 제목·→ 줄·조건문만 인정 |
| 절 제목만 인정하니 외부 팩에서 5/5 오탐 | 2 | 예외 절·조건문 인정 + 한 갈래로 묶음 → 1건 |
| 파이썬 패치 heredoc이 본문의 EOF·따옴표에 끊김 | 2 | 패치 스크립트를 파일로 써서 실행 |
| `find_skills`가 `skills/<사분면>/<이름>/`만 찾아 공개 리포 4개에서 스킬 0개 | 1 | skills/ 아래 어느 깊이든 찾게 |
| k-skill 7503쌍 전부, NVIDIA 1840쌍이 "공통부분" | 1 | 리포 공통 틀(5개 이상·30% 이상 스킬이 가진 줄) 제외 + 스텁 판단 보류 |
| 표 괘선 `|---|---|`이 공통 문장으로 셈 | 1 | 글자 3자 없는 줄 제외 |
| `next`가 없는 카탈로그(anthropics 20개)에 readchk가 검수없음 18건 | 1 | 카탈로그 감지 → 흐름 갈래 건너뜀 |
| 영어 스킬의 규칙을 판단기준으로 못 봄(wshobson 42/183) | 1 | 영어 절 제목·조건문 신호 추가 → 175/183 |
| 키워드 겹침 0.8 규칙이 NVIDIA physical-ai 두 DAG(같은 틀, 다른 일)를 동일로 분류 | 1 | 문장 덮임 0.9로 교체, labels.json에 음성으로 고정 |
| `validate-skills.sh`가 `evals/files/` 안의 고정 자료 SKILL.md를 카탈로그 스킬로 검사 | 1 | `-not -path '*/evals/*'`, `find_skills`도 evals/ 제외 |
| 평가 실행 서브에이전트 동시 20개 제한으로 baseline 5개 미실행 | 1 | 자리가 나면 다시 띄움 |
| `flow.py`가 docx·pptx 본문의 XML 이름공간(`w:author`, `a:buChar`, `p:sldIdLst`) 17개를 "불려도 폴더에 없는 스킬"로 냄 | 1 | 팩 접두어 4자 이상, 코드 조각·태그 안은 제외 |

## Notes

- 진행할 때마다 Phase 상태를 갱신한다: ⏸️ 대기 → 🔄 진행 → ✅ 완료
- 중요한 결정 전에 이 파일을 다시 읽는다.
- 모든 오류를 기록한다.
