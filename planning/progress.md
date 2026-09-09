# Progress Log

> 각 단계를 완료하거나 문제가 생기면 갱신한다. 날짜 오름차순.

## Session 2026-09-03

### Phase 1~2: 자료 파악 · 설계 ✅

**작업 내역**:

1. paperthin 전문(스킬 28개·규약·검증 스크립트), Jcurve_SKI 전체, ahastudio 문서를 읽음
2. 엔진(이 저장소) / 인스턴스(Jcurve_SKI) 분리, 스킬 6개 확정

### Phase 3~5: 구현 · 예시 · 문서 ✅

**작업 내역**:

1. skills/ 6개, templates/ 9개, check/ 4개 + _common, scripts/validate-skills.sh, CI
2. examples/before·after, README, CLAUDE.md
3. similarity io 축·표 이름 정규식 수정 (Error Log)

**생성/수정 파일**: 저장소 전체 (첫 커밋)

## Session 2026-09-03 (2)

### Phase 7: paperthin 점검 반영 ✅

**작업 내역**:

1. shower(README·skillmerge) · hate · mandela · ssotize · dedash · detool 실행, 결과는 findings.md
2. `check/mutations.sh`(변이 5개) · `check/check_spec_sync.py`(규격 가드) 신설, CI에 추가
3. README(용어표·설치 후 위치·프로필 선택·호출) · mergechk(알려진 한계) · skillmerge(외부 참조 표·스냅샷·문장 통일) · check-criteria(알려진 한계 절) · CLAUDE.md(규격 정본) 수정
4. readchk에 판단기준없음 갈래(한 갈래로 묶음), `_common.py`에 규격 정본과 `has_criteria`

**생성/수정 파일**: `check/mutations.sh`, `check/check_spec_sync.py` (신규) · `check/_common.py`, `check/readchk.py`, `check/run_check.py`, `README.md`, `CLAUDE.md`, `docs/check-criteria.md`, `skills/breadth/skillmerge/SKILL.md`, `skills/depth/mergechk/SKILL.md`, `.github/workflows/ci.yml`, `planning/*` (수정)

## Test Results

