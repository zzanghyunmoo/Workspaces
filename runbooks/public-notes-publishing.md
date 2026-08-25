---
title: Public notes publishing runbook
last_verified: 2026-08-25
---

# Public notes publishing

`zzanghyunmoo/notes-private`는 저장소 이름만 과거 명칭을 유지하는 public repository다.
`zWorkspaces`에서는 `notes/` 서브모듈로 연결하며 모든 tracked content를 공개 가능한
자료로 취급한다.

## 노트 작성

1. `notes/README.md`의 public-first 규칙을 확인한다.
2. 파일명, frontmatter, 본문과 첨부파일에서 credential, 내부 host, 개인 로컬 경로와
   비공개 원문을 제거한다.
3. 노트 저장소에서 변경을 검증하고 반영한 뒤 루트 저장소의 `notes` gitlink를 갱신한다.

## 블로그 승격

- `notes/`를 `blogs/`의 symlink, build input 또는 content loader로 연결하지 않는다.
- 게시할 문서만 검토해 `blogs/`의 별도 branch로 복사하고 블로그 저장소의 현재
  `AGENTS.md`, 테스트와 PR 절차를 따른다.
- 일반 Markdown 링크와 블로그 frontmatter로 정규화하고, 로컬 경로·private link·신규
  binary attachment가 남지 않았는지 확인한다.
- notes와 blog는 모두 public이지만, 노트가 존재한다는 사실이 자동 게시 승인을 뜻하지
  않는다.

## 과거 절차

Private vault canary와 `verify-private-boundary`를 사용하던 절차는 저장소 공개 전환으로
폐기됐다. 과거 이력 확인 외에는 실행하지 않는다.
