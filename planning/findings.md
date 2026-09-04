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

### ahastudio: File-based Planning Workflow

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

두 번째 냉독(수정 후, 별도 세션): README와 skillmerge 모두 **needs work → minor gaps**. 남은 걸림(작업 디렉터리·`planning/` 위치·표와 확인표 구분·`halt_at`·v0·5문항·`askflow`·`re0`·동일 판정에 판단기준 포함·손 대조의 🟢 정의)은 세 번째 커밋에서 인라인 정의로 해소.

### 실측 1: intake를 상류 산출물에 (2026-09-04)

재료는 남이 만든 형식이다: 와이어프레임 3개(`<!--WFDATA … -->` JSON, 노드·엣지·판단기준·예외·환경 코드)와 ATF 판정 보고서 1개(`atf-data` JSON, 태스크별 사람 여부·6기준·사용 범위). `SKILL.md`는 없다. 지시문대로 수행한 결과와 막힌 곳:

| 막힌 곳 | 처리 | 지시문에 더한 것 |
| --- | --- | --- |
| 카드의 "이름"이 태스크 이름(`lv6`)인지 스킬 이름(`skill` 필드)인지 | 태스크 이름을 공백 없이 정본으로, 스킬 이름은 병기 | 이름 우선순위 |
| 사람 여부가 설계도가 아니라 ATF에 있음 | 태스크 이름으로 두 파일을 이음 | 여러 파일을 이름으로 잇기 |
| 읽고 쓰는 것이 표가 아니라 메일함·OneDrive 폴더 | 표 칸은 `(없음)`, 저장 위치로 따로 적음 | 저장 위치 규칙 |
| 환경 코드(rd·api·cdx·wr·hm) 뜻을 모름 | 그대로 옮기고 "뜻 미확인" | 풀이 금지 |
| 스킬 사이 연결이 어느 파일에도 없음 | 출력과 입력이 같은 말일 때만 `(추정)`으로 잇고 확인표 C에 표시 | 추정 연결 표시 |

결과: 통폐합 후보 0쌍(입출력이 겹치는 쌍이 없음), 직선 체인 1개, 정지 지점 1곳(팀장 확인). ATF가 "검증 지점 하나 세우면 권장"이라 한 조건이 곧 계약의 `halt_at`이다. 인터뷰 목록 6개 중 가장 무거운 것은 데이터 정의(표가 하나도 없음)로, 프로필 저장소의 v2 프롬프트가 "질문 3이 가장 오래 걸린다"고 적어 둔 것과 같다.

또 하나: ATF 보고서의 6기준 출처 줄에 "Design Camp"가 있다. 사용자가 처음에 말한 "디자인캠프"는 이 6기준(반복성·위임 가능성·다단계성·순서 가변성·가치·검증 가능성)의 출처다. 엔진의 산출물 유형 표(다단계성 3개, 갈림길)가 그 기준의 ③·④를 옮긴 것임을 `docs/check-criteria.md`가 이미 말하고 있다.

### 실측 2: 공개 스킬 리포 6개 (2026-09-04)

