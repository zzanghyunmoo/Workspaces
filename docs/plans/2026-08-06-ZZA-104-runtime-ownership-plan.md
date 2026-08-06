---
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
execution: code
product_contract_source: ce-brainstorm
ticket: ZZA-104
---

# MDS Runtime Ownership and OMH Plugin Composition - Plan

## Goal capsule

MDS is the only owner of Claude Code, OpenCode, and Codex runtime revisions. OMH consumes the exact MDS-owned runtime identities and installs only the explicitly selected runtime-native plugins, including OpenCode OMO and Codex LazyCodex/OMO.

## Product contract

- MDS `update` remains the explicit, preview-first operation that resolves a newer stable runtime. Its host composition passes each selected runtime's exact version, archive digest, and executable digest through the MDS plan-bound runtime identity contract.
- Normal MDS `apply` never resolves a moving `latest` value.
- OMH must not reject an MDS-owned runtime merely because OMH's own agent catalog names a different version.
- OMH must not acquire, replace, or version-manage agent runtimes for the `mds-host` composition profile.
- OMH's selected add-ons remain independently pinned, previewed, and applied with exact digests. The initial supported pairs are OpenCode plus OMO and Codex plus LazyCodex/OMO.
- A missing, malformed, stale, untrusted, or non-matching MDS receipt blocks OMH before any plugin mutation.
- User-owned runtimes that have no matching MDS ownership receipt remain blocked; this does not weaken the existing ownership boundary.

## Scope

In scope: runtime-identity receipt handoff from MDS to OMH, plugin-only `mds-host` planning, runtime-pin removal from the OMH composition contract, tests and operator documentation.

Out of scope: automatic runtime update on ordinary setup, authentication automation, changing non-`mds-host` profile ownership, or accepting arbitrary PATH binaries.

## Implementation units

1. **MDS runtime receipt contract**
- Define a secret-free runtime identity projection for selected MDS-managed agents.
- Bind its version, archive digest, and executable digest into the outer MDS plan before OMH preview and pass the same value on child apply.
- Extend host-harness invocation to expose the identity only in its isolated child environment; OMH still resolves the executable from that trusted `PATH` and verifies its bytes against the identity.
- Tests: valid selected runtime handoff; omitted agent; changed executable; malformed or non-MDS identity rejection.

2. **OMH mds-host runtime validation**
   - Add the MDS runtime receipt input to the composition request and validate its shape, target, selected agents, executable identity, and catalog lineage.
   - For `mds-host`, derive agent readiness from the trusted MDS receipt and remove OMH's competing runtime version/digest gate.
   - Preserve the exact current behavior for personal/company profiles and user-owned runtime conflicts.
   - Tests: MDS-owned newer runtime accepts; missing/foreign/stale receipt blocks; normal profiles retain strict OMH runtime acquisition behavior.

3. **Plugin-only add-on planning and application**
   - Make `mds-host` include only explicitly requested runtime add-ons in its plan and receipt.
   - Ensure OpenCode OMO and Codex LazyCodex/OMO are shown as separate plugin actions, each with immutable source/version/digest evidence.
   - Tests: OpenCode plus OMO and Codex plus LazyCodex previews yield an exact digest and apply only plugin registrations; no runtime package is installed or replaced.

4. **Catalog/release and docs synchronization**
   - Remove duplicated agent-version ownership from the OMH composition release contract while retaining plugin compatibility metadata.
   - Update MDS and OMH operator docs with explicit `mds update` then `mds apply` then OMH plugin composition flow.
   - Validate release/package contracts so a future OMH release cannot reintroduce agent pins for `mds-host`.

## Verification

- MDS: focused receipt and host-harness tests, `go test ./...`, `go vet ./...`, and `go build ./cmd/mds`.
- OMH: focused composition/add-on tests plus `npm run typecheck`, `npm run build`, `npm run test:contracts`, `npm run test:integration`, and `npm run package:verify` as applicable.
- Windows manual QA: create a MDS-owned runtime receipt, preview OpenCode+OMO and Codex+LazyCodex with `mds-host`, apply the exact preview digest, then confirm native plugin registration without changing agent executables.

## Risks and sequencing

MDS receipt design lands first because OMH must not infer trust from PATH. OMH consumes the finalized receipt contract second. Release/catalog validation comes last because it binds the contract into distributed artifacts.
