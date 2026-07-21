---
title: "Our Moneyflow Flutter-only 1차 제품 출시 - Plan"
type: feat
date: 2026-07-21
ticket: ZZA-86
linear_url: https://linear.app/zzanghyunmoo/issue/ZZA-86/our-moneyflow-1차-제품-출시
linear_project_url: https://linear.app/zzanghyunmoo/project/our-moneyflow-1ccc547a369f
notion_url: https://app.notion.com/p/3a4ef22ad4fc8154b087c4a6a6c65396
origin: docs/brainstorms/2026-07-21-our-moneyflow-first-release-requirements.md
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
product_contract_source: ce-brainstorm
execution: code
deepened: 2026-07-21
revised: 2026-07-21
---

# Our Moneyflow Flutter-only 1차 제품 출시 - Plan

> Canonical Notion:
> [2026-07-21 ZZA-86 Our Moneyflow 1차 제품 출시 계획](https://app.notion.com/p/3a4ef22ad4fc8154b087c4a6a6c65396)
>
> Flutter-only 결정:
> [ZZA-88 Flutter-only 제품 경계 정정](https://app.notion.com/p/3a4ef22ad4fc8163bdf6cb3c4ca84eb2)

## Goal Capsule

- **Objective:** Our Moneyflow를 Flutter/Dart Android/iOS 앱으로 개발해 한국 양대
  스토어에 공개한다.
- **Current architecture:** 현재 확정 기술은 Flutter/Dart 단일 앱뿐이다.
- **Explicit exclusions:** 별도 API, server, sync worker와 database는 현재 범위 밖이다.
- **Decision gate:** 외부 backend, cloud, database 또는 동기화 서비스가 필요해지면
  사용자 명시 승인과 별도 티켓 전에는 기술을 선택하거나 구현하지 않는다.
- **Tail ownership:** 각 단위는 프로젝트 PR, work evidence, 최신-head review와
  merge closeout을 소유한다.

### Stop Conditions

- Flutter 이외의 runtime이나 외부 서비스를 사용자 승인 없이 추가한다.
- `projects/ReplaceMe`가 의도된 diff에 포함된다.
- 송금·결제 capability가 제품에 들어온다.
- 실제 금융 credential이나 token을 Flutter 앱에 포함하려 한다.
- 공식 provider와 보안 경계가 결정되지 않았는데 실제 은행 연결을 구현한다.
- fixture나 샘플 데이터를 실제 은행 연결로 표시한다.

## Product Contract

### 제품 범위

- 한국어·원화·개인 명의 입출금 계좌를 대상으로 한다.
- 계좌별 가계부, 월 예산, 남은 예산과 오늘부터 일평균 사용 가능액을 제공한다.
- 주·월·연 보고서와 계좌·카테고리별 상세를 제공한다.
- 데이터 신선도와 부분 실패를 숨기지 않는다.
- 읽기 전용이며 송금, 결제, 계좌 개설, 스크래핑과 신용카드 feed는 제외한다.

### Flutter-only 기술 계약

- 저장소 루트에 하나의 Flutter application을 둔다.
- Android와 iOS가 같은 Dart domain·state·UI 계약을 공유한다.
- 상태 관리, navigation, local persistence와 dependency injection은 ZZA-88 계획에서
  후보를 비교한 뒤 하나씩 pin한다.
- 금융 provider가 없는 단계에서는 versioned fixture와 local-first repository로
  모든 기능을 재현한다.
- 실제 은행 연동, 원격 동기화와 사용자 계정은 외부 서비스 아키텍처 승인 전에는
  interface와 fixture 경계까지만 다룬다.

### 핵심 동작

1. 사용자는 fixture 계좌를 선택하고 계좌별 거래와 잔액을 본다.
2. 거래를 카테고리로 분류하고 포함·제외를 되돌릴 수 있다.
3. 계좌별 월 예산을 설정하고 남은 예산과 일평균 사용 가능액을 구분해 본다.
4. 주·월·연 보고서를 이동하며 계좌·카테고리 상세를 확인한다.
5. 데이터가 partial 또는 stale이면 누락 범위와 다음 행동을 확인한다.
6. 연결 해제, 로컬 데이터 삭제와 앱 초기화를 서로 다른 행위로 수행한다.

### 데이터 규칙

- 금액은 KRW 정수로 처리한다.
- 기간은 Asia/Seoul 기준 반개구간으로 계산하고 주는 월요일에 시작한다.
- 은행 잔액과 예산상 사용 가능액을 같은 값으로 취급하지 않는다.
- fixture observation, normalized event와 사용자 override를 분리한다.
- local persistence 패키지는 ZZA-88에서 비교·결정하며 아직 특정 제품을 가정하지 않는다.

## Repository Shape

```text
projects/our-moneyflow/
├── android/
├── ios/
├── lib/
│   ├── app/
│   ├── core/
│   └── features/
├── test/
├── integration_test/
├── docs/
├── pubspec.yaml
└── analysis_options.yaml
```

Flutter가 생성하기 전까지 위 구조는 목표 상태이며 실제 파일 pin으로 간주하지 않는다.

## Delivery Units

### U1. 저장소 경계 전환 — ZZA-87

- `sre-ai-lab`을 public `our-moneyflow` 저장소로 직접 전환한다.
- 상태: 완료.

### U2. 재현 가능한 Flutter 앱 골격 — ZZA-88

- Flutter/Dart toolchain과 Android/iOS project를 pin한다.
- navigation, theme, localization, 환경 표시와 기본 오류 경계를 만든다.
- `flutter analyze`, unit/widget test와 가능한 platform build를 CI에서 재현한다.
- 별도 runtime이나 외부 서비스는 만들지 않는다.
- 첫 stacked PR은 잘못된 기술 계약을 Flutter-only로 정정한다.

### U3. Flutter fixture 원장 vertical slice — ZZA-89

- versioned fixture 계좌·거래를 앱에서 선택하고 조회한다.
- observation, economic event와 가역적 사용자 교정을 Dart domain으로 구현한다.
- local-first repository와 persistence 선택을 work evidence에 기록한다.

### U4. 예산과 주·월·연 보고서 — ZZA-90

- 하나의 Dart period engine으로 예산, 남은 예산, 일평균 사용 가능액과 보고서를 계산한다.
- summary와 detail이 같은 fixture generation을 사용함을 테스트한다.

### U5. 연결 신뢰 경계 — ZZA-91

- `complete`, `partial`, `stale`, `reauth-required` 상태와 사용자 행동을 fixture로 제공한다.
- 앱 secure storage와 privacy-safe logging 경계를 검증한다.
- 실제 provider secret, callback과 token exchange는 구현하지 않는다.

### U6. 로컬 삭제 수명주기 — ZZA-92

- 연결 해제, 특정 계좌의 로컬 데이터 삭제와 전체 앱 초기화를 분리한다.
- 재시작 뒤에도 삭제된 fixture 데이터가 복원되지 않음을 검증한다.
- 원격 데이터 삭제는 외부 서비스 결정 뒤 별도 계약으로 다룬다.

### U7. 공식 은행 한 곳 closed beta — ZZA-93

- 공식 provider와 외부 서비스 아키텍처를 사용자가 별도로 승인한 뒤에만 시작한다.
- 승인 전에는 Backlog와 stop condition을 유지한다.

### U8. 세 은행 release candidate — ZZA-94

- U7 승인 경계를 통과한 경우에만 국민·카카오·토스뱅크의 읽기 전용 동작을 검증한다.
- 부분 실패, 재인증, 정합성과 핵심 사용자 과업을 실제 기기에서 검증한다.

### U9. App Store·Google Play 공개 — ZZA-95

- Flutter 앱의 iOS archive와 Android app bundle을 재현한다.
- 개인정보, 접근성, 스토어 메타데이터와 fresh-user smoke를 검증한다.
- 양 스토어 공개와 안정화, KB·Notion·Linear closeout을 완료한다.

## Verification Contract

| Gate | Required evidence |
| --- | --- |
| Flutter source | `dart format --output=none --set-exit-if-changed .` |
| Static analysis | `flutter analyze` |
| Unit/widget | `flutter test` |
| Android | pinned SDK에서 debug/release build |
| iOS | macOS/Xcode 환경에서 simulator 또는 archive build |
| Fixtures | versioned fixture의 결정적 계산과 재실행 불변성 |
| Privacy | credential·token·계좌 원문·금액의 log/trace 유출 0건 |
| Workflow | project-local plan/work, code/doc review, guarded merge와 closeout |

실행할 수 없는 platform 검증은 성공으로 간주하지 않고 work evidence에 원인과 후속
검증 환경을 기록한다.

## Definition of Done

- Flutter/Dart 외 runtime이 사용자 승인 없이 추가되지 않았다.
- Android/iOS에서 동일한 가계부·예산·보고서 계약이 동작한다.
- fixture와 실제 금융 데이터가 화면과 저장 경계에서 명확히 구분된다.
- 송금·결제 capability가 없다.
- 실제 은행 연결은 공식 provider와 외부 서비스 아키텍처 승인 뒤에만 활성화된다.
- 각 티켓의 PR review, KB·Notion·work evidence와 Linear 상태가 동기화된다.

## Sources

- [Flutter application architecture](https://docs.flutter.dev/app-architecture/guide)
- [Flutter testing](https://docs.flutter.dev/testing/overview)
- [Flutter Android release](https://docs.flutter.dev/deployment/android)
- [Flutter iOS release](https://docs.flutter.dev/deployment/ios)
- [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Google Play Data Safety](https://support.google.com/googleplay/android-developer/answer/10787469)
