# Plan: Blog Migration Quartz → Astro + AstroPaper

**Date:** 2026-06-09
**Requirements:** [docs/brainstorms/2026-06-09-blog-migration-quartz-to-astropaper-requirements.md](../brainstorms/2026-06-09-blog-migration-quartz-to-astropaper-requirements.md)
**Target repo:** `blogs/` (git submodule → `github.com/zzanghyunmoo/zzanghyunmoo.github.io`)
**Default branch:** `v4` (Pages 배포 트리거 브랜치)

---

## 0. 사전 확인 (Pre-flight)

| Check | 명령 | 기대값 |
|---|---|---|
| Node 버전 | `node -v` | v22+ (워크플로 기준) |
| 작업 위치 | `pwd` | `blogs/` |
| 브랜치 | `git branch --show-current` | 작업 브랜치 (예: `migrate/astropaper`) |
| 백업 | `git tag pre-astropaper-migration` | 롤백 포인트 확보 |

> ⚠️ `blogs/`는 부모 워크스페이스의 **submodule**. 모든 git 명령은 `blogs/` 안에서 실행.

---

## 1. 작업 단위 (Implementation Units)

순서대로 진행. 각 단위 끝마다 커밋.

### Unit A — 백업 브랜치 + Quartz 파일 일괄 삭제
**Files touched:**
- (delete) `blogs/quartz/`
- (delete) `blogs/quartz.config.ts`, `blogs/quartz.layout.ts`
- (delete) `blogs/content/`
- (delete) `blogs/globals.d.ts`, `blogs/index.d.ts`
- (delete) `blogs/package.json`, `blogs/package-lock.json`
- (delete) `blogs/tsconfig.json`
- (delete) `blogs/Dockerfile`
- (delete) `blogs/.prettierrc`, `blogs/.prettierignore`, `blogs/.node-version`, `blogs/.npmrc`
- (keep) `blogs/.git`, `blogs/.gitignore`, `blogs/.gitattributes`, `blogs/.github/`, `blogs/LICENSE.txt`, `blogs/CODE_OF_CONDUCT.md`, `blogs/docs/`, `blogs/README.md`

**Steps:**
1. `cd blogs && git checkout -b migrate/astropaper`
2. `git tag pre-astropaper-migration` (현 HEAD 보존)
3. 위 delete 목록 `git rm -r ...`
4. `git commit -m "chore: remove Quartz scaffolding"`

**Verify:** `ls blogs/` → `.github/`, `LICENSE.txt`, `README.md`, `.git*` 정도만 남음.

---

### Unit B — AstroPaper 초기화
**Files touched:**
- (new) `blogs/package.json`, `blogs/package-lock.json`
- (new) `blogs/astro.config.ts`
- (new) `blogs/tsconfig.json`
- (new) `blogs/src/**`
- (new) `blogs/public/**`
- (new) `blogs/.vscode/`, `blogs/.editorconfig` 등 템플릿 자산

**Steps:**
1. 임시 디렉터리에 AstroPaper 템플릿 받기:
   ```bash
   cd /tmp
   git clone --depth=1 https://github.com/satnaing/astro-paper.git astropaper-src
   ```
2. `.git` 제외하고 `blogs/`로 복사:
   ```bash
   rsync -av --exclude='.git' --exclude='.github' /tmp/astropaper-src/ /Users/gurumee92/Workspaces/zWorkspaces/blogs/
   ```
   > `.github/` 제외 — 기존 Pages workflow는 Unit D에서 직접 교체.
3. `cd blogs && npm install`
4. `npm run dev` → 로컬 `http://localhost:4321` 동작 확인
5. `git add -A && git commit -m "feat: scaffold AstroPaper template"`

**Verify:**
- `npm run build` 무오류, `dist/` 생성됨.
- `dist/index.html` 존재.

---

### Unit C — 사이트 메타데이터 설정 (GitHub Pages용)
**Files touched:**
- (edit) `blogs/astro.config.ts` — `site` 필드
- (edit) `blogs/src/config.ts` (또는 AstroPaper 버전에 따라 `src/site.config.ts`) — site title, author, description, social

**Steps:**
1. `astro.config.ts`에서 `site: "https://zzanghyunmoo.github.io"` 설정. `base`는 user-site이므로 미설정.
2. `src/config.ts` 핵심 필드 채우기:
   ```ts
   export const SITE = {
     website: "https://zzanghyunmoo.github.io/",
     author: "짱현무",
     desc: "짱현무의 기술 블로그",
     title: "Zzang Hyun Moo",
     ogImage: "astropaper-og.jpg", // 기본값 유지
     lightAndDarkMode: true,
     postPerPage: 5,
     scheduledPostMargin: 15 * 60 * 1000,
   };
   ```
3. `LOCALE` 한국어 설정: `lang: "ko"`, `langTag: ["ko-KR"]`.
4. `SOCIALS`/`SHARE_LINKS` — 필요한 것만 활성화 (Open Decision: 사용자 입력 필요).
5. `git commit -m "feat: configure site metadata for GitHub Pages"`

**Verify:**
- `npm run build` 후 `dist/index.html`의 `<title>`, `<meta name="description">` 반영 확인.
- `npm run dev` → 헤더 제목 "Zzang Hyun Moo" 노출.

**Open decision (사용자 입력):**
- GitHub/Twitter/LinkedIn 등 소셜 링크 실제 URL
- 색상 토큰 커스터마이즈할지 여부 (안 하면 AstroPaper 기본값 유지)

---

### Unit D — GitHub Actions 워크플로 교체
**Files touched:**
- (replace) `blogs/.github/workflows/deploy.yml`

