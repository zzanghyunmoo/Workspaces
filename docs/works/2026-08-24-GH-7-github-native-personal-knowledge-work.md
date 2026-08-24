---
workflow_schema: compound-work/v2
ticket_id: GH-7
ticket_url: https://github.com/zzanghyunmoo/Workspaces/issues/7
ticket_completion: pending
remaining_prs:
ideation_status: waived
ideation_path:
ideation_waiver_reason: 사용자가 GitHub-native 방향을 확정한 뒤 ce-pov와 ce-brainstorm으로 범위·트레이드오프를 검증했으므로 별도 후보 생성은 중복이다.
plan_status: complete
plan_path: docs/plans/2026-08-24-GH-7-github-native-personal-knowledge-plan.md
plan_waiver_reason:
work_status: complete
pr_url: https://github.com/zzanghyunmoo/zzanghyunmoo.github.io/pull/18
closeout_status: pending
merged_pr_url:
merge_commit:
kb_paths:
closeout_completed_at:
---

# GH-7 GitHub-native 개인 지식 및 작업 관리 워크플로 작업 기록

## 작업 목표

GitHub Issue/PR과 저장소 Markdown을 개인 작업·지식 관리의 원본으로 단일화하고, private
Obsidian vault에서 기존 AstroPaper/Pagefind 블로그로 공개 가능한 글만 승격하는 경계를
구축한다.

## 주요 변경 지점

- `runbooks/compound_workflow_gate.py`에 v1 호환 `compound-work/v2`, GitHub Issue
  lifecycle, cross-repository review marker, remote canonical PR index 검증, Issue finalizer를
  추가했다.
- `.github` 템플릿, `docs/works`, `docs/kb`, `CONCEPTS.md`, 운영 runbook을 GitHub
  Issues/PR과 저장소 Markdown이 원본인 계약으로 전환했다. 과거 v1 문서는 그대로 유지한다.
- `runbooks/check_publication_candidate.py`와 guarded publication wrapper는 후보 파일의 전체
  commit history, 심볼릭 링크 탈출, secret/canary, 빌드 산출물, 승인 SHA, 빌드 timeout과
  빌드 중 HEAD 변경을 fail-closed로 검사한다.
- 별도 private 저장소 scaffold와 main 보호 hook을 준비했고, 기존 AstroPaper 블로그의
  `/wiki`, wiki tag, Pagefind 검색 smoke test는 `feat/github-native-wiki` 브랜치에 구성했다.
  private 저장소의 첫 main commit/push와 블로그 merge는 각각 명시 승인 전까지 보류한다.

## 검증

- 계획 문서 `ce-doc-review` 2회 완료. 완료 상태와 승인 대기 상태, private/public 경계,
  cross-repo evidence revision을 보강했다.
- `python3 -m unittest discover -s runbooks/tests -p 'test_*.py'`: 78 tests 통과.
- `bash runbooks/tests/test_publication_shell_guard.sh`: 통과. 정확한 승인 tuple, 전체 commit
  경로, build timeout/HEAD 고정, 외부 clone main 보호를 검증했다.
- `bash runbooks/tests/test_workflow_shell_guards.sh`: 통과. merge head 고정과 closeout debt
  pre-push 검증을 확인했다.
- adversarial 재검증에서 publication history 우회, 게시된 closeout 이후 Issue 미종료,
  미병합 stacked PR 누락의 세 blocker를 보완한 최신 staged snapshot에 새 finding이 없음을
  확인했다.
- 블로그 `npm run format:check`, `npm run lint`, `npm run build`,
  `npm run test:knowledge`: 모두 통과. 70 pages와 Pagefind 23 pages/4,711 words를 생성했다.
- 현재 환경에 사용 가능한 in-app browser가 없어 시각적 browser QA는 실행하지 못했다.

## GitHub 추적

- Issue: https://github.com/zzanghyunmoo/Workspaces/issues/7
- PR: https://github.com/zzanghyunmoo/zzanghyunmoo.github.io/pull/18
- 현재 lifecycle: `status:in-review`
- Plan: `docs/plans/2026-08-24-GH-7-github-native-personal-knowledge-plan.md`
- GitHub Project는 현재 token의 project scope가 없어 비차단 projection으로 보류한다.

## Merge closeout

PR review와 merge 승인 전이다. `ticket_completion: pending`, `closeout_status: pending`을 유지한다.
