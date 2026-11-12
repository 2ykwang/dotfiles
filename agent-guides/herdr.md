# Herdr

사용자가 Herdr 사용을 요청한 범위에서만 쓴다. 구문의 정본은 설치된 CLI다. 여기에 없는 것은 `herdr pane` 같은 그룹 도움말과 `herdr --skill`로 확인한다. `herdr` 단독은 TUI를 띄우고 `herdr workspace create` 같은 변경 명령은 인자 없이도 실행되므로 탐색용으로 쓰지 않는다.

## 시작 전 확인

1. `test "${HERDR_ENV:-}" = 1`이 실패하면 중단하고 알린다.
2. `herdr pane current --current`의 작업 경로와 화면 내용이 현재 대화와 맞는지 확인한다. 공유 Codex 데몬은 다른 세션의 환경변수를 물려받을 수 있다.
3. 맞지 않거나 `pane_not_found`면 아무것도 바꾸지 않는다. `herdr session list --json`의 세션마다 `agent list`와 `pane read`로 현재 대화가 있는 pane을 찾는다. 못 찾으면 사용자에게 묻는다.
4. 세션을 확인한 뒤에는 모든 로컬 명령에 `herdr --session "$session"`을 붙인다. 2번에서 맞았다면 세션 이름은 `herdr session list --json`에서 `socket_path`가 `$HERDR_SOCKET_PATH`인 항목이고, 3번에서 찾았다면 그 pane을 찾은 세션이다. 하위 에이전트에게도 세션명과 확인한 ID를 넘긴다.

## 기본값

- 기존 pane이나 에이전트로 되면 새로 만들지 않는다.
- 배치 지정이 없으면 현재 탭의 형제 pane, 현재 작업 경로에 만든다. tab, workspace, worktree는 요청받았을 때만 만든다.
- 항상 `--no-focus`를 붙인다. 사용자가 전환을 요청한 경우만 예외다.
- 넓은 pane은 `right`, 좁거나 긴 pane은 `down`으로 나눈다. 크기는 `herdr pane layout --pane "$pane"`로 확인한다.
- 새 tab과 workspace에는 root pane이 이미 있다. 그것부터 쓴다.
- **직접 만든 pane, tab, workspace의 이름은 `↳ `로 시작한다.** 사용자가 에이전트가 연 대상을 구분하는 표식이다.
- 직접 만들지 않은 대상은 이름을 바꾸거나 닫지 않는다.
- 대상은 ID, `--current`, 에이전트 이름으로 지정한다. UI 포커스에 의존하지 않는다.
- ID는 응답 JSON에서 읽는다. pane을 다른 workspace로 옮기면 ID가 바뀌므로 이동 응답의 새 ID를 쓴다.

## 만들기

```sh
herdr pane split "$pane" --direction right --cwd "$PWD" --no-focus            # .result.pane.pane_id
herdr pane rename "$new_pane" "↳ 용도"                                         # split 직후
herdr tab create --workspace "$ws" --cwd "$PWD" --label "↳ 용도" --no-focus    # .result.root_pane.pane_id
herdr workspace create --cwd "$PWD" --label "↳ 용도" --no-focus                # .result.root_pane.pane_id
```

| 필요                    | 수단                                           |
| ----------------------- | ---------------------------------------------- |
| 화면 나누기             | pane, tab                                      |
| 작업 묶음               | workspace                                      |
| Git checkout 분리       | worktree. 포트, DB, 비밀정보는 분리되지 않는다 |
| 실행 서버 분리          | session                                        |
| 실행 중인 터미널 재배치 | `pane move`, `swap`, `resize`, `zoom`          |

## 일반 명령

```sh
herdr pane run "$pane" "$command"
herdr pane wait-output "$pane" --regex "$pattern" --timeout 30000
herdr pane read "$pane" --source recent-unwrapped --lines 80
```

- `pane run` 성공은 접수일 뿐이다. 완료와 성공은 출력, 종료 코드, 산출물로 확인한다.
- `wait-output`은 이미 있는 출력에도 매칭된다. 명령 에코가 아닌 실제 출력 줄에 맞는 패턴을 쓴다. `--match`는 리터럴, `--regex`는 Rust 정규식이다.
- 셸 프롬프트가 아닌 pane에 보낸 입력은 전경 프로그램으로 간다. 불확실하면 `herdr pane process-info`로 확인한다.
- 텍스트는 `pane send-text`, Enter나 Esc, Ctrl+C 같은 키는 `pane send-keys`로 보낸다.
- 구문 오류는 종료 코드 2, 서버 오류는 종료 코드 1과 stderr의 JSON이다. `read`의 출력은 JSON이 아니라 텍스트다.

## 에이전트

```sh
herdr agent start "$name" --kind codex --pane "$pane"    # 모델 등 제품 옵션은 `--` 뒤에
herdr agent prompt "$name" "$prompt" --wait --timeout 45000
herdr agent read "$name" --source recent-unwrapped --lines 80
herdr agent get "$name"
```

