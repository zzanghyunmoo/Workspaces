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
ideation_waiver_reason: "사용자가 별도 ideation 결과를 폐기하고 확정된 요구사항으로 바로 구현하라고 지시"
plan_status: complete
plan_path: docs/plans/2026-08-21-NO-TICKET-lima-nvchad-jvm-dotnet-plan.md
plan_notion_url: https://app.notion.com/p/3c3ef22ad4fc8179a213f2f20ce4372f
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3c3ef22ad4fc81ad97e0d9f020192b8e
pr_url: https://github.com/zzanghyunmoo/my-desk-setup/pull/8
closeout_status: complete
merged_pr_url: https://github.com/zzanghyunmoo/my-desk-setup/pull/8
merge_commit: a98ba15a51e1d806ff544fe926149f66855cb017
kb_paths: docs/kb/developer-environments/2026-08-23-NO-TICKET-lima-nvchad-jvm-dotnet.md
notion_feature_status_url: https://app.notion.com/p/3c3ef22ad4fc81ad97e0d9f020192b8e
notion_ticket_url: https://app.notion.com/p/3c3ef22ad4fc81ad97e0d9f020192b8e
closed_at: 2026-08-23T00:00:00+09:00
---

# NO-TICKET Lima NvChad JVM and .NET IDE 작업 기록

## 작업 목표

Apple Silicon Lima guest에서 관리형 NvChad 하나로 기존 C++·Go·Python과
Java·Kotlin·C#의 편집, build, test, run, watch 및 실제 breakpoint debugging을
제공한다. Gradle/Spring Boot와 dotnet/ASP.NET Core API·MVC/Razor·Blazor의
필수 capability를 production Verify와 actual-target evidence로 fail-closed 검증한다.

Linear 티켓 생성과 상태 전환은 2026-08-21 사용자의 명시 요청으로 면제했다.
가짜 ticket ID, URL 또는 상태는 기록하지 않는다.

## 주요 변경 지점

- Catalog: `catalog/components/guest.yaml`, `catalog/locks/versions.lock.yaml`에 Java 25,
  Kotlin 2.3, Gradle 9.6, .NET SDK 10과 JVM/.NET LSP·DAP artifact의 exact URL·digest·
  runtime-tree identity를 고정했다. `nvim-jvm`, `nvim-dotnet`, `nvim-full` selection은
  slice별 exact dependency union으로 해석한다.
- Managed editor: `internal/adapters/guest/editor_config.go`와
  `editor_language_config.go`가 NvChad plugin graph, workspace trust, Java/Kotlin/Spring
  LSP, Roslyn+HTML Razor/Blazor cohost, formatter/linter, project action과 DAP 설정을
  결정적으로 생성한다. Roslyn은 첫 FileType 이전에 로드하고 managed `dotnet`으로
  exact server DLL을 실행하며 Spring client capability도 server 계약에 맞춰 명시한다.
- Project actions: Gradle wrapper와 managed `dotnet`만 사용해 build/test/run/watch를
  실행하고, stable project/profile picker와 root-scoped workspace trust를 적용한다.
  ASP.NET launch profile은 loopback URL만 허용하며 trust 철회와 중복 장기 작업은 해당
  root의 LSP와 process group을 TERM→bounded KILL로 정리한다. Java·Kotlin app/test 및
  .NET app/test/ASP.NET server debugging은 실제 breakpoint, stack, scope, known
  variable, continue/step/terminate 결과로 판정한다.
- Runtime publication: `internal/adapters/packages/runtime_tree.go`, `runtime_view.go`,
  `launcher.go`가 immutable generation을 원자적으로 게시하고 exact launcher/view를
  전환한다. 기존 process/session 중복 구현은 generated Neovim action으로 통합했다.
- Capability evidence: `internal/adapters/guest/capability_probe.go`,
  `internal/capability/expected.go`, `internal/doctor/checks.go`가 embedded Spring Boot,
  ASP.NET API/Razor/Blazor fixture를 실제 Lima에서 build/test/run/LSP/DAP probe하고
  expected capability 집합과 결과가 정확히 일치할 때만 ready로 판정한다.
- 운영 문서: project `docs/operations/lima-nvchad-jvm-dotnet.md`에 plan/apply/doctor,
  trust, action, debug, recovery와 repeat-apply 절차를 기록했다.

## 검증

- `go test -count=1 ./...`: 전체 패키지 통과. 로컬 포트 생성이 차단된 sandbox 실행은
  제한 밖에서 같은 명령으로 재실행했다.
- `go test -race -count=1 ./internal/adapters/guest ./internal/capability
  ./internal/doctor ./internal/evidence`: 통과.
- `go vet ./...`: 통과.
- `GOOS=linux GOARCH=arm64 go build ./cmd/mds`: 통과.
- `git diff --check`: 통과.
- Windows amd64 교차 컴파일과 GitHub Actions `windows-verify`: read-only runtime-tree
  durable flush와 exact legacy launcher migration 회귀를 포함해 통과.
- Apple Silicon Lima `mds` actual target:
  - catalog revision `sha256:4fa32141a04325fe89806e14c44a523be7f94bd65c90e0bb1c72af531874a23a`
  - reviewed plan digest `sha256:7d97a683da45f97456aa0b8ee0df44572e877cc789962ff86882deab819cffbc`
  - apply receipt `complete: true`; 이어서 실행한 repeat apply의 25개 outcome 전부
    `noop: true`
  - doctor `ready: true`; expected 26개 capability 전부 pass
  - LSP: Java, Kotlin, Spring, C#, Razor와 Blazor의 Roslyn+HTML cohost 통과
  - actions: JVM build/test/Spring endpoints와 .NET build/test/API run/watch endpoint 통과
  - DAP: Java·Kotlin app/test와 .NET app/test/ASP.NET server 모두
    breakpoint·source line·stack·scope·known variable·continue·step-in·step-over·
    terminate 통과
- 최신 project head의 `ce-code-review`와 `ce-doc-review`: findings/blocker 없이
  통과했고 PR에 head-bound passing marker를 각각 게시했다.
- GitHub Actions: 최신 head에서 `CI #42`와 `Target certification #38` 모두 통과.
- 미실행 검증: 없음. PR #8 승인 후 squash merge와 closeout을 완료했다.

## 외부 동기화

- Linear: 사용자 요청으로 전체 단계 waived.
- Project branch: `main`
- Project head: `a98ba15a51e1d806ff544fe926149f66855cb017`
- Pull request: https://github.com/zzanghyunmoo/my-desk-setup/pull/8
- Notion 요구사항: https://app.notion.com/p/3c3ef22ad4fc819eb3c0de18b70cff5e
- Notion 계획: https://app.notion.com/p/3c3ef22ad4fc8179a213f2f20ce4372f
- Notion 구현 기록: https://app.notion.com/p/3c3ef22ad4fc81ad97e0d9f020192b8e

## Merge closeout

PR #8을 squash merge하여 `main`을 최신화했다. merge commit은
`a98ba15a51e1d806ff544fe926149f66855cb017`이며, KB와 Notion 구현 기록을 갱신했다.
