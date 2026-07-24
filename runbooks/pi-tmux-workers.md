# Pi tmux 병렬 워커 운영 Runbook

`runbooks/pi_tmux_workers.py`는 여러 Pi 인스턴스를 tmux에서 실행하면서 쓰기
작업을 Git worktree로 격리하는 저장소 로컬 CLI다. 기본 원칙은 **여러 워커가
탐색하고 구현하되, 한 명의 코디네이터만 검토·커밋·통합한다**는 것이다.

## 제공하는 가드레일

- 쓰기 워커는 항상 새 `pi-worker/<run>/<worker>` 브랜치와 linked worktree를 쓴다.
- 쓰기 워커는 하나 이상의 repo-relative `--scope`를 선언해야 한다.
- linked worktree를 포함한 같은 Git common directory의 기존 워커와 scope가 겹치면
  새 워커 시작을 차단한다.
- 포트, DB, package install처럼 파일로 드러나지 않는 singleton은
  `--resource`로 예약하며 중복 예약을 차단한다.
- start/status/collect/stop/cleanup은 state-root advisory lock으로 직렬화되어
  동시 start가 scope, resource, worker-limit 검사를 우회하지 못한다.
- 쓰기 워커를 만들 때 기준 checkout이 dirty이면 시작하지 않는다.
- 읽기 워커는 Pi를 `--tools read,grep,find,ls`로 실행한다.
- 기본 동시 실행 한도는 4개다.
- 워커 프롬프트는 stage/commit/push/merge/rebase와 하위 워커 생성을 금지한다.
- `status`와 `collect`는 시작 commit부터 현재 HEAD와 working tree까지 검사한다.
  committed, staged, unstaged, untracked, ignored, index visibility flag,
  initialized nested submodule 경로를 모두 포함한다.
- metadata는 atomic replace로 저장하고 run/worker/session/repo/worktree/branch/base
  commit 계약과 symlink 부재를 매번 검증한다.
- tmux target은 exact session 이름으로 지정해 prefix가 비슷한 다른 worker를 건드리지
  않는다.
- tmux 상태를 확인할 수 없거나 Pi가 시작 직후 종료되면 fail closed 한다. 시작 실패
  시 변경이 생긴 worktree와 metadata는 복구를 위해 보존한다.
- `cleanup`은 실행 중, dirty, scope 위반, missing/mismatched worktree를 삭제하지 않으며
  브랜치도 삭제하지 않는다.
- 결과 수집은 pane log, 변경 경로, diff 통계만 저장하고 전체 patch는 저장하지 않는다.

> [!IMPORTANT]
> `--scope`는 OS sandbox가 아니라 사전 충돌 방지와 사후 위반 탐지 계약이다.
> Pi extension 자체도 프로세스 시작 시 임의 코드를 실행할 수 있으므로 read mode 역시
> 보안 sandbox가 아니다. 신뢰하지 않는 코드에는 별도 container/VM을 사용한다.

## 0. 사전 점검

```bash
python3 runbooks/pi_tmux_workers.py doctor
```

현재 환경처럼 tmux 3.2~3.4를 사용하면 `~/.tmux.conf`에는 다음만 추가한다.

```tmux
set -g extended-keys on
```

tmux 3.5 이상에서만 다음 설정도 함께 사용한다.

```tmux
set -g extended-keys-format csi-u
```

설정 변경 후에는 실행 중인 tmux 작업이 없을 때 서버를 재시작한다.

```bash
tmux kill-server
tmux
```

`doctor`는 설정을 자동 변경하거나 tmux 서버를 재시작하지 않는다.

## 1. 작업을 독립 slice로 나누기

각 워커의 task를 별도 Markdown 파일로 작성한다. task 파일에는 secret, token,
내부 credential을 넣지 않는다.

