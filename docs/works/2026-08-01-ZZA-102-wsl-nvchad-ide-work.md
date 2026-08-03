---
workflow_schema: compound-work/v1
ticket_id: ZZA-102
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-102/make-the-wsl-nvchad-cgopython-ide-reproducible-with-mds-apply
ticket_status: In Review
ticket_completion: pending
remaining_prs:
ideation_status: waived
ideation_path:
ideation_notion_url:
ideation_waiver_reason: Linear 티켓과 구현 준비가 끝난 단일 WSL IDE profile 범위가 이미 확정되어 별도 후보 탐색이 필요하지 않았다.
plan_status: complete
plan_path: docs/plans/2026-08-01-ZZA-102-wsl-nvchad-ide-plan.md
plan_notion_url: https://app.notion.com/p/3b1ef22ad4fc81048ec9ee92fedf0be9
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3b1ef22ad4fc813d954be68816256def
pr_url: https://github.com/zzanghyunmoo/my-desk-setup/pull/3
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url:
notion_ticket_url: https://app.notion.com/p/3b1ef22ad4fc813d954be68816256def
closed_at:
---

# ZZA-102 WSL NvChad IDE 작업 기록

## 작업 목표

WSL guest에서 C++, Go, Python용 NvChad IDE를 `mds apply --profile nvim-ide`로 재현하고, 기존 사용자 설정은 일반 apply에서 보존하며 명시적 adoption만 backup 후 관리 상태로 전환한다.

## 주요 변경 지점

- `catalog/components/guest.yaml`: IDE capability와 검증 가능한 C++, Go, Python language tool 설치 계약을 추가했다.
- `catalog/profiles/nvim-ide.yaml`: desktop 및 agent component 없이 Linux guest IDE graph만 선택하는 `nvim-ide` profile을 추가했다.
- `catalog/locks/versions.lock.yaml`: Pyright를 포함한 reviewed artifact identity를 고정했다.
- `internal/adapters/guest/editor.go`: user-owned `~/.config/nvim`의 기본 refusal과 timestamp backup을 남기는 explicit adoption을 구현했다.
- `internal/adapters/guest/ide.go`, `editor_config.go`, `plugin_tree.go`: NvChad starter와 IDE 설정의 선택 경계를 분리하고, 기존 managed tree의 누락·drift를 복구하며 lazy.nvim/NvChad/31개 plugin graph를 exact commit과 content-addressed runtime으로 고정했다. 실행 전후 실제 checkout HEAD와 실행 코드 clean 상태를 검사하고 final config를 headless restore/health로 로드한다.
- `internal/adapters/packages/functional.go`: clang-format, clang-tidy, lldb-dap, dlv, ruff, system Python debugpy와 C++ compile/run까지 실행 검증을 확장했다.
- `internal/cli/apply.go`, `root.go`: `--adopt-nvchad`를 apply 경로에만 연결하고 성공하는 WSL apply에서 production adapter option까지 전달되는 test seam을 추가했다.
- `tests/`와 golden plan: ownership, catalog resolution, managed tool behavior와 profile contract를 고정했다.

## 검증

- 깨끗한 Ubuntu 26.04 WSL에서 `mds apply --profile nvim-ide`가 완료됐다.
- plan digest는 `sha256:d300d9e275712047a01a84e179f550b3c0b33349490594f9c802e1c54e53d6c3`이다.
- base CLI, C toolchain, mise, Go 1.26.5, Neovim 0.11.5, pinned NvChad, Bun 1.3.14, Pyright 1.1.411, Python 3.14.6와 `nvim-ide-tools`가 `ready`로 확인됐다.
- PR #2 merge commit `61ede4860a9a2484a03693e4feed3cccc32c01c2`를 PR #3
  branch에 merge했다. `--adopt-nvchad`와 `--guest-bootstrap-archive` option을 함께
  보존하고 WSL/Lima certification profile에 새 IDE tool graph를 포함했다.
