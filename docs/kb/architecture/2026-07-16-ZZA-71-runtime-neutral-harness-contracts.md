---
title: ZZA-71 Runtime-neutral harness contracts
ticket: ZZA-71
merged_pr: https://github.com/zzanghyunmoo/oh-my-harness/pull/23
merge_commit: 32e73af3636bf79e0b2d47dcd4b7ce0cdf9b8c5f
work_evidence: docs/works/2026-07-16-ZZA-71-u2-neutral-contracts-work.md
notion_feature_status: https://www.notion.so/39eef22ad4fc819db113ce1029c899a4
notion_ticket: https://www.notion.so/39fef22ad4fc81ee9a61d2f9adb52ee7
last_verified: 2026-07-16
---

<!-- markdownlint-disable MD025 -->

# ZZA-71 Runtime-neutral harness contracts

## 현재 기능 상태

Oh My Harness U2가 PR #23으로 merge되어 네 runtime이 공유할 declarative contract
boundary가 `main`에 존재한다. 현재 제공되는 산출물은 다음과 같다.

- Harness profile, feature contract, runtime adapter와 conformance result용 JSON Schema
- U1 source receipt, ownership domain, 두 platform lane과 네 runtime version을 고정한
  `personal-v1` profile
- Schema shape와 semantic cross-reference, fail-closed terminal status, evidence identity를
  검증하는 hermetic Node test

ZZA-71은 완료되지만 parent ZZA-70은 U3-U18이 남아 있어 `In Review`를 유지한다.

## 주요 동작과 경계

- 모든 contract는 JSON Schema draft 2020-12와 stable repository `$id`를 사용하고 object
  shape를 닫는다.
- Required capability는 `ready`만 허용한다. Optional capability는 기존 여섯 readiness
  상태를 보존하며 safety class와 별도 필드로 선언한다.
- Upstream payload, source receipt, generated core, project overlay, native lifecycle과 personal
  configuration의 ownership domain을 분리한다.
- Terminal status는 `passed`, `failed`, `blocked`, `timeout`, `cancelled`, `infra-error`,
  `not-run`, `expired`이며 `passed`만 `countsAsPass: true`를 허용한다.
- Hosted certification metadata는 hosted tier에만 허용하고 hermetic/personal 결과와 섞지
  않는다.
- Evidence identity는 source, runtime, overlay, feature contract, fixture, oracle, provider와
  coordinator digest를 모두 요구한다.
- U2는 executable digest나 acquisition receipt의 실제 값을 제공하지 않는다. 해당 runtime
  descriptor instance는 U3가 소유하며 native gate와 isolation feasibility는 U16 범위다.

## 검증 결과

- `npm run test:harness`: 21/21 PASS
- CE 3.19.0 canonical upstream verify: 29 skills PASS
- `npm run profile:verify`: PASS
- `npm run test:workspace-connectors`: 31/31 PASS
- Ajv 5 draft 2020-12 strict compile: schema 4개 PASS
- Ajv personal profile validation: PASS
- Node syntax와 `git diff --check`: PASS
- 최신 head code/doc review와 guarded pre-merge gate: PASS
- GitHub Actions workflow가 없어 remote check run은 생성되지 않았다.

## 운영 및 사용 시 주의사항

- 새 profile이나 U3 descriptor를 추가할 때 schema validation만으로 끝내지 말고 stable ID,
  local reference, exact version과 source identity를 semantic validation으로 함께 확인한다.
- `not-run`이나 `expired`를 성공으로 정규화하지 않는다. Hosted 결과도 hermetic release
  verdict를 승격하지 않는다.
- Profile과 evidence artifact에는 credential, auth header, 사용자 홈 경로나 secret-bearing
  command argument를 저장하지 않는다.
- U3는 profile의 `descriptorRef`를 실제 immutable platform receipt와 연결해야 하며 U16
  proof 전에는 runtime readiness를 완료로 표시하면 안 된다.

## 관련 문서

- Work evidence: `docs/works/2026-07-16-ZZA-71-u2-neutral-contracts-work.md`
- Local implementation plan:
  `projects/oh-my-harness/docs/plans/2026-07-16-ZZA-71-u2-neutral-contracts-plan.md`
- Notion canonical feature status: <https://app.notion.com/p/39eef22ad4fc819db113ce1029c899a4>
- Notion canonical ticket document: <https://app.notion.com/p/39fef22ad4fc81ee9a61d2f9adb52ee7>
- Merged PR: <https://github.com/zzanghyunmoo/oh-my-harness/pull/23>