| Test | Input | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| validate-skills.sh | skills/ 6개 | 통과 | 통과 (6 skills) | ✅ |
| run_check.py --self | README 구조도 | 최상위 폴더 전부 안내 | 통과 | ✅ |
| similarity.py | examples/before | 회의록요약↔미팅노트정리 합침 후보 | 1.00/1.00/0.41 동일 → 합침 후보 | ✅ |
| check_contract.py --run-check | examples/after | 🟢 → L1~L4 전체 통과 | 🟢, 47/47 통과 | ✅ |
| readchk.py | examples/after | 미결 0, DECISIONS.md 변경 없음 | 미결 0 | ✅ |
| mutations.sh | examples/after 변이 5개 | 🔴 3 · 미결 1 · 알려진 한계 1 | 같음 | ✅ |
| check_spec_sync.py | templates · CLAUDE.md · docs | 정본과 일치 | 필드 9 · 키 6 · 값 3 일치 | ✅ |
| check_contract.py --run-check (외부) | Jcurve_SKI team-agent · ax-share-agent | 🟢 전체 통과 | 🟢 전체 통과 | ✅ |
| check_contract.py --run-check (외부) | Jcurve_SKI report-wording-pack | 원본과 같은 결과 | `data/` 없음 L1 실패 (원본 동일) | ✅ |
| readchk.py (외부) | team-agent | 오탐 최소 | 판단기준없음 1건(4스킬 묶음) | ⚠️ |
| dedash | 저장소 전체(.git 제외) | em-dash 0개, 검사 전부 통과 | 95 → 0, 전부 통과 | ✅ |
| similarity.py | examples/shared | 공통부분 → 참조 추출, 합침 아님 | 같은 문장 6줄, 참조 추출 | ✅ |
| similarity.py (외부) | Jcurve 두 팩 9스킬 | 공통부분 오탐 0 | 0 | ✅ |
| intake (사람이 지시문대로) | Jcurve upstream 와이어프레임 3 + ATF 1 | 카드·확인표·제안, 지어낸 값 0 | 카드 3, (없음) 9칸, (추정) 2곳, 인터뷰 항목 6 | ✅ |
| parse_skill | 공개 리포 6개 692 SKILL.md | 전부 파싱 | 692/692 | ✅ |
| similarity.py | k-skill 123 | 스텁은 판단 보류, 합침 후보 0 | 스텁 123, 후보 0 | ✅ |
| similarity.py | NVIDIA 351 | 진짜 중복은 잡고 가족은 묶음 | 동일 2, 가족 25(57·30·11·11·8…) | ✅ |
| similarity.py | anthropics · superpowers · wshobson | 오탐 최소 | 합침 0, 공통부분 1·0·3 | ✅ |
| readchk.py | anthropics 20개(카탈로그) | 흐름 갈래 없음 | 판단기준 없음 1건(5스킬)만 | ✅ |
| calibrate.py | labels.json 10쌍(저장소 5 + 바깥 5) | 전부 기대대로, 상수마다 양성·음성 사이 | 10/10. COPY_COVERAGE 1.00 vs 0.77, TXT_SAME 0.41 vs 0.24 | ✅ |
| mutations.sh | M6 writers 중복 | 🔴 + "기록자가 2명" | exit 2, 문구 1 | ✅ |
| 평가 1회차 (Sonnet, 스킬 있음) | 19 시나리오 82 단정문 | 통과율과 떨어진 자리 | 75/82 (0.91). 떨어짐: askflow 질문 2개, intake 혼합 2, planfiles 물러남 뒤 갱신 없음, weave 갈림길 오판 2, weave 동명이인에 skillmerge 재제안 | ⚠️ |
| 평가 1회차 (Sonnet, 스킬 없음) | 핵심 3스킬 10 시나리오 45 단정문 | 스킬 있음보다 낮게 | 28/45 (0.62). 승인 없이 파일 변경 2건, 확인표·(없음) 없음, weave·askflow로 안 넘김 | ✅ |
| 평가 2회차 (규칙 고친 뒤 재실행) | intake-혼합 · mergechk-주입 · skillmerge-승인합침 · weave-체인 | 고친 자리가 통과 | 3/6 · 4/4 · 5/7 · 4/4. weave 2→4, mergechk 중복 문구 확인, skillmerge 보류 사항 보존됐으나 대조표 없음·next 갈림길, intake는 다른 자리에서 떨어짐 | ⚠️ |
| 평가 3회차 (skillmerge `next` 규칙 뒤) | skillmerge-승인합침 | 7/7 | 7/7. 대조표 있음, next는 남길 스킬 값 유지 + 팀 결정으로 보고 | ✅ |
| flow.py | examples/prose 5개 | 순서 2 · 하위스킬 1 · 고아 1 · 없는 스킬 1 · 나열은 언급 | 그대로 | ✅ |
| flow.py --labels | superpowers 14개, 이름표 11간선 | 놓침 0 | 맞음 11 · 더 잡음 0 · 놓침 0 | ✅ |
| flow.py | anthropics 20개 | 간선 0 (카탈로그) | 0 | ✅ |
| flow.py · similarity · readchk (실측 3a) | 사용자 .claude/skills 11개 + /mnt/skills 41개 | 오탐 없이 판정 | 카탈로그, 합침 0, 바이트 동일 복사본 7, flow 오탐 17건 → 0 | ⚠️ |
| 평가 4회차 (Sonnet) | intake-prose · weave-확인간선만 | 추정 간선에 근거 문장, 확인된 것만 chain | 5/5 · 5/5. 채점자: prose README가 정답을 주어 단정문 3개가 가르지 못함, weave의 계약에 writers 없는 표 하나(단정문 없음) | ⚠️ |

## Session 2026-09-04 (3)

### Phase 9: 평가 · 상수 근거 · 채점에서 찾은 결함 수정 ✅

- 평가 19개 작성(skill-creator 서식), Sonnet 서브에이전트 33회 실행(스킬 있음 23, 없음 10), 채점자 서브에이전트 23회
- 상수 재도출: `check/labels.json` · `check/calibrate.py`, `COPY_COVERAGE` 규칙 교체, `examples/homonym/` 추가
- 채점에서 찾은 결함 수정: 계약 파서 writers 중복(변이 M6), skillmerge 대조표·`next` 규칙, weave 미결 규칙, intake 인터뷰 항목 규칙
- 생성·수정: `skills/*/*/evals/`, `check/calibrate.py`, `check/labels.json`, `examples/homonym/`, `check/_common.py`, `check/check_contract.py`, `check/mutations.sh`, `check/similarity.py`, `scripts/validate-skills.sh`, `.github/workflows/ci.yml`, `docs/check-criteria.md`, `README.md`, `CLAUDE.md`, 스킬 4개

## Session 2026-09-05

### Phase 10: 흐름 추정 ✅

- 신호 측정(4개 리포) → `check/flow.py` → `check/flow_labels.json`(superpowers 11간선 11/11) → `examples/prose/` → intake·askflow·weave 지시문 → CI · 문서 · 평가 2개 추가(미실행)
- 생성·수정: `check/flow.py`, `check/flow_labels.json`, `examples/prose/`, 스킬 3개, 평가 2개, `docs/check-criteria.md`, `README.md`, `CLAUDE.md`, `.github/workflows/ci.yml`, `planning/`