```bash
mkdir -p /tmp/pi-worker-tasks/ZZA-123

cat > /tmp/pi-worker-tasks/ZZA-123/api.md <<'TASK'
API validation slice를 구현하고 관련 focused test를 실행한다.
완료 시 변경 파일, 검증 결과, blocker를 보고한다.
TASK

cat > /tmp/pi-worker-tasks/ZZA-123/ui.md <<'TASK'
API 계약을 바꾸지 않고 UI error state slice를 구현한다.
완료 시 변경 파일, 검증 결과, blocker를 보고한다.
TASK
```

병렬 실행 전 다음을 확인한다.

1. 두 작업의 파일 scope가 겹치지 않는가?
2. 공용 type/API/schema/lockfile/generated artifact를 함께 바꾸지 않는가?
3. 같은 DB, dev server port, browser session, package install을 공유하지 않는가?
4. 한 작업 결과가 다른 작업의 선행 조건이면 병렬 대신 직렬로 실행했는가?

공유 API나 schema처럼 논리적으로 결합된 작업은 경로가 달라도 직렬 실행한다.

## 2. 워커 시작

### 쓰기 워커

프로젝트 repo는 해당 프로젝트 경로를 `--repo`로 전달한다. 기준 ref를 생략하면
현재 checkout의 `HEAD`에서 worktree를 만든다.

```bash
python3 runbooks/pi_tmux_workers.py start \
  --run ZZA-123 \
  --worker api \
  --mode write \
  --repo projects/ReplaceMe \
  --base HEAD \
  --task-file /tmp/pi-worker-tasks/ZZA-123/api.md \
  --scope src/api \
  --scope tests/api \
  --resource test-db

python3 runbooks/pi_tmux_workers.py start \
  --run ZZA-123 \
  --worker ui \
  --mode write \
  --repo projects/ReplaceMe \
  --task-file /tmp/pi-worker-tasks/ZZA-123/ui.md \
  --scope src/ui \
  --scope tests/ui \
  --resource browser:ui
```

`--scope .`은 repo 전체를 예약하므로 같은 repo의 다른 쓰기 워커와 병렬 실행할
수 없다. lockfile이나 공용 설정을 바꿀 가능성이 있으면 해당 경로도 scope에
포함한다.

### 읽기 워커

읽기 워커는 worktree를 만들지 않고 전달한 repo를 그대로 조사한다.

```bash
cat > /tmp/pi-worker-tasks/ZZA-123/review.md <<'TASK'
현재 validation 흐름과 기존 테스트 seam을 조사한다. 변경하지 말고 file:line 근거를 남긴다.
TASK

python3 runbooks/pi_tmux_workers.py start \
  --run ZZA-123 \
  --worker reviewer \
  --mode read \
  --repo projects/ReplaceMe \
  --task-file /tmp/pi-worker-tasks/ZZA-123/review.md
```

필요하면 워커별 모델과 thinking level을 지정할 수 있다.

```bash
--model openai/gpt-5.2-codex --thinking high
```

## 3. 모니터링과 메시지 전달

```bash
# 모든 관리 중인 워커
python3 runbooks/pi_tmux_workers.py status

# 한 run
python3 runbooks/pi_tmux_workers.py status --run ZZA-123

# 최근 pane 출력
python3 runbooks/pi_tmux_workers.py log \
  --run ZZA-123 --worker api --lines 300

# Pi editor에 steering message를 붙여넣고 Enter 전송
python3 runbooks/pi_tmux_workers.py send \
  --run ZZA-123 --worker api \
  --message "공용 schema는 수정하지 말고 blocker로 보고해줘"
```

`status`가 `SCOPE=VIOLATION:<path>`를 표시하면 해당 워커의 결과를 통합하지 않는다.
워커를 중지하고 변경 원인을 검토한 뒤, 올바른 scope로 작업을 직렬 재실행한다.

직접 접속이 필요하면 출력된 session 이름으로 attach한다.

```bash
tmux attach -t piw-ZZA-123-api
```

attach에서 빠져나올 때는 tmux detach(`Ctrl-b d`)를 사용한다. Pi 자체를 종료하지 않는다.

## 4. 결과 수집

```bash
python3 runbooks/pi_tmux_workers.py collect --run ZZA-123
```

