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
work_status: in_review
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

Kotlin 파일만 여는 managed NvChad 세션에서도 JVM 설정이 로드되어 Kotlin DAP adapter와
configuration이 즉시 등록되게 한다. 또한 프로젝트 디렉터리에서 파일 인자 없이 `nvim`
또는 `nvim <directory>`로 시작해 탐색기에서 파일을 열어도 C/C++·Go·Python·Java·Kotlin·
C# filetype과 LSP/DAP가 정상 활성화되게 한다. 소스 파일을 열기 전 NvimTree 화면에서도
`:MdsTrustWorkspace`가 존재하고 현재 프로젝트 루트를 인식하게 한다. 함께 발견된
host/guest `mds` revision 불일치와 workspace trust 상태를 정렬하고 actual-target
readiness를 다시 검증한다.

Linear 티켓 생성과 상태 전환은 2026-08-23 사용자의 명시 요청으로 면제했다. 가짜 ticket
ID, URL 또는 상태는 기록하지 않는다.

## 주요 변경 지점

- `internal/adapters/guest/editor_config.go`의 `renderPluginSpec`이 `nvim-jdtls` JVM setup을
  Java뿐 아니라 Kotlin filetype에서도 lazy-load한다. 이 setup이 Kotlin DAP adapter와
  launch configuration을 등록하므로 Kotlin-only 프로젝트가 Java buffer 선행 로드에
  의존하지 않는다.
- 같은 파일의 `renderManagedInit`이 UI 세션의 인자가 없거나 단일 디렉터리일 때 해당
  디렉터리를 current directory로 확정하고 NvimTree를 자동 포커스한다. 파일·다중 인자와
  headless 실행은 기존 시작 흐름을 유지한다.
- NvimTree가 첫 빈 버퍼를 프로젝트 파일에 재사용할 때 NvChad의 예약된 `FileType` 이벤트
  이후에도 filetype이 비어 있는 실제 경로를 보정한다. `BufReadPost`/`BufNewFile`에서
  파일명 기반 타입을 계산한 뒤 한 tick 지연해, 여전히 유효·로드 상태이며 filetype이 빈
  버퍼에만 `setfiletype`을 적용한다.
- `renderPluginSpec`이 `nvim-lspconfig`와 `configs.lspconfig`를 `VimEnter`에도 로드해,
  파일을 아직 열지 않은 directory-first 세션에서 workspace trust 명령을 등록한다.
- `internal/adapters/guest/editor_language_config.go`의 `workspaceTrustLua`가 NvimTree처럼
  실재하지 않는 가상 버퍼 이름을 받으면 current working directory로 돌아가 프로젝트
  marker를 탐색한다.
- `internal/adapters/guest/editor_slices_test.go`의
  `TestJVMPluginLoadsDAPSetupForKotlinBuffers`와
  `TestManagedInitSupportsDirectoryFirstSessions`가 Kotlin DAP 및 directory-first generated
  configuration 계약을 고정한다. `TestTrustCommandsLoadBeforeFirstProjectFile`과
  `TestWorkspaceTrustUsesCWDForVirtualProjectBuffers`가 파일 선행 로드 없는 trust 명령 및
  NvimTree root fallback 계약을 추가로 고정한다.
- Apple Silicon host와 `mds` Lima guest의 개발 CLI를 project commit
  `cd6b9ac7d71f3b5fc28fec1184ad0310c706bf24`로 정렬하고, 새 `nvim-full` plan digest로
  managed NvChad 설정을 재적용했다. 기존 CLI binary는 복구 가능한 별도 사본으로
  보존했다.
- Lima guest의 `Test` C# project root를 사용자 승인 범위에 따라 workspace trust에
  등록했다. 신뢰 전에는 Roslyn client가 0개였고, 신뢰 후 새 Neovim 세션에서 Roslyn이
  initialized 상태로 attach됐다.

## 검증

- 회귀 테스트 RED: `go test ./internal/adapters/guest -run
  TestJVMPluginLoadsDAPSetupForKotlinBuffers -count=1`이 수정 전 기대한 메시지로 실패.
- 회귀 테스트 GREEN: 같은 명령이 최소 코드 수정 후 통과.
- directory-first 회귀 테스트 RED: `go test ./internal/adapters/guest -run
  TestManagedInitSupportsDirectoryFirstSessions -count=1`이 자동 탐색기 계약 부재로 실패.
- directory-first 회귀 테스트 GREEN: 자동 NvimTree 시작과 지연 filetype 복구 계약 추가 후
  통과.
- workspace trust startup 회귀 테스트 RED:
  `TestTrustCommandsLoadBeforeFirstProjectFile`은 `VimEnter` 로딩 계약 부재로 실패했고,
  `TestWorkspaceTrustUsesCWDForVirtualProjectBuffers`는 NvimTree 가상 경로에서 root 목록이
  빈 값이라 실패했다.
