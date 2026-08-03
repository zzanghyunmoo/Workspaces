---
title: 계층형 관리 Neovim 런타임 복구의 소유권과 안전성 경계
date: 2026-08-03
category: architecture-patterns
module: guest-editor-runtime
problem_type: architecture_pattern
component: tooling
severity: high
applies_when:
  - 하나의 관리 런타임을 base action과 확장 action이 계층적으로 소유할 때
  - 사용자 홈 아래 checkout과 생성 설정을 자동 복구하거나 제거할 때
  - 실행할 plugin graph를 lock과 exact revision으로 재현해야 할 때
  - 중단 뒤에도 ownership이 모호한 부분 설치 상태를 남기면 안 될 때
tags: [neovim, nvchad, ownership-boundary, symlink-safety, pinned-plugin-graph, durable-publication]
related_components: [development_workflow]
---

# 계층형 관리 Neovim 런타임 복구의 소유권과 안전성 경계

## Context

관리형 Neovim 환경은 하나의 디렉터리를 한 컴포넌트가 독점하지 않는다. My Desk Setup의
`Editor`는 NvChad와 공통 플러그인 기반을 소유하고, `IDE`는 그 위에 언어 도구 설정과 IDE
전용 플러그인을 추가한다. 구현은 이 경계를 `basePluginSet`과 `idePluginSet`으로 구분한다
(`projects/my-desk-setup/internal/adapters/guest/editor_config.go:22`). 따라서 복구는 원하는 파일
전체를 다시 쓰는 작업이 아니라, 현재 상태가 어느 상위 계층까지 확장되었는지 판별하고 자기
계층만 수리하는 작업이어야 한다.

