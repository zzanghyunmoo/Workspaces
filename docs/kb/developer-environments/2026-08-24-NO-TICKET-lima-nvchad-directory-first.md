---
title: NO-TICKET Lima NvChad directory-first 프로젝트 인식
ticket: NO-TICKET
merged_pr: https://github.com/zzanghyunmoo/my-desk-setup/pull/9
merge_commit: e8aba0276a6880a0d8b33aac2568ed8f68fec078
work_evidence: docs/works/2026-08-23-NO-TICKET-lima-nvchad-kotlin-dap-fix-work.md
notion_feature_status: https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436
notion_ticket: https://app.notion.com/p/3c3ef22ad4fc81ad97e0d9f020192b8e
last_verified: 2026-08-24
module: my-desk-setup
tags: [lima, neovim, nvchad, workspace-trust, lsp, dap, java, kotlin]
problem_type: runtime
---

# Lima NvChad directory-first 프로젝트 인식

## 현재 기능 상태

My Desk Setup PR [#9](https://github.com/zzanghyunmoo/my-desk-setup/pull/9)을
squash merge하여 `main`에 반영했다. merge commit은
`e8aba0276a6880a0d8b33aac2568ed8f68fec078`이다.

Lima의 managed NvChad는 프로젝트 디렉터리에서 파일 인자 없이 `nvim` 또는
`nvim <directory>`로 시작해도 NvimTree를 프로젝트 root에 열고, source file을 열기 전에
`:MdsTrustWorkspace`와 `:MdsProjectAction`을 제공한다. NvimTree에서 처음 선택한 C++·Go·
Python·Java·Kotlin·C# 파일의 filetype과 언어별 LSP를 준비하며, Java/Kotlin project-tree
debug action은 표준 source root와 bounded nested Gradle/Maven module 안에서 adapter를
준비한다.

## 주요 동작과 경계

- Workspace trust는 canonical project root별로 명시적으로 승인한다. 미승인 root에서는
  project import, action과 DAP launch를 시작하지 않는다.
- `:MdsUntrustWorkspace`와 `:MdsProjectCancel`은 root의 진행 중 action과 pending debug
  preparation을 무효화한다. 취소 전에 예약된 callback은 launch generation이 달라지면
  Gradle을 시작하지 않는다.
- JVM 언어 판별은 root와 최대 4단계의 Gradle/Maven module, 표준 Java/Kotlin source
  layout만 검사한다. module directory 256개와 source entry 4096개 경계를 넘거나 source를
  검증할 수 없으면 fail closed한다.
- Java debug는 project source buffer를 background-load해 JDTLS와 Java DAP adapter를
  준비한다. Kotlin debug는 pinned executable adapter가 등록된 뒤에만 Gradle을 시작한다.
- 파일·다중 인자·headless·piped stdin으로 시작한 Neovim의 기존 입력 동작은 유지한다.
- Linear 티켓 생성과 상태 전환은 사용자 요청으로 `NO-TICKET` / `waived` 처리했다.

## 검증 결과

- PR 최신 head에서 GitHub Actions run `32694977715`의 Linux `verify`와
  `windows-verify`가 모두 통과했다.
- 전체 Go test, vet, macOS arm64/Linux arm64 build와 diff check를 통과했다.
- Lima `nvim-full` apply digest
  `sha256:59c726ccc082afc26cc33b51a55d5905acbbbc0b53b3cd29fd2b3837d5f9b641`를
  적용했고 repeat apply 25개 outcome이 모두 no-op이었다.
- 실제 project directory의 `nvim` 시작 직후 NvimTree root, workspace trust/action 명령,
  filetype 및 LSP attach를 확인했다.
- 실제 nested Gradle module의 NvimTree 상태에서
  `MDS_JAVA_TREE_DEBUG_READY`와 `MDS_KOTLIN_TREE_DEBUG_READY`를 확인했다.
- Production doctor는 `ready: true`, component 25개 ready, expected capability 26개 pass였다.
  Java·Kotlin·Spring·C#·Razor/Blazor LSP와 Java·Kotlin·.NET app/test/server DAP의 구조적
  breakpoint 검증을 포함한다.
- 최신 head의 code/doc review marker가 모두 PASS한 뒤 guarded merge를 통과했다.

## 운영 및 사용 시 주의사항

프로젝트 root에서 `nvim`을 실행하고 NvimTree 상태에서 `:MdsTrustWorkspace`를 한 번
승인한다. Source 또는 Spring 설정 파일을 연 뒤 `:LspInfo`로 client를 확인하고,
`:MdsProjectAction`에서 `build`, `test`, `run`, `debug-app`, `debug-test`를 실행한다.
진행 중인 장기 작업은 `:MdsProjectCancel`로 중단한다.

## 관련 문서

- 운영 절차: `projects/my-desk-setup/docs/operations/lima-nvchad-jvm-dotnet.md`
- Work evidence: `docs/works/2026-08-23-NO-TICKET-lima-nvchad-kotlin-dap-fix-work.md`
- 재사용 가능한 해결책:
  `docs/solutions/runtime-errors/managed-neovim-directory-first-project-recognition.md`
- Canonical Notion 구현 기록:
  https://app.notion.com/p/3c3ef22ad4fc81ad97e0d9f020192b8e