- workspace trust startup 회귀 테스트 GREEN: `VimEnter` 이벤트와 non-existent buffer의
  cwd fallback 추가 후 두 테스트 모두 통과.
- `go test -count=1 ./...`: 전체 패키지 통과.
- `go vet ./...`: 통과.
- macOS arm64 `go build ./cmd/mds`: 통과.
- Linux arm64 `CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build ./cmd/mds`: 통과.
- `git diff --check`: 통과.
- Lima `nvim-full` plan digest:
  `sha256:6651369419ffa42755cec159317c8f593fbf930c8f167a598ecef3e4da50bbad`.
- 첫 apply: `complete: true`; 실제 변경은 managed `nvchad` configuration 하나이며 나머지
  component는 noop.
- repeat apply: 25개 outcome 전부 `noop: true`.
- 실제 TUI에서 `cd ~/Test && nvim` 실행 직후 `cwd=/home/gurumee92.guest/Test`,
  `filetype=NvimTree`, window 2개를 확인했다. 방향키와 Enter로 `Program.cs`를 선택한 뒤
  `filetype=cs`, `roslyn initialized=true`, client 1개, CoreCLR adapter, C# DAP configuration
  2개를 확인했다.
- 새 커밋 적용 후 source file 없이 실제 TUI를 `/tmp/mds-trust-startup-probe`에서 시작했다.
  current buffer는 `/tmp/mds-trust-startup-probe/NvimTree_1`,
  `exists(':MdsTrustWorkspace')=2`, `require('configs.trust').roots(0)` 결과는 현재 project
  root 하나로 확인됐다.
- 파일 인자 없는 시작 뒤 지연 `:edit`에서도 Go `gopls`, Python `pyright`, C++ `clangd`,
  C# `roslyn` attach를 확인했다.
- Kotlin-only headless Neovim: `filetype=kotlin`, `kotlin_adapter=true`,
  `kotlin_configs=1`.
- `Test/Program.cs` headless Neovim: `roslyn initialized=true`, C# DAP adapter와 두
  configuration 확인.
- 최종 production doctor: exit 0, `ready: true`; component 25개 ready 및 expected capability
  26개 전부 pass. Java·Kotlin·Spring·
  C#·Razor·Blazor LSP/cohost와 Java·Kotlin·.NET app/test/server breakpoint DAP의 source,
  stack, scope, known variable, continue, step-in, step-over, terminate 결과를 확인했다.
- 새 커밋의 첫 전체 doctor는 Kotlin app DAP가 breakpoint·source·stack·scope·known
  variable·step-over까지 성공한 뒤 continue/terminate 단계에서 한 번 timeout됐다. 실패
  범위를 `--component nvim-jvm`으로 좁혀 재검증하자 Java/Kotlin DAP 4종과 JVM LSP가 모두
  pass했고, 이어 실행한 최종 `nvim-full` doctor는 exit 0, `ready: true`, expected
  capability 26개 전부 pass로 끝났다.
- 중간 doctor 한 번은 진단 명령을 중복 실행해 Kotlin compiler가 exit 137, Java DAP가
  timeout으로 실패했다. 중복 doctor 3개와 그 실행이 남긴 `/tmp/mds-capability-*` Gradle
  daemon만 종료하고 가용 메모리 2.7 GiB 상태에서 단일 doctor를 재실행해 위 최종 성공을
  확인했다. 사용자 Neovim/프로젝트 프로세스는 종료 대상에서 제외했다.
- 미실행 검증: GitHub Actions와 PR 최신 head의 `ce-code-review`·`ce-doc-review`. 로컬
  GitHub CLI token이 만료됐고 HTTPS Git credential도 없어 branch push와 PR 생성이
  차단됐다. SSH는 현재 client cipher/known-host 상태에서 안전하게 인증할 수 없어 임의
  우회하지 않았다.

## 외부 동기화

- Linear: 사용자 요청으로 전체 단계 waived.
- Project branch: `fix/no-ticket-nvchad-project-startup`.
- Project commits:
  `b5afb65d6bd7c9fb0815714704a738599e7b2877`,
  `839e8a9cbd61f6e5cec61815b7fb715c546000e1`,
  `c3f9018a8e2424463fca6ab59edec30d25e1cb64`,
  `cd6b9ac7d71f3b5fc28fec1184ad0310c706bf24`.
- Notion canonical 구현 문서:
  https://app.notion.com/p/3c3ef22ad4fc81ad97e0d9f020192b8e
- Pull request: https://github.com/zzanghyunmoo/my-desk-setup/pull/9
- Branch와 work evidence는 원격에 push됐으며 최신 head code/doc review 및 merge guard
  검증을 진행한다.

## Merge closeout

PR merge 전이므로 `closeout_status: pending`이다. Merge는 사용자의 별도 명시 승인과
guarded merge 검증 없이는 실행하지 않는다.
