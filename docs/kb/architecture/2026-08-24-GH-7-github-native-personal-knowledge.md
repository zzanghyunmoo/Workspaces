---
title: GitHub-native 개인 지식 및 작업 관리 워크플로
ticket: GH-7
ticket_url: https://github.com/zzanghyunmoo/Workspaces/issues/7
merged_pr: https://github.com/zzanghyunmoo/zzanghyunmoo.github.io/pull/18
merge_commit: 46dec7f1bf86cc4e07b33f33497ba2960ab6babc
work_evidence: docs/works/2026-08-24-GH-7-github-native-personal-knowledge-work.md
last_verified: 2026-08-24
---

<!-- markdownlint-disable MD025 -->

# GitHub-native 개인 지식 및 작업 관리 워크플로

## 현재 기능 상태

새 작업의 티켓·설계·구현 증거·리뷰·merge closeout은 GitHub Issue, 저장소 Markdown,
GitHub PR을 원본으로 사용한다. 공개 블로그에는 `/wiki` 진입점과 `wiki` 태그 기반 목록이
추가됐고, 개인 노트는 별도 private `notes-private` 저장소에 보관한다.

## 주요 동작과 경계

- 새 Issue는 `status:planned` → `status:in-progress` → `status:in-review` 순서로 이동한다.
- work evidence는 `compound-work/v2` 계약과 GitHub-native 문서 링크를 사용한다. 과거 v1
  문서의 Notion·Linear 필드는 호환성을 위해 유지한다.
- 공개 승격은 private/public 저장소를 분리하고, 후보 Markdown과 전체 commit history,
  symlink 탈출, secret/canary, 빌드 산출물, 정확한 승인 SHA를 guarded publication wrapper로
  검사한다.
- 최종 closeout은 KB 문서와 merge SHA를 root `main`에 발행한 뒤 canonical PR index의 모든
  PR이 merged인지 확인하고 Issue를 `completed`로 닫는다.

## 검증 결과

- Root Python test discovery: 78 tests passed.
- Publication/workflow shell guards와 ShellCheck passed.
- Blog `npm run format:check`, `npm run lint`, Astro build, Pagefind, `npm run test:knowledge`
  passed. Build는 70 pages, Pagefind는 23 pages/4,711 words를 인덱싱했다.
- PR #18 최신 head에서 `ce-code-review`와 `ce-doc-review`가 각각 pass marker를 게시했고,
  guarded merge가 그 head와 evidence revision을 검증했다.

## 운영 및 사용 시 주의사항

- `notes-private`를 공개 블로그의 submodule, symlink, content loader로 연결하지 않는다.
- 공개 push는 `runbooks/guarded-publication-push.sh`를 사용하고, private 원문은 항상 canary와
  민감정보 검사를 거친다.
- GH-7은 이번 closeout으로 완료됐지만, 이후 작업은 새 Issue와 새 v2 work evidence에서
  시작한다.

## 관련 문서

- GitHub Issue: https://github.com/zzanghyunmoo/Workspaces/issues/7
- Merged PR: https://github.com/zzanghyunmoo/zzanghyunmoo.github.io/pull/18
- Work evidence: `docs/works/2026-08-24-GH-7-github-native-personal-knowledge-work.md`
