# Findings & Decisions

> 기술적 발견, 중요한 결정이 있을 때마다 즉시 갱신한다.

## Requirements

- [x] 회사에 묶이지 않는다. 있는 자료를 파악하고, 워크플로우를 묻고, 비슷한 스킬을 통폐합한다.
- [x] 통합되지 않는 스킬이 많고 맥락이 비슷하면, 그것들을 덮는 워크플로우를 만든다.
- [x] paperthin을 전부 읽고 그 철학으로 세팅한다.
- [x] file-based planning workflow 방식으로 세팅한다.

## Research Findings

### paperthin (LilMGenius)

- 규약: `skills/<사분면>/<이름>/SKILL.md`, frontmatter `name`+`description`(+`disable-model-invocation`), 본문 Goal/Workflow/Rules/Verification. 검증은 `scripts/validate-skills.sh`(이름=폴더, plugin.json 등록, README 링크, `../` 금지, 설명 800자 이하, 4개 절).
- 사분면: depth(하나·지금) · breadth(여럿·지금) · coil(하나·여러 판) · mesh(여럿·여러 판). 트리거 범위로 분류한다.
- 철학: 자료를 믿고 저자를 믿지 않는다 · 일반 예시 · SSOT + 자기완결 · 절제 · 재귀. 스킬은 다른 스킬을 링크하지 않고 이름으로 부른다.
- 이 도메인에 옮긴 반사: `readchk`(재진술, 갈래 하나) → `mergechk`의 DECISIONS · `aim`(묻지 말고 제안) → `intake` · `ssotize`(감사 → 승인 → 통합) → `skillmerge` · `sip`(자기 산출물 검사) → 출하 체크리스트 · `re0`(이어붙이지 말고 v0) → 합친 스킬 작성 규칙 · negatives-as-corpus → `archive/`.
- 호출: 기본은 model-invoked. 사람이 결정할 행동(커밋·배포)이거나 손에 있는 것만으로 편향되는 스킬만 user-invoked.

### Jcurve_SKI (첫 인스턴스)

- 세 도구: 인터뷰 프롬프트 v2(확인표 통째 확인 → 빈 칸만 질문) · 통합 점검기(L0 계약 게이트 🟢🟡🔴 → L1~L4) · slide-pack.
- 실측으로 굳은 규칙: 게이트가 점검기보다 먼저(이름 어긋남이 진짜 충돌을 가린다) · `halt_at`은 체인 중간도 · `결정됨`이 있는 DECISIONS는 덮어쓰지 않음 · 수용된 위험 ⚠️는 실패와 구분하되 사라지지 않음 · 직선/태스크 적음은 탈락이 아니라 이름 붙이기.
- 회사 고유: 교육 세션 번호, 이노허브/Codex, SK CI 토큰(DESIGN.md), 상류 도구(ATF·WFDATA) 형식과 어댑터, 페르소나. → 그 저장소에 남긴다.
- 페르소나 인터뷰가 드러낸 이탈 지점: 확인 요청이 "완성 초안 전문"이라 비용이 크다 · 예외 처리가 사람에게 그대로 떨어진다. 부족 스킬은 새 표 없이 채웠다(제거 우선).

### ahastudio — File-based Planning Workflow

- 세 파일: tasks.md(계획·추적, 단계 시작 시) · findings.md(발견·결정, 조사 직후) · progress.md(세션 기록, 날짜 오름차순, 5문항 재부팅).
- Spec-driven(무엇을, top-down)과 짝: 여기서는 `agent-plan.md`가 spec, 세 파일이 과정.

### 팩 규격 (Jcurve_SKI와 호환)

| 규격 | 필드 |
| --- | --- |
| 스킬 frontmatter | name · owner · quadrant · human(자동/증강/사람고유, auto/augment/human 허용) · inputs · outputs · reads · writes · next(갈림길 `\|`) |
| 계약 블록 | tables · writers · chain(`;`로 경로) · payloads · threshold(±N%) · halt_at(콤마) |
| 정지 문구 | 본문에 "확인"+"멈" 또는 confirm+halt/stop/pause |

### paperthin 점검 결과 (2026-09-03, 두 번째 세션)

