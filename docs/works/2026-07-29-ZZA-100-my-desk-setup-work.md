---
workflow_schema: compound-work/v1
ticket_id: ZZA-100
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-100/my-desk-setup-크로스플랫폼-개발-환경-bootstrap-구현
ticket_status: In Progress
ticket_completion: pending
remaining_prs:
ideation_status: complete
ideation_path: docs/ideation/2026-07-29-cross-platform-development-environment-ideation.html
ideation_notion_url: https://app.notion.com/p/3acef22ad4fc812e9e96c4cdbb34a796
ideation_waiver_reason:
plan_status: complete
plan_path: docs/plans/2026-07-29-ZZA-100-my-desk-setup-plan.md
plan_notion_url: https://app.notion.com/p/3acef22ad4fc81a08204d8022f962bcb
plan_waiver_reason:
work_status: in_progress
work_notion_url: https://app.notion.com/p/3acef22ad4fc81f0b3dad0814f0cee1a
pr_url:
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
notion_feature_status_url: https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436
notion_ticket_url: https://app.notion.com/p/3acef22ad4fc81f0b3dad0814f0cee1a
closed_at:
---

# ZZA-100 작업 기록

## 작업 목표

macOS·Windows 호스트와 Ubuntu 26.04 LTS 표준 Linux 게스트에서 동일한 개발 환경을
재현하는 `my-desk-setup`을 구현한다. 전체 설치와 컴포넌트별 선택 설치를 같은
resolver로 지원하고, 인증은 자동화하지 않고 사용자가 직접 수행하도록 안내한다.

## 주요 변경 지점

- 저장소 전환(U1): 기존 `settings` 저장소의 모든 ref를 복구 번들로 보존하고
  검증한 뒤, 별도 파괴적 승인에 따라 `my-desk-setup`으로 이름과 기준 이력을
  전환한다.
- 워크스페이스 연결(U1): 루트 `.gitmodules`와 `projects/` gitlink를 새 저장소
  이름과 깨끗한 기준 커밋에 맞춘다.
- 계획 커널·CLI(U2 이후): Go 기반 `plan`, `apply`, `doctor`, `update` 명령과
  deterministic lock/digest, target-local recovery state를 구현한다.
- 대상 어댑터(U2 이후): macOS·Windows 호스트와 Ubuntu 26.04 LTS 게스트의 설치 계획,
  전송, 실행, 검증 계약을 구현한다.
- 설치 카탈로그(U2 이후): CLI, 언어·빌드 도구, Herdr, NvChad 기반 Neovim,
  AI 코딩 에이전트, 게스트 로컬 Docker Engine을 전체 또는 선택 설치한다.

## 검증

