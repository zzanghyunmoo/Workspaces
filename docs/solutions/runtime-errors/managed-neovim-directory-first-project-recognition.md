---
title: 관리형 Neovim의 directory-first 프로젝트 인식 복구
date: 2026-08-24
category: runtime-errors
module: my-desk-setup-guest-editor
problem_type: runtime_error
component: tooling
symptoms:
  - 프로젝트 디렉터리에서 nvim을 시작하면 source file을 직접 열기 전까지 workspace trust 명령과 LSP/DAP 준비가 동작하지 않음
  - NvimTree가 처음 재사용한 buffer의 filetype이 비어 같은 파일을 다시 열어야 LSP가 attach됨
  - NvimTree에서 시작한 JVM debug가 nested module과 adapter 준비 및 취소 경계를 안전하게 처리하지 못함
root_cause: config_error
resolution_type: code_fix
severity: medium
tags: [lima, neovim, nvchad, directory-first, workspace-trust, lsp, dap, jvm]
---

# 관리형 Neovim의 directory-first 프로젝트 인식 복구

## Problem

Lima의 managed NvChad를 프로젝트 디렉터리에서 파일 인자 없이 `nvim` 또는
`nvim <directory>`로 시작하면, 첫 언어 파일을 열기 전에는 NvimTree, workspace trust 명령과
프로젝트 action이 준비되지 않았다. NvimTree가 시작 buffer를 재사용한 경우 filetype이 빈
상태로 남아 같은 파일을 다시 열어야 LSP가 attach되는 file-first 의존성도 있었다.

