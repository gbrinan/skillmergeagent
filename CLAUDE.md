# skillmergeagent

흩어진 스킬을 파악(`intake`)하고, 워크플로우를 인터뷰(`askflow`)하고, 비슷한 것은 통폐합(`skillmerge`)하고, 나머지는 하나의 워크플로우로 엮고(`weave`), 처음부터 끝까지 위임되는지 판정(`mergechk`)하며, 과정은 세 파일에 남기는(`planfiles`) 스킬 스위트다. 이 문서는 스킬을 쓰고 만드는 규약이다. 사람이 읽는 정문은 [README](./README.md)다.

## 철학

- **자료를 믿고, 저자를 믿지 않는다.** 스킬을 만든 사람의 머릿속 맥락은 파일에 없으면 없는 것이다. 인벤토리는 파일에서만 나오고, 없는 값은 `(없음)`이다. 지어내지 않는다.
- **제거 우선.** 두 스킬이 같은 일을 하면 하나로 줄인다. 불필요함이 확인된 항목만 뺀다. 답을 모르는 규칙·예외·책임은 미확인으로, 의견이 갈린 것은 충돌로 보존하고 해당 실행을 보류한다. 고칠 것이 없는 한 판은 아무것도 바꾸지 않는다.
- **하나의 진실, 한 곳에.** 기획서(`agent-plan.md`)가 에이전트 정보의 원본이고 계약(`CONTRACT.md`)이 이름의 원본이다. 다른 문서는 복사하지 않고 가리킨다. 스킬은 각각 자기완결이라 혼자 설치돼도 돌아가야 하므로, 필요한 규칙은 다른 스킬을 링크하지 않고 본문에 적는다. 다른 스킬은 이름으로만 부른다.
- **회사에 묶이지 않는다.** `skills/`·`templates/`·`check/`에는 회사 이름, 교육 세션 번호, 특정 도구의 파일 형식, 브랜드 색을 두지 않는다. 그런 것은 이 엔진을 쓰는 프로필 저장소의 몫이다. 상류 산출물의 형식이 팀마다 다르다는 사실은 `intake`가 "넓게 찾고 끝까지 읽는다"로 흡수한다.
- **사람이 멈추는 자리를 먼저 적는다.** 자동으로 할 일과 사람이 확인할 일을 처음부터 나눈다. 정지 지점은 체인 끝뿐 아니라 중간도 계약에 적는다.
- **재귀.** 이 저장소는 자기 스킬로 자기를 만든다. `planning/`이 그 기록이다.

## 레이아웃

```text
skills/<사분면>/<이름>/SKILL.md
```

사분면은 paperthin의 개수 × 시간 축이다: `depth/` 지금 손에 든 하나를 다듬거나 판정, `breadth/` 여러 파일·스킬에 걸친 하나의 진실, `coil/` 판을 넘어 학습을 나르기. `mesh/`는 두지 않는다. 소규모 팀의 다관점 검증은 별도 스킬이 아니라 동작 테스트의 상호 검증으로 한다.

스킬은 **트리거 범위**로 분류한다. `mergechk`는 팩 하나를 판정하므로 `depth/`다. 그 안에서 여러 파일을 대조해도 그렇다.

이름은 그것이 켜는 반사로 짓는다. 평범한 진짜 단어(`intake`, `weave`)나 실제 용어의 압축(`mergechk`, `planfiles`). 낯선 사람이 이름만 보고 절반은 짐작할 수 있어야 한다. 모델 이름을 붙이지 않는다.

## SKILL.md 서식

```text
---
name: <kebab-name>            # 폴더 이름과 같게
description: "<트리거가 풍부한 한 줄>"
---

<한 줄: 이 스킬이 하는 일>

## Goal
## Workflow      (번호 붙은 단계)
## Rules         (제약)
## Verification  (끝내기 전 확인. 무엇이 바뀌었는지 보고)
```

