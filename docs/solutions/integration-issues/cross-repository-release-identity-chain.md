---
title: 공개 릴리스와 소비자 production lock 사이 identity drift 차단
date: 2026-08-05
category: integration-issues
module: my-desk-setup-host-harness
problem_type: integration_issue
component: testing_framework
symptoms:
  - "공개 OMH adapter의 Codex macOS x64 executable digest와 MDS production lock 값이 달랐다."
  - "형식 검사와 fixture-production 비교만으로는 함께 잘못 복사된 digest를 발견할 수 없었다."
root_cause: missing_validation
resolution_type: test_fix
severity: high
tags:
  - release-identity
  - artifact-digest
  - cross-repository
  - host-harness
---

# 공개 릴리스와 소비자 production lock 사이 identity drift 차단

## Problem

producer인 OMH가 공개한 archive의 runtime adapter identity와 consumer인 MDS의 release
fixture·production lock이 독립적으로 연결되지 않아, Codex macOS x64 executable digest
오타가 production 설정에 남을 수 있었다. 이 값이 틀리면 정상 executable 설치를 거부하거나
검토하지 않은 bytes를 올바른 identity로 오인할 수 있다.

## Symptoms

- PR [#6](https://github.com/zzanghyunmoo/my-desk-setup/pull/6) 리뷰에서 공개 OMH archive의
  Codex macOS x64 adapter digest와 production lock의 불일치가 발견됐다.
- 모든 digest가 64자리인지 검사하고 fixture와 production lock만 비교해도, 두 소비자 파일에
  같은 오타가 복사되면 검사가 통과할 수 있었다.

## What Didn't Work

- `projects/my-desk-setup/internal/catalog/validate.go`의 digest 형식 검사는 agent artifact에
  archive/executable SHA-256이 존재하고 유효한지만 확인한다. 값의 producer provenance까지
  증명하지는 않는다.
- fixture와 production lock을 직접 비교하는 것만으로는 공통의 잘못된 입력을 독립적으로
  검출할 수 없다.

## Solution

identity 검증을 producer bytes에서 production 설정까지 이어지는 세 단계로 닫았다.

1. `projects/my-desk-setup/tests/fixtures/catalog/host-harness/release-identity.json`이 공개
   archive의 tag, archive digest/size, source commit/tree와 catalog revision을 고정한다.
2. `projects/my-desk-setup/tests/contracts/host_harness_release_gate_test.go`의
   `TestHostHarnessReleaseGateRunsActualMergedArtifactPreviewAndApply`가 실제 archive bytes와
   sidecar를 fixture에 대조한다. `assertReleaseAdapterIdentities`는 그 archive에서 세 agent의
   네 host platform별 URL, archive digest, executable path와 executable digest를 읽어
   fixture lock과 비교한다.
3. `projects/my-desk-setup/tests/contracts/host_harness_catalog_test.go`의
   `TestProductionCatalogUsesPublishedHostHarnessRelease`가 fixture의 agent version과 전체
   artifact map을 production lock과 비교한다.

검증 흐름은 다음과 같다.

```text
published archive + sidecar
  -> release identity fixture
  -> extracted OMH agent adapters
  -> MDS fixture agent locks
  -> MDS production locks
```

이 chain이 공개 archive를 독립 기준으로 삼아 Codex macOS x64 오타를 발견했고,
production lock을 공개 adapter의 canonical executable digest로 바로잡았다.

## Why This Works

형식 검사는 값의 모양만, fixture-production 비교는 두 소비자 사본의 일치만 보장한다.
실제 producer archive에서 identity를 추출하는 중간 gate가 있어야 producer와 fixture가
일치한다. 그 뒤 fixture-production gate를 연결하면 어느 한 단계의 수동 복사 오류도 다음
경계에서 드러난다.

## Prevention

- producer release나 native agent version을 올릴 때 공개 예정 archive에서 fixture를
  재생성하고, actual archive → fixture → production lock gate를 같은 변경에서 실행한다.
- archive digest만 고정하지 말고 extracted executable digest도 플랫폼별로 고정·재검증한다.
- fixture와 production 값을 한 번에 수동 편집했다면 독립 producer-byte gate 없이 review를
  통과시키지 않는다.

## Related Issues

- [MDS PR #6](https://github.com/zzanghyunmoo/my-desk-setup/pull/6)
- `docs/kb/developer-environments/2026-08-05-ZZA-103-host-agent-harness.md`
- `docs/kb/releases/2026-08-05-ZZA-103-oh-my-harness-pi-free-release.md`