[My Desk Setup PR #9](https://github.com/zzanghyunmoo/my-desk-setup/pull/9)은 이 문제와
NvimTree에서 시작하는 Java/Kotlin debug 준비 경계를 함께 수정해 2026-08-24 `main`에
병합됐다.

## Symptoms

- 프로젝트 root에서 `nvim`을 실행해도 NvimTree가 자동으로 project directory를 열지 않았다.
- 첫 source file 전에는 `:MdsTrustWorkspace`와 `:MdsProjectAction`이 존재하지 않았다.
- NvimTree에서 처음 선택한 source buffer의 filetype이 비어 C++·Go·Python·Java·C#
  LSP가 attach되지 않았고, 같은 파일을 `:edit`로 다시 열면 동작했다.
- Source buffer가 아닌 NvimTree에서 JVM debug를 시작하면 nested Gradle/Maven module의
  언어와 adapter를 준비하기 어려웠다. 취소 또는 trust 철회 전에 예약된 준비 callback이
  늦게 완료되는 경계도 명시적 무효화가 필요했다.

## What Didn't Work

- **언어 파일을 먼저 여는 우회:** Java/Kotlin filetype은 JVM plugin setup을 실행하므로
  문제가 사라진 것처럼 보였다
  (`projects/my-desk-setup/internal/adapters/guest/editor_config.go:274`). 그러나 bare/directory
  start에서 파일보다 먼저 trust와 project action이 준비돼야 한다는 계약은 해결하지 못했다.
- **현재 buffer의 filetype만으로 JVM 언어 선택:** NvimTree는 Java/Kotlin source buffer가
  아니다. 현재 파일이 실제 project root 아래의 source일 때만 filetype을 우선하고, 그 외에는
  표준 source root를 탐색해야 한다
  (`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:818`).
- **프로젝트 전체를 제한 없이 탐색:** 큰 tree나 읽을 수 없는 subtree가 UI를 점유하거나
  잘못된 언어 fallback으로 숨을 수 있다. Source와 module 탐색은 오류를 호출자에게 돌려주고
  명시적 entry limit을 가져야 한다
  (`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:751`).
- **Gradle을 먼저 시작한 뒤 DAP 준비:** Adapter 준비가 실패하면 debug JVM만 attach를 기다리는
  process가 남는다. Adapter를 실제 등록한 뒤에만 Gradle을 시작해야 한다
  (`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:849`).

## Solution

### Directory-first startup을 managed module로 분리한다

Managed editor file 집합에 생성 설정의 startup module을 포함하고
(`projects/my-desk-setup/internal/adapters/guest/editor_config.go:95`), NvChad init이 이를 직접
로드한다(`projects/my-desk-setup/internal/adapters/guest/editor_config.go:326`). Startup module은
UI가 없는 headless session과 piped stdin, named zero-argument buffer, 파일 인자와 다중 인자를
건드리지 않는다. 인자가 없거나 실제 directory 하나인 경우에만 cwd를 project directory로
확정하고 NvimTree focus를 예약한다
(`projects/my-desk-setup/internal/adapters/guest/editor_config.go:383`).

NvimTree가 재사용한 buffer의 filetype 보정은 `BufReadPost`와 `BufNewFile`에서 수행한다. 예약
callback 시점에 buffer가 유효하고 loaded 상태이며 이름이 같고 filetype이 여전히 비어 있을
때만 `setfiletype`을 실행한다
(`projects/my-desk-setup/internal/adapters/guest/editor_config.go:359`). 다른 plugin이 먼저 정한
filetype이나 삭제·unload·rename된 stale buffer는 변경하지 않는다.

### Trust와 project action을 source file보다 먼저 노출한다

LSP plugin은 `VimEnter`, `BufReadPost`, `BufNewFile`에서 설정을 로드한다
(`projects/my-desk-setup/internal/adapters/guest/editor_config.go:262`). JVM/.NET slice의 LSP
설정은 project action setup도 호출한다
(`projects/my-desk-setup/internal/adapters/guest/editor_config.go:491`). 따라서 source file이
없어도 trust와 action 명령이 등록된다.

Trust root 탐색은 빈 buffer에서 cwd를 사용하고, 가상·미생성 path는 dirname에서 시작해
상위 project marker를 수집한다
(`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:40`). 가장 가까운 root를
선택하므로 nested project는 outer root와 별도 trust 경계를 유지한다
(`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:61`). Trust 철회는 해당
root의 LSP를 중단하고 action layer에 root-scoped 중단 event를 보낸다
(`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:120`).

### JVM debug를 source 판별, adapter 준비, process 실행으로 나눈다

Source resolver는 root와 bounded Gradle/Maven module 후보에서 표준
`src/main|test/java|kotlin`만 검사한다. Source tree당 4096 entry, module directory 256개를
초과하거나 `scandir`가 실패하면 성공으로 fallback하지 않는다
(`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:744`,
`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:775`). Java와 Kotlin
source가 모두 있으면 언어를 선택하고, 인식 가능한 source가 없으면 action을 중단한다
(`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:830`).

Adapter 준비는 trusted root에서만 시작한다. Java는 읽을 수 있는 project source buffer를
background-load해 JDTLS와 Java DAP 등록을 기다리고, Kotlin은 pinned executable adapter를
등록한다(`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:205`,
`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:245`). 준비 callback은
root별 preparation ID가 아직 pending인지와 `dap.adapters[adapter]`가 실제 존재하는지를 다시
확인한 뒤 resolved action을 반환한다
(`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:857`). Project action은
그 callback이 성공한 뒤에만 `run`을 호출한다
(`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:981`).

### 취소와 trust 철회를 launch generation으로 보호한다

Root를 중단하면 generation을 증가시키고 pending preparation을 제거한다. 실행 중 process
group에는 TERM을 보내고 2초 뒤 KILL fallback을 예약한다
(`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:700`). Gradle 실행과
debug port 준비 뒤 DAP attach 시점에도 같은 generation과 workspace trust를 검사한다
(`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:706`,
`projects/my-desk-setup/internal/adapters/guest/editor_language_config.go:937`). 늦게 도착한
adapter 또는 stdout callback은 취소 이후 새 Gradle process나 DAP session을 시작하지 못한다.

## Why This Works

프로젝트 발견과 명령 등록을 source-buffer side effect에서 분리했기 때문이다. Startup
module은 managed init에서 항상 로드되고 LSP/action setup은 `VimEnter`에 연결된다. 동시에
headless, stdin, named buffer, 파일·다중 인자 guard가 기존 Neovim 시작 모드를 보존한다.

JVM action은 무엇을 debug할지 판별하고 adapter가 실제 준비됐음을 증명한 뒤에만 process를
시작한다. 탐색 오류, untrusted root, adapter 누락과 취소된 callback은 Gradle 실행 전
fail closed한다. Root별 preparation ID와 launch generation을 callback마다 다시 검사하므로
오래 걸리는 JDTLS 준비가 취소를 되돌릴 수도 없다.

## Prevention

- Startup module이 managed file 집합과 init에 모두 연결됐는지 유지한다
  (`projects/my-desk-setup/internal/adapters/guest/editor_startup_test.go:172`).
- 실제 headless Neovim callback으로 bare/directory start는 NvimTree를 열고, named buffer,
  stdin, file, multi-argument, headless start는 열지 않는 계약을 함께 검증한다
  (`projects/my-desk-setup/internal/adapters/guest/editor_startup_test.go:290`).
- Filetype 복구는 정상 파일뿐 아니라 unknown extension, 삭제, unload, rename과 이미 선점된
  filetype을 검증한다
  (`projects/my-desk-setup/internal/adapters/guest/editor_startup_test.go:355`).
- JVM action은 NvimTree Java/Kotlin, mixed project 선택, nested Gradle module, adapter 누락,
  untrusted root, source 없음과 malformed source root를 각각 검증한다
  (`projects/my-desk-setup/internal/adapters/guest/editor_slices_test.go:325`).
- Pending JVM preparation 취소 테스트는 preparation은 시작됐지만 Gradle과 DAP 실행 횟수는
  0임을 확인한다
  (`projects/my-desk-setup/internal/adapters/guest/editor_slices_test.go:634`).
- Linux CI는 임의 PATH의 Neovim 대신 reviewed catalog의 URL, checksum, format과 executable을
  사용하는 locked artifact로 callback test를 실행한다
  (`projects/my-desk-setup/internal/adapters/guest/editor_test_helpers_test.go:36`).
- Managed `startup.lua` 누락과 drift는 editor readiness를 실패시켜야 한다
  (`projects/my-desk-setup/tests/adapters/guest_editor_runtime_test.go:253`).

실환경에서는 project root에서 `nvim`을 실행한 직후 NvimTree 상태에서
`:echo exists(':MdsTrustWorkspace')`와 `:echo exists(':MdsProjectAction')`이 각각 `2`인지
확인한다. `:MdsTrustWorkspace` 승인 후 source와 Spring 설정 파일의 `:LspInfo`, 이어서
`:MdsProjectAction`의 build, test, run, debug action을 확인한다. 장기 action과 pending
debug preparation은 `:MdsProjectCancel`로 중단한다.

## Related Issues

- [PR #9 — directory-first 프로젝트 인식 복구](https://github.com/zzanghyunmoo/my-desk-setup/pull/9)
- [계층형 관리 Neovim 런타임 복구의 소유권과 안전성 경계](../architecture-patterns/managed-neovim-runtime-repair-boundaries.md)
- [NO-TICKET work evidence](../../works/2026-08-23-NO-TICKET-lima-nvchad-kotlin-dap-fix-work.md)
- [Lima NvChad directory-first KB](../../kb/developer-environments/2026-08-24-NO-TICKET-lima-nvchad-directory-first.md)
