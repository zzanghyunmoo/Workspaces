---
date: 2026-07-03
topic: sre-ai-dotnet-creator-flywheel
mode: elsewhere-software
---

# SRE 경험을 중심에 둔 AI · .NET · 콘텐츠 플라이휠 아이디에이션

## 한 줄 결론

지금 가장 좋은 방향은 **C#/.NET으로 AI SRE 자동화 도구를 만들고, 그 과정을 개발 콘텐츠와 강의로 쌓는 것**이다.

게임 개발, 개발 인플루언서, AI 자동화 플랫폼을 각각 따로 키우려고 하면
시간이 너무 많이 찢어진다. 반대로 하나의 중심축을 잘 잡으면 관심사를 꽤
자연스럽게 연결할 수 있다. 경제 블로그는 별도 `money-flow` 프로젝트로 분리한다.

> **AI SRE 자동화 제품을 만든다.**  
> 그 과정을 **.NET 학습 기록**, **개발 강의**, **블로그/유튜브 콘텐츠**로 재가공한다.  
> 게임 개발은 별도 본업 후보가 아니라, C# 연습과 SRE 개념을 설명하는 시각화 실험으로 가져간다.  
> 경제 블로그는 `money-flow`에서 별도로 키운다.

## 왜 이 방향이 맞아 보이는가

현재 가진 강점은 꽤 선명하다.

- 7년차 SRE 경험
- Python, Go, Java/Spring 개발 경험
- Kubernetes 운영 경험
- Mimir, Loki, Tempo 기반 observability 플랫폼 구축·운영 경험
- 실제 운영 문제를 겪어본 감각
- 이제 C#/.NET/MS 생태계를 깊게 써보고 싶은 의지

이 조합은 흔하지 않다.  
그래서 완전히 새로운 분야로 처음부터 다시 시작하기보다, **기존 SRE 경험을 레버리지로 쓰면서 C#/.NET을 새 무기로 붙이는 쪽**이 좋다.

AI SRE나 incident automation 시장은 이미 Datadog, PagerDuty, Rootly 같은
플레이어가 움직이고 있다. 그래서 “나도 AI SRE Copilot 만들겠다”처럼 넓게
들어가면 묻히기 쉽다. 대신 처음에는 작고 명확한 문제를 잡는 편이 낫다.

개발 콘텐츠도 마찬가지다.  
그냥 “개발 강의합니다”보다, **7년차 SRE가 .NET과 AI로 운영 자동화 도구를 직접 만들어가는 기록**이 훨씬 더 기억에 남는다.

## 판단 기준

이번 아이디에이션에서는 아래 기준으로 아이디어를 골랐다.

1. 기존 SRE/o11y 경험을 얼마나 잘 살리는가
2. C#/.NET/MS 기술을 억지 없이 깊게 써볼 수 있는가
3. 제품, 블로그, 유튜브, 강의로 재활용하기 쉬운가
4. `money-flow` 프로젝트와 경계를 분명히 나눌 수 있는가
5. 게임 개발 관심사를 버리지 않되, 메인 방향을 흐리지 않는가

---

## 1. Alert Rule Clinic

**가장 먼저 해볼 만한 제품 아이디어.**

Prometheus/Mimir alert rule YAML을 넣으면 다음을 분석해주는 .NET 기반 웹앱 또는 CLI다.

- noisy alert 가능성
- threshold가 너무 빡세거나 느슨한지
- 빠진 label, annotation, runbook URL
- alert 설명 문구 개선
- 테스트 케이스 제안
- 비슷한 장애 상황에서 어떤 로그/메트릭을 같이 봐야 하는지

처음부터 Mimir API와 실시간으로 붙을 필요는 없다.  
첫 버전은 사용자가 YAML을 붙여 넣으면 정적 분석 + 휴리스틱 + LLM 리뷰로 결과를 주는 정도면 충분하다.

이 아이디어가 좋은 이유는 범위가 작기 때문이다.  
“AI가 장애 대응을 다 해줍니다”는 너무 크고 뻔하다. 반면 alert rule은
SRE라면 누구나 겪는 구체적인 고통이고, 네 경험도 바로 드러난다.

