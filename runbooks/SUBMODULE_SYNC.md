# Git Submodule 싱크 런북

## 개요

이 문서는 Workspaces 프로젝트의 Git 서브모듈을 관리하고 싱크하는 방법을 설명합니다.

## 서브모듈 구조

현재 프로젝트는 3개의 서브모듈로 구성되어 있습니다:

| 서브모듈 | 경로 | 원격 저장소 | 현재 브랜치 |
|---------|------|-----------|-------------|
| blogs | blogs | https://github.com/zzanghyunmoo/zzanghyunmoo.github.io.git | v4 |
| settings | projects/settings | https://github.com/zzanghyunmoo/settings.git | main |
| studies | projects/studies | https://github.com/zzanghyunmoo/studies.git | - |

## 서브모듈 싱크 단계

### 1단계: .gitmodules 파일 확인

```bash
cat .gitmodules
```

이 명령어로 현재 등록된 서브모듈들을 확인할 수 있습니다.

### 2단계: 서브모듈 URL 싱크

```bash
git submodule sync
```

- `.gitmodules` 파일에 정의된 URL로 서브모듈 설정을 업데이트합니다.
- 원격 저장소 URL이 변경된 경우에 필요합니다.

### 3단계: 서브모듈 초기화 및 업데이트

```bash
git submodule update --init --recursive
```

**명령어 설명:**
- `--init`: 등록된 서브모듈이 없으면 초기화합니다.
- `--recursive`: 중첩된 서브모듈까지 모두 업데이트합니다.

이 명령어는 다음 작업을 수행합니다:
1. 서브모듈을 등록합니다
2. 원격 저장소에서 클론합니다
3. 적절한 커밋으로 체크아웃합니다

### 4단계: 서브모듈 상태 확인

```bash
git submodule status
```

출력 형식:
```
<commit-sha> <path> (<branch>)
```

- 앞에 `-`가 표시되면 초기화되지 않은 상태
- `+`가 표시되면 현재 커밋과 다른 상태
- 공백이면 정상 상태

## 자주 사용하는 서브모듈 명령어

### 서브모듈 목록 보기
```bash
git submodule
```

### 모든 서브모듈 최신 커밋으로 업데이트
```bash
git submodule update --remote
```

### 특정 서브모듈 업데이트
```bash
git submodule update --remote <서브모듈_경로>
```

예시:
```bash
git submodule update --remote blogs
```

### 서브모듈 삭제
```bash
git submodule deinit <서브모듈_경로>
git rm <서브모듈_경로>
```

### 모든 서브모듈 최신으로 풀 (각 서브모듈 디렉토리에서)
```bash
git submodule foreach git pull origin main
```

## 문제 해결

### 서브모듈이 초기화되지 않은 경우
```bash
git submodule init
git submodule update
```

### 서브모듈 분리된 HEAD 상태인 경우
```bash
cd <서브모듈_경로>
git checkout main  # 또는 적절한 브랜치
```

### 서브모듈 URL이 변경된 경우
```bash
git submodule sync
git submodule update --init --recursive
```

## 전체 싱크 프로세스 스크립트

전체 싱크를 한 번에 수행하는 스크립트:

```bash
#!/bin/bash
# 전체 서브모듈 싱크 스크립트

echo "1. 서브모듈 URL 싱크..."
git submodule sync

echo "2. 서브모듈 초기화 및 업데이트..."
git submodule update --init --recursive

echo "3. 서브모듈 상태 확인..."
git submodule status

echo "완료!"
```

## 참고사항

- 메인 레포지토리에서는 서브모듈의 특정 커밋만을 추적합니다
- 서브모듈 내에서 작업하려면 해당 서브모듈 디렉토리로 이동해서 작업하세요
- 서브모듈 변경사항을 메인 레포지토리에 반영하려면 서브모듈 커밋 후 메인 레포지토리에서 커밋해야 합니다

## 마지막 싱크 기록

- **날짜:** 2026-02-01
- **상태:** 성공
- **싱크된 서브모듈:**
  - blogs: e22ac58f (heads/v4)
  - projects/settings: b6011eeb (heads/main)
  - projects/studies: a9c847c