**Steps:**
1. 기존 deploy.yml 내용을 다음으로 교체 (공식 `withastro/action@v3` 사용):
   ```yaml
   name: Deploy Astro site to GitHub Pages

   on:
     push:
       branches: [v4]
     workflow_dispatch:

   permissions:
     contents: read
     pages: write
     id-token: write

   concurrency:
     group: "pages"
     cancel-in-progress: false

   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: withastro/action@v3
           with:
             node-version: 22

     deploy:
       needs: build
       runs-on: ubuntu-latest
       environment:
         name: github-pages
         url: ${{ steps.deployment.outputs.page_url }}
       steps:
         - id: deployment
           uses: actions/deploy-pages@v4
   ```
2. **트리거 브랜치는 `v4` 유지** (현 default branch와 일치) — `main` 변경은 별도 작업.
3. `git commit -m "ci: replace Quartz deploy with Astro Pages workflow"`

**Verify (push 전):** YAML syntax 검증 — `npx -y @action-validator/cli .github/workflows/deploy.yml` 또는 GH Actions tab에서 워크플로 인식 확인.

---

### Unit E — README + .gitignore 갱신
**Files touched:**
- (rewrite) `blogs/README.md`
- (verify/edit) `blogs/.gitignore` — `dist/`, `node_modules/`, `.astro/` 포함 확인

**Steps:**
1. README 본문을 AstroPaper 기준으로 재작성:
   - 프로젝트 설명 (Astro + AstroPaper 기반 기술 블로그)
   - `npm install` / `npm run dev` / `npm run build` 명령
   - 새 글 작성 가이드 (`src/content/blog/<slug>.md`, frontmatter schema)
   - 배포 방식 (push to `v4` → GitHub Actions → Pages)
2. `.gitignore` 확인 — AstroPaper 템플릿 기본값이면 그대로.
3. `git commit -m "docs: rewrite README for Astro setup"`

---

### Unit F — 최종 검증 + 부모 워크스페이스 submodule 포인터 업데이트
**Files touched:**
- (edit) `blogs/` submodule pointer in parent repo

**Steps:**
1. `cd blogs && npm run build` — 무오류 확인
2. `npm run dev` — 로컬 시각 확인 (다크/라이트 토글, 한국어 깨짐 여부, 샘플 글 노출)
3. `git push origin migrate/astropaper`
4. PR 생성 → `v4`로 머지 → Action 통과 → `https://zzanghyunmoo.github.io` 갱신 확인
5. 부모 워크스페이스로 돌아와서:
   ```bash
   cd /Users/gurumee92/Workspaces/zWorkspaces
   git add blogs
   git commit -m "chore: bump blogs submodule to AstroPaper migration"
   ```

**Verify (success criteria — from requirements):**
- ✅ 로컬 `npm run dev` 동작
- ✅ `npm run build` 무오류
- ✅ Action 통과, `zzanghyunmoo.github.io`가 새 디자인으로 갱신
- ✅ 다크/라이트 토글 동작, 한국어 정상
- ✅ AstroPaper 샘플 글이 목록/태그/RSS에 노출

---

## 2. 의존성 그래프

```
A (delete Quartz)
  └─> B (scaffold AstroPaper)
        └─> C (configure site)
              └─> D (replace workflow)  [parallel-safe with E]
              └─> E (README)            [parallel-safe with D]
                    └─> F (verify + parent submodule bump)
```

D와 E는 다른 파일을 만지므로 병렬 가능. 다만 본 작업 규모상 순차 진행 권장.

---

## 3. 위험 및 완화

| 위험 | 발생 시점 | 완화 |
|---|---|---|
| AstroPaper Node 버전 요구 (v20+) 미충족 | Unit B `npm install` | `.node-version` 또는 nvm으로 v22 사용 |
| GitHub Pages 환경 미설정 | Unit F push 후 | Repo Settings → Pages → Source = "GitHub Actions" 확인 |
| user-site (`<user>.github.io`)이라 base path 문제 | Unit C/F | `site: "https://zzanghyunmoo.github.io"`, `base` 미설정 |
| 한국어 폰트 렌더링 어색 | Unit F 시각 검증 | `src/styles/`에서 `font-family`에 `Pretendard`, `"Apple SD Gothic Neo"`, `system-ui` fallback 추가 (필요 시 follow-up) |
| submodule pointer 안 올라가서 부모에서 옛 커밋 가리킴 | Unit F | 부모 레포에서 `git add blogs && git commit` 잊지 말 것 |
| 트리거 브랜치 `v4` vs `main` 혼동 | Unit D | 현 default `v4` 유지. 변경은 follow-up |

---

## 4. 롤백 절차

문제 발생 시:
```bash
cd blogs
git checkout v4
git reset --hard pre-astropaper-migration
git push --force-with-lease origin v4   # ⚠️ 신중히
```

PR 단계에서 발견 시: PR 닫고 `migrate/astropaper` 브랜치 폐기.

---

## 5. Out of scope (follow-up 후보)

- 색상/폰트 본격 커스터마이징
- 댓글 시스템 (giscus 등)
- 검색 강화 (Pagefind는 AstroPaper 기본 포함됨)
- Analytics 통합 (구 Quartz는 Plausible 사용)
- default branch를 `main`으로 변경

---

## 6. 실행 체크리스트

- [ ] A. 백업 + Quartz 삭제
- [ ] B. AstroPaper 스캐폴드
- [ ] C. 사이트 메타데이터 + locale=ko
- [ ] D. Pages workflow 교체
- [ ] E. README 재작성
- [ ] F. 검증 + 푸시 + 부모 submodule bump

---

## Approval gate

이 계획대로 진행해도 될지 사용자 승인 필요 →
승인 시 `03-implement` (또는 직접 구현) 단계로 진행.