콘텐츠화하기도 쉽다.

- “좋은 Prometheus alert rule의 조건”
- “noisy alert를 줄이는 방법”
- “Mimir alert rule을 AI로 리뷰해보기”
- “.NET으로 SRE 도구 만들기 1편”

**확신도:** 높음  
**복잡도:** 중간  
**주의점:** 실제 사례와 반례가 부족하면 AI 답변이 뻔해질 수 있다. 초반부터 예제 rule corpus를 같이 모아야 한다.

---

## 2. One Spine, Four Outputs Flywheel

이건 제품 아이디어라기보다 운영 원칙에 가깝다. 하지만 전체 방향을 정하는 데 가장 중요하다.

앞으로 무언가를 만들 때마다 결과물을 네 가지로 쪼갠다.

1. 코드 저장소
2. 블로그 글
3. 유튜브 영상 또는 쇼츠
4. 강의 자료, 체크리스트, PDF, 템플릿

예를 들어 Alert Rule Clinic의 첫 기능을 만든다면, 결과물은 이렇게 나온다.

- GitHub repo: `.NET으로 Prometheus rule analyzer 만들기`
- 블로그: `나쁜 alert rule이 장애 대응을 망치는 이유`
- 유튜브: `AI로 Mimir alert rule 리뷰해보기`
- 자료: `Prometheus Alert Rule Review Checklist`

이 구조가 없으면 제품 개발, 개발 인플루언서, 강의가 서로 경쟁한다.  
반대로 이 구조가 있으면 하나의 작업이 여러 채널로 퍼진다. 경제 블로그는 이 흐름에 억지로 끼우지 않는다.

이미 `projects/blog-automation`에 블로그 자동화 프로젝트가 있는 것도 힌트다.
지금 당장 완성된 콘텐츠 플랫폼을 만들 필요는 없지만, 장기적으로는 이
플라이휠을 자동화하는 방향도 자연스럽다.

**확신도:** 매우 높음  
**복잡도:** 낮음  
**주의점:** 템플릿 없이 하면 금방 흐트러진다. 처음부터 “기능 하나 = 콘텐츠 3~4개”라는 규칙을 정해두는 게 좋다.

---

## 3. .NET AI SRE Lab Series

C#/.NET/MS 기술을 배우기 위한 공개 실험실이다.

구성은 대략 이렇게 잡을 수 있다.

- ASP.NET Core API
- Semantic Kernel 또는 Microsoft Agent Framework
- Azure OpenAI 또는 OpenAI API
- .NET Aspire 실험
- local Kubernetes/kind/k3d
- Grafana stack 또는 샘플 telemetry
- Alert Rule Clinic, Runbook Studio 같은 작은 도구들

핵심은 “.NET 공부합니다”가 아니라, **SRE가 실제로 쓸 만한 AI 도구를 .NET으로 만들어본다**는 점이다.

이 시리즈는 포트폴리오 역할도 한다.  
나중에 누가 봐도 “이 사람은 SRE 경험만 있는 게 아니라 .NET으로 제품을 만들 수 있구나”가 보여야 한다.

추천하는 첫 모양은 크지 않다.

```text
/sre-ai-lab
  /src
    AlertRuleClinic.Api
    AlertRuleClinic.Cli
  /samples
    alerts/
    incidents/
  /docs
    episodes/
```

**확신도:** 높음  
**복잡도:** 중간  
**주의점:** lab 자체가 목적이 되면 안 된다. 1번 Alert Rule Clinic 같은 구체적인 기능을 중심에 두고 lab을 키워야 한다.

---

## 4. Incident Benchmark & Demo Bank

AI SRE 도구를 만들 때 가장 큰 문제는 “그래서 이게 잘하는지 어떻게 증명하지?”다.

그래서 제품보다 먼저, 혹은 제품과 동시에 작은 benchmark/demo bank를 만드는 것도 좋다.

예를 들면 이런 것들이다.

- 잘못 설계된 alert rule 예시
- noisy alert 예시
- 장애 타임라인 샘플
- Loki 로그 샘플
- Mimir metric 샘플
- Tempo trace 샘플
- 나쁜 runbook과 좋은 runbook 비교
- 기대되는 AI 분석 결과

