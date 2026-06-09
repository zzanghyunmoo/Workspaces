# Blog Migration: Quartz → Astro + AstroPaper

**Date:** 2026-06-09
**Mode:** CE Brainstorm (feature/migration)
**Status:** Approved → ready for `02-plan`

---

## What we're building

`blogs/` 디렉터리의 기술 블로그를 **Quartz 4** 기반에서 **Astro + AstroPaper** 기반으로 전면 교체한다.
기존 GitHub Pages 배포 (`zzanghyunmoo.github.io`)는 유지한다.

## Why

- 현재 Quartz의 디자인/테마가 마음에 들지 않고 커스터마이징 학습 비용이 큼.
- Obsidian Vault 스타일(`content/01_Project/`, `04_Archive/`)이 일반 블로그에 비해 어색함.
- "글만 쓰면 자동으로 예쁘게 나오는" 환경을 원함 → 정형화된 블로그 SSG가 더 적합.
- AstroPaper는 모던/미니멀 디자인, 다크모드, 한국어 폰트 적용 용이, GitHub Pages 호환.

## Decision summary

| 항목 | 결정 |
|---|---|
| SSG | **Astro + AstroPaper 템플릿** |
| 배포 | GitHub Pages 유지 (현 도메인 `zzanghyunmoo.github.io`) |
| 콘텐츠 마이그레이션 | **기존 글 전체 삭제** — 새로 시작 |
| 폴더 구조 | AstroPaper 기본 (`src/content/blog/*.md`), Obsidian Vault 구조 폐기 |
| 디렉터리 | `blogs/` 그대로 사용 (안의 내용물만 교체) |

## Scope

### In scope
- 기존 Quartz 관련 파일/디렉터리 제거 (`quartz/`, `quartz.config.ts`, `quartz.layout.ts`, `content/`, Quartz 의존성 등)
- AstroPaper 템플릿 신규 설치 및 초기 설정 (사이트 메타데이터, 한국어 locale, 다크모드 색상)
- GitHub Pages 배포 워크플로 교체 (`.github/workflows/deploy.yml`)
- 기존 콘텐츠(`content/` 전체) 삭제 — 마이그레이션 없이 새로 시작
- AstroPaper의 샘플 글 1~2개로 동작 검증 후 그대로 두거나 제거
- README 갱신 (Quartz → AstroPaper 빌드/실행 가이드)

### Out of scope
- Obsidian 백링크/그래프뷰 기능 (포기)
- 자체 디자인 시스템 구축 (AstroPaper 기본 테마 + 소량 색상 토큰 조정만)
- 콘텐츠 본문 리라이팅 (제목/frontmatter만 정리)
- 댓글, 검색, 분석 등 추가 통합 (필요 시 후속 작업)

## Files/modules that will change

```
blogs/
├── quartz/                    [DELETE]
├── quartz.config.ts           [DELETE]
├── quartz.layout.ts           [DELETE]
├── content/                   [DELETE — 전체]
├── globals.d.ts               [DELETE — Quartz 전용]
├── index.d.ts                 [DELETE — Quartz 전용]
├── package.json               [REPLACE — AstroPaper 의존성]
├── package-lock.json          [REGENERATE]
├── tsconfig.json              [REPLACE — Astro 기본]
├── Dockerfile                 [DELETE — 불필요]
├── .github/workflows/deploy.yml [REPLACE — Astro 빌드 → Pages]
├── README.md                  [REWRITE]
└── src/                       [NEW]
    ├── content/blog/*.md      [수동 이관 글]
    ├── config.ts              [사이트 메타데이터]
    └── ...                    [AstroPaper 기본 구조]
```

## Responsibility boundaries

- **AstroPaper 템플릿**: 레이아웃, 라우팅, RSS, 태그 페이지, 검색, 다크모드.
- **사용자가 손대는 곳**: `src/config.ts` (사이트 정보), `src/content/blog/*.md` (글), `src/styles/` (색상 토큰).
- **건드리지 않을 곳**: AstroPaper의 컴포넌트/유틸 — 업그레이드 가능성 보존.

## What can fail

| 위험 | 완화책 |
|---|---|
| GitHub Pages base path 미스매치 (404) | `astro.config.ts`의 `site`/`base`를 현 URL에 맞게 설정 |
| 한국어 폰트 깨짐 | `src/styles/`에서 system font + Pretendard/Noto Sans KR fallback |
| Quartz 잔여 파일이 빌드에 끼어듦 | 단계별 삭제 후 `npm run build` 검증 |
| 배포 워크플로 권한 부족 | Pages settings를 "GitHub Actions" source로 전환 확인 |

## How we verify success

1. `cd blogs && npm install && npm run dev` → 로컬에서 AstroPaper 사이트가 뜸.
2. `npm run build` 무오류, `dist/`에 정적 파일 생성.
3. `main` push 시 GitHub Action이 통과하고 `https://zzanghyunmoo.github.io`가 새 디자인으로 갱신됨.
4. 다크/라이트 모드 토글 동작, 한국어가 깨지지 않음.
5. AstroPaper 기본 샘플 글이 블로그 목록/태그/RSS에 정상 노출.

## Alternatives considered

| 옵션 | 채택? | 이유 |
|---|---|---|
| **Astro + AstroPaper** | ✅ | 모던 디자인 + 현 Node 환경 그대로 + Markdown-only |
| Hugo + PaperMod | ❌ | 가장 간단하나 Go 바이너리 설치 부담, 커스터마이징 시 Go 템플릿 학습 |
| Jekyll + Chirpy | ❌ | Ruby 환경 필요, 빌드 느림 |
| Quartz 유지하며 테마만 손보기 | ❌ | 사용자가 명시적으로 거부 (디자인/커스터마이징 어려움이 핵심 불만) |

## Open decisions (handoff에서 결정)

- AstroPaper의 site author/이메일/소셜 링크 값 (실제 정보 입력 시점)
- 색상 토큰 커스터마이즈 범위 (기본값 그대로 갈지, 브랜드 색 적용할지)

## Approval

> User: "Astro + AstroPaper (추천)" + "let's go (기존 글은 지워도 돼)" — 2026-06-09 ✅