기본 저장 위치:

```text
~/.local/state/pi-tmux-workers/<run>/artifacts/<worker>/
├── pane.log
├── metadata.json
├── changed-paths.txt   # write mode
├── diff-stat.txt       # committed, unstaged, staged 통계
└── guard.txt           # write mode scope pass/violation
```

수집 로그에는 워커가 출력한 민감 정보가 포함될 수 있다. 공유하거나 커밋하기 전에
검토하고, 더 이상 필요하지 않으면 삭제한다. 전체 diff는 worktree에서 직접 검토한다.

```bash
git -C <status에 표시된 CWD> status --short
git -C <status에 표시된 CWD> diff --check
git -C <status에 표시된 CWD> diff
```

## 5. 단일 코디네이터 통합

병렬 워커는 통합자가 아니다. 코디네이터 한 명이 다음 순서를 지킨다.

1. 모든 worker log와 `guard.txt`를 확인한다.
2. worker worktree의 실제 diff를 task와 scope에 대조한다.
3. focused test와 통합 검증을 코디네이터가 다시 실행한다.
4. 한 번에 한 worker slice만 stage하고 커밋한다.
5. dependency 순서대로 통합 브랜치에 cherry-pick하거나 병합한다.
6. 충돌이 나면 자동 결합하지 말고 뒤쪽 slice를 통합된 tree에서 직렬 재실행한다.

프로젝트 repo(`projects/` 아래)는 default branch에서 통합하지 않는다. 티켓 브랜치에서
통합하고 PR/MR을 연다. zWorkspaces 루트 메타 작업만 기존 `AGENTS.md` 규칙에 따라
root `main` 직접 반영이 가능하다.

워커 프롬프트는 commit을 금지하므로, 커밋이 필요할 때 코디네이터가 해당 worktree에서
검토와 검증을 끝낸 후 수행한다. `git add .` 대신 slice 파일만 명시적으로 stage한다.

## 6. 중지와 정리

```bash
# 한 워커만 중지
python3 runbooks/pi_tmux_workers.py stop --run ZZA-123 --worker api

# run 전체 중지
python3 runbooks/pi_tmux_workers.py stop --run ZZA-123

# clean worktree와 worker metadata 정리
python3 runbooks/pi_tmux_workers.py cleanup --run ZZA-123 --worker api
python3 runbooks/pi_tmux_workers.py cleanup --run ZZA-123
```

`cleanup`은 다음 상황에서 실패한다.

- tmux session이 아직 실행 중임
- worktree에 staged, unstaged, untracked, ignored 또는 index-hidden 변경이 남아 있음
- 시작 commit 이후 committed change에 scope 위반이 남아 있음
- worktree 경로가 사라졌거나 Git registration과 metadata가 일치하지 않음
- tmux 상태를 신뢰할 수 없거나 Git이 worktree 제거를 거부함

worker branch는 증거와 복구 지점을 보존하기 위해 자동 삭제하지 않는다. 통합과 검증이
완료된 뒤 코디네이터가 명시적으로 삭제한다.

```bash
git branch -d pi-worker/ZZA-123/api
```

## 환경 변수

| 변수 | 기본값 | 의미 |
| --- | --- | --- |
| `PI_TMUX_MAX_WORKERS` | `4` | 동시 실행 한도, 최대 16 |
| `PI_TMUX_STATE_ROOT` | `~/.local/state/pi-tmux-workers` | metadata와 수집 결과 |
| `PI_TMUX_WORKTREE_ROOT` | `~/.pi/worktrees` | 쓰기 worker worktree |
| `PI_TMUX_TMUX_BIN` | `tmux` | 테스트·특수 설치용 tmux 경로 |
| `PI_TMUX_PI_BIN` | `pi` | 테스트·특수 설치용 Pi 경로 |

## 검증

```bash
python3 -m unittest runbooks.tests.test_pi_tmux_workers
python3 -m unittest discover -s runbooks/tests -p 'test_*.py'
```