- 통합 head `ab073ab439d9a5976f355ec7a5fa0076576388ff`의 최종 리뷰에서 selection boundary,
  기존 managed tree migration, plugin graph pin, tool probe와 문서 구조 누락을 발견했다.
- 수정 head `1999833d5264bf24ec3cb9daaa79c403d310d642`에서 NvChad starter와 IDE 설정을
  별도 action으로 분리하고, exact plugin lock과 IDE 전체 tool probe를 추가했다. 중복 child
  plan/solution은 제거하고 canonical Notion·워크스페이스 문서로 통합했다.
- 최종 head `7ce2838f18e54a82433ffce8d1ecc3cf4447cb84`에서 moving code 실행 전 pinned
  config/lazy.nvim을 게시하고, 실제 31개 plugin checkout의 SHA와 clean 상태를 검증하며,
  최종 IDE config의 headless restore/health와 Neovim zero-exit 초기화 오류 탐지를 추가했다.
  config-only repair는 ready package 설치를 반복하지 않고, system Python debugpy와 C/C++
  compile/run probe, 성공하는 `--adopt-nvchad` CLI wiring 테스트를 포함한다.
- 보강 head `bd0eee4832750c37e58a6d4225dd34e418938fa4`에서 clangd만 존재하는 부분 설치도
  full package verify 실패 후 apply로 복구하고, IDE 설치 뒤 base plugin drift도 다시 감지한다.
  관리 Neovim launcher는 검증한 절대 경로로 실행하며 ownership marker와 config/runtime
  경로의 모든 중간 symlink를 거부한다. 최종 IDE runtime은 lock 밖 checkout을 제거하고
  디렉터리 이름 집합이 lock의 31개와 정확히 일치해야 ready가 된다.
- 최종 head `d90d4c9b23978af652404710aeb94da1be37672d`에서 Editor는 base checkout만
  소유하고 IDE-only drift는 IDE action이 복구하도록 action 경계를 고정했다. runtime root는
  ownership marker를 포함한 staging directory를 durable publish해 중단 시 빈 unowned root를
  남기지 않는다. Windows에서는 regular launcher를 확인하되 POSIX 실행 비트는 비-Windows에서만
  요구하고, editor/runtime 테스트를 별도 파일로 분리했다.
- 최종 head에서 `go test ./...`, `go test -race ./...`, `go vet ./...`, `mds`,
  `mds-evidence`, `mds-release` build, actionlint, 전체 shell shellcheck와
  `git diff --check`를 통과했다.
- 로컬 Neovim 0.11.1의 격리된 임시 home에서 base와 IDE 31개 plugin graph를 실제 GitHub
  checkout으로 restore하고 `checkhealth`까지 완료하는 opt-in network smoke를 통과했다.
- 깨끗한 WSL 실제 apply 증빙은 최초 기능 head에서 수행했다. 최종 head는 자동·실제 Neovim
  smoke로 검증했으며 clean WSL 전체 apply 재실행은 수행하지 않았다.
- 최신 head `d90d4c9b23978af652404710aeb94da1be37672d`의 GitHub CI와 code/doc review는
  진행 중이다.

## 외부 동기화

- Linear [ZZA-102](https://linear.app/zzanghyunmoo/issue/ZZA-102/make-the-wsl-nvchad-cgopython-ide-reproducible-with-mds-apply)는 `In Review` 상태다.
- canonical Notion [계획](https://app.notion.com/p/3b1ef22ad4fc81048ec9ee92fedf0be9)과 [티켓 구현 문서](https://app.notion.com/p/3b1ef22ad4fc813d954be68816256def)를 생성하고 이 문서와 같은 범위·검증 경계를 기록했다.

## Merge closeout

PR #3 merge 후 KB, Notion 기능 현황·티켓 결과, merge commit과 Linear `Done` 전환을 기록한다.
