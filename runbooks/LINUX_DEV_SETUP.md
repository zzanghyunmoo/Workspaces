# 리눅스 개발 환경 세팅 런북

## 개요

이 문서는 Ansible을 사용하여 리눅스 데스크톱에 개발 환경을 자동으로 구성하는 방법을 설명합니다.

## 사전 요구사항

- **운영체제**: Debian 기반 리눅스 (Ubuntu 등)
- **권한**: sudo 권한 필요 (패키지 설치용)
- **Ansible**: 버전 2.9 이상

## Ansible 설치

Ansible이 설치되어 있지 않은 경우:

```bash
sudo apt update
sudo apt install -y ansible
```

설치 확인:
```bash
ansible --version
```

## 개발 환경 세팅 실행

### 1단계: settings 서브모듈 이동

```bash
cd projects/settings
```

### 2단계: Linux Playbook 실행

```bash
ansible-playbook playbooks/linux.yml
```

이 명령은 다음 작업을 자동으로 수행합니다:
- 시스템 패키지 설치
- 개발 언어 설치 (Go, Node.js, Python, Rust)
- Shell 환경 설정 (oh-my-zsh, powerlevel10k)

## 설치된 도구

### 시스템 패키지

| 패키지 | 용도 |
|--------|------|
| build-essential | C/C++ 컴파일러 및 빌드 도구 |
| zsh | Z Shell |
| git | 버전 관리 시스템 |
| htop | 시스템 모니터링 |
| wget | 웹 다운로드 도구 |
| curl | 데이터 전송 도구 |
| vim | 텍스트 에디터 |
| tmux | 터미널 멀티플렉서 |
| tree | 디렉토리 트리 표시 |
| jq | JSON 처리 도구 |
| fzf | 퍼지 파인더 |

### 개발 언어 및 도구

| 도구 | 버전 | 설치 방법 |
|------|-------|---------|
| Go | 1.22.2+ | tar.gz 다운로드 및 설치 |
| Node.js | 18.x | apt 패키지 매니저 |
| Python | 3.12.3+ | apt 패키지 매니저 |
| uv (Python 패키지 매니저) | 0.9.28+ | GitHub 릴리스 |
| Rust | 최신 버전 | rustup 설치 스크립트 |
| NVM (Node Version Manager) | 0.40.4+ | GitHub 릴리스 |
| npm | 최신 버전 | apt 패키지 매니저 |

### Shell 환경

| 도구 | 용도 |
|------|------|
| oh-my-zsh | Zsh 설정 프레임워크 |
| powerlevel10k | Zsh 테마 |

## 설치 경로

### 사용자 수준 바이너리
- `~/.local/bin/uv` - Python 패키지 매니저
- `~/.nvm/` - Node Version Manager
- `~/.cargo/bin/` - Rust 도구
- `~/.go/bin/` - Go 도구

### 시스템 수준 패키지
- `/usr/bin/` - 대부분의 시스템 패키지
- `/usr/local/go/bin/` - Go

## PATH 설정

`.zshrc` 파일에 다음 PATH 설정이 추가됩니다:

```bash
export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/.nvm:$PATH"
export PATH="$HOME/.go/bin:$PATH"
```

## NVM 사용법

Node.js 버전 관리를 위해 NVM 사용:

```bash
# NVM 로드
source ~/.nvm/nvm.sh

# Node.js 최신 버전 설치
nvm install node

# 특정 버전 설치
nvm install 18.19.1

# 기본 버전 설정
nvm alias default node

# 사용 가능한 버전 목록
nvm ls-remote

# 설치된 버전 목록
nvm ls
```

## Rust 사용법

Rust 개발 환경 설정:

```bash
# Rustup 업데이트
rustup update

# Cargo로 패키지 설치
cargo install ripgrep

# 프로젝트 생성
cargo new myproject
```

## Go 사용법

Go 개발 환경 설정:

```bash
# Go 모듈 초기화
go mod init myproject

# 의존성 설치
go get github.com/package/example

# 프로젝트 빌드
go build
```

## uv 사용법

uv (Python 패키지 매니저) 사용:

```bash
# 가상 환경 생성
uv venv

# 패키지 설치
uv pip install requests

# requirements.txt에서 설치
uv pip install -r requirements.txt
```

## 문제 해결

### Ansible 실행 실패

**문제**: sudo 권한 필요
```bash
# 현재 사용자가 sudo 권한이 있는지 확인
sudo whoami
```

**문제**: Ansible 설치되지 않음
```bash
sudo apt install -y ansible
```

### uv 설치 실패

**문제**: `/tmp/uv` 디렉토리 없음
- `python.yml` playbook이 자동으로 디렉토리를 생성하도록 수정됨

**문제**: uv 바이너리를 찾을 수 없음
```bash
# PATH 확인
echo $PATH

# 수동으로 PATH 추가
export PATH="$HOME/.local/bin:$PATH"
```

### Shell 변경사항 적용

새 터미널에서 변경사항이 적용되지 않는 경우:

```bash
# .zshrc 다시 로드
source ~/.zshrc
```

## Playbook 구조

```
playbooks/
├── linux.yml          # 리눅스 메인 플레이북
├── mac.yml            # macOS 플레이북
└── windows.yml        # 윈도우 플레이북

roles/
└── packages/
    ├── tasks/
    │   ├── main.yml           # 메인 태스크
    │   ├── mac.yml            # macOS용 패키지
    │   ├── ohmyzsh.yml        # Zsh 설정
    │   └── languages/
    │       ├── golang.yml     # Go 설치
    │       ├── nodejs.yml     # Node.js/NVM 설치
    │       ├── python.yml     # Python/uv 설치
    │       └── rust.yml       # Rust 설치
    └── vars/
        └── main.yml           # 패키지 변수
```

## 마지막 세팅 기록

- **날짜**: 2026-02-01
- **상태**: 성공
- **설치된 버전**:
  - Go: 1.22.2
  - Node.js: v18.19.1
  - Python: 3.12.3
  - uv: 0.9.28
  - zsh: 5.9
  - NVM: 0.40.4
- **수정사항**:
  - `python.yml`: uv 추출 시 디렉토리 생성 태스크 추가
  - `python.yml`: uv 바이너리 경로 수정 (`/tmp/uv/uv` → `/tmp/uv/uv-x86_64-unknown-linux-gnu/uv`)

## 참고사항

- Playbook은 idempotent하게 작성되어 여러 번 실행해도 안전합니다
- 시스템 패키지 설치에는 sudo 권한이 필요합니다
- 사용자 수준 설치는 sudo 없이 진행됩니다
- Shell 설정은 `.zshrc` 파일에 추가됩니다
- 새 터미널을 열면 모든 설정이 자동으로 적용됩니다

## 다음 단계

1. 터미널을 다시 시작하거나 `.zshrc`를 다시 로드
2. 필요한 Node.js 버전을 NVM으로 설치
3. 프로젝트별 가상 환경 생성
4. 개발에 필요한 추가 도구 설치