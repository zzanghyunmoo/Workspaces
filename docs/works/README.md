# Work Evidence

`docs/works/`는 티켓 단위 구현 기록과 Compound Engineering 단계 증빙을 보관한다.
Notion `개발 문서 > 티켓`이 canonical source이며, 로컬 work 문서는 PR·Git·검증에서
참조할 수 있는 동기화 사본이다.

## 파일 규칙

- 경로: `docs/works/<YYYY-MM-DD>-<TICKET>-<topic>-work.md`
- 한 티켓이 여러 PR로 나뉘면 PR마다 work evidence를 하나씩 두고 파일명에 `pr-<number>`를
  포함한다. 각 문서는 단일 `pr_url`과 해당 PR의 review/closeout만 소유한다.
- 시작점: `docs/works/_template.md`
- `ticket_id`, Linear URL, Notion URL, 로컬 ideation/plan 경로를 frontmatter에 기록한다.
- `## 주요 변경 지점`, `## 검증`, `## 외부 동기화`는 placeholder가 아닌 실제 결과를
  담는다.
- 아이디에이션이나 계획을 생략한 긴급 수정은 `waived`와 구체적인 사유를 기록한다.
- 토큰, API key, 내부 host, 개인 로컬 경로는 기록하지 않는다.

## 상태 전이

1. `ce-work` 시작 시 Linear 티켓을 `In Progress`로 바꾸고 `work_status: in_progress`인
   work 문서를 만든다.
2. PR 생성 후 `pr_url`, `ticket_status: In Review`, `work_status: complete`를 반영해 root
   `main`에 먼저 게시한다.
3. PR 최신 head에 대해 `ce-code-review`와 `ce-doc-review`를 실행하고 각각 별도 댓글을
   남긴다.
4. Merge 후 KB와 Notion을 정리하고 `closeout_status: complete`로 갱신한다. 티켓의 마지막
   PR이면 `ticket_completion: complete`, `ticket_status: Done`으로 바꾼다. 후속 PR이 남으면
   `ticket_completion: pending`, `ticket_status: In Review`, `remaining_prs`를 유지한다.

## 리뷰 댓글 marker

리뷰 댓글 마지막에는 PR 최신 head SHA를 포함한 marker를 한 개씩 둔다. Merge를 실행하는
인증 사용자와 같은 GitHub OWNER/MEMBER/COLLABORATOR가 게시한 댓글만 신뢰한다. 새 commit이
push되면 SHA가 달라지므로 두 리뷰를 다시 실행해야 한다.

<!-- markdownlint-disable MD013 -->

```html
<!-- ce-review:v1 type=code ticket=ZZA-123 head_sha=<40-char-sha> verdict=pass -->
```

```html
<!-- ce-review:v1 type=doc ticket=ZZA-123 head_sha=<40-char-sha> verdict=pass -->
```

<!-- markdownlint-enable MD013 -->

각 댓글에는 findings, 검증 범위, blocker 여부를 설명하는 실제 review summary가 있어야 하며
marker만 있는 댓글은 gate를 통과하지 않는다. `verdict=pass`는 blocker를 해결하고 최신
head를 다시 검토한 뒤에만 사용한다. Blocker가
있으면 같은 형식의 `verdict=fail` marker를 남기며, gate는 review type별 최신 trusted
verdict만 인정한다.

## Gate 명령

Gate는 현재 작업 디렉터리의 Git checkout을 검증 대상으로 사용한다. `projects/` 아래의
독립 repository PR을 다룰 때는 반드시 해당 project repository root에서 실행한다. 이렇게
해야 `origin/main`, PR head, `docs/works` evidence와 local closeout debt가 같은 repository를
가리킨다. Windows Git Bash처럼 `python3`가 실행 불가능한 app alias인 환경에서는 정상
Python 3 `python`을 자동 선택하며, 필요하면 `COMPOUND_PYTHON`으로 interpreter를 지정한다.

```bash
# 로컬 work 문서 구조 확인
python3 runbooks/compound_workflow_gate.py validate-work \
  --evidence docs/works/<work-file>.md

# PR merge 전: origin/main의 증빙과 최신-head 리뷰 댓글 확인
python3 runbooks/compound_workflow_gate.py pre-merge \
  --evidence docs/works/<work-file>.md \
  --repo OWNER/REPO \
  --pr NUMBER

# Merge 후 closeout을 local HEAD에서 확인
python3 runbooks/compound_workflow_gate.py closeout \
  --evidence docs/works/<work-file>.md \
  --repo OWNER/REPO \
  --pr NUMBER

# Closeout commit을 push한 뒤 origin/main 반영을 확인하고 로컬 debt 해제
python3 runbooks/compound_workflow_gate.py ack-closeout \
  --repo OWNER/REPO \
  --pr NUMBER
```

Gate는 Linear/Notion URL의 허용 host와 local artifact를 검증하지만 외부 본문·상태를 API로
재검증하지는 않는다. 실제 Linear 상태 전이와 Notion 본문 동기화는 connector 결과를 확인한
에이전트의 attestation이며, URL만 기록해 갱신을 가장해서는 안 된다.

`runbooks/guarded-pr-merge.sh`는 pre-merge gate를 자동 실행하고 merge 성공 시 대상
repository의 local Git config `compound.closeout-*` 항목에 closeout debt를 기록한다.
공용 pre-push hook은 root와 project repository 모두에서 pending closeout이 실제 push 대상
commit에 완성되지 않았으면 다음 push를 차단한다. 이 local debt와 hook은 보조 방어선이므로
`--no-verify`, 다른 clone, GitHub UI를 막지는 못한다. 조직 차원의 강제는 같은 gate를
required check/ruleset으로 승격해야 한다.