본문은 한국어, 절 제목은 영어로 둔다. 검증 스크립트와 다른 에이전트가 같은 뼈대를 인식하도록.

## 호출

여섯 스킬 모두 model-invoked다. 사용자도 이름으로 부를 수 있다. 어느 것도 파일을 지우지 않는다. 기존 스킬의 통폐합은 `skillmerge`가 계획 보고와 명시적 승인 뒤 수행한다. `intake`는 읽기 전용, `mergechk`는 팩 안에 `DECISIONS.md`·`REMEDIATION.md`만 쓴다. 나머지는 기획서·계약·planning 파일을 만든다. 선택적 생성 후 훅은 등록된 산출물에 한정해 검토를 요청한다. 정리 판단·승인 경계의 정본은 [docs/refine-agent.md](docs/refine-agent.md), 연결 절차는 [docs/post-generation-hook.md](docs/post-generation-hook.md)다.

user-invoked로 둘 후보가 있었다면 `skillmerge`다. 통폐합 반사가 늘 손에 있으면 과잉 합침으로 기울 수 있다. 그 위험은 "감사 먼저, 승인 뒤 변경, 빈 결과는 유효"라는 규칙이 막는다. 실측에서 과잉 합침이 보이면 그때 user-invoked로 바꾼다.

## 규약

스킬은 자기완결이다. 아래는 스킬 사이 관계가 곧 스킬인, 의도된 예외다.

- **파이프라인**: `intake` → `askflow` → `skillmerge` → `weave` → `mergechk`. 각자 앞 단계의 산출물을 입력으로 받지만, 앞 단계가 없으면 스스로 만든다(`askflow`는 인벤토리가 없으면 `intake`를 먼저 돈다).
- **점검기 오케스트레이션**: `mergechk`는 `check/`의 스크립트를 순서대로 부른다(`readchk.py` → `check_contract.py --run-check`). 스크립트가 없는 환경에서는 `docs/check-criteria.md`를 손으로 돈다.
- **planning 기록**: 다섯 스킬 모두 끝에 "`planning/`이 있으면 …에 적는다(`planfiles`)" 한 줄을 갖는다. `planfiles`는 그 세 파일의 규칙을 정하는 유일한 집이다.
- **편집 안전**: 바꿀 대상이 있는지 확인하고 없으면 MISS로 보고, 유니코드 안전(`PYTHONUTF8=1`), 한 건씩 치환: `skillmerge`에 인라인. 파일을 바꾸는 스킬이 늘면 같은 문구를 복사한다.
- **삭제 대신 보관**: `skillmerge`의 폐기는 `archive/`로 옮긴다. `autobahn`의 negatives-as-corpus와 같은 규칙이다.

## 파일 기반 계획 (이 저장소에서 작업할 때)

세션을 시작하면 `planning/tasks.md` → `findings.md` → `progress.md`를 먼저 읽는다. 발견은 `findings.md`에 즉시, 단계 전환과 결정과 오류는 `tasks.md`에, 세션 기록과 테스트 결과는 `progress.md`에 적는다. 세션을 끝낼 때 `progress.md`의 5문항 답을 갱신한다. 규칙 전문은 `planfiles` 스킬에 있다.

## 문답으로 설계하기

자료가 없어도 askflow가 목적·시작/입력·결과부터 한 질문씩 채운다. 순서는 에이전트가 초안으로 제안하고 사용자 답으로 구체화한다. 확정·추정·미확인·해당 없음·충돌을 구분하며 표 정의는 실제 표를 쓰는 업무에만 필요하다. 분기·예외·정지·필수 입력 공급처·담당·완료 기준이 정해지면 설계를 전달하고 질문을 끝낸다.

