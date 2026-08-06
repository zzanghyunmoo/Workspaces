---
title: "ZZA-104 OMH MDS runtime identity composition"
ticket: ZZA-104
component: oh-my-harness
status: merged
pr: https://github.com/zzanghyunmoo/oh-my-harness/pull/40
merge_commit: d30e42113c0a589d11f8505b4afff55c643e62ed
---

# OMH MDS runtime identity composition

`mds-host`는 MDS가 선택·검증한 runtime identity의 executable digest와 trusted PATH 실행 파일의 bytes를 대조한다. 일치하면 OMH catalog의 runtime version pin이 다르더라도 runtime을 재설치하지 않고 workflow와 native plugin/add-on만 합성한다.

이 digest는 `verify-agent` action까지 유지돼 preview와 apply가 서로 다른 runtime identity를 검증하지 않는다. unsupported platform과 duplicate identity는 fail-closed이며 personal/company profile의 runtime acquisition 정책은 변경하지 않는다.

검증은 macOS, Ubuntu, Windows GitHub Actions와 `npm run test:contracts`, focused MDS host contract test로 수행했다. 현재 local integration suite의 `zod` lock mismatch는 이번 PR과 무관한 설치 drift로 분리했다.
