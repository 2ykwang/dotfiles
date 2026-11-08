# 작업 공간, 원격과 확장

기능별 구문은 설치된 명령 그룹과 `herdr api schema`로 확인한다. 이 문서는 CLI와 API 중 필요한 표면을 고르는 기준을 설명한다. [CLI 문서](https://herdr.dev/tui/docs/cli-reference/), [Socket API 문서](https://herdr.dev/tui/docs/socket-api/)

## 작업 공간과 Git checkout

workspace, tab, pane은 화면과 작업 맥락을 관리한다. workspace와 tab 생성 응답의 root pane을 첫 프로세스에 사용한다. 작업 경로는 `--cwd`, 새 프로세스의 환경은 반복 가능한 `--env KEY=VALUE`로 지정할 수 있다. Herdr가 관리하는 socket과 ID 환경변수를 임의로 덮어쓰지 않는다.

worktree는 실제 Git checkout을 관리하는 기능이다. 해당 프로젝트의 생성 도구와 작업 위치 지침을 먼저 따른다. 기존 checkout 사용과 새 생성, 파일 삭제를 구분한다.

| 필요                         | 기능과 효과                                                          |
| ---------------------------- | -------------------------------------------------------------------- |
| 기존 checkout 파악           | `worktree list --cwd` 또는 `--workspace`                             |
| 브랜치별 checkout 생성       | `worktree create`. 기존 브랜치를 열거나 새 브랜치를 만들 수 있음     |
| 기존 checkout을 Herdr에 열기 | `worktree open --path` 또는 `--branch`                               |
| 화면만 닫기                  | `workspace close`. Git checkout 삭제와 별개                          |
| 연결된 checkout 삭제         | `worktree remove --workspace`. Git worktree를 제거하며 브랜치는 남김 |

기본 base와 저장 위치를 추측하지 않고 도움말, 설정, 실제 Git 상태로 확인한다. `--trust-repository`는 출처를 검증한 저장소에만 사용하며, 실패를 우회하는 기본 옵션으로 붙이지 않는다. `--force`나 workspace의 `--group`도 사용자가 요청한 삭제 범위를 확대하는 수단으로 사용하지 않는다.

## 세션과 SSH 머신

`session list --json`은 이름 있는 실행 세션을 찾는 기능이다. workspace, tab과 별개다. `--session`과 `session attach`로 접속 대상을 선택할 수 있으며, 세션 중지나 서버 중지는 그 안의 프로세스에 영향을 준다. 현재 작업을 조회하려고 다른 세션을 중지하거나 새 서버를 실행하지 않는다.

원격 화면에 접속하는 `--remote`와 등록된 머신에 API 명령을 보내는 `--machine`을 구분한다.

```sh
herdr machine list --json
herdr --machine "$machine" agent list
herdr --machine "$machine" pane list
herdr --machine "$machine" agent prompt "$remote_agent" "$prompt" --wait --timeout 45000
```

`machine`은 활성화된 저장 프로필 ID 또는 고유하고 대소문자가 맞는 label이다. 임의의 SSH hostname을 `--machine` 값으로 쓰지 않는다. 검색과 후속 조작 모두 같은 prefix를 유지하고, 원격에서 받은 ID와 이름을 사용한다. 로컬 `--current`와 ID는 원격 대상을 가리키지 않는다. TUI에서 선택한 머신도 기존 패널의 CLI 대상을 바꾸지 않는다.

저장 프로필의 원격 세션을 사용하므로 `--machine`에 `--session`, `--remote`를 함께 붙이지 않는다. 전달 경로는 실행 중인 호환 서버가 필요하며 설치나 서버 시작을 대신하지 않는다. 반면 `machine add`는 연결과 원격 준비를 수행할 수 있으므로 별도 설정 요청 범위에서 다룬다. 연결 오류 뒤 변경이 미반영됐다고 단정하지 않고 원격 상태를 확인한다. [원격 명령](https://herdr.dev/tui/docs/cli-reference/)

## 알림, 연동과 설정

| 필요                         | 사용할 기능                                        | 적용 범위 확인                                   |
| ---------------------------- | -------------------------------------------------- | ------------------------------------------------ |
| 완료나 개입 필요 알리기      | `notification show`의 title, body, position, sound | 의미 있는 상태 변화에만 알림                     |
| 에이전트 세션 복원 연동 조사 | `integration status`                               | 지원되는 에이전트 감지와 integration 설치를 구분 |
| 연동 설치와 제거             | `integration install`, `uninstall`                 | 해당 에이전트의 hook과 설정을 변경하는 작업      |
| 설정 형식 검증과 기본값 확인 | `config check`, `--default-config`                 | 기본값 출력이 현재 설정 덮어쓰기를 뜻하지 않음   |
| 바꾼 설정 반영               | `server reload-config`                             | 요청한 설정을 확인한 후 사용. 서버 재시작과 구분 |

Copilot, Claude, Codex integration은 세션 식별과 복원 연동에 사용된다. 이 세 제품의 작업 상태는 Herdr의 화면 감지와 구분해서 이해한다. 제품별 인증, 모델, 승인 설정을 Herdr 연동 설치로 해결하려 하지 않는다. [연동 문서](https://herdr.dev/tui/docs/integrations/)

## 플러그인으로 반복 작업 제공

플러그인은 `herdr-plugin.toml`과 실행 명령으로 구성된다. action, event hook, 관리되는 terminal pane, link handler 등으로 기존 CLI와 API를 재사용할 수 있다. 언어나 별도 SDK에 고정되지 않는다. [플러그인 문서](https://herdr.dev/tui/docs/plugins/)

1. 기존 기능을 찾을 때 `plugin list`, `plugin action list`, `plugin log list`를 확인한다.
2. 이미 있는 action이나 pane으로 해결되면 그 진입점을 사용한다. 다른 세션에서 설치한 플러그인도 보일 수 있다.
3. 새 플러그인이 필요하면 manifest와 실제 실행 코드를 확인하고, 설치 또는 연결이 요청된 범위에서 `install`이나 로컬 `link`를 사용한다.
4. 플러그인은 사용자 권한으로 실행되고, 등록과 활성화 상태는 같은 사용자의 세션 사이에 공유된다. 별도 테스트 workspace가 플러그인 설치 상태까지 격리하지는 않는다.

`plugin pane open`은 split, tab, overlay, zoomed, popup 배치를 제공한다. popup은 일반 pane과 다르고 `HERDR_PANE_ID`를 제공하지 않으므로 pane이나 agent 대상으로 간주하지 않는다. 플러그인 프로세스에서 Herdr를 호출할 때는 `HERDR_BIN_PATH`를 우선한다.

## socket API로 확장

CLI wrapper가 있으면 먼저 사용한다. CLI에 없는 기능이나 지속 구독이 필요할 때 현재 설치의 schema에서 method와 params를 확인한다.

```sh
herdr api snapshot
herdr api schema --output "$schema_path"
```

macOS와 Linux의 raw 연결은 해당 세션의 `HERDR_SOCKET_PATH`를 사용한다. 요청은 `id`, `method`, `params`를 가진 JSON 한 줄로 전송한다. 출력도 응답과 이벤트를 구분해 읽는다. 다른 플랫폼의 연결은 CLI와 공식 문서를 따른다.

| 필요한 능력                         | API                                                   | 사용 판단                                                                      |
| ----------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------ |
| 전체 상태로 로컬 캐시 초기화        | `session.snapshot`                                    | 일회성 스냅샷이며 구독이 아님                                                  |
| 구조와 상태 변경에 반응             | `events.subscribe`, `events.wait`                     | 반복 전체 조회 대신 필요한 이벤트를 구독하거나 대기                            |
| 화면 구성을 데이터로 읽기           | `layout.export`                                       | 분할 방향, 비율, pane 정보로 된 트리                                           |
| 기존 분할 비율만 변경               | `layout.set_split_ratio`                              | 실행 중인 터미널을 유지하면서 정밀하게 조절                                    |
| 선언한 배치를 새 터미널로 펼치기    | `layout.apply`                                        | 새 탭을 생성. `tab_id` 지정 시 기존 탭을 교체하고 그 프로세스를 종료할 수 있음 |
| 사용자화된 상태 표시                | `workspace.report_metadata`, `pane.report_metadata`   | source와 token, TTL로 소유권과 유효 기간을 정함                                |
| 에이전트 목록 정렬과 필터           | `agent.view.set`, `agent.view.clear`                  | 상태, 종류, workspace나 사용자 token으로 볼 대상을 구성                        |
| scrollback, 선택 영역, 링크 등 제어 | `pane.scroll`, `pane.selection.read` 등의 schema 항목 | CLI에서 찾지 못한 세부 기능을 현재 schema에서 탐색                             |

**`layout.apply`는 실행 중인 터미널을 보존하는 재배치가 아니다.** export 결과에 `pane_id`가 있어도 기존 PTY와 scrollback을 유지하지 않는다. 작업을 유지할 때는 `pane move`, `swap`, `resize` 또는 `layout.set_split_ratio`를 선택한다. [배치 API 계약](https://herdr.dev/tui/docs/socket-api/#raw-methods)

이벤트를 사용하는 클라이언트는 먼저 구독하고 authoritative 조회로 현재 상태를 맞춘다. 이벤트를 snapshot 위에 무조건 재생하지 않는다. 재연결이나 캐시가 의심되는 경우 snapshot을 다시 읽는다. 구독의 type과 수신 이벤트의 표기, 필터 필드는 schema에서 확인한다.

agent view는 현재 서버의 표시 상태에 영향을 주며 source 단위로 교체와 해제된다. 단순 조사 중 사용자 필터를 임의로 바꾸지 않는다. 플러그인 소유 source는 `plugin:` 규약을 따르고, 그 외 호출자가 해당 namespace를 사칭하지 않는다.

## 기능 조합 예시

아래는 고정 실행 순서가 아니라 목적에 따른 조합이다. 제품 종류는 사용자 선택에 따른다.

| 목적                        | 조합                                                                                       |
| --------------------------- | ------------------------------------------------------------------------------------------ |
| 독립적인 검토를 모아 판단   | 기존 agent 또는 필요한 패널과 agent 생성, 범위가 다른 prompt, 상태 대기, 응답 수집         |
| 준비된 서비스에 테스트 실행 | 서버 pane 실행, 준비 로그 대기, 테스트 pane 실행, 종료 코드와 결과 확인                    |
| 긴 작업 중 개입 시점 파악   | agent나 출력 조건 대기, 필요한 경우 이벤트 구독, 개입 내용 확인과 알림                     |
| 브랜치별 실험               | 승인된 worktree 생성이나 기존 checkout 열기, workspace 관리, 해당 경로의 명령과 agent 실행 |
| 실행 중인 작업의 화면 정리  | 현재 layout 조회, move나 swap, resize나 zoom. 템플릿 교체와 구분                           |
