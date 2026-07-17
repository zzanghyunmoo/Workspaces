---
title: 홈 AI 인프라는 Linux 실행면에서 수렴시키고 관측성을 계층별로 분리한다
date: 2026-07-17
category: architecture-patterns
module: home-ai-infra-v1
problem_type: architecture_pattern
component: infrastructure
severity: high
applies_when:
  - macOS와 Windows 같은 이종 호스트에 같은 개인용 Kubernetes 플랫폼을 재현할 때
  - 절전·재부팅·네트워크 변경이 있는 개인 호스트의 가용성 경계를 정할 때
  - LiteLLM과 일반 애플리케이션의 템레메트리를 Langfuse·ClickStack에 연결할 때
  - OpenTelemetry Collector의 Deployment·DaemonSet·gateway 역할을 나눌 때
  - UI health보다 깊은 end-to-end 관측성 검증이 필요할 때
symptoms:
  - 호스트별 설정 차이가 Kubernetes manifest와 운영 명령까지 퍼진다
  - 노트북 하나의 절전이 다른 호스트의 control plane 가용성을 깨뜨린다
  - LLM 도메인 문제와 Kubernetes·service 문제를 하나의 관측 화면에서 억지로 풀려고 한다
  - Collector UI나 health endpoint는 살아 있지만 신호의 실제 저장 여부는 모른다
root_cause: platform_and_observability_boundaries_are_conflated
resolution_type: architecture_boundary
tags:
  - home-ai-infra
  - lima
  - wsl2
  - k3s
  - opentelemetry
  - clickstack
  - langfuse
  - litellm
  - end-to-end-smoke
related_components:
  [development_workflow, operations, observability, ai_platform]
---

# 홈 AI 인프라는 Linux 실행면에서 수렴시키고 관측성을 계층별로 분리한다

## Context

Home AI Infra v1은 macOS와 Windows에서 같은 k3s·LiteLLM·Langfuse·ClickStack
구성을 재현해야 했다. 두 호스트는 OS, 가상화, 네트워크, GPU 경로가
다르고 개인 장비이므로 절전과 재부팅이 일상적이다. 이 차이를 애플리케이션
계층까지 노출하거나 두 장비를 하나의 control plane으로 묶으면 재현성과
가용성이 호스트 상태에 종속된다.

관측성도 경계가 필요했다. Kubernetes event·container log·일반 service
trace와 LLM generation·token·cost는 같은 요청에서 나오지만 답하는 질문이
다르다. 하나의 backend에 모든 역할을 주면 데이터 계약과 장애 분리가
흐려진다.

2026-07-17에 macOS Lima 경로는 k3s node `Ready`, Helm workload·PVC,
LiteLLM·Langfuse·HyperDX health, OTLP trace·metric·log 전송, ClickHouse 실제
row 적재까지 통과했다. Windows WSL2/RTX 4060 경로는 구현과 정적
검증까지만 완료되었다.