- 실행 완료:
  - Linear `ZZA-100` 상태를 `In Progress`로 전환했다.
  - Notion `개발 문서 > 티켓` 아래 canonical 구현 기록을 생성했다.
  - 기존 `settings` 전체 ref를 다음 소유자 전용 복구 번들로 보존했다.
    - 경로:
      `/Users/gurumee92/Workspaces/.recovery/my-desk-setup/2026-07-29/settings-all-refs-2026-07-29.bundle`
    - 권한: 상위 디렉터리 `0700`, 번들 `0600`
    - SHA-256:
      `9c608e7e567a800f48f4a30431b916e01a18197d2cdeb8d5c8e8225f92d2dd8a`
    - 포함 ref: `main` `ff117fba701f`, feature
      `a97e377f7408`, `origin/HEAD`, `origin/main`, detached `HEAD`
    - `git bundle verify`: complete history, 5 refs, 통과
    - 독립 clone의 두 tip `git cat-file -t`: 모두 `commit`
    - 독립 clone `git fsck --full --strict`: 통과
  - GitHub 원격을 재확인했다.
    - 저장소: `zzanghyunmoo/settings`, public, viewer `ADMIN`
    - 기본 브랜치: `main`
    - 원격 브랜치 tip: `main` `ff117fba701f`, feature `a97e377f7408`
    - `main` branch protection API: 보호되지 않음(HTTP 404)
  - 루트 gitlink는 feature tip `a97e377f7408`을 가리키고, 로컬 submodule은
    같은 커밋의 clean detached HEAD임을 확인했다.
  - 승인 후 사용할 orphan Go baseline을 격리된 임시 Git 저장소
    `/private/tmp/my-desk-setup-baseline.FrL3Pi`에 만들었다.
    - root commit: `5326d4e` (`chore: initialize my-desk-setup Go baseline`)
    - 파일: `README.md`, `LICENSE`, `AGENTS.md`, `go.mod`, `go.sum`,
      `cmd/mds`, `internal/version`, CI, repository transition test
    - 기존 원격이나 워크스페이스 submodule에는 push·복사하지 않았다.
    - `go test ./...`: 3개 package 통과
    - `go vet ./...`: 통과
    - `go build ./cmd/mds`: 통과
    - `go run ./cmd/mds --version`: `dev`
  - 같은 격리 저장소의 티켓 브랜치 `zza-100/bootstrap`에서 U2 Environment
    Intent Graph를 구현하고 local commit `1c12767`
    (`feat: define the environment intent catalog`)로 고정했다.
    - 엄격한 YAML 로드와 closed Go domain type
    - component/capability 단일 소유권, dependency/reference/cycle 검증
    - macOS host, Windows host, WSL guest, Lima guest 모든 cell의
      `supported`/`unsupported`/`action-required` 명시
    - target-installer 및 target-dependency 호환성 검증
    - credential-like material과 미사용/missing version lock 거부
    - 순서 독립 canonical JSON과 SHA-256 catalog revision
    - `all`, profile, component/capability selection의 단일 resolver
    - owner/minimal profile과 초기 host/guest component catalog
    - `notion-cli`가 `notion-desktop`을 resolve하지 않고 guest `all`에 GUI가
      들어가지 않는 계약 테스트
    - `go test ./...`, `go vet ./...`, `go build ./cmd/mds`, `git diff --check`
      통과
  - canonical 계획과 Linear의 표준 guest가 `Ubuntu 26.04 LTS`임을 재확인하고,
    work evidence와 Notion 구현 기록에 잘못 적힌 `Debian 13`을 바로잡았다.
  - 격리 티켓 브랜치에서 U3 target discovery와 guest handoff를 구현하고 local
    commit `28698b3` (`feat: model target discovery and guest handoff`)로
    고정했다.
    - stable target ID와 mutable facts fingerprint 분리
    - macOS/Windows/WSL/Lima local discovery 및 WSL/Lima inventory parser
    - 복수 guest 발견 시 explicit target 선택 강제
    - Ubuntu 26.04 amd64/arm64 cloud image URL과 공식 SHA-256 pin
    - shell string을 만들지 않는 `executable + argv` WSL/Lima transport
    - timeout과 stdout/stderr 크기 제한
    - host/guest CLI·catalog revision handoff mismatch 차단
    - systemd inactive guest의 Docker 단계를 `action-required`로 차단
    - macOS POSIX/Windows PowerShell release bootstrap과 checksum 검증
    - `go test ./...`, `go vet ./...`, `go build ./cmd/mds`,
      `git diff --check`, `sh -n`, `shellcheck` 통과
    - 로컬에 `pwsh`가 없어 PowerShell parser 검증은 미실행
  - 격리 티켓 브랜치에서 U4 deterministic planning CLI를 구현하고 local
    commit `7f7a5be` (`feat: add deterministic planning CLI`)로 고정했다.
    - reviewed catalog를 Go binary에 embed하고 필요할 때만 `--catalog`로 override
    - `mds plan`의 `--all`, `--profile`, 반복 `--component`, `--interactive`
      입력을 하나의 normalized Selection과 resolver로 처리
    - dependency 순서, target eligibility, exact/manager/manual version,
      verification과 blocker를 stable `mds.plan/v1`으로 생성
    - human/JSON renderer가 같은 Plan을 소비
    - plan에 wall-clock 값을 넣지 않고 canonical SHA-256 digest 생성
    - 같은 의미의 all/profile/component selection이 byte-equivalent plan/digest를
      만드는 테스트
    - guest all의 GUI 0개, host all의 guest toolchain 0개 테스트
    - Notion CLI가 Notion Desktop을 resolve하지 않는 JSON golden plan
    - plan 전후 state directory와 target facts가 byte-identical인 통합 테스트
    - `go test ./...`, `go vet ./...`, `go build ./cmd/mds`,
      `git diff --check` 통과
  - 격리 티켓 브랜치에서 U5 exact apply와 recovery state를 구현하고 local
    commit `f85f1ff` (`feat: add exact apply and recovery state`)로 고정했다.
    - expected digest와 plan payload digest를 첫 write 전에 재계산
    - target preimage를 첫 write 전에 재관찰하고 fingerprint mismatch 거부
    - target-local single-writer lock, fsync journal, atomic receipt
    - root/symlink/non-regular state path 거부와 `0700`/`0600` 권한
    - action별 Observe → Apply → Verify → Observe 수렴
    - 실패 node의 downstream만 blocked하고 독립 node는 계속 실행
    - same-digest 재실행에서 이미 verified인 action을 no-op 처리
    - installer 성공과 journal write 사이 crash를 주입한 뒤 재관찰로 수렴
    - stale digest와 changed preimage에서 state/adapter mutation 0
    - target state isolation과 concurrent writer 차단 테스트
    - `go test ./...`, `go test -race ./...`, `go vet ./...`,
      `go build ./cmd/mds`, `git diff --check` 통과
  - 승인 대기 중인 새 구현도 임시 디렉터리 유실에 대비해 별도 영구 bundle로
    보존했다.
    - 경로:
      `/Users/gurumee92/Workspaces/.recovery/my-desk-setup/2026-07-29/my-desk-setup-pre-approval-2026-07-29.bundle`
    - 권한: `0600`
    - SHA-256:
      `f21019196c6fed419b937ed1f4e1272ec1c84552af04d28318812051216fa643`
    - refs: orphan baseline `5326d4e`, 티켓 브랜치 `f85f1ff`
    - `git bundle verify`: complete history, 3 refs, 통과
  - 격리 티켓 브랜치에서 U6/U7 production adapter와 실제 `apply` 연결을
    구현하고 local commit `3d9fd9e`
    (`feat: connect production host and guest apply adapters`)로 고정했다.
    - `internal/adapters/packages/`: Homebrew auto-update/implicit-upgrade 억제,
      WinGet exact ID, apt noninteractive `sudo -n`, mise/Bun exact version,
      checksum-verified binary/zip/tar.gz vendor install과 원자적 launcher
    - `internal/adapters/host/`: macOS desktop read-only probe, Windows WinGet
      inventory, Lima pinned Ubuntu 26.04 생성·시작, WSL/Ubuntu 설치와
      reboot/first-run `action-required` resume
    - `internal/adapters/guest/`: pinned NvChad config ownership, no-auto-update
      agent launcher, guest-local systemd Docker Engine/Compose와 외부
      `DOCKER_HOST` 충돌 차단
    - `internal/cli/apply.go`, `internal/execution/runner.go`: current-target
      재관찰, exact plan digest/preimage 확인, typed `action-required` receipt와
      journal, host가 guest filesystem을 직접 바꾸지 않는 실행 경계
    - `internal/transport/`: WSL/Lima 환경변수와 working directory를
      정렬된 guest argv로 전달하고 host process 환경과 분리
    - 공식/검증된 배포 경로로 Herdr `0.7.5`, ACLI `1.3.22-stable`,
      Notion CLI `0.21.5`, Linear CLI `2.3.0`을 pin해 guest `all`의
      24개 컴포넌트가 WSL/Lima 모두 blocker 0개로 계획됨
    - 인증/login/token probe는 installer, verification, receipt에 넣지 않음
    - macOS 실제 read-only host plan: host action 12개, guest-owned action
      0개, Xcode 수동 경계 1개
    - `go test ./...`, `go test -race ./...`, `go vet ./...`,
      `go build ./cmd/mds`, `git diff --check`, `sh -n`, `shellcheck` 통과
    - 로컬에 `pwsh`가 없어 수정한 Windows bootstrap의 PowerShell parser
      검증은 미실행
  - U6/U7 및 `apply` 구현을 포함한 새 복구 bundle을 추가로 보존했다.
    - 경로:
      `/Users/gurumee92/Workspaces/.recovery/my-desk-setup/2026-07-29/my-desk-setup-pre-approval-u7-2026-07-29.bundle`
    - 권한: `0600`
    - SHA-256:
      `aaaa81a4b35804f07dbe2ab36cb9edd35df0ab4c1c14c4e9af60ad9e34220b60`
    - refs: orphan baseline `5326d4e`, 티켓 브랜치 `3d9fd9e`
    - `git bundle verify`: complete history, 2 refs, 통과
    - 별도 clone `git fsck --full`과 두 ref 확인 통과
  - 격리 티켓 브랜치에서 U8 read-only doctor와 명시적 exact update를
    구현하고 local commit `6e456a2`
    (`feat: add read-only doctor and explicit updates`)로 고정했다.
    - `mds doctor`: 현재 target만 대상으로 설치·버전·소유권 상태를
      `Observe`하고, 설치·기능 실행·인증 probe 없이 stable
      `mds.doctor/v1` human/JSON report 생성
    - `mds update`: npm exact candidate 자동 발견 또는 검토된 candidate JSON을
      입력받아 lock diff와 resulting target plan을 먼저 출력하고, 같은
      update digest를 명시한 경우에만 적용
    - update 전에 plan payload, catalog/lock preimage, target fingerprint를
      재검증하고 stale digest에서는 lock·state mutation 0
    - 후보 provenance와 artifact URL을 absolute HTTPS로 제한하고 artifact
      SHA-256을 실제 32-byte hex digest로 검증
    - scoped npm package path encoding, rate limit, unsupported provider,
      user-owned NvChad 보호, mds-managed config replacement/restore,
      symlinked lock directory 차단 테스트
    - apply/update의 잘못된 output format을 첫 mutation 전에 거부
    - `go test ./...`, `go test -race ./...`, `go vet ./...`,
      `go build ./cmd/mds`, `git diff --check`, `shellcheck` 통과
    - 실제 macOS에서 `mds doctor --component xcode --format json`을 실행해
      `mds.doctor/v1`, `action-required`, 인증 미실행과 실행 전후 Git 상태
      동일을 확인
  - U8을 포함한 complete-history 복구 bundle을 이전 U7 bundle과 별도로
    보존했다.
    - 경로:
      `/Users/gurumee92/Workspaces/.recovery/my-desk-setup/2026-07-29/my-desk-setup-pre-approval-u8-2026-07-29.bundle`
    - 권한: `0600`
    - SHA-256:
      `e2d6a78dc7527ae3d42d5e660f91d8dacbb66048d1472952fd729ad977635ba4`
    - refs: orphan baseline `5326d4e`, 티켓 브랜치 `6e456a2`
    - `git bundle verify`: complete history, 2 refs, 통과
    - 별도 clone에서 branch tip 확인과 `git fsck --full --strict` 통과
  - 격리 티켓 브랜치에서 U9 실행 격리, 실제 대상 증거, 결정적 release,
    운영 문서와 review hardening을 완료하고 최종 local tip `4763239`로
    고정했다.
    - `2952509`: 명령 실행 환경을 target별 allowlist로 격리
    - `8920d45`: 실제 target의 plan·doctor·CLI·binary identity를 묶는
      `mds.target-evidence/v1` capture/strict verify 구현
    - `a3899b5`: 6개 OS/architecture artifact, checksum, manifest를 같은
      source epoch에서 재현하는 release pipeline과 promotion gate 구현
    - `c503501`: bootstrap, update, recovery, release 운영 절차 문서화
    - `ca1ae71`: 공용 setup primitive 단순화
    - `e77c0af`: `ce-code-review`에서 검증된 P1 14건을 수정
    - `4763239`: 실제 macOS capture에서 발견한 doctor의 stable
      `action-required` exit `4`를 보존하고 report의 `ready`와 exit signal
      불일치를 거부
  - `ce-code-review`는
    `/tmp/compound-engineering/ce-code-review/20260730-002105-0903f17d`에서
    실행했다.
    - owner profile 대상 인증, managed launcher, JSON exit 계약, doctor
      기능 검증, receipt schema, guest handoff, crash lock, partial receipt,
      update lock, npm tarball/SRI/SHA, Windows durable replace, release
      promotion, fresh target evidence, Docker local socket 관련 P1 14건을
      validator가 확인했고 모두 `e77c0af`에서 수정했다.
    - 선택 입력 관련 후보 1건은 validator가 false positive로 기각했다.
    - review 이후 실제 macOS 증거 실행으로 exit taxonomy 회귀를 발견했고,
      test-first 수정과 focused review를 반복한 최종 결과는 findings 0건이다.
  - 최종 head에서 다음 검증을 통과했다.
    - `go test ./...`
    - `go test -race ./...`
    - `go vet ./...`
    - `golangci-lint run ./...`
    - `actionlint`
    - `shellcheck bootstrap/*.sh scripts/*.sh`
    - darwin/linux/windows × amd64/arm64의 `go build ./...`
    - `git diff --check`
    - Gitleaks `8.30.1`의 source history scan과 최종 release directory scan
  - `0.1.0-rc.1` release를 최종 head에서 두 번 만들고 byte-identical임을
    `diff -qr`로 확인했다.
    - commit:
      `4763239146730f0491947a9a8756abee931bfdb4`
    - build date: `2026-07-30T02:14:21Z`
    - catalog revision:
      `sha256:98f3989c245a3a311bb8bb0dfe49329b583ef022f75103ce7742416e4488afc0`
    - release verification: 두 디렉터리 모두
      `scripts/verify-release.sh` 통과
    - artifact binary SHA-256:
      - darwin/amd64:
        `634a840a199aff631d46723c5484f4f7ff1cf87f456274753c6fe4e1076b965a`
      - darwin/arm64:
        `ea68bf29ae39365f754621a43fade4a1b1ee374633a33f136135b9622cb85a6c`
      - linux/amd64:
        `bbbd44c66ed062ca411b7811bf3eea0fb985d439ce00987746cf9fa2066ba93d`
      - linux/arm64:
        `153654d364150aa19bdbf1afb6c4d5a41aea93078f4d9f5577a42191e9d5394e`
      - windows/amd64:
        `b433d26f58169c44ee661c3412db8117c31187b78915373b3893ac775869a2c6`
      - windows/arm64:
        `3a66f7715864c18e9f01fd219bc8fc1fb5fc2c47fb15e435f1d3d1baa81c7a1c`
  - 최종 darwin/arm64 release bootstrap을 임시 prefix에서 checksum pin으로
    설치하고 `mds --version`의 version·commit·date와 macOS host plan의
    schema·target·catalog revision을 검증했다.
  - 같은 최종 binary로 실제 macOS host evidence를 capture했다.
    - bundle:
      `/private/tmp/mds-macos-evidence-4763239.pDqObs/macos-host`
    - target fingerprint:
      `sha256:57f0f28b1d1c225fbff55f69083408d92b3d4982eec1a31f1ef8432c39a48f60`
    - plan digest:
      `sha256:823d76fe4465fd16ce0ef4e0a11a9ba6b1fb23a29bdf9c86a5b13fdf65b074b3`
    - ready: Chrome, KakaoTalk, Linear Desktop, Notion Desktop, Slack
    - user-owned/version conflict: Bun, Claude Code, Codex, OpenCode
    - unready: managed `mds` Lima guest, WezTerm
    - manual action required: Xcode
    - 결과는 정직하게 `blocked`이며 evidence는 보존됐다.
    - checksum, CLI revision, catalog revision, target, binary SHA,
      plan digest, 45분 freshness를 지정한 strict identity verification은
      통과했다.
    - conflict/unready가 남아
      `--require-publication-acceptable` promotion verification은 예상대로
      실패했다.
    - evidence directory Gitleaks scan은 통과했다.
  - U9 최종 complete-history 복구 bundle을 영구 경로에 보존했다.
    - 경로:
      `/Users/gurumee92/Workspaces/.recovery/my-desk-setup/2026-07-30/my-desk-setup-final-u9-4763239-2026-07-30.bundle`
    - SHA-256:
      `81b41a5c2acb3708d31830ae5d0d25805637622429b3a56dee62ed9a00812048`
    - refs: baseline `5326d4e`, 티켓 브랜치 `4763239`, 이전 origin 추적 ref
    - `git bundle verify`: complete history, 5 refs, 통과
    - 별도 clone에서 `git fsck --full --strict`, head/baseline tip,
      최종 `go.mod` byte 비교 통과
