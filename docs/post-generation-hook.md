# 생성 후 정리 훅 사용

생성 완료 → 대상 등록 → Stop에서 한 번 재검토 → 승인된 정리 → 결과 기록.
판단 규칙은 [refine-agent.md](refine-agent.md) 한 곳에 있다. 훅은 임의 파일을 찾아 편집하지 않는다.

## 설치와 대상 등록

Node.js 20 이상과 전체 저장소가 필요하다. 스킬만 설치하면 훅은 포함되지 않는다.

1. `node scripts/post-generate.cjs config`의 JSON을 대상 프로젝트 `.codex/hooks.json`의 기존 hooks와 병합한다. 기존 훅을 덮어쓰지 않는다. Node는 PATH에서 찾고 스크립트는 절대 경로이므로 다른 컴퓨터에서 다시 생성한다. 현재 로컬 clone에는 설정을 만들어 두었으며 개인 경로 설정은 gitignore한다.
2. 호스트의 hooks 활성화·프로젝트 신뢰·명령 신뢰를 확인하고 새 세션에서 로딩을 확인한다. 이 작업은 전역 설정을 바꾸지 않는다. 설정을 만들었다는 사실만으로 현재 실행 중인 세션에 로드됐다고 간주하지 않는다. [Codex 공식 hooks](https://learn.chatgpt.com/docs/hooks).
3. `askflow` 또는 `weave`가 초안 문답을 끝내고 산출물을 전달할 때, **호스트 세션의 작업 디렉터리에서** 아래처럼 실제 `session_id`와 이번 생성 파일만 등록한다. 팩이 하위 폴더여도 cwd를 바꾸지 않는다.

```sh
node "<suite>/scripts/post-generate.cjs" arm "<실제 session_id>" "agent-plan.md" "team-agent/AGENTS.md"
```

파일 목록은 예시다. 존재하는 생성 Markdown만 나열하고 대화 transcript·고객 원본·훅 설정은 넣지 않는다. 실제 세션 ID를 확보하지 못하면 추측하지 말고 수동 검토로 전환하고 자동 훅 미등록이라고 보고한다. 다른 에이전트 호스트는 이 설정으로 검증하지 않았다.

## 결과와 재개

`node "<suite>/scripts/post-generate.cjs" status "<session_id>"`로 확인한다.

| 상태 | 의미 |
| --- | --- |
| pending | 등록됨, 아직 검토 요청 전 |
| reviewing | 검토 요청됨, 아직 완료 아님 |
| clean / refined | 작성자가 무변경 / 정리 완료로 기록함 |
| needs-input | 감사안 승인 또는 충돌 결정 대기 |
| failed | 스냅샷/검토 지침 준비 실패, 원인을 해소한 뒤 명시적으로 retry |
| stale: true | 등록/검토 기준 내용 이후 변경됨 |

승인 답변을 받으면 `resume "<session_id>"`으로 같은 검토를 이어간다. 끝나면 `finish "<session_id>" clean|refined|needs-input "<report.md>"`를 실행한다. 보고서는 비어 있지 않은 별도 Markdown이어야 한다. clean인데 생성물이 바뀌었으면 명령이 거부한다. 검토 후 새 생성 작업이 있었다면 새 파일 목록으로 arm한다. 같은 내용 재등록은 no-op이다.

## 안전과 한계

스냅샷 저장 등 검토 준비가 실패하면 자동 재시도하지 않는다. 디스크·권한 등 원인을 해소한 뒤 `node "<suite>/scripts/post-generate.cjs" retry "<session_id>"`로 새 시도를 등록한다. 이전 사본은 덮어쓰거나 삭제하지 않으며 다음 Stop에서 한 번만 재검토를 요청한다. 진행 중인 검토나 승인 대기를 retry로 초기화할 수 없다.

세션별 상태·변경 전 사본은 작업 폴더의 `.skillmerge-review/`에 보존한다. 사본에는 생성물 원문이 있으므로 Git·외부 공유 대상에서 제외한다. `status`의 snapshots 경로에서 필요한 파일만 수동 복원할 수 있다. 자동 삭제하지 않는다.

자동 추가 턴은 생성 묶음당 최대 한 번이다. 재검토 중 재등록은 거부하고, 다른 Stop 훅의 연속 실행 중이면 pending을 유지한다. 중단되거나 미완료면 경고를 내지만 무한 루프를 만들지 않는다. 이 장치는 보안 강제 게이트가 아니며 작성자가 명령·상태를 조작할 수 있다. 의미 보존·승인 여부는 에이전트의 실제 감사 기록을 읽어 확인해야 한다. 독립 평가나 실제 업무 실행을 통과한 것으로 표시하지 않는다.