[k-skill](https://github.com/NomaDamas/k-skill)(123) · [NVIDIA/skills](https://github.com/nvidia/skills)(351) · [wshobson/agents](https://github.com/wshobson/agents)(183) · [anthropics/skills](https://github.com/anthropics/skills)(20) · [obra/superpowers](https://github.com/obra/superpowers)(14) · [vercel-labs/skills](https://github.com/vercel-labs/skills)(1). 읽기 전용으로 파서·유사도·readchk를 돌렸다.

| 본 것 | 결과 |
| --- | --- |
| frontmatter 파싱 | 692/692. name=폴더 일치는 NVIDIA 333/351(따옴표 값 18개, 파서가 따옴표를 벗기게 고침), anthropics 19/20(`template/`) |
| 우리 필드(inputs·outputs·reads·writes·next) | 0/692. 공개 스킬은 name·description(+license·metadata·allowed-tools)만 쓴다. 팩 규격은 팀 팩의 것이고, 공개 카탈로그에는 유사도의 본문 축만 통한다 |
| 레이아웃 | `skills/<이름>/`(anthropics·superpowers·NVIDIA), `plugins/<x>/skills/<이름>/`(wshobson), 루트 바로 아래(k-skill). 우리 `skills/<사분면>/<이름>/`는 없었다 |
| k-skill | 123개 전부 `npx … instruct`로 본문을 받아오는 생성 스텁. 틀을 빼면 본문이 없어 SKILL.md만으로는 같은 일인지 알 수 없다 → 스텁 보류 |
| NVIDIA | 진짜 중복 1쌍(`nvidia-skill-finder`가 skills/와 plugins/ 두 곳), 본문 87% 같은 1쌍, 그리고 doca-(57개)·tao-(30개)·dicom·vss·jetson 가족이 36~75줄을 나눠 씀 → 가족마다 참조 파일 하나 |
| anthropics·superpowers·wshobson | 합침 후보 0. 공통부분 1·0·3쌍(작음). 유사도가 부풀리지 않았다 |
| readchk를 카탈로그에 | anthropics 20개에 검수없음 18건이 떴다(모든 스킬이 끝점). `next`가 하나도 없으면 카탈로그로 보고 흐름 갈래를 건너뛰게 고쳤다 |
| 판단기준 감지(영어) | wshobson 42/183 → 175/183, NVIDIA 151 → 이후 재측정 필요 |

배운 것: 공개 카탈로그에서 통폐합의 신호는 입출력이 아니라 "같은 틀을 나눠 쓰는 가족"이다. 가족은 합칠 대상이 아니라 참조 파일 하나로 뽑을 대상이다. 그리고 생성 스텁은 유사도로 판단하면 안 된다.

### 상수 재도출 (2026-09-04)

`similarity.py`의 상수 7개에 근거를 대려고 이름표 쌍 10개(`check/labels.json`: 저장소 안 5, 바깥 5)를 잡고 `calibrate.py`로 각 규칙의 가장 약한 양성과 가장 강한 음성을 쟀다.

| 상수 | 양성 | 음성 | 판정 |
| --- | --- | --- | --- |
| IO_SAME 0.6 | 1.00 | 0.25 | 빈 구간 넓음 |
| TAB_SAME 0.5 | 1.00 | 0.67 (동명이인) · 1.00 (다른 일, retry-request↔quote-parse) | 홀로는 못 가른다. io와 함께만 |
| TXT_SAME 0.3 | 0.41 | 0.24 | 여유 0.17, 쌍 둘. 가설 |
| 키워드 0.8 (입출력 없음) | 1.00 | **0.87** | 음성이 임계값을 넘는다 → 오류 |
| COPY_COVERAGE 0.9 (교체) | 1.00 | 0.77 | 진짜 중복은 문장이 전부 같고, 틀만 같은 것은 77% |
| TXT_READ 0.5 | 0.89 | 0.15 (99분위 0.39) | 신호로 충분 |

배운 것: 상수에 근거를 대려 하면 오류가 나온다. 0.8은 실측 2에서 "진짜 중복 1쌍, 본문 87% 같은 1쌍"이라고 적을 때 둘째 쌍을 의심하지 않은 결과였다. 두 파일을 diff하니 다른 DAG 두 개였다. 키워드 집합은 틀을 못 가르고 문장 덮임이 가른다. 점수 가중치(0.45·0.25·0.30)는 분류에 안 쓰이므로 근거 대신 "정렬용"이라고 적었다.

### 스킬 평가 (2026-09-04)

Anthropic 지침의 빈 곳 두 개(스킬별 평가 3개 이상, 다른 모델로 시험)를 한 번에 채웠다. skill-creator의 `evals.json` 서식으로 스킬 6개에 시나리오 19개를 쓰고, Sonnet 서브에이전트로 스킬 있음 19개와 스킬 없음(baseline) 10개를 돌려 채점했다. 결과 표는 `progress.md`. 여기에는 판단만 적는다.

| 배운 것 | 근거 |
| --- | --- |
| 스킬의 값어치는 점검기 출력을 옮겨 적는 데 있지 않고 **멈추는 것·묻는 것·지어내지 않는 것**에 있다 | 점검기(similarity·check_contract)가 있는 시나리오는 baseline도 비슷하게 통과했다(mergechk 3개: 4/4·4/4·3/4). 갈린 항목은 승인 전 파일 변경(baseline이 shared/를 만들고 두 SKILL.md를 고침), weave로 넘기기, (없음)·(추정) 표기, 인터뷰 항목이었다 |
| 채점자가 점검기의 결함을 찾았다 | 계약의 writers에 한 표가 두 번 적히면 파서가 덮어써서 "중복"이 "불일치"로 보고됐다. `duplicate_writers`로 고치고 변이 M6으로 고정 |
| 합침 v0는 하류가 쓰는 항목을 잃을 수 있고 아무 검사도 그것을 못 본다 | 회의록요약만 만들던 "보류 사항" 구분을 스킬 있음·없음 둘 다 v0에서 빠뜨렸다(안건정리 2단계가 쓴다). 스킬 9단계에 원본 항목 대조표 규칙을 더했다. 2회차에서는 남았다 |
| 같은 일을 하는 두 스킬의 `next`가 다른 것은 갈림길이 아니라 미결이다 | weave가 `;` 경로 둘로 그렸고(2/4), 규칙 한 줄을 더하자 4/4. skillmerge도 `next: A \| B`로 지어낸 것을 같은 규칙으로 막았다 |
| intake의 서식 혼합 시나리오가 가장 불안정하다 | 1회차 3/5, 2회차 3/6인데 떨어진 항목이 서로 다르다(출처 경로, 저장 위치 보존, (추정) 자리). Sonnet에서 지시문의 세부 규칙을 절반쯤만 따른다. 지시문을 더 늘리기보다 시나리오를 실측 3(사람 답이 있는 실제 팀 폴더)으로 넘긴다 |
| 단정문 절반은 가르지 못한다 | 채점자 지적: "파일이 안 바뀌었다"·"halt_at에 안건확정"·"REMEDIATION 없음"은 도구나 고정 자료가 대신 만족시킨다. 가르는 단정문은 행동(멈춤·질문·표기)에 대한 것이다. 다음 평가 손질 때 이 기준으로 걸러낸다 |
| 다른 모델 시험은 됐다 | 실측 1(intake)은 이 세션의 모델이 직접 했고, 평가 33회는 Sonnet이 했다. 같은 지시문이 두 모델에서 같은 곳(승인 게이트, 미결 처리)에서 잘 서고 같은 곳(세부 표기 규칙)에서 흔들린다 |

### H2 결정: 공통 부분 추출 (2026-09-04)

`similarity.py`에 네 번째 신호를 넣었다: 불릿·번호를 뗀 12자 이상 문장을 몇 줄 공유하는가. 3줄 이상이면 동일·동명이인 다음 순위로 "공통부분 → 참조 추출"을 제안한다. `examples/shared/`의 두 스킬(고객 회신 · 협력사 재요청)은 입출력·표가 전혀 다르지만 메일 설정 6줄이 같아 이 분류로 잡히고, 외부 팩(Jcurve 두 팩 9스킬)에서는 오탐이 없었다. `skillmerge`는 이 쌍을 합치지 않고 문단을 `shared/<주제>.md`로 옮겨 두 스킬이 가리키게 한다.

### 2번 결정: planning-with-files (2026-09-03)

선택지는 셋이었다. (A) 전환: 파일명이 `task_plan.md`로 고정이고 설정 불가, 문서가 다른 스킬과의 공존을 다루지 않으며 훅은 특정 호스트 플러그인 설치에서만 전부 붙는다. (B) 이름만 맞추기: 같은 파일을 두 스킬이 쓰게 되어 덮어쓰기 위험이 커진다. (C) 유지 + 물러나기: `planfiles`가 `task_plan.md`를 보면 그 파일을 쓰고 `planning/`을 만들지 않는다. C를 골랐다. 스킬을 더하지 않고 규칙 한 줄로 충돌을 없앤다.

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