- 미실행:
  - 저장소 rename, orphan baseline, force-push, 원격 브랜치 정리는 승인 전이므로
    실행하지 않았다.
  - 실제 Windows/WSL target 인증은 현재 macOS 실행 환경에서 수행할 수 없어
    미실행이다.
  - Lima `2.1.4`에는 `home-ai-infra`라는 별도 stopped Ubuntu guest만 있고,
    제품이 소유할 `mds` guest는 없다. 사용자 소유 VM을 시작하거나 변경하지
    않았으며 `lima-guest:mds` 인증은 저장소 전환과 명시적 apply 뒤 실행한다.
  - macOS 실제 evidence가 conflict/unready를 포함하므로 release promotion은
    아직 차단 상태다.

## 외부 동기화

- Linear: [ZZA-100](https://linear.app/zzanghyunmoo/issue/ZZA-100/my-desk-setup-크로스플랫폼-개발-환경-bootstrap-구현)
  — `In Progress`
- Notion 계획:
  [My Desk Setup 구현 계획](https://app.notion.com/p/3acef22ad4fc81a08204d8022f962bcb)
- Notion 구현 기록:
  [ZZA-100 My Desk Setup 구현 기록](https://app.notion.com/p/3acef22ad4fc81f0b3dad0814f0cee1a)

## Merge closeout

아직 merge 전이다. PR merge 뒤 KB 경로, Notion 기능 현황·티켓 문서,
merge commit, Linear `Done` 전환 결과를 기록한다.