- pane은 터미널 위치, agent는 그 안의 프로세스다. `agent start`는 pane을 만들지 않으며 셸 프롬프트 상태의 pane이 필요하다.
- `kind`는 사용자가 지정한 제품(`claude`, `codex`, `copilot`)이다. 역할에 제품을 고정하지 않는다.
- `name`은 `[a-z][a-z0-9_-]{0,31}` 형식이고 live 에이전트 사이에서 고유해야 한다.
- `agent start` 성공은 입력 준비까지 확인한 결과다. 뒤에 sleep이나 상태 조회를 붙이지 않는다.
- 프롬프트에는 목표, 맥락, 대상 경로, 허용한 변경 범위, 완료 조건을 넣는다.
- 여러 에이전트가 같은 파일을 동시에 편집하게 하지 않는다.
- `--wait`는 `idle`, `done`, `blocked` 중 하나에서 끝난다. 상태는 성공의 근거가 아니다. 응답이나 산출물로 확인한다.
- 이미 작업 중인 에이전트는 `herdr agent wait "$name" --timeout "$ms"`로 기다린다.
- 응답이 `read`로 안 보일 때만 에이전트에게 임시 Markdown 파일로 쓰게 한다.

| 결과                              | 행동                                                                                                                                                                             |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `blocked`, `agent_blocked`        | `--source visible`로 화면을 읽는다. 승인된 범위 밖이면 사용자에게 묻는다. 프롬프트를 다시 보내지 않는다                                                                          |
| `agent_pane_busy`                 | pane이 셸 프롬프트 상태가 아니다. 새 pane이면 `pane wait-output "$pane" --match "❯"`로 프롬프트를 기다린 뒤 다시 시작한다. 아니면 `pane process-info`로 전경 프로세스를 확인한다 |
| `agent_not_ready`                 | 에이전트와 이름은 남아 있다. `get`, `read`로 화면을 확인하고 기다린다. 다시 시작하지 않는다                                                                                      |
| `timeout`, `agent_prompt_stalled` | 이미 입력됐을 수 있다. 상태와 출력을 읽은 뒤 재전송을 판단한다                                                                                                                   |
| `agent_not_found`                 | 이름 해제나 ID 변경을 확인하고 `agent list`로 다시 찾는다                                                                                                                        |
| `unknown`, 상태와 화면 불일치     | `herdr agent explain "$name"`으로 확인한다. 성공으로 해석하지 않는다                                                                                                             |

## 왕복 줄이기

- 대상이 정해지면 전체 목록을 다시 조회하지 않고 ID를 재사용한다.
- 독립적인 조회는 한 번의 도구 호출에서 병렬로 실행한다. 의존하는 명령은 응답을 파싱해 같은 실행 안에서 잇는다.
- 정상 결과 뒤에 목록, 프로세스 정보, 레이아웃을 다시 조회하지 않는다.
- 기다릴 때는 `pane wait-output`, `agent wait`, `agent prompt --wait`를 쓴다. 고정 sleep을 쓰지 않는다.

## 금지와 주의

- `herdr server stop`, 세션 중지, Herdr 프로세스 종료를 하지 않는다. 격리가 필요한 실험은 이름 있는 테스트 세션에서 한다.
- `layout.apply`에 `tab_id`를 주면 그 탭의 프로세스가 종료될 수 있다. 실행 중인 터미널의 재배치에 쓰지 않는다.
- `workspace close`는 화면만 닫는다. `worktree remove`는 checkout을 지우고 브랜치는 남긴다.
- worktree는 해당 프로젝트의 생성 도구와 작업 위치 지침을 먼저 따른다.
- `--force`, `--group`, `--trust-repository`를 실패 우회용으로 붙이지 않는다.
- integration과 plugin의 설치, 제거, 설정 변경은 요청받았을 때만 한다. 설정을 바꾼 뒤에는 `herdr config check`, `herdr server reload-config` 순으로 반영한다.
- `agent.view.set`은 사용자의 사이드바 표시를 바꾼다. 조사 목적으로 호출하지 않는다.
- `herdr notification show`는 완료나 사용자 개입이 필요한 상태 변화에만 쓴다.

## 확장

- CLI에 없는 기능만 socket API로 한다. `herdr api schema --output "$path"`로 저장해 필요한 method만 읽는다. 현재 상태는 `herdr api snapshot`으로 읽는다.
- 요청은 `HERDR_SOCKET_PATH`에 `id`, `method`, `params`를 담은 JSON 한 줄로 보낸다.
- 지속 감시는 반복 조회 대신 `events.subscribe`, `events.wait`를 쓴다.
- 사이드바 표시값은 `pane report-metadata`, `workspace report-metadata`의 token으로 넣는다. `plugin:` source는 플러그인만 쓴다.
- 플러그인은 `herdr-plugin.toml`과 실행 명령으로 구성된다. 설치와 활성화 상태는 모든 세션이 공유하므로 테스트 세션으로 격리되지 않는다.
- 플러그인 안에서는 `HERDR_BIN_PATH`로 Herdr를 호출한다. popup pane에는 `HERDR_PANE_ID`가 없다.
- 새 플러그인을 만들기 전에 `herdr plugin list`, `herdr plugin action list`로 기존 기능을 확인한다.

SSH 머신(`--machine`, `--remote`)과 terminal attach는 해당 그룹 도움말과 `herdr --skill`을 따른다. `--machine`에는 `--session`, `--remote`를 함께 붙이지 않는다.

문서: [CLI](https://herdr.dev/tui/docs/cli-reference/), [Socket API](https://herdr.dev/tui/docs/socket-api/), [플러그인](https://herdr.dev/tui/docs/plugins/), [에이전트 자동화](https://herdr.dev/tui/docs/agent-automation/)
