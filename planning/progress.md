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

## Error Log

| Timestamp | Error | Attempt | Resolution |
| --- | --- | --- | --- |
| 2026-09-03 | similarity가 체인 인접 쌍을 동명이인으로 분류 | 1 | io를 in/in·out/out 평균으로 |
| 2026-09-03 | L3 용어 일관에 문장 조각이 표 이름으로 등장 | 1 | TABLE_RE 공백 제거 |
| 2026-09-03 | has_criteria가 본문의 단어만으로 통과, 이후 절 제목만 인정하니 외부 팩 오탐 5/5 | 2 | 절 제목·→·조건문 인정, 한 갈래로 묶음 |
| 2026-09-03 | 파이썬 패치 heredoc이 본문 EOF·따옴표에 끊김 (2회) | 2 | 패치를 파일로 써서 실행 |

## 5-Question Reboot Check

| Question | Answer |
| --- | --- |
| 1. 현재 어느 단계인가? | Phase 7 점검 반영, PR #1에 두 번째 커밋 |
| 2. 다음에 할 일은? | 사용자 결정 3개(dedash · planning-with-files · 공통부분 추출) 반영, 그다음 실제 팀 폴더 실측 |
| 3. 목표는? | tasks.md의 Goal |
| 4. 지금까지 배운 것? | findings.md의 Learnings |
| 5. 완료한 작업은? | 위 세션 기록 |
