---
workflow_schema: compound-work/v1
ticket_id: NO-TICKET
ticket_url:
ticket_status: waived
ticket_completion: waived
remaining_prs:
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: "병합 후 발견된 Kotlin-only lazy-load 및 directory-first 시작 회귀의 원인과 최소 수정 범위가 실제 Lima 재현으로 확정됨"
plan_status: waived
plan_path:
plan_notion_url: https://app.notion.com/p/3c3ef22ad4fc8179a213f2f20ce4372f
plan_waiver_reason: "기존 canonical 계획 범위 안의 managed NvChad 시작·filetype 계약 수정이며 사용자가 이슈 트래커 단계를 명시적으로 제외함"
work_status: complete
work_notion_url: https://app.notion.com/p/3c3ef22ad4fc81ad97e0d9f020192b8e
pr_url: https://github.com/zzanghyunmoo/my-desk-setup/pull/9
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url: https://app.notion.com/p/3c3ef22ad4fc81ad97e0d9f020192b8e
closed_at:
---

# NO-TICKET Lima NvChad directory-first 인식 및 Kotlin DAP 수정 기록

## 작업 목표

Lima의 managed NvChad를 프로젝트 디렉터리에서 파일 인자 없이 `nvim` 또는
`nvim <directory>`로 시작해도 NvimTree, workspace trust 명령, 언어별 filetype과
LSP/DAP 준비가 정상 동작하게 한다. Kotlin-only 세션에서도 pinned Kotlin debug adapter를
등록하되, 실제 launch는 workspace trust를 검사하는 `:MdsProjectAction` 경로로만 제공한다.
파일·다중 인자·headless·piped stdin 시작은 기존 입력과 자동화 동작을 보존한다.

Linear 티켓 생성과 상태 전환은 사용자의 명시 요청으로 면제했다. 가짜 ticket ID, URL 또는
상태는 기록하지 않는다.

## 주요 변경 지점

- `internal/adapters/guest/editor_config.go`의 `renderStartupConfig`가 directory-first UI
  시작을 별도 managed `lua/configs/startup.lua`로 렌더링한다. 인자가 없거나 단일 디렉터리인
  경우에만 cwd를 확정하고 NvimTree를 포커스하며, named buffer·다중 인자·headless·
  `StdinReadPre` 경로는 건드리지 않는다.
- 같은 startup module은 NvimTree가 시작 buffer를 재사용해 filetype이 비는 경우
  `BufReadPost`/`BufNewFile`에서 확장자를 감지한다. scheduled callback 직전에 buffer의
  유효성, load 상태, 원래 이름과 이미 지정된 filetype을 다시 확인해 stale buffer를
  변경하지 않는다. 상대 `event.file`은 감지에 사용하되 identity 비교는 실제 buffer 이름을
  사용한다.
- `renderManagedInit`이 startup module을 로드하고, no-slice `Editor.Observe`도 plugin spec을
  제외한 모든 base-owned configuration을 정렬해 검사하므로 `startup.lua` 누락과 drift를
  readiness 실패로 보고한다.
- `renderPluginSpec`은 JVM 설정을 Java와 Kotlin buffer에서 모두 lazy-load하고 trust 명령을
  첫 project file 전에 노출한다. `renderJVMConfig`은 pinned Kotlin adapter만 등록하며
  unrestricted `dap.configurations.kotlin`은 만들지 않는다. Java/Kotlin debug action은
  `renderProjectActions`가 trusted root와 launch generation을 검사한 뒤 adapter type을
  선택한다. NvimTree에서 시작한 Java action은 project source buffer를 background-load해
  JDTLS와 Java adapter 준비를 기다리고, Kotlin action은 pinned adapter를 명시적으로
  등록한 뒤에만 Gradle을 시작한다.
- JVM project action의 언어 판별은 root와 최대 4단계 안의 Gradle/Maven module에서 표준
  `src/main|test/java|kotlin` source root만 bounded scan한다. module directory는 최대 256개,
  각 source tree는 최대 4096개 entry까지만 검사하고 생성물·VCS·dependency cache는 제외한다.
  mixed Java/Kotlin project는 언어를 선택하게 하며, untrusted root, 취소된 비동기 adapter 준비,
  읽을 수 없는 source tree 또는 준비되지 않은 adapter는 Gradle 시작 전에 fail closed 처리한다.
- `internal/adapters/guest/editor_language_config.go`의 workspace root 탐색은 실재하지 않는
  named buffer를 cwd로 오인하지 않고 그 경로의 dirname에서 시작한다. 따라서 NvimTree
  virtual buffer는 현재 project root를 찾고, nested marker 아래의 새 파일은 outer trust를
  상속하지 않는다.
- `internal/adapters/guest/editor_startup_test.go`는 실제 headless Neovim callback으로 bare,
  directory, file, multi-argument, headless, named zero-argument, stdin 시작과 C++·Go·Python·
  Java·C# filetype 복구를 실행한다. 실제 `BufReadPost` autocmd와 empty/relative/unmatched
  filename, deleted/unloaded/renamed/claimed buffer 경계도 검증한다. Kotlin adapter setup과
  Kotlin project action의 `dap.run(type="kotlin")`도 실행한다. NvimTree Java/Kotlin 판별,
  mixed project 선택, nested Gradle module 탐색, active Java buffer 우선순위, background Java
  LSP/DAP 준비, adapter unavailable·source 없음·malformed source root·untrusted root의
  fail-closed 경계와 pending JVM 준비 취소도 실제 headless callback으로 검증한다.
