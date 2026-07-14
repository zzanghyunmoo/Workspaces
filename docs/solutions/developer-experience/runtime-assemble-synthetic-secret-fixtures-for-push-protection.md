---
title: 합성 시크릿 탐지 픽스처는 provider 형상을 런타임에 조립한다
date: 2026-07-14
category: developer-experience
module: replaceme-secret-leak-scanner
problem_type: developer_experience
component: testing_framework
severity: medium
applies_when:
  - "시크릿 스캐너 테스트가 provider token 형상을 정확히 재현해야 할 때"
  - "실제 자격 증명이 아닌 합성 픽스처가 GitHub push protection에 차단될 때"
  - "production 탐지 규칙과 저장소의 secret guardrail을 모두 유지해야 할 때"
tags: [github-push-protection, gh013, secret-scanning, test-fixtures, slack-token, runtime-assembly]
related_components: [github, testing, security-tooling, pull-request-workflow]
---

<!-- markdownlint-disable MD013 MD025 -->

# 합성 시크릿 탐지 픽스처는 provider 형상을 런타임에 조립한다

## Context

ReplaceMe [PR #23](https://github.com/zzanghyunmoo/ReplaceMe/pull/23)의 시크릿 누출 스캐너 회귀 테스트에 문법적으로 유효한 Slack 형태의 합성 토큰을 하나의 문자열 리터럴로 넣자, 이 작업 세션의 `git push`가 GitHub GH013 push protection에 차단되었다. 실제 자격 증명은 아니었지만 정적 탐지는 테스트 의도보다 저장소에 기록된 문자열 형상을 먼저 본다.

이전 세션에서도 같은 경계가 확인됐다. GitHub는 커밋된 소스 표현을 검사하고, 회귀 테스트는 실행 중 재구성된 값을 검사한다. 따라서 fixture를 런타임에 조립하면 두 검사가 서로 다른 표현을 보면서도 각자의 안전 계약을 유지할 수 있다. (session history)

해결은 GitHub의 unblock URL을 사용하는 것도, production 정규식을 약화하는 것도 아니었다. 현재 테스트는 실행 시점에 정확한 token shape를 복원한다 (`projects/ReplaceMe/tests/scripts/test_scan_local_secret_leaks.py:159-170`). 테스트는 스캐너가 provider label을 보고하는 동시에 토큰 값 자체는 출력하지 않는지도 검증한다 (`projects/ReplaceMe/tests/scripts/test_scan_local_secret_leaks.py:171-178`).

production 스캐너는 계속 GitHub, GitLab, Anthropic, Slack token patterns를 검사한다 (`projects/ReplaceMe/scripts/scan-local-secret-leaks.py:32-48`). `scan`은 로그에서 설정된 secret exact value와 common token pattern을 찾고 (`projects/ReplaceMe/scripts/scan-local-secret-leaks.py:212-217`), `main`은 실제 값 대신 key와 pattern label만 출력한 뒤 nonzero로 종료한다 (`projects/ReplaceMe/scripts/scan-local-secret-leaks.py:253-288`).

## Guidance

합성 detector fixture가 push protection과 충돌하면 다음 순서로 처리한다.

1. 경고 위치가 실제 자격 증명인지 합성 테스트 데이터인지 먼저 확인한다. 실제 값이면 즉시 폐기·회전하고 일반적인 secret incident 절차를 따른다.
2. 합성 값이라면 provider-shaped 문자열이 커밋된 소스에서 연속되지 않도록 작은 조각으로 나누고, 테스트 실행 시점에만 결합한다.
3. 결합된 런타임 값이 production regex에 실제로 매치되는지 검증한다. regex를 fixture에 맞춰 느슨하게 만들거나 탐지 대상을 제거하지 않는다.
4. 탐지 결과에는 provider label이 포함되고, 합성 토큰 값 자체는 stdout/stderr에 포함되지 않는다고 함께 단언한다.
5. 푸시 전에 focused test, lint, 가능한 로컬 secret scan을 실행한다.

피해야 할 대응은 다음과 같다.

- **완전한 fake secret literal 유지:** 가짜라는 의미 정보는 정적 push protection에 전달되지 않는다.
- **push-protection bypass 또는 unblock:** 안전장치 예외를 남길 필요가 없는 합성 fixture 문제다.
- **production regex 약화:** 테스트 데이터를 통과시키려고 탐지 범위를 줄이면 실제 로그 누출을 놓치는 blind spot이 생긴다.

소스 분할은 **합성 detector fixture에만** 허용되는 테스트 작성 기법이다. 실제 자격 증명을 숨기거나 유효한 secret 탐지를 회피하는 데 사용해서는 안 된다. 실제 자격 증명은 조각내어 커밋하지 말고 저장소 밖의 승인된 secret store와 주입 경로로 관리한다.

## Why This Matters

시크릿 스캐너 테스트는 서로 다른 두 안전장치를 동시에 만족해야 한다. 테스트 대상 스캐너에는 실제 provider 형상의 입력을 제공해야 하지만, Git 저장소와 원격 push protection에는 자격 증명처럼 보이는 연속 문자열을 남기지 않아야 한다. 런타임 조립은 production 정규식을 보존하면서 이 경계를 맞춘다.

label 검증과 값 비출력 검증을 함께 두는 것도 중요하다. 탐지는 성공했더라도 진단 메시지가 문제의 토큰을 그대로 출력하면 스캐너 자체가 두 번째 누출 경로가 된다. 현재 테스트의 `assertIn(label, output)`과 `assertNotIn(token, output)` 조합은 탐지와 redaction을 함께 고정한다 (`projects/ReplaceMe/tests/scripts/test_scan_local_secret_leaks.py:174-178`).

## When to Apply

다음 조건을 모두 만족할 때 적용한다.

- secret, DLP, push-protection 또는 provider token detector의 합성 fixture를 작성한다.
- 테스트가 production과 같은 정확한 token shape를 런타임에 필요로 한다.
- 커밋 전 정적 스캐너가 소스의 연속 리터럴도 자격 증명으로 판정할 수 있다.
- 실제 자격 증명은 전혀 사용하지 않는다.

일반 application code, 설정 파일, 문서 예시, 실제 credential 처리에는 이 기법을 적용하지 않는다. provider가 공식 테스트 토큰이나 명시적 mock 형식을 제공하고 그것이 production 경로를 충분히 검증한다면 그 방식을 우선한다.

## Examples

문서의 `<digits>`와 `<letters>`는 설명용 메타표기다. 다음처럼 완전한 provider-shaped 값을 하나의 소스 리터럴에 넣는 방식은 피한다.

```python
# Before: 실제 코드에서 placeholder가 유효한 길이의 연속 문자라면
# 정적 push protection이 Slack token으로 판정할 수 있다.
tokens = {
    "Slack token": "xoxb-<digits>-<letters>",
}
```

대신 현재 테스트처럼 실행 시점에 정확한 값을 만든다.

```python
# After: 커밋된 소스에는 완전한 Slack token shape가 연속해서 존재하지 않는다.
tokens = {
    "Slack token": "".join(
        ("xo", "xb-", "1234567890", "-abcdefghijklmnopqrstuvwxyz")
    ),
}

output = result.stdout + result.stderr
for label, token in tokens.items():
    assert label in output
    assert token not in output
```

이 패턴은 현재 fixture와 같은 경계를 사용한다 (`projects/ReplaceMe/tests/scripts/test_scan_local_secret_leaks.py:159-178`). 현재 production Slack regex는 Slack `xox*`와 `xapp` token shape를 검사한다 (`projects/ReplaceMe/scripts/scan-local-secret-leaks.py:43-47`).

## Related

- `projects/ReplaceMe/tests/scripts/test_scan_local_secret_leaks.py:159-178` — provider-shaped 합성 토큰의 런타임 조립, label 탐지, 값 비출력 회귀 테스트.
- `projects/ReplaceMe/scripts/scan-local-secret-leaks.py:32-48` — common provider token patterns.
- `projects/ReplaceMe/scripts/scan-local-secret-leaks.py:212-217` — 로그에 exact-value와 pattern 검사를 적용하는 탐지 함수.
- `projects/ReplaceMe/scripts/scan-local-secret-leaks.py:253-288` — 실제 값 대신 key와 label만 보고하고 실패하는 경로.
- [PR #23 — ZZA-68 Notion canonical 문서 구조와 운영 사실 동기화](https://github.com/zzanghyunmoo/ReplaceMe/pull/23) — 이 패턴을 적용한 변경. 2026-07-14 `main`에 squash merge됐다.
- `docs/solutions/conventions/pr-description-template.md` — GitHub-visible 문서에서 token을 노출하지 않는 일반 redaction 규칙.
- `docs/solutions/workflow-issues/pr-merge-requires-explicit-approval.md` — 안전 guardrail을 우회하지 않는 워크플로 원칙.