기본 산출물은 agent-plan.md 하나다. 기존 스킬이나 설치된 실행 환경 없이도 설계할 수 있지만 없는 능력은 미구현으로 남긴다. 실행 팩·계약을 요청했거나 기존 팩을 수정할 때만 아래 규격을 적용한다. 기획서의 미결은 계약에 확정값으로 넣지 않는다. 설계 완료와 실제 실행 검증은 별도 상태다. 상세 질문 선택과 종료 규칙은 askflow가 소유한다.

## 계약과 팩 규격

점검기가 읽는 규격은 두 가지다. 서식은 `templates/`에 있다.

- **스킬 frontmatter** (`templates/skill-card.md`): `name` · `owner` · `quadrant` · `human`(자동·증강·사람고유) · `inputs` · `outputs` · `reads` · `writes` · `next`. 사람고유 스킬은 본문에 "확인"과 "멈"(또는 confirm·halt)이 든 절을 둔다.
- **계약 블록** (`templates/CONTRACT.md`): `tables` · `writers`(표당 하나) · `chain`(갈림길은 `;`) · `payloads` · `threshold`(±N%) · `halt_at`(중간 포함).

규격의 정본은 `check/_common.py`의 `SKILL_FIELDS` · `CONTRACT_KEYS` · `HUMAN_VALUES`다. 규격을 바꾸면 거기서 시작해 `templates/`, 이 문서, `docs/check-criteria.md`, `examples/after/`를 따라 바꾼다. `check/check_spec_sync.py`가 복사본의 어긋남을, `check/mutations.sh`가 점검기의 한계 변화를 CI에서 잡는다.

## 출하 전 확인

1. **SKILL.md**가 위 서식을 따른다. `name`이 폴더와 같다.
2. **README** 색인에 사분면·호출·읽기 전용 열과 링크가 있고, **plugin.json**에 경로가 등록돼 있다. `scripts/validate-skills.sh`가 둘 다 확인한다.
3. **README 구조도**가 실재하는 최상위 폴더를 전부 안내한다. `python3 check/run_check.py --self`.
4. **예시가 통과한다.** `python3 check/similarity.py examples/before`가 합침 후보를 내고, `examples/homonym`은 동명이인으로 남고, `python3 check/check_contract.py examples/after --run-check`가 0으로 끝나고, `readchk.py examples/after`가 `DECISIONS.md`를 바꾸지 않는다. `bash check/mutations.sh` · `python3 check/check_spec_sync.py` · `python3 check/calibrate.py`도 통과한다. `python3 check/flow.py examples/prose`가 순서 2 · 하위스킬 1 · 고아 1 · 없는 스킬 1을 낸다.
5. **상수에는 근거가 있다.** `similarity.py`의 임계값은 `check/labels.json`의 이름표 쌍이 가르는 값이다. 상수를 바꾸려면 먼저 반대 사례를 이름표에 더하고 `calibrate.py`가 보고하는 여유를 본다.
6. **스킬마다 평가가 있다.** `skills/<사분면>/<이름>/evals/evals.json`에 시나리오 3개 이상. 스킬 지시문을 고치면 그 시나리오를 다시 돌려 `planning/progress.md`에 적는다.
5. **회사 고유 명사가 없다.** `skills/`·`templates/`·`check/`·`docs/`에 회사 이름·세션 번호·브랜드 색이 없다.
6. **package.json** 버전은 크기가 아니라 종류로 올린다: 기존 동작이 틀렸으면 patch, 맞지만 좁았으면 minor, 대체 없는 제거는 major.
7. **planning/**에 이번 세션의 발견·결정·오류가 들어갔다.

커밋 메시지는 처음부터 인수인계용으로 쓴다. 제목 한 줄, 빈 줄, 실제로 달라진 것마다 `-` 한 줄. diff나 버전이 이미 증명하는 것은 적지 않는다.

## 지역 출처

`.re0/`와 `*.local.md`는 gitignore된 이 저장소만의 출처 기록이다. 규격이 아니라 역사와 낙서다. `planning/`은 반대로 커밋한다. 다음 세션이 그것을 읽고 시작하기 때문이다.