- `internal/adapters/guest/editor_test_helpers_test.go`는 authoritative Linux amd64 CI에서
  PATH의 임의 Neovim을 사용하거나 테스트를 skip하지 않는다. production catalog의 exact
  URL·archive SHA·format·executable을 `artifact.Snapshotter`로 획득해 동일한 HTTPS,
  checksum, bounded extraction과 cleanup 계약을 재사용한다.

## 검증

- 최신 project head: `0ffc8cf2eb1a86f9bbb94ade140879ccfd9a32e1`.
- `go test -count=1 ./...`: 전체 패키지 통과.
- `go vet ./...`: 통과.
- macOS arm64 `go build ./cmd/mds`: 통과.
- Linux arm64 `CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build ./cmd/mds`: 통과.
- `git diff --check`: 통과.
- 최종 macOS arm64 CLI SHA-256:
  `6ec7334d002550bd2ea5a96c301e34e61a821ba7099ac5c75ada667901275c07`.
- 최종 Linux arm64 CLI SHA-256:
  `842f0b11a4672b8c242fad8957914348deea5a549d6a33f41b9a12eb07b70de8`.
- 최종 Lima `nvim-full` plan digest:
  `sha256:59c726ccc082afc26cc33b51a55d5905acbbbc0b53b3cd29fd2b3837d5f9b641`.
- 최종 production 변경 apply: `complete: true`; managed `nvchad` configuration만 변경되고
  나머지 24개는 no-op이었다. 같은 digest의 repeat apply는 25개 outcome 전부
  `noop: true`였다.
- 최신 config의 실제 TUI에서 project directory의 `nvim` 시작 직후 current buffer가
  `NvimTree_1`, `filetype=NvimTree`, cwd와 trust root가 project root, startup module이 loaded,
  `:MdsTrustWorkspace`와 `:MdsProjectAction`이 모두 존재함을 확인했다.
- Kotlin-only headless Neovim에서 `filetype=kotlin`, pinned Kotlin adapter 등록,
  `kotlin_configurations=0`, `:MdsProjectAction` 존재를 확인했다. untrusted workspace에서는
  project import와 실행이 차단됐다.
- 최종 적용 config에서 source file을 열지 않은 NvimTree 상태와 `services/api` nested Gradle
  module을 구성해 Java project source를 background-load한 뒤 JDTLS와 `dap.adapters.java`가 준비되는
  `MDS_JAVA_TREE_DEBUG_READY`를 확인했다. 같은 NvimTree 상태에서 실행 가능한 pinned Kotlin
  adapter가 nested module source로 등록되는 `MDS_KOTLIN_TREE_DEBUG_READY`도 확인했다.
- 최종 production doctor: exit 0, `ready: true`; component 25개 ready 및 expected capability
  26개 전부 pass. Component readiness는 C++·Go·Python toolchain을 포함하고, capability
  검증은 Java·Kotlin·Spring·C#·Razor/Blazor LSP와 Java·Kotlin·.NET app/test/server DAP의
  구조적 breakpoint 결과를 포함한다.
- doctor가 남긴 PPID 1의 Gradle 9.6 daemon과 nested Java probe가 남긴 JDTLS·Gradle 8.9
  daemon은 각각 exact PID와 command를 확인한 뒤 TERM으로 종료했다. 사용자 Neovim 및
  project process는 종료하지 않았다.
- GitHub Actions run `32694977715`: 최신 head에서 Linux `verify`와 `windows-verify` 모두 pass.
- 최신 head `ce-code-review`에서 nested module 미탐색, untrusted adapter 선행 준비,
  `:MdsProjectCancel` 뒤 stale callback launch 위험 3개를 발견해 commit `0ffc8cf`로 수정했다.
  전체 검증과 실제 Lima probe를 다시 통과했고 남은 actionable finding은 없다.
- 최신 head의 별도 `ce-doc-review`는 doctor의 component readiness와 구조적 capability 검증
  범위를 구분하도록 한 문장을 바로잡았고, 남은 proposed fix·decision·FYI observation은 없다.

## 외부 동기화

- Linear: 사용자 요청으로 전체 단계 waived.
- Project branch: `fix/no-ticket-nvchad-project-startup`.
- Project PR: https://github.com/zzanghyunmoo/my-desk-setup/pull/9
- 최종 project head: `0ffc8cf2eb1a86f9bbb94ade140879ccfd9a32e1`.
- Notion canonical 구현 문서:
  https://app.notion.com/p/3c3ef22ad4fc81ad97e0d9f020192b8e
- PR 최신 head에 별도 code/doc review 댓글과 passing marker를 게시한 뒤 guarded merge
  precheck를 실행한다.

## Merge closeout

PR merge 전이므로 `closeout_status: pending`이다. Merge는 사용자의 별도 명시 승인과
guarded merge 검증 후 실행하며, 이후 KB·Notion 기능 현황·work evidence를 갱신한다.
