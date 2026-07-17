---
title: Authoritative blocked generation을 feasibility 성공과 분리한다
date: 2026-07-17
category: architecture-patterns
module: oh-my-harness-feasibility
problem_type: architecture_pattern
component: testing_framework
severity: high
applies_when:
  - 여러 runtime과 격리 backend를 실제 행동 proof로 검증할 때
  - blocked 결과도 재현 가능한 review evidence로 보존해야 할 때
  - fixture 또는 self-asserted JSON이 production pass를 위조할 위험이 있을 때
  - 일부 substrate가 관리자 권한이나 별도 host 정책을 요구할 때
tags: [feasibility-gate, fail-closed, characterization, proof-receipt, blocked-generation, trusted-evidence]
related_components: [development_workflow, tooling, assistant]
---

# Authoritative blocked generation을 feasibility 성공과 분리한다

## Context

Runtime feasibility 작업은 실패 결과도 재현 가능하게 남겨야 하지만, 완전한 실패 기록을
곧바로 구현 완료나 지원 성공으로 오해하기 쉽다. Oh My Harness U16 계획은 blocked를
포함한 완전한 generation을 명시적으로 게시할 수 있게 하면서도, 모든 proof가 통과하지
않으면 명령이 non-zero를 반환하고 후속 breadth를 열지 않도록 정했다
(`docs/plans/2026-07-17-ZZA-73-u16-runtime-feasibility-plan.md:71-73`).

실행 과정에서 이 구분이 실제로 필요했다. 초안은 10개 complete non-pass receipt와
`current.json` pointer를 만들었지만, real runtime·OCI·Tart driver와 trusted proof
경계가 없어서 `characterizer-implementation-complete/support-blocked`에도 미달했다
(`docs/works/2026-07-17-ZZA-73-u16-runtime-feasibility-work.md:44-48`). Pure test와
static verification이 통과했다는 사실만으로 실제 feasibility를 주장할 수 없었다.

## Guidance

Feasibility pipeline에는 다음 세 상태를 명시적으로 분리한다.

1. **Authoritative blocked generation**
   - 요구된 receipt cardinality와 schema, digest, secret scan, atomic pointer 규칙을 만족한다.
   - 실패 이유와 recovery action을 review 가능한 형태로 보존한다.
   - 모든 blocked·failed·timeout·cancelled·infra-error·not-run 결과는
     `countsAsPass:false`를 유지한다
     (`docs/plans/2026-07-17-ZZA-73-u16-runtime-feasibility-plan.md:71-73`).
2. **Implementation complete, support blocked**
   - Pure contract뿐 아니라 production composition root가 생성하는 real non-injectable
     runtime/backend driver, hostile fixture, trusted evidence 검증이 존재한다.
   - 환경 또는 existential seam이 실패해도 구현 자체는 review할 수 있지만 티켓과
     dependent breadth는 열린 채로 둔다
     (`docs/plans/2026-07-17-ZZA-73-u16-runtime-feasibility-plan.md:94`).
3. **Feasibility gate passed**
   - 모든 runtime tuple과 backend receipt가 실제 native gate, provider route, trusted
     control, effective isolation과 teardown을 증명한다.
   - 이 상태만 티켓 완료와 dependent breadth unlock을 허용한다
     (`docs/plans/2026-07-17-ZZA-73-u16-runtime-feasibility-plan.md:95-97`).

Static verifier는 evidence의 내부 일관성만 확인하고 환경을 다시 실행하지 않는다. Live
characterization과 explicit publication을 분리하고, pointer 교체를 logical commit point로
사용한다. 완전한 blocked generation도 authoritative review evidence가 될 수 있지만 성공
exit나 support unlock으로 정규화하지 않는다
(`docs/plans/2026-07-17-ZZA-73-u16-runtime-feasibility-plan.md:149-151`).

Passing evidence는 fixture가 재구성할 수 있는 boolean과 digest만 신뢰해서는 안 된다.
Production composition root가 real driver를 내부에서 만들고, capability-bound control
channel, emitter/observer identity, backend effective-state observation과 teardown evidence를
receipt에 결합해야 한다. Fixture API는 publication과 `countsAsPass:true`에 도달하지 못하게
분리한다
(`docs/plans/2026-07-17-ZZA-73-u16-runtime-feasibility-plan.md:145`).

## Why This Matters

Blocked truth를 게시하지 않으면 실패 원인과 exact substrate 상태가 임시 로그에 흩어져
재현성과 reviewability를 잃는다. 반대로 blocked generation을 성공으로 취급하면 아직
실행되지 않은 runtime이나 검증되지 않은 isolation을 지원한다고 오판해 후속 기능이 잘못된
가정 위에 쌓인다.

U16에서는 static blocked generation이 `u16GatePassed:false`와 non-zero를 반환했지만,
독립 리뷰가 actual acquisition, native discovery, gate/provider/control probe와 effective
OCI/Tart teardown이 없음을 확인했다
(`docs/works/2026-07-17-ZZA-73-u16-runtime-feasibility-work.md:52-74`). 이때 PR을 열지 않고
티켓을 `In Progress`로 유지한 것은 실패 기록을 버린 것이 아니라 proof 수준에 맞는 shipping
상태를 선택한 것이다.

## When to Apply

- 여러 runtime, OS, architecture 또는 isolation backend의 지원 여부를 characterization할 때.
- exact binary/image identity와 실제 행동 proof가 모두 지원 계약에 포함될 때.
- 환경 blocker도 durable evidence로 남겨야 하지만 downstream 작업을 열어서는 안 될 때.
- test fixture와 production proof driver가 같은 schema를 사용해 provenance 혼동 위험이 있을 때.
- 관리자 권한, virtualization 또는 network policy처럼 repository 코드만으로 해소할 수 없는
  substrate 조건이 있을 때.

단순 unit test 실패처럼 재실행만으로 판정할 수 있는 작업에는 이 3단계 모델이 필요하지 않다.
이 패턴은 **지원 가능성 자체가 산출물**이고 실패 evidence에도 장기적인 review 가치가 있을 때
적용한다.

## Examples

좋은 판정:

```text
10 receipts complete, 8 runtime receipts blocked, 2 backend receipts blocked
schema/digest/static verification = pass
aggregate exit = non-zero
work status = In Progress
breadth unlock = false
```

잘못된 판정:

```text
10 blocked receipts were written successfully
therefore characterizer implementation = complete
therefore runtime support = passed
```

환경 blocker를 만난 경우에도 fallback으로 성공시키지 않는다. U16 계획은 OCI/Tart 부재,
policy mismatch, virtualization 실패, teardown residue 또는 host visibility가 있으면 affected
tuple을 차단하고 host나 `sandbox-exec`을 passing fallback으로 사용하지 않도록 규정한다
(`docs/plans/2026-07-17-ZZA-73-u16-runtime-feasibility-plan.md:66`). 실제 U16 실행도 승인된
PF 정책이 없어 Tart lane을 차단하고 fallback을 사용하지 않았다
(`docs/works/2026-07-17-ZZA-73-u16-runtime-feasibility-work.md:76-78`).

## Related

- `docs/plans/2026-07-17-ZZA-73-u16-runtime-feasibility-plan.md` — 세 상태와 10-receipt
  acceptance boundary를 정의한 계획.
- `docs/works/2026-07-17-ZZA-73-u16-runtime-feasibility-work.md` — blocked generation과
  미완성 real-driver 경계를 확인한 실행 증빙.
- `docs/solutions/workflow-issues/run-passport-contract-before-dependent-follow-ups.md` —
  downstream 작업 전에 공통 evidence 계약을 먼저 고정하는 관련 패턴.
