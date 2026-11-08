# 터미널과 에이전트 조작

구문은 설치된 명령 그룹과 `herdr --skill`을 우선한다. 이 문서의 셸 변수에는 실제 응답에서 확인한 값과 요청 내용을 넣는다. 예시 이름이나 ID를 현재 대상으로 간주하지 않는다. [공식 자동화 문서](https://herdr.dev/tui/docs/agent-automation/)

## 대상과 배치

사용자가 지정한 세션이나 이미 검증한 작업 대상이 있으면 그 세션을 사용한다. 대상 지정이 없으면 현재 대화의 세션을 먼저 확인한다. `herdr pane current --current`는 명령 실행 환경이 가리키는 호출 패널을 조회한다. 공유 Codex 데몬의 상속 환경은 현재 대화 화면과 다를 수 있으므로, 성공하더라도 작업 경로와 대화 내용이 현재 요청과 일치하는지 확인한다. **패널 조회 실패나 불일치가 있으면 새 workspace 생성도 진행하지 않는다.**

실행 중인 로컬 세션은 `herdr session list --json`으로 찾고, `herdr --session "$session_name" agent list`에서 후보를 좁힌 뒤 `herdr --session "$session_name" pane read "$pane_id" --source recent-unwrapped --lines 80`으로 현재 대화를 대조한다. 제목이나 경로만으로 확정하지 않는다. 검증 이후의 모든 로컬 명령에는 같은 `--session`을 명시한다. 아래 예시의 `herdr`에도 이 접두사를 적용한다. 하위 에이전트에게는 세션명과 그 세션에서 확인한 ID를 함께 전달한다.

일부 명령은 대상 생략 시 UI 포커스를 사용하므로 이후 조작에는 확인한 ID, 검증된 호출 환경의 `--current`, 고유한 에이전트 이름을 사용한다. ID와 이름은 서버별 범위다.

| 생성 또는 이동     | 다음에 사용할 응답 필드                                                             |
| ------------------ | ----------------------------------------------------------------------------------- |
| `workspace create` | `.result.workspace.workspace_id`, `.result.tab.tab_id`, `.result.root_pane.pane_id` |
| `tab create`       | `.result.tab.tab_id`, `.result.root_pane.pane_id`                                   |
| `pane split`       | `.result.pane.pane_id`                                                              |
| `pane move`        | `.result.move_result.pane.pane_id`                                                  |

호출 정보가 실제 대화와 맞지 않으면 `agent list`에서 작업 경로와 제목으로 후보를 좁히고 `pane read`에서 현재 사용자 요청을 대조한다. 포커스나 제목만으로 대상을 확정하지 않는다. 대상 확인이 불가능하면 추측해 입력하지 않는다.

일반적인 workspace 간 이동에서는 공개 pane ID가 바뀐다. 이동한 프로세스의 상속 환경은 그대로지만 이전 ID를 호출 문맥에서 해석하므로 해당 프로세스의 `--current`는 계속 사용할 수 있다. 다른 호출자는 이동 응답의 새 ID를 사용한다. 고유 에이전트 이름으로도 이동한 대상을 찾을 수 있다. [이동 동작](https://herdr.dev/tui/docs/agent-automation/#agent-identity-and-launch)

배치가 필요하면 `pane layout`, `neighbor`, `edges`로 형상과 이웃을 확인한다. 사용자가 지정한 방향을 우선하며, 방향이 없으면 넓은 패널은 오른쪽, 좁거나 긴 패널은 아래 분할을 고려한다. 반복 분할로 사용할 수 없는 크기를 만들지 않는다.

```sh
herdr pane split "$pane_id" --direction "$direction" --cwd "$task_cwd" --no-focus
herdr tab create --workspace "$workspace_id" --cwd "$task_cwd" --label "$label" --no-focus
herdr workspace create --cwd "$task_cwd" --label "$label" --no-focus
```

`direction`은 `right` 또는 `down`이다. 위 명령은 선택지이며 모두 실행하는 순서가 아니다. 생성 응답의 root pane부터 사용한다.

| 배치 변경 목적                                  | 수단                                            |
| ----------------------------------------------- | ----------------------------------------------- |
| 같은 탭에서 두 터미널 위치 교환                 | `pane swap`                                     |
| 다른 탭이나 workspace로 실행 중인 터미널 옮기기 | `pane move`                                     |
| 경계 조절, 한 패널 확대와 복귀                  | `pane resize`, `pane zoom`                      |
| 의미 있는 표시 이름 부여                        | `workspace rename`, `tab rename`, `pane rename` |

이 조작들은 실행 중인 터미널을 다루는 수단이다. 템플릿을 새로 펼치는 `layout.apply`와 구분한다. 해당 API는 [탭과 프로세스를 교체할 수 있다](automation.md#socket-api로-확장).

## 일반 명령과 대화형 프로그램

셸 명령은 셸 프롬프트가 입력을 받을 때 실행한다. 기존 프로그램이 전경을 점유하면 입력은 그 프로그램으로 전달된다. 화면으로 불명확할 때 `pane process-info`로 셸 PID와 전경 프로세스를 확인한다.

```sh
herdr pane run "$pane_id" "$command"
herdr pane wait-output "$pane_id" --regex "$ready_pattern" --timeout 30000
herdr pane read "$pane_id" --source recent-unwrapped --lines 80
```

`pane run`은 명령과 Enter를 전달한다. 반환 성공은 명령 실행 완료를 뜻하지 않는다. 로그의 준비 표식이나 결과를 확인하고, 성공 여부가 필요하면 명령의 종료 코드나 산출물도 확보한다.

`wait-output`은 이미 존재하는 출력도 매칭한다. 실행마다 다른 표식이나 현재 실행에 해당하는 로그를 선택한다. 입력한 명령의 에코를 결과로 잘못 읽지 않도록 실제 출력 한 줄에 맞는 패턴을 쓴다. `--match`는 리터럴 부분 문자열, `--regex`는 줄 단위 Rust 정규식이다.

텍스트만 입력할 때는 `pane send-text`, Enter나 Esc, Ctrl+C 같은 UI 입력에는 `pane send-keys`를 쓴다. Ctrl+C는 대상의 전경 프로세스에 영향을 주므로 해당 작업을 중단하려는 경우에 사용한다. AI에게 작업을 줄 때는 아래 agent 표면을 우선한다.

## Copilot, Claude, Codex 공통 제어

| 사용자가 선택한 제품 | `agent_kind` | 기본 실행 파일 |
| -------------------- | ------------ | -------------- |
| GitHub Copilot CLI   | `copilot`    | `copilot`      |
| Claude Code          | `claude`     | `claude`       |
| Codex                | `codex`      | `codex`        |

세 종류는 같은 `start`, `prompt`, `read`, `wait`, `get`, `send-keys`, `rename`, `focus`, `explain` 표면을 사용한다. 다른 종류와 현재 지원 목록은 `herdr agent`로 찾는다. 에이전트 종류와 내부에서 쓰는 모델은 별도 선택이다.

기존 에이전트를 쓸 때는 `agent list`로 이름이나 pane ID를 찾고 `agent get`으로 상태를 확인한다. `claude` 같은 종류 이름이나 terminal ID를 agent 대상으로 쓰지 않는다. 새로 시작할 때는 사용 가능한 대화형 셸 패널이 먼저 필요하다.

```sh
herdr agent start "$agent_name" --kind "$agent_kind" --pane "$pane_id"
herdr agent prompt "$agent_name" "$prompt" --wait --timeout 45000
herdr agent read "$agent_name" --source recent-unwrapped --lines 80
```

`agent_name`은 live 에이전트 사이에서 고유하고 `[a-z][a-z0-9_-]{0,31}` 형식이어야 한다. 이름은 해당 에이전트가 종료되거나 교체되면 해제된다. 모델 등 제품 고유 옵션은 그 제품의 도움말로 확인하고 시작 명령의 `--` 뒤에 전달한다. 다른 제품의 옵션을 그대로 재사용하지 않는다.

프롬프트에는 목표, 관련 맥락과 결정, 대상 경로, 허용한 변경 범위, 완료 조건을 포함한다. 역할에 필요한 정보만 전달하고, 모은 결과를 다음 에이전트의 입력으로 사용할 수 있다. 처음부터 별도 파일 응답을 강제할 필요는 없다.

| 상태      | 해석과 다음 행동                                                                 |
| --------- | -------------------------------------------------------------------------------- |
| `idle`    | 입력 가능한 대기 상태. 실제 전경과 대화 화면이 맞는지도 확인                     |
| `working` | 작업 진행 중. 새 작업 제출과 현재 작업 완료 대기를 구분                          |
| `done`    | CLI 관점에서 아직 확인하지 않은 완료 상태. 작업 성공은 응답이나 산출물로 확인    |
| `blocked` | 질문이나 승인 등 사용자 개입 화면을 감지. 내용을 읽고 승인된 범위에서 처리       |
| `unknown` | 에이전트는 있지만 상태를 확실히 분류하지 못함. `get`, `read`, `explain`으로 확인 |

`agent prompt --wait`는 제출 후 `idle`, `done`, `blocked` 중 정착 상태를 기다린다. 이미 작업 중이면 기존 작업의 완료가 이 대기를 충족할 수 있다. 비작업 상태에서 제출한 경우에는 활동 감지가 필요하며, 감지되지 않으면 `agent_prompt_stalled`가 날 수 있다.

이미 실행 중인 에이전트를 기다릴 때는 `agent wait`를 쓴다. 기본 정착 상태 대기면 충분하고, 특정 상태가 필요한 경우에만 `--until`을 사용한다. timeout을 생략하면 무기한 기다릴 수 있다. `done`의 확인 여부는 CLI와 TUI 클라이언트별로 다를 수 있다. [대기와 상태](https://herdr.dev/tui/docs/agent-automation/#choose-the-control-surface)

## 출력과 직접 접속

| 읽기 source        | 선택 기준                                                        |
| ------------------ | ---------------------------------------------------------------- |
| `visible`          | 현재 렌더링된 화면과 대화형 질문 확인                            |
| `recent`           | 줄바꿈을 포함한 최근 렌더링 출력                                 |
| `recent-unwrapped` | 화면 폭에 따른 줄바꿈을 합친 로그와 응답. 일반적인 기본 선택     |
| `detection`        | agent 상태 판별에 사용한 하단 스냅샷. `agent read`의 진단용 선택 |

색이나 스타일이 판단 근거일 때만 `--format ansi`를 사용한다. `pane read`, `agent read`의 기본 출력은 텍스트이며 모든 CLI 응답이 JSON인 것은 아니다.

`--lines`를 늘려도 애플리케이션의 전체 대화 기록이 보장되지는 않는다. alternate screen과 일반 셸 scrollback은 다르다. 완료 응답을 더 읽어도 찾을 수 없을 때만 에이전트에게 임시 Markdown 파일로 결과를 저장하게 하고 같은 머신에서 읽는다.

사용자가 직접 접속하거나 대화형 입출력을 중계해야 하면 `agent attach`, `terminal attach`, `terminal session observe`, `terminal session control`을 검토한다. terminal ID는 pane이나 agent 대상과 구분한다. `--takeover`는 입력 제어를 가져오는 선택이므로 단순 출력 조회에 붙이지 않는다. 구체적인 접속과 해제 키는 `herdr terminal`로 확인한다.

## 오류가 날 때만 추가 확인

| 결과                                    | 다음 행동                                                                                                                           |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `agent_not_ready`                       | 시작한 에이전트와 이름이 남아 있을 수 있다. `get`, `read`로 초기 화면을 확인하고 입력 준비를 기다린다. 시작을 바로 반복하지 않는다. |
| `agent_blocked`                         | 질문 화면을 읽는다. 프롬프트 재전송으로 해결하려 하지 않는다.                                                                       |
| `timeout`, `agent_prompt_stalled`       | 이미 입력됐을 수 있다. 현재 상태와 출력을 읽은 뒤 재전송 여부를 판단한다.                                                           |
| `agent_not_found`, 이동 뒤 이전 ID 실패 | 이름 해제나 ID 변경 여부를 확인하고 관련 목록과 이동 응답으로 대상을 다시 찾는다.                                                   |
| 상태와 화면이 불일치                    | `agent explain`으로 감지 근거를 확인한다. 미분류를 성공으로 해석하지 않는다.                                                        |
| 지원하지 않는 명령이나 method           | 관련 도움말과 `status`로 CLI, 서버 버전을 확인한다. 서버 중지나 업데이트를 자동 해결책으로 쓰지 않는다.                             |

CLI 구문 오류는 종료 코드 2, 서버 오류는 보통 종료 코드 1과 stderr의 JSON으로 구분한다. 정상 명령도 stdout이 비어 있을 수 있다. 성공 근거는 명령의 반환 계약과 실제 결과를 함께 본다.
