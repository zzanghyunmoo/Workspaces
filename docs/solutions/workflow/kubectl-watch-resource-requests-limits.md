---
title: kubectl로 워크로드 request/limit을 watch로 지속 확인하기 (파드 라벨셀렉터 함정)
date: 2026-07-03
category: workflow
module: kubernetes-monitoring
problem_type: workflow_issue
component: tooling
severity: low
applies_when:
  - 특정 Deployment/파드의 CPU·메모리 request/limit을 눈으로 계속 지켜보고 싶을 때
  - 리소스 스펙 변경(누가 kubectl edit / 배포로 바꾸는 순간)을 잡아내고 싶을 때
  - node-exporter-operator 등 kube-monitor 네임스페이스 워크로드를 점검할 때
tags: [kubectl, watch, resources, requests-limits, label-selector, node-exporter-operator, kube-monitor, sre]
---

# kubectl로 워크로드 request/limit을 watch로 지속 확인하기 (파드 라벨셀렉터 함정)

## Context

`node-exporter-operator`(context `d01-dataplatform-prod-001`, ns `kube-monitor`)의
리소스 request/limit을 **지속적으로 눈으로 확인**하고 싶은 요구에서 출발.

두 가지 마찰이 있었다.

1. `kubectl get`에 request/limit은 기본 컬럼으로 안 나온다 → jsonpath / custom-columns 필요.
2. **파드 라벨셀렉터 함정**: 관례적으로 쓰는 `app.kubernetes.io/name=node-exporter-operator`로
   조회하면 결과가 **빈 헤더만** 나온다. 이 워크로드의 실제 라벨은 구식 `app=node-exporter-operator`다.
   (같은 네임스페이스의 `kube-prometheus-stack` 계열은 `app.kubernetes.io/*` 표준 라벨을 쓰기 때문에
   습관적으로 표준 라벨을 넣으면 조용히 실패한다.)

## Guidance

### 1) 올바른 라벨셀렉터부터 확인한다

배포마다 selector가 다르므로, 파드 조회 전에 Deployment의 `matchLabels`를 먼저 본다.

```bash
kubectl -n kube-monitor get deploy node-exporter-operator -o jsonpath='{.spec.selector.matchLabels}{"\n"}'
# => {"app":"node-exporter-operator"}   ← 표준 app.kubernetes.io/name 아님!
```

### 2) request/limit 지속 확인 watch 커맨드

Deploy 스펙과 실제 러닝 파드를 함께 보면 "스펙은 바뀌었는데 파드 롤아웃 전"인 상태도 감지된다.

```bash
watch -n 2 'echo "== DEPLOY SPEC =="; \
kubectl -n kube-monitor get deploy node-exporter-operator -o custom-columns="CONTAINER:.spec.template.spec.containers[*].name,CPU-REQ:.spec.template.spec.containers[*].resources.requests.cpu,CPU-LIM:.spec.template.spec.containers[*].resources.limits.cpu,MEM-REQ:.spec.template.spec.containers[*].resources.requests.memory,MEM-LIM:.spec.template.spec.containers[*].resources.limits.memory"; \
echo; echo "== RUNNING POD =="; \
kubectl -n kube-monitor get pod -l app=node-exporter-operator -o custom-columns="POD:.metadata.name,CONTAINER:.spec.containers[*].name,CPU-REQ:.spec.containers[*].resources.requests.cpu,CPU-LIM:.spec.containers[*].resources.limits.cpu,MEM-REQ:.spec.containers[*].resources.requests.memory,MEM-LIM:.spec.containers[*].resources.limits.memory"'
```

- `-n 2` = 2초 주기(원하면 `-n 10` 등으로 조정). 종료는 `Ctrl+C`.
- `watch`는 화면을 계속 점유하므로 **에이전트 세션 안이 아니라 사용자 터미널에서 직접 실행**하는 게 낫다.
  (Claude Code 세션에서 굳이 돌리려면 프롬프트에 `! ` 접두사 사용.)

### 3) 다른 워크로드로 일반화

네임스페이스/이름/셀렉터만 바꾸면 임의의 Deployment에 재사용 가능하다. 핵심은 **셀렉터를 추측하지 말고
`.spec.selector.matchLabels`로 먼저 확인**하는 것.

## Why This Matters

- request/limit은 **스펙(정적) 값**이라 누가 `kubectl edit`/배포로 바꾸기 전엔 변하지 않는다.
  즉 watch의 실질적 용도는 실시간 그래프가 아니라 **"변경되는 순간을 포착"**하는 것이다.
  (정기 알림이 목적이면 watch 대신 Meerkat 경보(`kube_pod_container_resource_limits` 메트릭)나 스케줄 잡이 맞다.)
- 라벨셀렉터가 틀리면 `kubectl get pod -l ...`은 **에러 없이 빈 결과**를 반환한다 —
  "파드가 없다"로 오인하기 쉬우므로 selector를 항상 사실로 확인해야 한다.
- request == limit이면 Guaranteed QoS. 확인 당시 `node-exporter-operator`의 `manager` 컨테이너는
  CPU 1/1, Mem 1Gi/1Gi로 Guaranteed였다.

## When to Apply

- 특정 워크로드의 리소스 스펙을 눈으로 지켜보거나 변경 순간을 잡고 싶을 때.
- 조회 결과가 비어 나올 때 라벨셀렉터 불일치를 첫 번째 의심 지점으로 삼을 때.

## Examples

셀렉터 함정 재현 → 교정:

```bash
# ❌ 표준 라벨 가정 — 빈 헤더만 반환 (에러 아님)
kubectl -n kube-monitor get pod -l app.kubernetes.io/name=node-exporter-operator -o custom-columns=...
# POD   CONTAINER   ...   (행 없음)

# ✅ 실제 라벨로 교정
kubectl -n kube-monitor get pod -l app=node-exporter-operator -o custom-columns=...
# node-exporter-operator-7c46c6dcb8-4crrw   manager   1   1   1Gi   1Gi
```
