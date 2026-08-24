---
title: GitHub-native Personal Knowledge Workflow - Plan
type: feat
date: 2026-08-24
topic: github-native-personal-knowledge-workflow
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
execution: code
ticket: GH-7
ticket_url: https://github.com/zzanghyunmoo/Workspaces/issues/7
---

# GitHub-native Personal Knowledge Workflow - Plan

## Goal Capsule

- **Objective:** 개인 작업 추적과 지식 문서를 GitHub 및 저장소 Markdown으로 단일화하고, 비공개 노트와 공개 블로그 사이에 안전한 승격 경계를 둔다.
- **Product authority:** GitHub Issue [GH-7](https://github.com/zzanghyunmoo/Workspaces/issues/7)와 이 요구사항 문서가 범위를 정한다.
- **Open blockers:** 없음. 세부 파일·검증기 설계는 구현 계획에서 확정한다.

---

## Product Contract

### Summary

GitHub Issues와 저장소 Markdown을 작업 및 지식의 원본으로 삼고, 기존 AstroPaper/Pagefind 블로그를 공개 표면으로 유지한다.
비공개 개인 노트는 별도 Obsidian 호환 저장소에 두며 공개 콘텐츠는 명시적인 검토를 거쳐 블로그로 승격한다.

### Problem Frame

현재 워크플로는 Linear, Notion, 로컬 문서, GitHub PR에 같은 상태와 문서를 반복해서 기록한다.
이 구조는 개인 운영에 비해 무겁고, 실제로 병합 후 상태와 문서를 다시 맞추는 정합성 작업을 발생시켰다.
공개 블로그는 이미 AstroPaper, GitHub Pages, Pagefind로 운영 중이므로 새 공개 플랫폼을 추가하면 같은 역할의 표면과 유지비만 늘어난다.

### Key Decisions

- **GitHub-native control plane:** 티켓은 GitHub Issue, 구현과 리뷰는 GitHub PR, 현재 상태와 검증 근거는 저장소 문서가 담당한다.
- **Repository docs over GitHub Wiki:** 위키 원본은 별도 Git 저장소인 GitHub Wiki가 아니라 PR과 검증을 함께 받을 수 있는 저장소 Markdown으로 유지한다.
- **Preserve the public incumbent:** 공개 블로그는 AstroPaper와 Pagefind를 유지하며 Starlight로 교체하지 않는다.
- **Separate private and public repositories:** 비공개 Obsidian 노트는 공개 블로그 저장소와 물리적으로 분리한다.
- **Delay semantic indexing:** Qdrant, FastEmbed, 임베딩 인덱서, 검색 MCP는 실제 검색 실패가 측정되기 전까지 추가하지 않는다.

### Requirements

**Work tracking**

- R1. 새 작업은 GitHub Issue URL과 `GH-<number>` 식별자를 canonical ticket으로 사용해야 한다.
- R2. 작업 상태는 GitHub Issue의 열린 상태와 명시적인 lifecycle label로 표현하고, 최종 closeout이 끝난 뒤에만 Issue를 닫아야 한다.
- R3. 여러 저장소의 작업을 한눈에 볼 필요가 있을 때 GitHub Project는 집계 보드로 사용할 수 있지만 Issue와 저장소 문서를 대체하는 원본이 되어서는 안 된다.
- R4. PR은 해당 Issue와 work evidence를 연결해야 하며, stacked PR이 남아 있을 때 Issue를 자동으로 닫아서는 안 된다.

**Knowledge and documentation**

- R5. 아이디에이션, 요구사항, 계획, 작업 증빙, merge closeout, 재사용 가능한 해결책은 지정된 저장소 `docs/` 경로의 Markdown을 canonical source로 사용해야 한다.
- R6. 새 워크플로에서 Notion 이중 발행과 Linear 상태 동기화는 필수 조건이 아니어야 한다.
- R7. 기존 Linear/Notion 기반 역사 문서는 출처 보존을 위해 일괄 수정하지 않아야 하며, 검증기는 legacy evidence와 새 GitHub-native evidence를 구분해야 한다.
- R8. GitHub Wiki는 새 canonical surface로 사용하지 않아야 한다.

**Personal notes and publishing**

- R9. 비공개 개인 노트는 공개 블로그와 다른 private Git repository에 일반 Markdown으로 저장해야 한다.
- R10. 노트 작성 규칙은 표준 Markdown 링크를 기본으로 하고 Obsidian 전용 block reference에 공개 계약이 의존하지 않게 해야 한다.
- R11. 공개 승격은 자동 동기화가 아니라 선택한 문서를 검토 후 AstroPaper content contract에 맞게 복사하는 흐름이어야 한다.
- R12. 비공개 저장소의 경로, 원문, 첨부파일이 공개 build artifact에 포함되지 않는 검증 경계가 있어야 한다.

**Public knowledge surface**

- R13. 기존 AstroPaper 배포, RSS, 태그, Pagefind 검색은 유지해야 한다.
- R14. 공개 wiki 성격의 글은 기존 블로그 안에서 식별하고 탐색할 수 있어야 하며 별도 Starlight 사이트를 요구하지 않아야 한다.
- R15. 공개 사이트 변경은 블로그 프로젝트의 기존 branch/PR/Pages 검증 규칙을 따라야 한다.

### Key Flows

- F1. Work lifecycle
  - **Trigger:** 구현할 새 작업이 생긴다.
  - **Steps:** GitHub Issue 생성 → lifecycle label 갱신 → 계획 및 work evidence 연결 → PR 리뷰 → merge closeout → Issue 종료.
  - **Outcome:** 작업 상태와 코드·문서 증빙이 GitHub와 저장소 안에서 추적된다.
  - **Covers:** R1, R2, R3, R4, R5, R6.
- F2. Private note capture
  - **Trigger:** 공개 여부가 정해지지 않은 메모나 학습 기록을 남긴다.
  - **Steps:** private vault에 Markdown으로 기록 → 링크와 첨부를 로컬 경계 안에서 유지 → 필요한 경우 Git으로 백업한다.
  - **Outcome:** 초안과 개인 정보가 공개 사이트와 분리된다.
  - **Covers:** R9, R10, R12.
- F3. Public promotion
  - **Trigger:** private note가 공개할 수준으로 정리된다.
  - **Steps:** 민감 정보와 비공개 링크 검토 → AstroPaper frontmatter와 표준 링크로 정리 → 블로그 branch/PR로 발행 → Pages와 Pagefind 확인.
  - **Outcome:** 공개 가능한 지식만 기존 사이트에 축적된다.
  - **Covers:** R11, R12, R13, R14, R15.

### Acceptance Examples

- AE1. **Covers R1, R2, R4.** 새 기능의 work evidence가 GitHub Issue URL을 가리키고 lifecycle label이 `in-progress`에서 `in-review`로 바뀌며, 최종 closeout 전에는 Issue가 열린 상태를 유지한다.
- AE2. **Covers R5, R6, R7.** 새 문서에는 Notion URL이 없어도 검증이 통과하고, 기존 Linear/Notion evidence는 역사 기록으로 계속 해석된다.
- AE3. **Covers R9, R11, R12.** private vault의 일반 노트는 공개 빌드에 나타나지 않고, 수동으로 승격한 문서만 블로그 검색 결과에 나타난다.
- AE4. **Covers R13, R14.** 기존 블로그 글과 RSS가 유지되면서 wiki로 분류된 글을 별도 진입점과 Pagefind에서 찾을 수 있다.

### Success Criteria

- GitHub-native work evidence를 검사하는 자동화 테스트가 통과한다.
- 새 템플릿과 가드레일에서 필수 Notion/Linear 필드가 제거된다.
- GitHub Issue, PR, 계획, work evidence, KB 사이의 추적 링크가 한 방향으로 이어진다.
- 기존 블로그 빌드와 Pagefind 인덱싱이 회귀하지 않는다.
- private vault의 샘플 고유 문구가 공개 build artifact에 존재하지 않는다.

### Scope Boundaries

- Starlight 또는 Quartz로 공개 블로그를 교체하지 않는다.
- GitHub Wiki를 별도 문서 원본으로 추가하지 않는다.
- Qdrant, FastEmbed, 벡터 데이터베이스, 자동 Markdown 임베딩 동기화를 추가하지 않는다.
- 완전 자동 private-to-public 게시 파이프라인을 만들지 않는다.
- 기존 역사 문서의 Notion/Linear 링크를 일괄 삭제하지 않는다.

### Dependencies and Assumptions

- GitHub CLI 인증과 repository 권한이 유지된다고 가정한다.
- 공개 블로그의 현재 AstroPaper/Pagefind 계약이 정상 동작한다고 가정한다.
- private repository의 최초 기본 브랜치 생성은 프로젝트 main 보호 규칙에 따라 별도 승인 없이는 push하지 않는다.

### Sources and Research

- `AGENTS.md`
- `docs/solutions/workflow-issues/notion-first-dual-published-documentation.md`
- `docs/solutions/conventions/ticket-code-doc-pr-split-and-tracker-sync.md`
- `docs/brainstorms/2026-06-09-blog-migration-quartz-to-astropaper-requirements.md`
- `blogs/src/content.config.ts`
- [GitHub Issues documentation](https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues)
- [GitHub Projects documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects)
- [GitHub Wiki documentation](https://docs.github.com/en/communities/documenting-your-project-with-wikis/about-wikis)
- [Qdrant MCP server](https://github.com/qdrant/mcp-server-qdrant)
