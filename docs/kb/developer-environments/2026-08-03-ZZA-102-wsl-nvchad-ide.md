---
title: ZZA-102 WSL NvChad C++·Go·Python IDE 재현
ticket: ZZA-102
merged_pr: https://github.com/zzanghyunmoo/my-desk-setup/pull/3
merge_commit: 157566d34d60a8dc3680fad68fa5bb3cf4d46b83
work_evidence: docs/works/2026-08-01-ZZA-102-wsl-nvchad-ide-work.md
notion_feature_status: https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436
notion_ticket: https://app.notion.com/p/3b1ef22ad4fc813d954be68816256def
last_verified: 2026-08-03
---

# ZZA-102 WSL NvChad C++·Go·Python IDE 재현

## 현재 기능 상태

PR [#3](https://github.com/zzanghyunmoo/my-desk-setup/pull/3)은 squash merge commit
`157566d34d60a8dc3680fad68fa5bb3cf4d46b83`으로 병합됐다. `main`에서 Linux guest용
`nvim-ide` profile을 선택하면 NvChad 기반 C++, Go, Python IDE와 필요한 CLI tool graph를
동일한 resolver·plan·apply·doctor 계약으로 관리한다.

## 주요 동작과 경계

- `Editor` action은 NvChad starter, 공통 config와 base plugin set을 소유한다. `IDE` action은
  언어별 config와 IDE-only plugin set을 소유하므로 base repair가 exact IDE plugin spec을
  덮어쓰지 않는다.
- lazy.nvim과 31개 plugin checkout은 reviewed commit으로 고정된다. restore 뒤 lockfile,
  실제 checkout SHA·clean state와 directory name 집합을 다시 확인한다.
- 기존 사용자 `~/.config/nvim`은 일반 apply에서 덮어쓰지 않는다. 사용자가
  `--adopt-nvchad`를 명시한 경우에만 timestamp backup을 만든 뒤 관리 상태로 전환한다.
- ownership marker, config/runtime 경로의 중간 symlink와 관리 경계 밖 경로는 거부한다.
  runtime root는 marker를 포함한 staging directory 단위로 durable publish한다.
- 관리 Neovim은 검증된 `$HOME/.local/bin/nvim` 절대 경로로 실행한다. Windows에서는 정규
  launcher를 요구하되 POSIX executable bit는 Linux/macOS에서만 검사한다.
- 로그인, token과 서비스 인증은 자동화하지 않으며 사용자가 직접 실행한다.

## 검증 결과

- 최종 PR head `fb57c3d9cde044a7d345a9249b2337d848ea9228`에서 Linux/Windows GitHub CI와
  fixture scanner가 통과했고, code/doc review가 모두 PASS했다.
- `go test ./...`, `go test -race ./...`, `go vet ./...`, 세 CLI build, actionlint, 전체 shell
  shellcheck와 `git diff --check`를 통과했다.
- 로컬 Neovim 0.11.1의 격리된 임시 home에서 base와 IDE 31개 plugin graph를 실제 GitHub
  checkout으로 restore하고 `checkhealth`까지 완료하는 network smoke를 통과했다.
- 깨끗한 Ubuntu 26.04 WSL에서 최초 기능 head의
  `mds apply --profile nvim-ide`가 완료됐다. 최종 merged head에서는 자동 검증과 실제 Neovim
  smoke를 수행했으며 clean WSL 전체 apply는 다시 실행하지 않았다.

## 운영 및 사용 시 주의사항

- WSL에서 상태를 다시 확인할 때는
  `mds doctor --target wsl-guest:Ubuntu-26.04 --profile nvim-ide`를 사용한다. config, exact
  plugin graph와 C++/Go/Python tool probe가 모두 ready여야 성공한다.
- 사용자 Neovim 설정을 자동 병합하지 않는다. adoption 전에 backup 경로와 plan digest를
  확인한다.
- Windows host editor 설정은 이 profile의 범위가 아니다. 개발 런타임과 Neovim IDE는
  Linux guest에서 실행한다.
- 최종 merge commit의 clean WSL end-to-end apply가 필요하면 별도 실제 target 인증으로
  실행하고, 최초 기능 head의 결과를 merge commit 증빙으로 재사용하지 않는다.

## 관련 문서

- Work evidence:
  `docs/works/2026-08-01-ZZA-102-wsl-nvchad-ide-work.md`
- 재사용 패턴:
  `docs/solutions/architecture-patterns/managed-neovim-runtime-repair-boundaries.md`
- Notion canonical feature status:
  <https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436>
- Notion canonical ticket document:
  <https://app.notion.com/p/3b1ef22ad4fc813d954be68816256def>
