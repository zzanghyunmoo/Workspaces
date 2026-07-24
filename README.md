# 짱현무의 모든 레포

모든 레포의 최상위 워크스페이스입니다.

## 현재 우선순위

### 1. .NET Foundation Lab

- 경로: `projects/dotnet-foundation-lab`
- 목적: 매일 1시간씩 C#/.NET 기본기, 자료구조/알고리즘, 네트워크, DB를 정리
- 운영: 제품 작업과 분리된 고정 학습 루틴

### 2. Our Moneyflow

- 경로: `projects/our-moneyflow`
- 목적: 여러 은행 계좌를 읽기 전용으로 연결해 계좌별 가계부·예산과 주·월·연
  보고서를 제공한다
- 기술 방향: Flutter/Dart Android/iOS 단일 앱
- 현재 단계: ZZA-87 저장소 전환·closeout 완료,
  Flutter 골격은 ZZA-88에서 시작

## 보류/중지한 프로젝트

- `projects/money-pipeline` — 로컬 submodule 제거, Linear/Notion 중지 처리
- `projects/random-tower-defense` — 로컬 submodule 제거, Linear/Notion 중지 처리

원격 GitHub 저장소 삭제는 이 워크스페이스에서 수행하지 않았습니다. 필요하면 GitHub에서 수동으로 확인 후 삭제합니다.

## Pi tmux 병렬 작업

여러 Pi worker를 동시에 실행할 때는 쓰기 작업을 Git worktree로 격리하고 단일
코디네이터가 결과를 통합합니다.

```bash
python3 runbooks/pi_tmux_workers.py doctor
```

시작, 모니터링, scope/resource 충돌 방지, 결과 수집, 정리 절차는
[`runbooks/pi-tmux-workers.md`](runbooks/pi-tmux-workers.md)를 따릅니다.
