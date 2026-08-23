---
module: my-desk-setup
tags: [neovim, nvchad, java, kotlin, dotnet, aspnet, lima]
problem_type: workflow
---

# Lima NvChad JVM/.NET 개발 환경

## 현재 상태

PR [#8](https://github.com/zzanghyunmoo/my-desk-setup/pull/8)을 squash merge하여
`main`에 반영했다. merge commit은 `a98ba15a51e1d806ff544fe926149f66855cb017`이다.

Apple Silicon Lima guest에서 NvChad 하나로 기존 언어와 Java·Kotlin·C#을 함께 사용한다.
Gradle/Spring Boot, dotnet/ASP.NET Core API·Razor·Blazor 편집, build/test/run/watch와
실제 breakpoint DAP를 지원하며 doctor expected capability 26/26을 통과했다.

## 운영 경계

- 의존성은 catalog/lock의 exact URL·digest와 managed runtime만 사용한다.
- ASP.NET launch profile은 loopback만 허용하고 workspace trust는 root 범위로 적용한다.
- apply 재실행은 25개 outcome 모두 noop이어야 하며, doctor가 ready가 아니면 배포를 완료로
  간주하지 않는다.

## 검증

CI #42, Target certification #38, code/doc review marker 모두 merge 전 최신 head에서
통과했다. 로컬 `projects/my-desk-setup`은 merge 후 `main`과 `origin/main`이 동일한
commit을 가리키며 clean 상태다.

관련 구현 기록: https://app.notion.com/p/3c3ef22ad4fc81ad97e0d9f020192b8e