이 패턴은 [my-desk-setup PR #3](https://github.com/zzanghyunmoo/my-desk-setup/pull/3)에서
`main`에 병합됐다. 현재 구현에서 `Editor`는 base 플러그인 집합만 관찰하고
(`projects/my-desk-setup/internal/adapters/guest/editor.go:111`), `IDE`는 관찰·적용·검증에
전체 IDE 집합을 사용한다(`projects/my-desk-setup/internal/adapters/guest/ide.go:46`).

## Guidance

### 공유 트리의 기반 집합과 상위 집합을 명시한다

`expectedPluginPins`는 base 경계에서는 base 핀만, IDE 경계에서는 전체 핀을 반환한다
(`projects/my-desk-setup/internal/adapters/guest/editor_config.go:251`). 플러그인 디렉터리
검사는 알려진 전체 핀을 허용하되 현재 액션 집합만 필수로 요구한다
(`projects/my-desk-setup/internal/adapters/guest/plugin_tree.go:547`). 이 규칙 덕분에 base
액션은 정상적인 IDE 확장을 오염으로 오판하지 않는다.

```go
func expectedPluginPins(set pluginSet) []pluginPin {
	if set == idePluginSet {
		return pluginPins
	}
	return basePluginPins
}
```

### 하위 계층 복구가 검증된 상위 계층을 덮어쓰지 않게 한다

같은 NvChad revision의 복구에서 `Editor.Apply`는 공통 설정과 base 런타임만 수리한다
(`projects/my-desk-setup/internal/adapters/guest/editor.go:168`). 복구 함수는 플러그인 명세가
정확한 IDE 명세임을 확인하면 생성 경로 lua/plugins/init.lua를 쓰기 대상에서 제외한다
(`projects/my-desk-setup/internal/adapters/guest/editor_config.go:201`). 알 수 없는 명세는
보존하지 않고 관리형 base 명세로 복구한다. 즉, 검증된 상위 상태만 보존하고 임의 drift는
신뢰하지 않는다.

```go
includeIDE, ready, _, err := inspectPluginSpecification(root)
if err != nil || !ready || !includeIDE {
	return writeEditorConfiguration(root)
}
files := make(map[string]string, len(editorConfiguration)-1)
for relativePath, content := range editorConfiguration {
	if relativePath != "lua/plugins/init.lua" {
		files[relativePath] = content
	}
}
return writeConfigurationFiles(root, files)
```

### 마커와 모든 조상 디렉터리를 심볼릭 링크 비추적 방식으로 검사한다

관리 경로는 먼저 root 밖으로 벗어나는지 확인하고, root부터 target까지 각 구성 요소를
`Lstat`으로 검사해 심볼릭 링크나 비디렉터리를 거부한다
(`projects/my-desk-setup/internal/adapters/guest/path_safety.go:11`). 디렉터리를 만들 때도 같은
경계를 적용하며, 소유권 마커는 정규 파일만 허용한다
(`projects/my-desk-setup/internal/adapters/guest/path_safety.go:44`,
`projects/my-desk-setup/internal/adapters/guest/path_safety.go:79`). 런타임 root는 마커 바이트가
기대 스키마와 정확히 같아야 소유된 것으로 인정한다
(`projects/my-desk-setup/internal/adapters/guest/plugin_tree.go:388`).

### 검증에는 PATH 이름이 아니라 검증된 절대 실행기 경로를 사용한다

`managedNeovimExecutable`은 `$HOME/.local/bin/nvim` 절대 경로를 구성하고 조상 디렉터리,
파일 유형과 실행 권한을 확인한다
(`projects/my-desk-setup/internal/adapters/guest/plugin_tree.go:507`). 검증 단계는 그 경로만
사용해 `Lazy! restore`와 `checkhealth`를 실행한다
(`projects/my-desk-setup/internal/adapters/guest/plugin_tree.go:170`). Windows에서는 정규 파일
여부를 검사하되 POSIX 실행 비트는 요구하지 않는다.

### 잠금 파일과 실제 체크아웃 전체를 함께 검증한다

잠금 그래프는 31개 플러그인의 branch와 commit을 생성한다
(`projects/my-desk-setup/internal/adapters/guest/editor_config.go:36`). IDE 검증은 restore 후
검토된 lockfile 바이트를 되돌린 다음 전체 런타임을 다시 관찰한다
(`projects/my-desk-setup/internal/adapters/guest/plugin_tree.go:205`). 최종 관찰은 필수 checkout
누락, 예상 밖 checkout, pinned commit drift를 모두 실패로 처리한다. 31개라는 수량과 각
commit의 40자리 핀은 회귀 테스트의 명시적 계약이다
(`projects/my-desk-setup/tests/adapters/guest_editor_runtime_test.go:746`).

### 런타임 root와 소유권 마커를 하나의 원자적 게시 단위로 만든다

새 root가 필요하면 최종 경로의 부모에 staging 디렉터리를 만들고, 그 안에 마커를 먼저
내구성 있게 기록한 뒤 staging 전체를 게시한다
(`projects/my-desk-setup/internal/adapters/guest/plugin_tree.go:343`). `PublishDirectory`는 staged
tree를 동기화하고 디렉터리를 원자적으로 rename한다
(`projects/my-desk-setup/internal/durable/publication.go:12`). 따라서 최종 root는 “없음” 또는
“유효한 마커를 포함한 관리형 root”로 관찰되며, 중단 뒤 마커 없는 빈 root가 남는 상태를
피한다.

## Why This Matters

- base 복구가 전체 설정을 다시 쓰면 IDE가 소유한 plugin spec을 `return {}`로 낮춰 IDE
  기능을 없앨 수 있다. exact IDE 명세 보존과 액션별 관찰 경계가 이 계층 역전을 막는다.
- 사용자 홈 아래 관리 경로에서 marker나 중간 디렉터리의 symlink를 따라가면 관리 범위 밖
  파일을 읽거나 덮어쓰거나 삭제할 수 있다. 최종 파일뿐 아니라 모든 조상이 신뢰 경계다.
- PATH 이름은 셸과 앞선 PATH 항목에 따라 다른 binary를 선택할 수 있다. 검증된 절대
  launcher를 실행해야 검증 대상과 실제 실행 대상이 일치한다.
- Neovim 명령 성공만으로는 재현성이 증명되지 않는다. 일부 plugin이 빠지거나 moving
  revision이 섞여도 명령은 성공할 수 있으므로 restore 뒤 exact graph를 다시 확인해야 한다.
- root를 먼저 만들고 marker를 나중에 쓰면 중단 시 “존재하지만 소유되지 않은 root”가
  남는다. marker를 완성한 staging directory를 게시하면 이 관찰 가능한 중간 상태를 없앤다.

## When to Apply

- 두 개 이상의 설치 액션이 같은 설정 또는 cache tree를 계층적으로 공유할 때.
- 자동 repair가 다른 컴포넌트 소유 파일이나 plugin을 보존해야 할 때.
- 사용자 쓰기 가능한 home 아래에서 ownership marker를 근거로 수정·삭제·실행할 때.
- 외부 프로세스로 설치 상태를 검증하며 PATH 오염을 차단해야 할 때.
- lockfile의 exact graph가 제품 계약이고 restore가 lockfile이나 checkout을 바꿀 수 있을 때.
- directory 존재가 ownership이나 복구 가능성을 결정해 부분 생성 상태를 허용할 수 없을 때.

각 액션이 완전히 분리된 경로만 소유하고 상위 집합 관계가 없다면 base/IDE 집합 모델은
필요하지 않다. 사용자 제어 경로의 symlink 검사, 절대 실행기 검증과 원자적 게시 원칙은
그 경우에도 유효하다.

## Examples

필수 회귀 검증은 단순히 “repair 후 Ready”만 확인하지 않는다.

- base plugin drift를 수리하기 전후 IDE plugin spec byte가 같은지 검사한다
  (`projects/my-desk-setup/tests/adapters/guest_editor_runtime_test.go:451`).
- IDE 전용 plugin만 drift시켰을 때 `Editor`는 Ready이고 `IDE`만 Absent인지 검사한다
  (`projects/my-desk-setup/tests/adapters/guest_editor_runtime_test.go:507`).
- config/runtime marker와 중간 parent를 외부 경로 symlink로 바꿔도 외부 sentinel이
  보존되는지 검사한다
  (`projects/my-desk-setup/tests/adapters/guest_editor_runtime_test.go:99`).
- lock entry와 실제 checkout 이름 집합이 정확히 같고 모든 commit이 40자리 핀인지 검사한다
  (`projects/my-desk-setup/tests/adapters/guest_editor_runtime_test.go:759`).
- directory publication 후 staging이 사라지고 staged manifest가 destination에 보이는지
  검사한다(`projects/my-desk-setup/internal/durable/publication_test.go:29`). 동기화할 tree의
  symlink 거부는 별도 회귀 테스트가 고정한다
  (`projects/my-desk-setup/internal/durable/publication_test.go:90`).

## Related

- [ZZA-102 work evidence](../../works/2026-08-01-ZZA-102-wsl-nvchad-ide-work.md)
- [ZZA-102 plan](../../plans/2026-08-01-ZZA-102-wsl-nvchad-ide-plan.md)
- [Authoritative blocked generation과 publication 경계](authoritative-blocked-generation-is-not-feasibility-success.md)
- [독립 프로젝트를 standalone repository와 submodule로 운영하는 규칙](../workflow-issues/independent-projects-as-standalone-repos-submodules.md)
