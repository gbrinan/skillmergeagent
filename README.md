# skillmergeagent — 흩어진 스킬을 하나의 워크플로우로

**팀원들이 각자 만든 스킬을 파악하고, 워크플로우를 인터뷰로 확정하고, 비슷한 것은 통폐합하고, 합쳐지지 않는 것은 하나의 워크플로우로 엮어, 처음부터 끝까지 위임되는지 검증한다.**

어느 회사, 어느 팀, 어느 에이전트(Claude Code, Codex, OpenCode, Cursor 등)에서든 같은 방식으로 쓴다. 회사 고유의 것(디자인 토큰, 교육 세션 이름, 상류 도구의 파일 형식)은 이 저장소에 두지 않는다. 그런 것은 이 엔진을 쓰는 **프로필 저장소**(예: [Jcurve_SKI](https://github.com/gbrinan/Jcurve_SKI))에 둔다.

설계 철학은 [paperthin](https://github.com/LilMGenius/paperthin)의 "더하지 말고 덜어낸다", 과정 기록은 [file-based planning workflow](https://github.com/ahastudio/til/blob/main/ai/file-based-planning-workflow.md)의 세 파일 패턴이다.

## 15초 시작

```bash
npx skills@latest add gbrinan/skillmergeagent --global --agent '*'
```

그다음 팀원들의 스킬이 든 폴더를 열어 두고 에이전트에게 말한다:

```
이 폴더의 스킬들을 하나의 팀 에이전트로 묶고 싶어.
```

`intake`가 먼저 읽고 제안하며, 빈 칸은 `askflow`가 묻고, 비슷한 것은 `skillmerge`가, 나머지는 `weave`가, 검증은 `mergechk`가 맡는다. 진행 상황은 `planfiles`가 `planning/` 세 파일에 남긴다.

## 지도

paperthin의 사분면(개수 × 시간)을 그대로 쓴다. 이 저장소에 `mesh/`는 없다. 소규모 팀의 다관점 검증은 별도 스킬이 아니라 동작 테스트의 상호 검증으로 한다(제거 우선).

```text
                 지금                          여러 판에 걸쳐
 하나        depth/  이 하나가 깨끗하고 참인가       coil/  이번 판이 다음 판을 가르쳤는가
             intake · askflow · mergechk           planfiles
 여럿        breadth/  하나의 진실이 어디서나 같은가
             skillmerge · weave
```

## 색인

### `depth/`

| 스킬 | 하는 일 | 범위 | 호출 | 읽기 전용 |
| --- | --- | --- | --- | --- |
| 📥 **[intake](./skills/depth/intake/SKILL.md)** | 자료를 먼저 읽고 스킬 카드 인벤토리와 확인표를 제안한다. 묻지 않는다 | 폴더 하나 | model | ✔ |
| 🎤 **[askflow](./skills/depth/askflow/SKILL.md)** | 아는 것은 확인표로 통째 확인, 없는 것만 한 번에 하나씩 묻는 워크플로우 인터뷰 | 팩 하나 | model | |
| ✅ **[mergechk](./skills/depth/mergechk/SKILL.md)** | 계약 게이트(🟢🟡🔴) → L1~L4 점검 → 읽은 바와 미결 기록 | 팩 하나 | model | |

### `breadth/`

| 스킬 | 하는 일 | 범위 | 호출 | 읽기 전용 |
| --- | --- | --- | --- | --- |
| 🧲 **[skillmerge](./skills/breadth/skillmerge/SKILL.md)** | 같은 일을 하는 스킬을 찾아 승인 뒤 하나로 합친다. 폐기는 보관 | 스킬 여럿, 팩 여럿 | model | |
| 🧵 **[weave](./skills/breadth/weave/SKILL.md)** | 합쳐지지 않는 스킬을 체인·갈림길·정지 지점으로 엮어 처음부터 끝까지 덮는다 | 스킬 여럿 | model | |

### `coil/`

| 스킬 | 하는 일 | 범위 | 호출 | 읽기 전용 |
| --- | --- | --- | --- | --- |
| 🗂️ **[planfiles](./skills/coil/planfiles/SKILL.md)** | tasks·findings·progress 세 파일을 영구 메모리로 쓴다 | 프로젝트 하나 | model | |

모두 model-invoked다. 어느 것도 파일을 지우지 않고, 변경이 있는 스킬(`skillmerge`)은 계획을 보고하고 승인을 받은 뒤에만 바꾼다.

## 전체 흐름

```text
들어오는 것: 팀원들이 각자 만든 SKILL.md · 프롬프트 · 설계도 · 체크리스트 (형식 제각각)
      │
      ├─ intake      전부 읽고 → 스킬 카드 인벤토리 + 확인표 A(구성)·B(판단기준)·C(순서) → "이대로 맞습니까?"
      │
      ├─ askflow     확인표 통째 확인 → (없음) 칸만 한 질문씩 → agent-plan.md(SSOT) + CONTRACT.md
      │
      ├─ skillmerge  유사도 감사(check/similarity.py) → 동일·포함은 합침 계획 → 승인 → v0로 재작성, 폐기는 archive/
      │
      ├─ weave       남은 스킬을 맥락 군집 → outputs↔inputs로 체인 → 갈림길·halt_at → 커버리지 표(빠진 스킬 0)
      │
      └─ mergechk    readchk → DECISIONS.md · 계약 게이트 🟢🟡🔴 → L1~L4 · 사람 판정 2개(실제 실행·오류 주입)

내내: planfiles  planning/tasks.md(계획) · findings.md(발견·결정) · progress.md(세션 기록·오류)
```

각 단계는 앞 단계의 산출물을 그대로 입력으로 받는다. 기획서 하나가 끝까지 따라간다. 정해지지 않은 것이 있어도 멈추지 않는다. `mergechk`가 미결을 `DECISIONS.md`에 적고 가장 무거운 것 하나만 앞세운다.

## 산출물 — 끝나면 손에 남는 것

팀 폴더 하나다. 실제 예시는 [`examples/after/`](examples/after/).

```text
팀-agent/
├── README.md          사용법 3줄 + 기획서 링크          (처음 여는 사람)
├── agent-plan.md      기획서 8절 — 이것이 원본(SSOT)    (사람 + 점검기)
├── AGENTS.md          역할 · 입출력 · 도구 · 트리거      (사람)
├── CONTRACT.md        표 · 기록자 · 순서 · 정지 지점     (점검기가 읽음)
├── DECISIONS.md       이해한 바 + 아직 안 정해진 것      (나중에 감사하는 사람)
├── skills/<사분면>/<이름>/SKILL.md   합치고 엮은 스킬들   (AI)
├── archive/<이름>/    합치며 폐기한 스킬 + 이유          (다음 판의 자료)
└── data/              원본 데이터
```

| 필수 파일 | 없으면 |
| --- | --- |
| `README.md` · `agent-plan.md` · `AGENTS.md` | L1 실패 |
| `CONTRACT.md` | 계약 게이트가 🔴로 멈추고 채울 서식을 알려줌 |
| `DECISIONS.md` | 없어도 됨. `readchk.py`가 만들어 줌 |

## 파일 기반 계획 — 세 파일이 기억이다

컨텍스트가 리셋되면 에이전트는 작업을 잊고, 긴 작업 중에 목표를 잃고, 실패한 시도를 반복한다. 그래서 과정은 `planning/` 아래 세 파일에 산다.

| 파일 | 역할 | 갱신 시점 |
| --- | --- | --- |
| **tasks.md** | 목표(북극성) · 단계 · 결정 · 오류 | 단계를 시작·끝낼 때 |
| **findings.md** | 인벤토리 · 데이터 명세 · 기술 결정 · 만난 문제 | 발견 직후 즉시 |
| **progress.md** | 세션별 작업 내역 · 테스트 결과 · 오류 로그 · 5문항 재부팅 | 세션마다 |

서식은 [`templates/`](templates/)에, 이 저장소 자신의 기록은 [`planning/`](planning/)에 있다. 기획서(`agent-plan.md`)가 "무엇을" 만들지의 원본이라면 세 파일은 "어떻게 진행됐는지"의 기록이다.

## 점검 도구

```bash
python3 check/similarity.py <폴더> [<폴더>...]        # 통폐합·체인 후보 (읽기 전용)
python3 check/readchk.py <팩>                          # 읽은 바 + 미결 → DECISIONS.md
python3 check/check_contract.py <팩> --run-check       # 계약 게이트 → 통과 시 L1~L4 점검
python3 check/run_check.py --self                      # 이 저장소 자신: README 구조도 ↔ 실제 폴더
bash scripts/validate-skills.sh                        # 스킬 카탈로그 규약
```

기준과 판정 철학은 [`docs/check-criteria.md`](docs/check-criteria.md).

## 문제와 해법

**스킬은 더해지기만 한다.** 팀원마다 하나씩 만들면 이름만 다른 같은 스킬이 생기고, 같은 표에 둘이 쓰고, 같은 규칙이 다른 값으로 두 곳에 산다. 그대로 묶으면 그럴듯하고 바쁘고 조용히 유지보수가 불가능한 팀 에이전트가 된다.

이 저장소의 스킬은 반대로 건다. **모두 덜어낸다.**

- `intake`는 묻는 대신 읽고 제안한다. 질문 목록이 줄어든다.
- `askflow`는 파일이 이미 답한 것을 다시 묻지 않는다. 인터뷰가 줄어든다.
- `skillmerge`는 스킬 수를 줄인다. 합칠 것이 없으면 아무것도 바꾸지 않는다.
- `weave`는 스킬을 더 만들지 않고 순서와 정지만 더한다.
- `mergechk`는 통과시키기 위해서가 아니라 탈락시키기 위해 있다.
- `planfiles`는 대화 기억 대신 파일 세 개만 믿는다.

> 어려운 것은 기능을 더하는 게 아니라 절제다. 고칠 것이 없는 한 판은 아무것도 바꾸지 않는다. 그 절제가 제품이다.

## 저장소 구조

```text
skillmergeagent/
├── README.md            ← 지금 읽고 있는 문서 (사람용)
├── CLAUDE.md            ← 에이전트·기여자용 규약 (철학 · 서식 · 출하 체크리스트)
├── skills/              ← 스킬 6개 (depth · breadth · coil)
├── templates/           ← tasks·findings·progress, 스킬 카드, 계약, 기획서, 결정 기록 서식
├── check/               ← 유사도 감사 · readchk · 계약 게이트 · 통합 점검기
├── scripts/             ← 스킬 카탈로그 검증
├── docs/                ← 점검 기준
├── examples/            ← before/ (통폐합 전, 팀원 3명의 날것) · after/ (합치고 엮어 점검 통과한 팩)
└── planning/            ← 이 저장소 자신의 tasks · findings · progress (스킬로 스킬을 만든 기록)
```

> 폴더를 새로 추가하면 이 구조도에도 추가한다. `run_check.py --self`가 README와 실제 폴더가 어긋나면 실패로 알려준다.

## 출처

- 철학과 스킬 해부: [paperthin](https://github.com/LilMGenius/paperthin) (MIT) — `readchk`·`aim`·`ssotize`·`sip`의 반사를 이 도메인으로 옮겼다. 포크가 아니라 같은 규약을 따르는 별도 스위트다.
- 과정 기록: [ahastudio/til — File-based Planning Workflow](https://github.com/ahastudio/til/blob/main/ai/file-based-planning-workflow.md) — 세 파일 패턴을 `planfiles`와 `templates/`로 옮겼다.
- 첫 인스턴스: [Jcurve_SKI](https://github.com/gbrinan/Jcurve_SKI) — 한 회사의 에이전트 제작 교육에서 실측으로 다듬어진 인터뷰 프롬프트·계약 게이트·점검기가 이 엔진의 원형이다. 회사 고유 부분은 그 저장소에 남고, 일반화된 부분이 여기로 왔다.
