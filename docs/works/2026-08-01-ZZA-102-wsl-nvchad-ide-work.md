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
- `internal/adapters/guest/ide.go`, `editor_config.go`: NvChad starter와 IDE 설정의 선택 경계를 분리하고, 기존 managed tree의 누락·drift를 복구하며 lazy.nvim/NvChad/전체 plugin graph를 exact commit으로 고정했다.
- `internal/adapters/packages/functional.go`: clang-format, clang-tidy, lldb-dap, dlv, ruff, debugpy까지 IDE tool 실행 검증을 확장했다.
- `internal/cli/apply.go`: `--adopt-nvchad`를 apply 경로에만 연결했다.
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
- 수정 head에서 `go test ./...`, 영향 범위 `go test -race`, `go vet ./...`, `mds`,
  `mds-evidence`, `mds-release` build, actionlint, 전체 shell shellcheck와
  `git diff --check`를 통과했다.
- 깨끗한 WSL 실제 apply 증빙은 최초 기능 head에서 수행했다. 수정 head의 exact plugin lock은
  자동 테스트로 검증했으며 clean WSL 재실행은 수행하지 않았다.
- 최신 head의 GitHub CI와 code/doc review는 진행 중이다.

## 외부 동기화

- Linear [ZZA-102](https://linear.app/zzanghyunmoo/issue/ZZA-102/make-the-wsl-nvchad-cgopython-ide-reproducible-with-mds-apply)는 `In Review` 상태다.
- canonical Notion [계획](https://app.notion.com/p/3b1ef22ad4fc81048ec9ee92fedf0be9)과 [티켓 구현 문서](https://app.notion.com/p/3b1ef22ad4fc813d954be68816256def)를 생성하고 이 문서와 같은 범위·검증 경계를 기록했다.

## Merge closeout

PR #3 merge 후 KB, Notion 기능 현황·티켓 결과, merge commit과 Linear `Done` 전환을 기록한다.
