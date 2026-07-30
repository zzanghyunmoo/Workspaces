---
workflow_schema: compound-work/v1
ticket_id: ZZA-100
ticket_url: https://linear.app/zzanghyunmoo/issue/ZZA-100/my-desk-setup-크로스플랫폼-개발-환경-bootstrap-구현
ticket_status: Done
ticket_completion: complete
remaining_prs:
ideation_status: complete
ideation_path: docs/ideation/2026-07-29-cross-platform-development-environment-ideation.html
ideation_notion_url: https://app.notion.com/p/3acef22ad4fc812e9e96c4cdbb34a796
ideation_waiver_reason:
plan_status: complete
plan_path: docs/plans/2026-07-29-ZZA-100-my-desk-setup-plan.md
plan_notion_url: https://app.notion.com/p/3acef22ad4fc81a08204d8022f962bcb
plan_waiver_reason:
work_status: complete
work_notion_url: https://app.notion.com/p/3acef22ad4fc81f0b3dad0814f0cee1a
pr_url: https://github.com/zzanghyunmoo/my-desk-setup/pull/1
closeout_status: complete
merged_pr_url: https://github.com/zzanghyunmoo/my-desk-setup/pull/1
merge_commit: 58b22df0dc80617be0ab11c3515bb79cfba0b14b
kb_paths: docs/kb/developer-environments/2026-07-30-ZZA-100-my-desk-setup.md
notion_feature_status_url: https://app.notion.com/p/3acef22ad4fc81e0813ff060d2fdd436
notion_ticket_url: https://app.notion.com/p/3acef22ad4fc81f0b3dad0814f0cee1a
closed_at: 2026-07-30T10:14:33Z
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
    - capture bundle:
      `/private/tmp/mds-macos-evidence-4763239.pDqObs/macos-host`
    - 영구 보존 bundle:
      `/Users/gurumee92/Workspaces/.recovery/my-desk-setup/2026-07-30/evidence/macos-host-4763239`
    - 영구 디렉터리 권한 `0700`, 파일 권한 `0600`
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
    - 영구 복제 뒤 `checksums.txt` 재검증과 Gitleaks 재검사도 통과했다.
  - U9 최종 complete-history 복구 bundle을 영구 경로에 보존했다.
    - 경로:
      `/Users/gurumee92/Workspaces/.recovery/my-desk-setup/2026-07-30/my-desk-setup-final-u9-4763239-2026-07-30.bundle`
    - SHA-256:
      `81b41a5c2acb3708d31830ae5d0d25805637622429b3a56dee62ed9a00812048`
    - refs: baseline `5326d4e`, 티켓 브랜치 `4763239`, 이전 origin 추적 ref
    - `git bundle verify`: complete history, 5 refs, 통과
    - 별도 clone에서 `git fsck --full --strict`, head/baseline tip,
      최종 `go.mod` byte 비교 통과
  - U9 이후 `ce-doc-review`의 여섯 reviewer lens로 계획과 구현의 일치,
    보안·운영·검증 계약을 재검토하고 U10 hardening을 완료했다. 위
    `4763239` release/evidence/bundle은 검토 전 역사적 증거로 보존하되,
    최종 review head와 release identity는 `80f866a`로 대체한다.
    - 계획 문서는 읽기 전용 target discovery와 apply 시점 guest
      provisioning 의존성을 분리하고, `conflict` outcome, target
      image/catalog identity, `review_commit`/`release_commit`, update 전체
      target matrix, CI trust boundary와 approval-gated remote cutover를
      명시했다.
    - `4fa9602`: fresh guest가 host release에 embed된 같은 release Linux
      archive URL·SHA-256과 bounded stdin bootstrap으로
      `~/.local/bin/mds`를 owner-only·atomic하게 self-provision한다.
      apt/Docker privilege preflight는 `/usr/bin/sudo -n true`만 사용하고
      비밀번호를 묻지 않으며, Docker group 변경은 root-equivalent 권한임을
      알리는 사용자 수동 action으로 남겼다. WSL은 pinned `.wsl` artifact를
      checksum 검증한 뒤 `wsl.exe --install --from-file`로 설치한다.
    - `221e2a0`: update plan/apply가 대상 component의 모든 eligible
      macOS/Windows/WSL/Lima × amd64/arm64 compatibility matrix를 검증하고
      vendor artifact 누락 시 lock publication을 거부한다.
    - `5d99a8b`: GitHub Actions를 full commit SHA로 pin하고 actual-target
      runner를 네 허용 target/label pair, credential-free OS account와
      protected environment 계약으로 제한했다.
    - `196bb5b`: Ubuntu target YAML과 pinned image URL·SHA-256을 canonical
      catalog revision 및 Lima/WSL plan action input에 포함해 guest image를
      reviewed plan identity에 묶었다.
    - `80f866a`: shellcheck가 지적한 WSL 오류 문자열을 정리하고 최종
      review head를 고정했다.
  - 최종 head `80f866abe5f9570e382309c08f988fabca1fff3a`에서 다음
    검증을 다시 통과했다.
    - `git diff --check`
    - `go test ./...`
    - `go test -race ./...`
    - `go vet ./...`
    - `golangci-lint run ./...` — `0 issues`
    - `actionlint`
    - `shellcheck bootstrap/*.sh scripts/*.sh`
    - darwin/linux/windows × amd64/arm64의 `go build ./...`
    - Gitleaks `8.30.1` source history scan — 19 commits, leak 0
  - `0.1.0-rc.1` release를 최종 head에서 두 번 만들고 두 디렉터리의
    `scripts/verify-release.sh`, `diff -rq`와 release Gitleaks scan을
    통과했다.
    - commit:
      `80f866abe5f9570e382309c08f988fabca1fff3a`
    - build date: `2026-07-30T03:06:25Z`
    - catalog revision:
      `sha256:20ace324d143c47fd8dfe1f079c7d31c21dfabb295aedb476910faeaa30574dd`
    - release directories:
      `/private/tmp/mds-final-release-80f866a-one.xulkP0/dist`,
      `/private/tmp/mds-final-release-80f866a-two.5XfCKu/dist`
    - archive/binary SHA-256:
      - darwin/amd64:
        `ec36e32ff7dd4c74ad32334e86a3a94d8b22a922575f477d7447110a6545e611` /
        `e8e9033993ed7fa1970f252c2ad2a7308d90dfdb93935ded6bc05e970cdc647a`
      - darwin/arm64:
        `740a3181878e4915bfa0403d81728d2baba8adafd9c400e28875d66b18446ad4` /
        `8ef14cddd5909ee46e438cd11387621b05e8ee90c62294af5e0284a2bb7e55ee`
      - linux/amd64:
        `fbe916be11589b7d6a4a37332f7363577b210c225b7fa97a556b0f5eec268359` /
        `126c2ea58301281a79e6af8995172929c0c2920c4c1136310e2729c1adcb3469`
      - linux/arm64:
        `a5401b04302ab185733c58eb8daf3307abf3396ea778ffe77fe142d97e264e1f` /
        `90d173173704d91ecba12c595e4d153aaf794f5572ac9f134e99e408bd73efd4`
      - windows/amd64:
        `3b6d4a4e54c4a24dddc608e77cd2ffb7607e5a1eacf3e123dd117a5e797da619` /
        `fa502fa1ea1af681d6760dc01891556b3a981b9ecb1094469657d1b5c3e6fff1`
      - windows/arm64:
        `ccbc82a4d8733c5c1f913020aa635ca0a194bc75b1023511e6f9d53f69110730` /
        `2c8679faa0003b91506e94c3cbad367f577e5936bcd77aba2394db5b5a470ed1`
  - 최종 darwin/arm64 release binary로 실제 macOS host evidence를 다시
    capture하고 strict identity를 검증했다.
    - 임시 capture:
      `/private/tmp/mds-macos-evidence-80f866a.XhHxqF/macos-host`
    - 영구 보존:
      `/Users/gurumee92/Workspaces/.recovery/my-desk-setup/2026-07-30/evidence/macos-host-80f866a`
    - 영구 디렉터리 권한 `0700`, 파일 권한 `0600`
    - target fingerprint:
      `sha256:bb9b70fb486d058e00388a3e42f48610f690bb4faec974b44de6ae9b97963d08`
    - plan digest:
      `sha256:f653439b450ee8a60ab473e02293cf8b72358226c4b6a11976640e26cd8e7e75`
    - binary SHA-256:
      `8ef14cddd5909ee46e438cd11387621b05e8ee90c62294af5e0284a2bb7e55ee`
    - ready: Chrome, KakaoTalk, Linear Desktop, Notion Desktop, Slack
    - conflict: Bun, Claude Code, Codex, OpenCode
    - unready: Lima `mds`, WezTerm
    - action-required: Xcode
    - 결과는 정직하게 `blocked`이며 commit/catalog/plan/binary/freshness
      exact identity verification, checksum 재검증과 Gitleaks scan은
      통과했다. conflict/unready가 남아 publication acceptable 검증은
      예상대로 실패했다.
  - U10 최종 complete-history 복구 bundle을 영구 경로에 보존했다.
    - 경로:
      `/Users/gurumee92/Workspaces/.recovery/my-desk-setup/2026-07-30/my-desk-setup-final-u10-80f866a-2026-07-30.bundle`
    - SHA-256:
      `46d5be7f5d2744523838d31b74c4ca4b0a2b6d42bc8a5a79a865553bcaca1600`
    - 권한: `0600`
    - refs: baseline `5326d4e`, 티켓 브랜치 `80f866a`, 이전 origin 추적 ref
    - `git bundle verify`: complete history, 5 refs, 통과
    - 별도 clone에서 `git fsck --full --strict`, exact HEAD와
      최종 `go.mod` byte 비교 통과
  - U11 final PR hardening을 최신 PR staging snapshot에 적용했다.
    - bootstrap privilege allowlist를 절대 경로로 고정하고, guest binary와
      owner marker를 archive/binary SHA-256 및 durable transaction marker로
      결합해 중단 뒤 재시도에서도 기존 또는 다음 정확한 binary만 허용한다.
    - metadata/npm 요청은 redirect를 계속 거부하고, checksum-pinned GitHub
      Release와 guest bootstrap만 credential-free HTTPS redirect를 최대 3회
      허용하도록 네트워크 계약과 테스트를 분리했다.
    - WSL/Lima image identity를 root-owned
      `/etc/mds/image-identity-v1`에서 관측하고 embedded catalog와 일치할 때만
      certification에 사용해, 기대값을 실제값처럼 합성하지 않도록 했다.
    - guest lifecycle을 `preparing` → `committed` 소유권 상태로 바꿔
      late success 또는 같은 이름의 외부 guest를 자동 채택하지 않도록 했다.
      최종 review에서 발견한 stale committed receipt 경계도
      `mds.guest-ownership/v3`의 무작위 creation nonce와 root-owned image
      marker를 결속해 닫았다. live marker의 nonce가 다르거나 기존 guest가
      stopped여서 mutation 없이 검증할 수 없으면 start/bootstrap을 수행하지
      않는다.
    - catalog YAML과 lock을 runtime에서도 checked-in JSON Schema와 semantic
      규칙으로 검증하고, mise lock/config는 두 목적지를 모두 preflight한 뒤
      lock-first 순서로 게시한다.
    - Unix process group과 관측 가능한 descendant, Windows Job Object를
      cancellation에 연결하고 CLI entrypoint의 첫 signal은 unwind, 두 번째
      signal은 강제 종료가 되도록 했다. double-fork/reparented daemon과 원격
      WSL/Lima 자식은 보장 범위가 아님을 운영 문서에 명시했다.
    - update intent/receipt publication을 공용 durable primitive로 통합하고,
      certification의 최초·반복 apply receipt와 publication 실패 테스트를
      강화했다.
    - privilege validator가 `sudo`, `/bin/sudo`와 shell wrapper를 transport
      전에 거부하도록 해 `/usr/bin/sudo` exact allowlist 우회를 차단했다.
    - target별 installer enum과 명시적 empty field를 published JSON Schema가
      semantic validator와 동일하게 거부하도록 raw JSON parity test를 추가했다.
    - Windows downloader는 하나의 10분 cancellation token을 redirect/header와
      비동기 body read 전체에 적용해 headers 뒤 stalled body도 bounded하게
      중단한다.
  - U11 staging snapshot에서 다음 검증을 통과했다.
    - `git diff --cached --check`
    - `go test ./...`
    - `go test -race ./...`
    - `go vet ./...`
    - `golangci-lint run ./...` — `0 issues`
    - `actionlint`
    - `shellcheck bootstrap/macos.sh internal/adapters/host/guest-bootstrap.sh scripts/*.sh`
    - darwin/linux/windows × amd64/arm64의 `go build ./cmd/...`
    - windows/amd64·windows/arm64의 전체 test package cross-compile
    - 같은 synthetic release identity의 deterministic release build/verify
    - Gitleaks `8.30.1` source history와 release directory scan — leak 0
  - PR #1은 orphan bootstrap baseline부터 하나의 end-to-end control-plane
    계약을 처음 게시하는 변경이라 현재 197개 파일 규모다. 구현은 U1–U11의 작은
    local commit으로 검증했지만, 지금 PR을 다시 나누면 중간 commit이 buildable
    repository transition을 나타내지 못하고 bootstrap/catalog/plan/apply/
    evidence/release 계약의 상호 검증을 깨뜨린다. 따라서 이 첫 baseline PR에
    한해 대형 PR 분리를 `waived`하고, 후속 기능은 작은 티켓/PR로 분리한다.
  - staging snapshot의 `ce-code-review`는
    `/tmp/compound-engineering/ce-code-review/20260730-163000-final2`에서
    P1 한 건과 고유 P2 세 건을 확인했다.
    - relative/alternate `sudo`와 shell wrapper의 privilege allowlist 우회
    - committed ownership receipt가 same-name replacement guest를 채택하는 문제
    - published target schema의 empty/incompatible installer 허용
    - Windows `ResponseHeadersRead` 뒤 stalled body의 timeout 누락
    - 위 blocker는 모두 코드와 회귀 테스트로 수정했다.
  - 후속 canonical snapshot
    `/tmp/compound-engineering/ce-code-review/20260730-173000-final4`
    (`full.diff` SHA-256
    `18fb32ae584b2d0f788c8e6bf5f0f005acb6cafdfb30f6b355d9315a4a57a15f`)
    리뷰에서 다음 blocker와 품질 문제를 추가로 확인했다.
    - catalog-originated verification이 privileged installer allowlist나
      interpreter를 통해 root mutation을 우회할 수 있는 문제
    - WSL 최초 기본 사용자가 root여도 준비 완료로 판단하는 문제
    - guest certification이 parsed creation nonce를 host committed ownership
      record와 대조하거나 evidence fingerprint에 결속하지 않는 문제
    - 내부 명령 최대 예산 합과 같은 180분 job timeout으로 후처리 여유가 없는
      문제
    - guest runtime 단일 파일 1,000줄 초과와 Observe의 ownership marker 이중
      probe
    - 이를 해결해 catalog verification을 별도 non-privileged v1 probe
      계약으로 분리했다. 후속 final5 보안 리뷰에서 executable-only allowlist도
      임의 Python/Bun file, Git shell alias, `gh auth token`과 대체 executable
      path를 허용할 수 있음을 확인해, embedded catalog의 component별
      `command`·`functional` 전체 argv exact match와 Docker guest-local endpoint
      exact 변형만 허용하도록 다시 닫았다.
    - WSL 기본 UID·passwd home·`$HOME`을 확인해 root이면 bootstrap 전에
      `action-required`로 중단한다.
    - 최초 구현은 workflow dispatcher가 host committed record의 creation
      nonce를 입력했으나 final5 리뷰에서 그 값의 authority가 caller에게 있음을
      확인했다. dispatcher input을 제거하고 target별 전용 runner service의
      root-owned `MDS_EXPECTED_GUEST_CREATION_NONCE`만 사용해 live marker와
      대조하며, 관측 nonce를 guest target facts, plan fingerprint와
      certification bundle identity에 포함한다.
    - actual-target job timeout을 240분으로 늘려 내부 최대 명령 예산 180분과
      checkout·compile·verify·upload 사이에 60분 여유를 뒀다.
    - guest lifecycle을 `runtime.go`, `guest_handoff.go`,
      `guest_ownership.go`로 분리하고 Observe의 marker read를 한 번으로 줄였다.
    - 각 수정은 직접 privilege escape, exact catalog argv, runner-local nonce,
      replacement nonce, root-default WSL, workflow margin, single marker read
      회귀 테스트로 고정했다. guest runtime과 1,000줄을 넘은 test file도 역할별
      파일로 분리했다.
  - final6 code snapshot은
    `/tmp/compound-engineering/ce-code-review/20260730-184500-final6`
    (`full.diff` SHA-256
    `d6cecc1d37b6e924bac1f820e2012b6e183fb09b77b2e1e2005af9787c1b0f8e`)
    이다. 정확성·보안·테스트 reviewer는 P1/P2/P3 0건으로 판정했다.
    - `go test ./...`, `go test -race ./...`, `go vet ./...`,
      `golangci-lint run ./...`, `actionlint`, `shellcheck`, `git diff --check`
      통과
    - darwin/linux/windows × amd64/arm64 `go build ./cmd/...`와
      windows/amd64·windows/arm64 전체 test package cross-compile 통과
    - 같은 synthetic identity의 release 두 번이 byte-identical하고 두 bundle의
      strict verify 및 Gitleaks `8.30.1` source/release scan 통과
    - 문서 적대적 검토에서 최신 U11 head의 actual macOS evidence 부재 표현,
      final snapshot 증빙과 Lima 수동 certification nonce 인자를 지적받아
      README·bootstrap·target evidence 문서와 이 work evidence를 수정했다.
  - final7 doc review는 위 세 수정은 확인했지만 actual-target runner의 외부
    trust boundary를 실제로 준비할 runbook이 없고 work evidence도 final7
    identity를 반영하지 않았다고 판정했다.
    - `docs/operations/target-certification-runner.md`에 네 target별 전용
      account/work directory/exact label, protected ref/environment와 reviewer,
      host committed ownership record 위치·schema/provider/name/image/nonce
      검증, guest systemd service의 root-owned nonce 주입, dispatch preflight와
      guest 재생성 시 nonce rotation 순서를 추가했다.
    - 최신 canonical snapshot은
      `/tmp/compound-engineering/ce-code-review/20260730-200000-final12`
      (`full.diff` SHA-256
      `975842daf9fc474a4129a1d201307b054c9c2d51d70813f886a5b4222e9b5f3f`)
      이며 final6 이후 child 변경은 운영 문서 정정과 runner runbook 추가뿐이다.
      runner 계정의 Docker group을 전면 금지하면 guest Docker probe가 불가능한
      모순도 final9 전에 제거했다. blanket admin/passwordless sudo는 금지하되
      prompt 없는 system/Docker prerequisite는 dispatch 전 준비하고 reviewed
      target-local Docker group membership만 허용한다.
    - final9 doc review에서 개인 repository에 존재하지 않는 runner group을
      전제한 절차와 Windows host의 WSL ownership record를 POSIX path/mode로
      검사한 절차를 발견했다. final10은 repository-level runner 직접 등록으로
      정정하고, PowerShell에서 user profile path·non-reparse regular file·owner
      및 NTFS ACL·JSON identity를 확인한 뒤 `wsl.exe --user root`로 live marker와
      대조하는 별도 WSL 절차를 추가했다. final11은 live marker를 읽기 전에
      WSL 안에서 regular/non-symlink와 root owner/group 및 허용 mode까지 검사한다.
      final11 correctness review가 shell AND-list의 실패 arm 누락을 발견해
      final12에서 비정규/reparse marker가 명시적 `exit 74`로 fail closed하도록
      고정했다.
    - final12의 `correctness.json`, `security.json`, `testing.json`,
      `doc-review.json`은 모두 최신 snapshot SHA를 확인했고 P1/P2/P3 0건으로
      pass/ready-to-merge 판정했다. PowerShell runbook snippet의 native Windows
      dry run과 네 actual target 인증은 미실행 잔여위험으로 유지한다.
    - canonical Notion 계획과 티켓 문서도 final12 path/hash, 네 reviewer pass,
      runner trust boundary와 현재-head 네 actual target 미실행 상태로
      동기화하고 재조회해 확인했다.
    - final12 reviewed tree를 child commit
      `2f087b69b4113054468f6eff29552cc51e50ecc7`
      (`fix(review): harden bootstrap and certification boundaries`)로 고정했다.
      push 전 복구 bundle
      `/Users/gurumee92/Workspaces/.recovery/my-desk-setup/2026-07-30/my-desk-setup-final-u12-2f087b6-2026-07-30.bundle`
      (SHA-256
      `b969093ea357ee810c660507d44038a4520e8673c09f6e3d788e3413526a3ce0`,
      mode `0600`)을 만들고 complete history 7 refs, 독립 clone
      `git fsck --full --strict`, exact HEAD와 `go.mod` byte 비교를 통과했다.
  - final12를 PR에 push한 뒤 처음 실행된 Windows native `go test ./...`가
    Windows 이식성 경계를 드러냈다.
    - read-only handle의 `File.Sync`가 `Access is denied`를 반환하던 durable
      publication은 Windows에서 write-capable handle로 flush하도록 수정했다.
    - 종료 뒤 비어 있는 Windows Job Object를 다시 terminate해 정상 명령을
      `invalid argument` 실패로 바꾸던 경로는 active process count를 확인하고
      종료 race 뒤 empty job만 명시적으로 정상 처리하도록 수정했다.
    - checkout CRLF가 embedded `mise.toml`·`mise.lock` identity를 바꾸지 않도록
      loader의 LF normalization과 `.gitattributes`를 추가했다.
    - POSIX guest bootstrap shell 및 executable mode assertion은 POSIX에서
      계속 실행하고, Windows에서는 같은 content·ownership·non-regular path
      계약과 native PowerShell cancellation을 검증하도록 경계를 명시했다.
    - PowerShell cancellation test는 `MethodInvocationException`의 inner
      `OperationCanceledException`까지 확인하고, HTTP success response가
      pipeline으로 출력되지 않도록 했다.
  - 위 수정을 child commit
    `a403984392a52b0e744a3874ff63d583f9dacbe1`
    (`fix(windows): make native verification portable`)로 push했다.
    - canonical snapshot:
      `/tmp/compound-engineering/ce-code-review/20260730-213000-final13`
    - `full.diff` SHA-256:
      `bbca7bfc26c23cca824d832b645f205abb95f65ddc400cbfc579431d89b5f3ad`
    - local `go test ./...`, `go test -race ./...`, `go vet ./...`,
      `golangci-lint run ./...`, `actionlint`, `shellcheck`, `git diff --check`
      통과
    - Windows amd64·arm64 전체 package cross-compile 통과
    - GitHub Actions run `30531180807`: hosted `verify`와
      `windows-verify`의 native `go test ./...` 및 Windows CLI build 통과
    - fixture contract 통과, PR actual-target job은 설계대로 skipped
    - final13 document review가 이 work evidence의 final12 stale 표현과
      계획·catalog 문서의 raw exact-byte 표현을 지적해, 최신 head/검증과
      LF-normalized exact-content 계약으로 바로잡았다.
  - final13 push 직후 complete-history 복구 bundle을 별도로 보존했다.
    - 경로:
      `/Users/gurumee92/Workspaces/.recovery/my-desk-setup/2026-07-30/my-desk-setup-final-u13-a403984-2026-07-30.bundle`
    - SHA-256:
      `2f8899928bbb2198b35a383a31f33d0e137ae91579209aed8e656d2b908e4d69`
    - 권한: `0600`
    - complete history 7 refs, 독립 clone `git fsck --full --strict`,
      exact HEAD와 `go.mod` byte 비교 통과
  - final13 correctness review는 empty Job Object 처리에서 attach 실패 경로를
    구분하지 못한 P2를 발견했다.
    - Windows process tree가 `CREATE_SUSPENDED` root를 만든 뒤
      `AssignProcessToJobObject` 전에 실패하면 job의 active process는 0이지만
      root는 살아 있다. `attached` 상태를 atomic하게 추적하고 attach 전에는
      root process를 직접 종료한 뒤 wait하도록 수정했다.
    - 실제 Windows에서 unattached suspended root가 2초 안에 종료되는 전용
      회귀 테스트를 추가했다.
    - testing review의 비차단 P3였던 Node 20 action 경고도 공식 Node 24 기반
      `actions/checkout v7.0.1`과 `actions/setup-go v7.0.0`의 exact commit
      pin으로 갱신하고 workflow pin 계약 테스트를 함께 수정했다.
    - final13 document review의 raw exact-byte 문서 드리프트는 계획과 child
      catalog 문서를 LF-normalized exact-content 계약으로 동기화해 해결했다.
  - 위 review 수정을 child commit
    `6f79d4fbfe1703737ac46b4dcb55c26d3fb9b6ca`
    (`fix(review): close Windows process and workflow gaps`)로 push했다.
    - canonical snapshot:
      `/tmp/compound-engineering/ce-code-review/20260730-220000-final14`
    - `full.diff` SHA-256:
      `5ae1200a0a21b686d7c37a374829b50fd237b124dd5cfe11177f39b599e8bffc`
    - local `go test ./...`, focused `go test -race`, `go vet ./...`,
      `golangci-lint run ./...`, `actionlint`, `shellcheck`, `git diff --check`
      통과
    - Windows amd64·arm64 전체 package cross-compile 통과
    - GitHub Actions run `30531997719`의 hosted `verify`,
      `windows-verify`, Node 24 action runtime과 새 suspended-root test는
      통과했다. 이후 correctness 재리뷰가 아래 동시성 P2를 발견했다.
  - final14 correctness 재리뷰는 `terminateRootProcess`가 `Cmd.ProcessState`를
    읽는 동안 `Wait`가 같은 값을 쓰는 data race 가능성을 발견했다.
    - `ProcessState` 읽기를 완전히 제거하고 Go의 thread-safe `Process.Kill`
      상태만 사용한다. 이미 wait/release된 Windows process의
      `os.ErrProcessDone`과 `ERROR_INVALID_PARAMETER`만 정상 종료로 정규화한다.
    - 실제 `command.Run`/wait 완료 뒤 terminate를 호출하는 Windows 전용
      released-root 회귀 테스트를 추가했다.
  - 위 수정은 child commit
    `5ca2b52013f070e482cbdeac7e00e45b637e3bc6`
    (`fix(review): remove Windows process-state race`)로 push했다.
    - canonical snapshot:
      `/tmp/compound-engineering/ce-code-review/20260730-223000-final15`
    - `full.diff` SHA-256:
      `c4d5c55f96a89d66f96d514bc45b94b99201b13bce5e2aa6ebbb9dcb0edb8bb9`
    - local 전체 test/vet/lint/action/shell/diff 검증과 Windows
      amd64·arm64 전체 package cross-compile 통과
    - GitHub Actions run `30532338650`에서 Ubuntu verify는 통과했지만,
      Windows native released-root test가 `invalid argument`를 반환해
      `windows-verify`는 실패했다.
  - final15 실패 로그로 Go Windows `os.Process`가 wait 뒤 handle을 release한
    상태에서는 kernel `ERROR_INVALID_PARAMETER`가 아니라 별도
    `syscall.EINVAL`을 반환함을 확인했다.
    - `os.ErrProcessDone`, `syscall.EINVAL`, kernel
      `ERROR_INVALID_PARAMETER`의 이미 종료된 세 상태만 정상화한다.
    - 위 수정은 child commit
      `cb85413beca723873e883cfc0e5ca324756630a0`
      (`fix(windows): normalize released process errors`)로 push했다.
    - canonical snapshot:
      `/tmp/compound-engineering/ce-code-review/20260730-230000-final16`
    - `full.diff` SHA-256:
      `d8a664ae1441d49c7a6e6fc0b9aae5102f09d6dec9b6f9275a2b1cb83cb5640b`
    - focused test/vet/lint, Windows amd64 compile와 diff 검증 통과
    - GitHub Actions run `30532557502`: exact head의 hosted `verify`와
      `windows-verify` 전체 test 및 Windows CLI build 통과, annotation 0
    - target certification run `30532557506`의 fixture contract 통과,
      PR actual-target job은 설계대로 skipped
    - final16 `correctness.json`, `security.json`, `testing.json`,
      `doc-review.json`은 snapshot SHA와 exact head/base를 확인했고
      P1/P2/P3 0건으로 pass/ready-to-merge 판정했다.
    - GitHub OWNER `zzanghyunmoo`가 exact head에 code/doc review marker를
      각각 게시했고, API 재조회로 `author_association: OWNER`와 marker
      본문을 확인했다.
      - code review:
        [comment 5129390806](https://github.com/zzanghyunmoo/my-desk-setup/pull/1#issuecomment-5129390806)
      - doc review:
        [comment 5129392239](https://github.com/zzanghyunmoo/my-desk-setup/pull/1#issuecomment-5129392239)
  - final16 complete-history 복구 bundle을 영구 경로에 보존했다.
    - 경로:
      `/Users/gurumee92/Workspaces/.recovery/my-desk-setup/2026-07-30/my-desk-setup-final-u16-cb85413-2026-07-30.bundle`
    - SHA-256:
      `f8c2fa411386ff53079f2243d01390b703f62fa179d28e44a78e8aebacac69df`
    - 권한: `0600`
    - complete history 7 refs, 독립 clone `git fsck --full --strict`,
      exact HEAD와 `go.mod` byte 비교 통과
- 미실행:
  - PR merge와 merge closeout은 아직 실행하지 않았다. 실제 merge는 exact
    approval packet을 현재 turn에서 별도로 승인받은 뒤 guarded merge로만
    수행한다.
  - 현재 final review head의 실제 macOS/Windows/WSL/Lima target 인증은
    모두 미실행이다. `80f866a`의 macOS `blocked` bundle은 역사적 진단이며
    현재 head evidence가 아니다.
  - Lima `2.1.4`에는 `home-ai-infra`라는 별도 stopped Ubuntu guest만 있고,
    제품이 소유할 `mds` guest는 없다. 사용자 소유 VM을 시작하거나 변경하지
    않았으며 `lima-guest:mds` 인증은 저장소 전환과 명시적 apply 뒤 실행한다.
  - macOS 실제 evidence가 conflict/unready를 포함하므로 release promotion은
    아직 차단 상태다.

## 외부 동기화

- Linear: [ZZA-100](https://linear.app/zzanghyunmoo/issue/ZZA-100/my-desk-setup-크로스플랫폼-개발-환경-bootstrap-구현)
  — `Done`
- Notion 계획:
  [My Desk Setup 구현 계획](https://app.notion.com/p/3acef22ad4fc81a08204d8022f962bcb)
- Notion 구현 기록:
  [ZZA-100 My Desk Setup 구현 기록](https://app.notion.com/p/3acef22ad4fc81f0b3dad0814f0cee1a)
- GitHub PR:
  [#1 my-desk-setup bootstrap](https://github.com/zzanghyunmoo/my-desk-setup/pull/1)
- GitHub latest-head review marker:
  [code](https://github.com/zzanghyunmoo/my-desk-setup/pull/1#issuecomment-5129390806),
  [doc](https://github.com/zzanghyunmoo/my-desk-setup/pull/1#issuecomment-5129392239)

## Merge closeout

- PR #1을 exact approved packet과 guarded merge로 squash merge했다.
  - review head: `cb85413beca723873e883cfc0e5ca324756630a0`
  - merge commit: `58b22df0dc80617be0ab11c3515bb79cfba0b14b`
  - merged at: `2026-07-30T10:10:57Z`
  - 원격 `zza-100/bootstrap` branch 삭제 확인
- root workspace submodule을 `projects/settings`에서
  `projects/my-desk-setup`으로 이동하고 `.gitmodules` URL을
  `https://github.com/zzanghyunmoo/my-desk-setup.git`로 바꿨다. gitlink와
  local detached submodule은 모두 merge commit을 가리킨다.
- GitHub Git API에서 review head와 merge commit의 tree가 모두
  `c0cbcc216365d40dba6d21d262e570ac2d0e469b`임을 확인했고 local submodule의
  `HEAD^{tree}`도 일치했다. merge commit에서 `go test ./...` 전체가
  통과했다.
- root workflow gate unit test 22건과 `validate-work`, `git diff --check`를
  통과했다. `markdownlint-cli2`와 `markdownlint` executable은 없어 Markdown
  lint는 실행하지 못했다.
- root closeout commit `de805b47c6472203a9ebdbc438cba2f53be43b83`을 원격
  `main`에 push하고 closeout debt를 ack했다. 원격 clean shallow clone에서
  `projects/my-desk-setup` submodule init, merge commit checkout, 이전
  `projects/settings` 경로 부재와 clean root status를 확인했다.
- 현재 기능 상태와 운영 경계를
  `docs/kb/developer-environments/2026-07-30-ZZA-100-my-desk-setup.md`에
  기록했다.
- Notion `디자인 문서 > 기능 현황`과 `개발 문서 > 티켓`을 merge commit,
  최종 검증과 actual-target 미실행 경계로 동기화하고 재조회했다.
- 마지막 PR이 병합되고 closeout 산출물이 준비돼 Linear ZZA-100을 `Done`으로
  전환했다.
- merge commit의 실제 macOS·Windows·WSL·Lima target certification은 여전히
  미실행이며, 해당 evidence 전까지 release promotion을 차단한다.