Notion
[아키텍처 아이디에이션](https://app.notion.com/p/3a0ef22ad4fc814caaf4fba60e449a13)을
canonical source로 삼고, 이 문서는 검증 후 재사용할 경계를 추출한다.

## Guidance

### 1. 플랫폼 차이는 Linux 실행면에서 끝낸다

macOS에서는 Lima Ubuntu VM, Windows에서는 WSL2 Ubuntu를 호스트
adapter로 쓴다. 호스트별 Terraform과 bootstrap script는 Linux 실행면을 준비하고
접속 계약을 만드는 책임까지만 가진다.

Ubuntu 안에 들어온 뒤는 공통 Ansible role이 package, systemd, pinned k3s를
관리한다. k3s 위의 namespace, Secret 주입 계약, Helm values, 검증 명령은
플랫폼별로 복제하지 않는다.

```text
macOS   -> Lima Ubuntu --+
                         +-> common Ansible -> k3s -> common Helm values
Windows -> WSL2 Ubuntu --+
```

플랫폼 분기가 `bootstrap/`와 `terraform/environments/`밖으로 넘어간다면
경계가 흐려진 신호로 본다.

### 2. 개인 호스트는 같은 선언을 쓰는 독립 cluster로 시작한다

두 노트북을 하나의 Kubernetes cluster로 묶으면 배치 효율은 높아지지만,
절전·재부팅·IP 변경·방화벽 차이가 control plane과 node readiness에 바로
전파된다. v1은 각 호스트에 single-node k3s를 만들고 같은 선언 bundle을
적용한다.

이 선택은 multi-node를 영구히 금지하는 것이 아니다. 두 호스트의 상시 가동,
사설 네트워크, backup, 재해 복구, control-plane quorum 요구가 생긴 뒤에
다시 판단한다.

### 3. IaC 도구는 자원이 아니라 책임 경계로 나눈다

| 계층            | 책임                                                          |
| --------------- | ------------------------------------------------------------- |
| Terraform       | 호스트 profile, bootstrap 입력·fingerprint, 실행면 생성       |
| Ansible         | Ubuntu 패키지·systemd, k3s 설정·고정 버전, 선택적 GPU runtime |
| Helm/Kubernetes | 공통 애플리케이션과 관측성 계약                               |
| Make/runbook    | 사용자 명령과 검증 순서                                       |

Lima와 WSL을 일괄적으로 소유하는 Terraform provider가 없기 때문에
`local-exec`를 bootstrap 경계에만 쓸 수 있다. 이를 이유로 cluster 내부
리소스까지 임의 shell로 생성하지 않는다.

### 4. 관측성은 플랫폼 신호와 LLM 도메인 신호로 나눈다

```text
LiteLLM
  |- Langfuse callback ----------------> Langfuse
  |   generation, usage, latency, cost
  |
  `- OTLP -----------------------------> platform OTel Collector
                                          `-> ClickStack -> ClickHouse/HyperDX
apps / Kubernetes signals -------------^
```

- Langfuse는 LLM generation, usage, latency, cost, score처럼 LLM 도메인 질문에
  답한다.
- ClickStack은 Kubernetes event, container log, 일반 trace·metric·log와 시간대
  상관관계를 본다.
- platform OTel Collector는 애플리케이션에 일관된 OTLP endpoint를 제공하고
  ClickStack의 내부 수집 계약을 감춘다.

prompt·response 본문은 유출 표면이 될 수 있으므로 기본 수집을 끄고,
masking·retention·access control을 같이 정한 후 필요한 범위만 켠다.

### 5. single-node Deployment의 노드 커버리지를 DaemonSet 완료로 일반화하지 않는다

현재 platform Collector는 1 replica `Deployment`다. single-node에서는 이 Pod가
유일한 node에 스케줄되므로 node-local log file에 접근할 수 있다. 이 결과는
multi-node의 모든 node log 수집을 증명하지 않는다.

multi-node로 확장할 때는 다음으로 분리한다.

- Agent DaemonSet: 각 node의 `filelog`, kubeletstats, hostmetrics 수집
- Gateway Deployment: 애플리케이션 OTLP 수신, 중앙 처리, backend export
- cluster receiver: Kubernetes event처럼 중복되면 안 되는 신호를
  단일 역할에서 수집

DaemonSet manifest가 있다는 사실만으로 전환을 완료했다고 판단하지 않는다.
노드별 log 수집, Collector 자기 log 순환 방지, event 중복 방지, gateway 장애 시
버퍼링을 실기로 검증해야 한다.

### 6. health보다 저장소 적재를 성공 기준으로 삼는다

`make smoke`는 UI와 port를 확인한 뒤 OTLP HTTP로 고유한 trace·metric·log를
보내고 ClickHouse에서 다음을 직접 조회한다.

| 신호   | 검증 대상                                                         |
| ------ | ----------------------------------------------------------------- |
| trace  | `default.otel_traces` / `SpanName='host-to-cluster-smoke'`        |
| metric | `default.otel_metrics_gauge` / `MetricName='home_ai_infra_smoke'` |
| log    | `default.otel_logs` / smoke body                                  |

이 검증은 다음 경로를 한 번에 증명한다.

```text
host port-forward -> platform Collector -> ClickStack Collector -> ClickHouse
```

UI HTTP 200, Collector readiness, 입력 포트 open은 이 경로의 부분 증거일 뿐이다.

## Why This Matters

Linux 경계에서 플랫폼 차이를 끝내면 호스트가 달라도 Kubernetes 이후의
설정·배포·검증을 공유할 수 있다. 독립 cluster는 한 장비의 생명주기를
다른 장비의 장애로 전파시키지 않는다.

관측성을 계층별로 나누면 “모델 요청의 token·cost가 왜 이렇게 나왔나”는
Langfuse에서, “같은 시간에 LiteLLM Pod와 Collector에 무슨 일이 있었나”는
ClickStack과 Kubernetes에서 답할 수 있다. backend 하나에 모든 의미를 억지로
싣지 않아도 된다.

마지막으로 저장소 적재 smoke는 시스템이 실제로 쓸 수 있는 경로를
검증한다. 부분별 health만 통과한 상태를 end-to-end 성공으로 오판하는
것을 막는다.

## When to Apply

다음 조건에서 이 패턴을 적용한다.

- 개인 노트북, 워크스테이션, 홈랩처럼 상시 가동이 보장되지 않는 호스트를
  재현 가능한 Kubernetes 기반으로 쓸 때
- macOS·Windows 호스트 자동화를 하나의 애플리케이션 배포 계약으로 수렴시켜야
  할 때
- 일반 OpenTelemetry backend와 LLM 전용 관측 backend를 함께 운영할 때
- single-node에서 검증한 node-local 수집을 multi-node로 확장할 때
- 관측성 배포의 완료 조건을 저장소 기준으로 고정해야 할 때

다음 상황은 별도 설계가 필요하다.

- 상시 가동, multi-node HA, 자동 failover가 필수인 운영 클러스터
- 인터넷에 직접 노출하거나 다중 사용자·tenant를 수용하는 플랫폼
- 중앙 secret manager, backup, retention, TLS, RBAC가 아직 없는 구성을
  production-ready로 표현해야 하는 경우

## Examples

### 피해야 할 구성

```text
Mac control plane <---- unstable home network ----> Windows worker
       |
       `-> platform-specific manifests and direct backend endpoints
```

한 호스트가 잠들면 클러스터 가용성이 흔들리고, 애플리케이션이 backend별
endpoint와 플랫폼 차이를 직접 알게 된다.

### 권장 구성

```text
Mac -> Lima -> k3s A ----+
                          +-- same desired state and smoke contract
Windows -> WSL2 -> k3s B -+

each cluster:
apps -> platform OTel gateway -> ClickStack
LiteLLM -> Langfuse callback
```

호스트 상태는 독립적이지만 선언과 검증 계약은 공유한다.

### 검증 계약

```bash
make doctor
make validate
make bootstrap PLATFORM=macos
make secrets
make deploy
make expose
make smoke
```

`make smoke`의 성공은 UI HTTP 200에서 끝나지 않고 ClickHouse 신호별 table의
matching row를 요구한다.

## Validation Boundary

2026-07-17 기준 검증 상태는 다음과 같다.

- **통과:** macOS Lima VM, k3s `v1.36.2+k3s1`, platform workload·PVC, three UI/API
  health, OTLP gRPC/HTTP, ClickHouse trace·metric·log row
- **통과:** 동일 macOS bootstrap 재실행 `changed=0`
- **정적 검증만 통과:** Windows WSL2 bootstrap, NVIDIA runtime/device plugin 구성
- **미검증:** Windows 실제 host의 localhost forwarding, RTX 4060 allocatable GPU,
  Windows cluster end-to-end smoke
- **미구현:** Ollama를 포함한 model runtime·workload, provider model list
- **미검증:** multi-node Agent DaemonSet + Gateway Deployment topology

하나의 플랫폼에서 통과한 사실을 다른 플랫폼이나 배치 topology의
성공으로 일반화하지 않는다.

## Related

- Notion canonical:
  [2026-07-17 홈 AI 인프라 아키텍처 아이디에이션](https://app.notion.com/p/3a0ef22ad4fc814caaf4fba60e449a13)
- 검증된 소스 snapshot:
  [`home-ai-infra@518ff19`](https://github.com/zzanghyunmoo/home-ai-infra/tree/518ff19c142d8a829a3e67edf2edb5f95427b120)
- 구현·검증 증빙:
  [`docs/works/2026-07-17-ZZA-74-home-ai-infra-v1-work.md`](https://github.com/zzanghyunmoo/home-ai-infra/blob/518ff19c142d8a829a3e67edf2edb5f95427b120/docs/works/2026-07-17-ZZA-74-home-ai-infra-v1-work.md)
- 운영 가이드:
  [`docs/runbooks/operations.md`](https://github.com/zzanghyunmoo/home-ai-infra/blob/518ff19c142d8a829a3e67edf2edb5f95427b120/docs/runbooks/operations.md)
- 관측성 검증 스크립트:
  [`scripts/smoke.sh`](https://github.com/zzanghyunmoo/home-ai-infra/blob/518ff19c142d8a829a3e67edf2edb5f95427b120/scripts/smoke.sh)
- 기술 블로그:
  [개인 홈 AI 플랫폼 만들기](https://zzanghyunmoo.github.io/posts/home-ai-platform-series/)
- `docs/solutions/workflow/submodule-edit-and-pointer-bump.md` — 기술 블로그 서브모듈 발행 후
  parent pointer를 동기화하는 워크플로.
