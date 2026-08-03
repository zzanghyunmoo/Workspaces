---
title: ZZA-102 WSL NvChad IDE 재현 계획
date: 2026-08-01
ticket_id: ZZA-102
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-102/make-the-wsl-nvchad-cgopython-ide-reproducible-with-mds-apply
notion_url: https://app.notion.com/p/3b1ef22ad4fc81048ec9ee92fedf0be9
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
---

# ZZA-102 WSL NvChad IDE 재현 계획

이 문서는 Notion [ZZA-102 WSL NvChad IDE 재현 계획](https://app.notion.com/p/3b1ef22ad4fc81048ec9ee92fedf0be9)을 canonical source로 동기화한 로컬 계획이다.

## Product Contract

### Goal Capsule

WSL guest에서 `mds apply --profile nvim-ide` 한 번으로 C++, Go, Python용 NvChad IDE를 재현한다. 기존 사용자 소유 `~/.config/nvim`을 자동으로 덮어쓰지 않으며, 명시적 adoption만 복구 가능한 backup을 만든 뒤 mds 관리 상태로 전환한다.

### Requirements

- `nvim-ide` profile은 C++, Go, Python runtime과 Neovim, NvChad, IDE tooling만 선택한다.
- clangd, gopls, Pyright, formatter, linter, debugger는 reviewed artifact 또는 distro package 계약으로 설치하고 실제 command를 검증한다.
- 일반 apply는 user-owned Neovim configuration을 변경하지 않는다.
- `--adopt-nvchad`를 명시한 경우에만 기존 configuration을 timestamp backup으로 보존한다.
- editor, package manager, AI agent 인증은 실행하지 않는다.

## Planning Contract

의존성 순서는 catalog와 immutable lock 정의 → editor ownership 및 IDE 설정 경계 → CLI 통합과 검증 순서다. `nvchad`는 starter만 소유하고 `nvim-ide-tools`가 LSP·formatting·linting·DAP 설정을 소유해 선택 설치 경계를 보존한다.

## Implementation Units

### U1 — Catalog, profile, immutable pins

1. `catalog/components/guest.yaml`에 IDE capability와 language tool graph를 추가한다.
2. `catalog/profiles/nvim-ide.yaml`에 Linux guest용 `nvim-ide` profile을 추가한다.
3. Pyright artifact와 버전을 lock하고 managed Bun 경로로 실행한다.
4. lazy.nvim, NvChad와 전체 plugin graph를 immutable commit으로 고정한다.

### U2 — NvChad ownership, adoption, IDE configuration boundary

1. 일반 apply는 user-owned `~/.config/nvim`을 거부한다.
2. `--adopt-nvchad`를 명시한 경우에만 timestamp backup으로 이동한 뒤 managed starter를 게시한다.
3. NvChad starter와 IDE tool configuration을 서로 다른 component action으로 게시·관찰·검증한다.
4. 기존 mds-managed NvChad에 새 IDE configuration이 없거나 drift된 경우 `nvim-ide-tools` action이 이를 absent로 감지해 복구한다.

### U3 — CLI integration, tests, and documentation

1. adoption flag는 `apply`에만 전달하고 `doctor`와 `update`에는 전달하지 않는다.
2. ownership refusal, backup adoption, selection boundary, exact profile graph, plugin lock, catalog/golden plan과 runtime behavior를 자동 테스트한다.
3. 깨끗한 Ubuntu 26.04 WSL guest에서 실제 apply와 doctor를 검증한다.
4. 운영 문서와 work evidence를 canonical Notion 문서에 맞춰 동기화한다.

## Verification Contract

- `go test ./...`, `go test -race ./...`, `go vet ./...`, `go build ./cmd/mds`
- catalog 및 golden plan 회귀 테스트
- user-owned configuration refusal와 explicit adoption backup 테스트
- 깨끗한 Ubuntu 26.04 WSL에서 `mds apply --profile nvim-ide` 실행 후 모든 selected action이 `ready`

## Definition of Done

- `nvim-ide`가 의도한 WSL IDE graph만 선택한다.
- 일반 apply는 기존 설정을 보존하고 adoption은 발견 가능한 backup을 남긴다.
- clean WSL apply에서 전체 action이 ready다.
- 최신 main을 통합한 PR head에서 code/doc review와 CI가 모두 통과한다.

## 추적

- Linear: [ZZA-102](https://linear.app/zzanghyunmoo/issue/ZZA-102/make-the-wsl-nvchad-cgopython-ide-reproducible-with-mds-apply)
- PR: [my-desk-setup #3](https://github.com/zzanghyunmoo/my-desk-setup/pull/3)
- Work evidence: `docs/works/2026-08-01-ZZA-102-wsl-nvchad-ide-work.md`