| 반사 | 결과 |
| --- | --- |
| shower README | needs work: 용어(팩·L1~L4·확인표·🟢🟡🔴·8절) 미정의, 설치 후 check/ 위치 없음, 프로필 연결 방식 없음 → 용어표·설치 절·"프로필은 선택" 추가 |
| shower skillmerge | needs work: mergechk·weave·CONTRACT·next·re0 미정의, "판단기준 합집합/하나로/다르면 안 합침" 상충, archive 위치 → 표 8행으로 정의+부재 시 지침, 문장 통일 |
| hate | 근본 반론: mergechk는 서류 점검이고 증거는 저자가 쓴 예시뿐. 첫 못: 변이 테스트 |
| 변이 테스트 | 체인 뒤집기·정지 지점 기록·임계값 상충 🔴 / 규칙 전부 삭제 → 미결 / 본문 무의미 → 통과(알려진 한계). `mutations.sh`로 고정 |
| mandela | Jcurve_SKI 예시 3개(남이 만든 팩)에 엔진 점검기: 2 통과, 1은 원본과 같은 `data/` 실패. similarity: 5스킬 팩 합침 후보 0(정답), paperthin 28스킬 0(입출력 frontmatter 없으면 못 봄) |
| ssotize | 팩 규격이 엔진 12곳·프로필 10곳에 재진술. `check_spec_sync.py`가 정본(`_common.py`)과 대조 |
| dedash | em-dash 95개(문서 46·코드 주석 49). user-invoked라 미적용, 결정 대기 |
| detool | README의 도구 이름은 설치 런북 성격. 유지 |
| 외부 린터 skillscheck | 사분면 중첩 레이아웃을 스킬로 오인(에러 3), 한국어 설명을 "when 없음"으로 경고. 도입 보류 |

### 도입 후보 판정

도입: H1 합치기 전 스냅샷(Hermes rollback) · H3 규격 드리프트 가드(paperthin check-catalog-sync). 보류: H2 공통부분 추출(분류 의미 변경이라 사용자 결정) · H4 planning-with-files(파일명 고정·공존 불가) · H5 사용량 신호(런타임 카운터 없음) · H6 skillscheck · H8 상류 어댑터(프로필 몫). 불가: H7 SkillOpt(실행 궤적 전제).

## Technical Decisions

| Decision | Rationale |
| --- | --- |
| `check/_common.py`로 파서 통합 | 세 스크립트가 같은 frontmatter·계약 파서를 따로 들고 있었다 (SSOT) |
| L2 "명세 안의 표" = 기획서의 표 + 계약 tables | 확장자 없는 이름(DB 테이블·시트 탭)도 계약에 적으면 인식되게 |
| `archive/` 아래 SKILL.md는 스킬로 세지 않음 | 폐기 스킬이 기록자 중복·고아로 잡히지 않도록 |
| similarity 분류는 제안이지 판정이 아님 | 합칠지는 팀이 정한다. 스크립트는 후보만 |

## Issues Encountered

### 1. similarity io 축 오분류

**문제**: in∪out을 한 집합으로 재니 체인 인접 쌍(A.out = B.in)의 io가 0.67로 나와 "동명이인"이 됐다.

**해결**: in/in과 out/out을 따로 재고 평균.

**결과**: 인접 → 체인으로 정정. 중복 쌍은 여전히 1.00.

### 2. 표 이름 정규식이 문장 조각을 잡음

**문제**: 공백을 이름의 일부로 허용해 "이번 주 회의록이 회의록목록.csv"가 표 이름이 됐다.

**해결**: 공백 제거. 언더스코어·하이픈 변형만 표기 변형으로 본다.

### 4. 판단기준 탐지의 오탐

**문제**: 절 제목만 인정하니 규칙을 불릿으로만 적은 외부 팩(team-agent)에서 5/5가 미결.

**해결**: 예외 절·"→" 줄·조건문(…이면 …한다) 인정, 스킬별 갈래를 한 갈래로 묶음. 4/5 → 1건.

**결과**: 미결이라 막지 않는다. 남은 오탐은 "## 판단기준" 제목 하나로 해소된다고 메시지에 적었다.

## Resources

- 철학·규약 원문: https://github.com/LilMGenius/paperthin (README, CLAUDE.md, docs/invocation.md)
- 세 파일 패턴 원문: https://github.com/ahastudio/til/blob/main/ai/file-based-planning-workflow.md
- 첫 인스턴스: https://github.com/gbrinan/Jcurve_SKI (check/통합점검-기준.md, prompts/lv5-packaging-prompt-v2.md)
- 점검 기준: `docs/check-criteria.md`

## Learnings

### (2026-09-03) 점검기의 한계를 CI에 적어 두면 "검증"이라는 말이 정직해진다

변이 테스트 없이는 "전체 통과"가 무엇을 뜻하는지 아무도 모른다. 잡는 것 3개와 못 잡는 것 2개를 `mutations.sh`에 고정하니, README가 "검증한다" 대신 "구조·계약을 판정하고 동작은 사람이 확인한다"고 정확히 말할 수 있게 됐다. 한계가 줄어들면 그 스크립트가 실패해서 문서를 고치게 만든다.

### (2026-09-03) 엔진과 인스턴스는 규격으로 이어진다

두 저장소가 코드를 링크로 공유하면 어느 쪽도 혼자 설치돼 돌지 않는다. 대신 팩 규격(frontmatter·계약 블록)을 같게 유지하면 인스턴스의 어댑터가 만든 팩을 엔진의 점검기가 그대로 읽는다. 공유하는 것은 코드가 아니라 계약이다.