## Session 2026-09-09

### Phase 11: 정보가 부족해도 문답으로 설계

- 기준: 08d0469696691d5b4a5c9c5d47836d361b4f7792의 독립 로컬 clone. 원격 게시·전역 스킬 설치 없음.
- 변경: askflow의 최소 정보·상태·질문 선택·종료 조건, intake의 무자료 진입, weave의 설계 산출과 의미 확인, mergechk의 설계/실행 팩 구분. 템플릿·README·CLAUDE·점검 기준·평가를 동기화했다. 스킬 수는 6개 유지, 버전 0.2.0.
- 실행 검사: 스킬 카탈로그 6개, 평가 JSON 26시나리오의 서식·입력 경로, 규격 동기, README 구조, 기존 after 계약과 L1~L4 43/43, readchk 원본 무변경, 내부 보정쌍 5/5, prose 흐름·before 중복·homonym 보존 모두 exit 0.
- 외부 보정쌍 5개는 로컬 자료가 없어 건너뛰었다. 26개 평가의 모델 실행 통과를 의미하지 않는다. 모델 기반 전체 반복 평가와 실제 사용자 업무의 전후 비교는 미실시.
- 수동 표면 확인: 작성 에이전트가 합성 사용자 답으로 무자료 시작 → 목적 → 결과 → 추정 순서 확인 → 표 없는 완성 설계를 생성했다. 추가로 정책 충돌·답변 보류 경로를 적용했다. 실제 입출력은 docs/workflow-dialogue.md에 있으며 독립 평가로 주장하지 않는다.
- 실행 환경: Git Bash와 번들 Python 3.12.14. validate-skills.sh의 체크아웃 CRLF는 LF로 포맷 정규화했고 의미 변경 없음.
- 추가 회귀: 원본 M0와 변이 M1~M6의 기대 결과 전부 통과. 첫 시도는 공백 포함 TMPDIR를 기존 mutations.sh가 따옴표 없이 전달해 실패·시간초과했다. 인자가 Codex와 2/... 두 개로 나뉨을 확인했고 공백 없는 기본 임시 경로로 다시 실행해 통과했다. 테스트의 재귀 정리는 같은 Bash 안에서 임시 경로 범위를 검증하는 함수로 제한했다.
- 첫 시도가 인접 Codex 폴더에 만든 DECISIONS.md는 생성 시각(15:47:15)과 Git 미추적 여부로 이번 실행 산출물임을 확인했다. 원본 삭제 대신 이 작업의 .re0/qa/misdirected-readchk.md로 이동해 보관했고 인접 폴더에 파일이 남지 않았음을 확인했다. 기본 권한에서는 이동이 거부돼 자동 검토를 거친 권한 확장 후 복구했다. 사용자 기존 파일은 제거하지 않았다. 잘못된 테스트 프로세스는 종료돼 남아 있지 않다.
- 편집 도구 준비 중 저장된 원문 부재와 정확하지 않은 검색 문자열로 패치 조립이 중단됐다. 파일을 다시 읽어 일치 검증 후 적용했다. README 패치도 강조 표기의 불일치로 적용 전 거부돼 정확한 줄로 수정했다. 실패한 시도에서 부분 수정은 없었다.

## Earlier Error Log

### Phase 12: 생성 후 정리 훅 (2026-09-09)