이 자료는 여러 곳에 재사용된다.

- 제품 테스트 데이터
- 유튜브 데모
- 블로그 예제
- 강의 실습 자료
- “AI SRE 도구 비교” 콘텐츠

AI SRE 시장은 이미 붐비고 있다.  
그 안에서 차별화하려면 “우리도 AI로 분석합니다”보다 **무엇을 잘한다고 말할 수 있는 기준**이 필요하다.

처음부터 거대한 benchmark를 만들 필요는 없다.  
5개 정도의 작은 incident scenario로 시작하면 된다.

**확신도:** 중간 이상  
**복잡도:** 중간  
**주의점:** 데이터셋 설계에 욕심을 내면 오래 걸린다. 처음에는 데모와 학습 자료로 쓸 수 있는 정도면 충분하다.

---

## 5. Money-flow 분리 원칙

경제 블로그와 돈 관련 실험은 이 로드맵에서 빼고, 별도 `money-flow`
프로젝트에서 다룬다. 이 문서의 중심은 AI SRE 자동화 제품, .NET 학습,
개발 콘텐츠, 강의 자산이다.

- `money-flow`: 경제 블로그, 돈/흐름/수익화 실험
- 이 문서: Alert Rule Clinic, .NET AI SRE Lab, 개발 강의/자료
- 겹칠 수 있는 주제는 링크만 남기고 운영 리듬은 분리

경제 블로그까지 한 문서에 넣으면 초점이 흐려진다. 별도 프로젝트로 빼면
SRE AI 로드맵은 더 선명해지고, `money-flow`도 독립적으로 키울 수 있다.

**확신도:** 높음  
**복잡도:** 낮음  
**주의점:** cloud cost나 개발자 수익화 이야기가 떠오르더라도, 이 문서에서는
제품/강의의 보조 맥락으로만 다룬다. 경제 콘텐츠 기획은 `money-flow`에서 따로 한다.

---

## 6. SRE Micro-Runbook Studio

운영하면서 생기는 작은 지식을 runbook card로 바꾸는 아이디어다.

예를 들어 이미 정리해둔 `kubectl로 request/limit watch하기` 같은 문서는 좋은 출발점이다. 이런 내용을 아래 형식으로 바꾼다.

- 문제 상황
- 언제 쓰는지
- 명령어
- 왜 이 명령어가 필요한지
- 자주 하는 실수
- 안전 주의사항
- 관련 메트릭
- 짧은 퀴즈
- 영상 스크립트 초안

이건 제품으로도 갈 수 있고, 콘텐츠 포맷으로도 갈 수 있다.

처음에는 제품을 만들기보다 카드 포맷을 잡는 게 먼저다.  
카드가 20개, 50개, 100개 쌓이면 그때 검색, 분류, AI 추천, 자동 실행 같은 기능이 자연스럽게 붙는다.

**확신도:** 중간 이상  
**복잡도:** 중간  
**주의점:** 그냥 명령어 모음이 되면 가치가 약하다. “왜 이걸 쓰는지”와 “어디서 실수하는지”가 핵심이다.

---

## 7. SRE Simulation Game

게임 개발은 버릴 필요가 없다. 다만 메인 방향과 분리해서 가져가면 에너지가 많이 분산된다.

그래서 게임은 **SRE 개념을 설명하는 시각화 도구**로 가져가는 게 좋아 보인다.

예를 들어 Unity로 작은 tower defense 스타일 프로토타입을 만든다.

- alert = 적
- runbook = tower
- SLO budget = 체력
- noisy alert = 자원을 낭비하게 만드는 적
- 좋은 alert routing = 효율적인 방어 경로
- 장애 전파 = wave 확산

이건 대박 게임을 만들자는 방향이 아니다.  
SRE 개념을 더 쉽게 설명하기 위한 콘텐츠 실험이다.

잘 만들면 유튜브에서 차별화 포인트가 된다.  
“장애 대응을 tower defense로 설명해봤습니다” 같은 영상은 일반적인 강의보다 기억에 남는다.