- 구현: scripts/post-generate.cjs. 등록 파일·세션 분리, Stop 1회 요청, 복구 사본, clean/refined/needs-input, 승인 답변 후 resume, 변경된 내용의 stale 표시. 새 외부 의존성 없음. 버전 0.3.0.
- 규칙 정본: docs/refine-agent.md. askflow·weave에는 생성 종료점 연결만 추가. SSOT의 감사안 승인 게이트·고유 정보 보존을 적용했고, 기계 계약 필드·독립 설치 규칙은 강제 추출 대상에서 제외했다.
- RED→GREEN: 첫 실행은 구현 부재로 4개 실패. 추가 회귀는 등록 이후 변경된 파일의 검토 기준 시점과 config 명령 부재 2개를 검출했다. 기준을 Stop 시점으로 수정하고 config를 구현했다. 최종 CLI 13/13 통과, node --check 통과.
- 수동 표면: out/hook-qa의 합성 파일 2개를 등록하고 로컬 .codex/hooks.json의 실제 command를 Windows cmd에서 stdin Stop 이벤트로 호출했다. decision=block·정본 규칙·범위·사본 경로가 반환됨. 구현자가 중복 2문단을 기획서 참조로 바꾸고 장식 1문장을 제거했다. 고유 첨부 예외·30분/60분 충돌은 보존하고 보고서로 needs-input 기록. 후속 Stop은 경고만 반환, 추가 block 없음. 기획서·참조를 직접 읽어 확인했다. 사본과 시연 파일은 Git 제외 경로에 보존했다.
- 자동 회귀: 스킬 카탈로그 6개(명시적 번들 Python으로 재실행 성공), 평가 JSON 6개/26시나리오 서식·경로, 규격 동기, README 구조, 기존 after 계약 GREEN 및 L1~L4 43/43, git diff --check 통과. 전체 모델 평가 실행을 뜻하지 않는다. 새 훅 테스트를 CI에 추가했다.
- 오류/환경: 편집 직후 LSP 훅이 서버 미설치·사용자의 이전 설치 거절을 보고했다. 재설치하지 않고 Node 구문/CLI 검사로 확인했다. Git Bash MCP transport가 닫혀 native PowerShell로 전환. 아직 생성 중인 시연 폴더의 cwd 시작 실패 1회, PowerShell node -e 인용 손실 1회는 JSON 파이프+설정 command 직접 실행으로 해소했다. exec의 Bash shell override는 WSL E_ACCESSDENIED를 반환해 명시적 Git Bash 실행으로 전환했다. 카탈로그 검사 첫 실행은 WindowsApps python3 때문에 실패했다. README 자기 검사에서 새 로컬 out 폴더 미안내를 발견해 구조도에 추가했다.
- 자체 구조 검토: 훅 상태 전이 139줄, CLI 테스트 126줄. 외부 입력은 경계에서 JSON/경로를 확인하고 파일 순회·셸 실행·삭제를 구현하지 않는다. 상태 분기는 switch로 처리하고 환경 오류는 CLI 경계에서 표시한다. 별도 로깅 체계·추상화 계층·정리용 새 스킬은 추가하지 않았다.
- 한계: CLI 프로토콜과 수동 합성 편집을 검증했다. 현재 앱 세션의 자동 Stop 재개·독립 모델의 의미 보존·실제 사용자 승인 인터뷰·타 호스트 실행은 미검증. 로컬 프로젝트 설정만 준비했고 전역 설정·원격 저장소는 변경하지 않았다. 사용 시 실제 session_id와 호스트 신뢰/활성화가 필요하다. 상태/보고서는 작성자 진술이며 보안 강제 게이트가 아니다.

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-09-03 | similarity가 체인 인접 쌍을 동명이인으로 분류 | 1 | io를 in/in·out/out 평균으로 |
| 2026-09-03 | L3 용어 일관에 문장 조각이 표 이름으로 등장 | 1 | TABLE_RE 공백 제거 |
| 2026-09-03 | has_criteria가 본문의 단어만으로 통과, 이후 절 제목만 인정하니 외부 팩 오탐 5/5 | 2 | 절 제목·→·조건문 인정, 한 갈래로 묶음 |
| 2026-09-03 | 파이썬 패치 heredoc이 본문 EOF·따옴표에 끊김 (2회) | 2 | 패치를 파일로 써서 실행 |

## 5-Question Reboot Check

### PR 준비 검토 (2026-09-09)

독립 맥락 검토가 weave의 '계약이 있는 실행 팩에만' 조건과 기존 팩 누락 게이트의 충돌을 발견했다. 실행 팩 여부로 검사 대상을 결정하고 계약·필수 파일이 누락되면 RED로 유지하도록 지시문 한 곳을 고쳤다. QA에서 스냅샷 실패 뒤 claim이 남아 재개할 수 없음을 재현했다. 회귀 테스트가 pending/failed 불일치로 실패하는 것을 먼저 확인한 뒤 failed 상태와 명시적 retry를 추가했다. 자동 재시도는 없고 이전 사본은 보존한다. README 기존 흐름도의 설계 모드 표시는 비차단 후속 개선으로 남긴다. 커밋별 검토 결과·배포 상태는 PR 본문과 로컬 .re0/pr-review-ledger.md에서 확인한다.

| Question | Answer |
| --- | --- |
| 1. 현재 어느 단계인가? | Phase 12 훅 구현·CLI 검증·수동 합성 정리 시연 완료 |
| 2. 다음에 할 일은? | 새 호스트 세션에서 로컬 hooks 신뢰/활성화와 실제 생성→자동 재개 확인. 독립 모델 평가는 별도. 원격 게시·전역 설치는 미실시; LICENSE는 기존 미결 |
| 3. 목표는? | tasks.md의 Goal |
| 4. 지금까지 배운 것? | findings.md의 Learnings |
| 5. 완료한 작업은? | 위 세션 기록 |