**확신도:** 중간  
**복잡도:** 중간  
**주의점:** 재미있어서 메인 프로젝트 시간을 잡아먹기 쉽다. 반드시 timebox를 걸어야 한다.

---

## 아쉽지만 첫 번째 선택에서는 밀린 아이디어들

아래 아이디어들도 나쁘지는 않다. 다만 지금 바로 중심축으로 삼기에는 범위가 크거나, 위 아이디어의 하위 기능에 가깝다.

- **Incident Timeline Generator**  
  좋지만 로그·메트릭·트레이스·배포 이벤트 연동이 필요해 첫 MVP로는 크다.
- **SRE Change Reviewer**  
  PR/Helm/alert rule 리뷰 도구로 유망하지만, Alert Rule Clinic 이후가 자연스럽다.
- **Zero-Dashboard Incident Brief**  
  Slack/Teams 연동까지 가면 범위가 빨리 커진다.
- **Flight Black Box for Deployments**  
  멋진 방향이지만 첫 단계로는 복잡하다.
- **Open-source Grafana-stack .NET connectors**  
  검색 유입과 신뢰도에는 좋지만, 단독 제품보다는 보조 자산에 가깝다.
- **Blog Automation .NET port**  
  기존 자산을 살릴 수 있지만, 먼저 무엇을 계속 발행할지 정하는 게 우선이다.
- **Enterprise-grade AI SRE platform**  
  장기적으로는 중요하지만, 지금은 검증 전 과투자에 가깝다.

---

## 추천하는 첫 번째 선택

첫 번째로는 **Alert Rule Clinic**을 추천한다.

이유는 단순하다.

- 네 SRE 경험이 바로 드러난다.
- C#/.NET으로 만들 명분이 있다.
- AI 기능이 억지스럽지 않다.
- 너무 크지 않다.
- 블로그와 유튜브 소재로 바로 쓸 수 있다.
- 나중에 Runbook Studio, Incident Benchmark, .NET AI SRE Lab으로 확장하기 좋다.

처음부터 SaaS를 만들 필요는 없다.  
아래 정도면 충분히 첫 실험이 된다.

```text
사용자가 Prometheus alert rule YAML을 붙여 넣는다.
도구가 rule을 읽는다.
도구가 문제 후보를 설명한다.
도구가 개선된 annotation/runbook/test idea를 제안한다.
결과를 markdown report로 저장한다.
```

이 정도만 되어도 첫 블로그와 첫 영상이 나온다.

---

## 당장 해볼 수 있는 2주짜리 실험

이건 계획이라기보다 감을 보기 위한 작은 실험이다.

1. Alert Rule Clinic용 샘플 alert rule 10개를 모은다.
2. 좋은 rule / 나쁜 rule 기준을 간단히 정리한다.
3. ASP.NET Core 또는 CLI로 YAML 입력을 받는다.
4. LLM에게 리뷰 프롬프트를 보내고 markdown report를 만든다.
5. 이 과정을 블로그 1편, 유튜브 1편으로 만든다.
6. 글/영상 끝에 “이런 도구가 있으면 쓸 것 같은지”를 묻는다.

이 실험의 목표는 완성도가 아니다.  
**제품, 학습, 콘텐츠가 한 번에 굴러가는지 확인하는 것**이다.

## 최종 정리

지금은 네 관심사를 하나로 줄이는 게 아니라, **순서를 정하는 게 중요하다.**

추천 순서는 이렇다.

1. **Alert Rule Clinic**으로 첫 제품 wedge를 잡는다.
2. 이 과정을 **.NET AI SRE Lab Series**로 공개한다.
3. 모든 기능을 **블로그·유튜브·강의 자료**로 재가공한다.
4. 경제 블로그와 돈 이야기는 **money-flow** 프로젝트로 분리한다.
5. 게임 개발은 **SRE Simulation Game**처럼 교육용 시각화 실험으로 timebox한다.

이렇게 가면 네 가지 관심사가 서로 싸우지 않는다.  
하나의 중심 프로젝트가 제품이 되고, 콘텐츠가 되고, 강의가 되고, 장기적으로는 개인 브랜드와 수익 파이프라인이 된다.
