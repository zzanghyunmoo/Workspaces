---
title: Private knowledge publishing runbook
last_verified: 2026-08-24
---

# Private knowledge publishing

개인 노트는 공개 `zWorkspaces`와 블로그 checkout 밖의 별도 PRIVATE repository에 둔다.
공개 저장소에는 private remote URL, local path, symlink, submodule 또는 자동 content loader를
추가하지 않는다.

## Private vault 준비

같은 이름의 repository가 있으면 새로 만들지 말고 owner와 visibility를 확인한다. 없으면
GitHub에서 빈 PRIVATE repository를 먼저 만든다. 실제 remote 생성과 최초 `main` push는 사용자
승인 대상이므로 승인 packet 없이 실행하지 않는다.

```sh
gh repo view zzanghyunmoo/notes-private --json nameWithOwner,visibility
```

`visibility`가 정확히 `PRIVATE`인 것을 확인한 뒤 공개 workspace 밖에 clone한다. 평범한 폴더를
먼저 만들고 나중에 Git repository로 바꾸지 않는다.

```sh
PUBLIC_WORKSPACE_ROOT="<public-workspace-root>"
PRIVATE_NOTES_ROOT="<private-notes-root>"
git clone git@github.com:zzanghyunmoo/notes-private.git "$PRIVATE_NOTES_ROOT"
python3 "$PUBLIC_WORKSPACE_ROOT/runbooks/check_publication_candidate.py" \
  verify-private-boundary \
  --public-root "$PUBLIC_WORKSPACE_ROOT" \
  --private-root "$PRIVATE_NOTES_ROOT"
"$PUBLIC_WORKSPACE_ROOT/runbooks/install-main-guard-hooks.sh" \
  --repo "$PRIVATE_NOTES_ROOT"
```

Vault의 기본 제외 대상은 `.obsidian/workspace*`, `.trash/`, OS 임시 파일, `.env*`, credential과
secret 파일이다. private 원문과 local 경로는 public Issue, PR, work evidence 또는 실행 로그에
복사하지 않는다.

최초 push 승인 뒤에도 실제 push 직전에 `gh repo view ... --json visibility`를 다시 실행하고
`PRIVATE`가 아니면 중단한다. 오래전에 확인한 visibility를 그대로 신뢰하지 않는다.

## 공개 후보 규칙

공개 후보는 한 개 Markdown 문서로 준비하고 AstroPaper frontmatter와 표준 Markdown 링크로
정규화한다. 다음 항목은 거부된다.

- Obsidian wikilink/embed와 block reference
- `/Users/...`, `/home/...`, `file://`, `obsidian://` 같은 private local path
- private key, GitHub/AWS/Slack token, password/secret 형태의 값
- 상대 경로 image/file attachment와 신규 binary blob
- private vault에 둔 고유 canary

Binary asset 승격은 현재 자동 허용하지 않는다. 필요한 경우 metadata 제거와 별도 공개 검토
계약을 먼저 추가한다.

## 첫 public push 전 검사

Canary는 command line 인자로 넘기거나 출력하지 않고 현재 shell 환경에 주입한다. Wrapper는
candidate뿐 아니라 base 이후 모든 신규 commit message와 reachable blob을 검사하므로, secret을
commit한 뒤 HEAD에서 지운 history도 거부한다. Build 출력은 공개 로그에 private 내용이 섞이지
않도록 wrapper 내부에서 폐기하며 `dist`와 Pagefind 결과를 다시 검사한다.

```sh
read -r -s PUBLICATION_CANARY
export PUBLICATION_CANARY

git -C blogs fetch --quiet --no-tags origin \
  +refs/heads/v4:refs/remotes/origin/v4
blog_remote="$(git -C blogs remote get-url origin)"
blog_base="$(git -C blogs rev-parse origin/v4)"
blog_head="$(git -C blogs rev-parse HEAD)"
# 사용자에게 remote, branch, head, 공개 diff와 검사 계획을 제시하고 승인받은 뒤에만 설정한다.
export PUBLICATION_PUSH_APPROVED=1
export PUBLICATION_PUSH_APPROVED_REMOTE="$blog_remote"
export PUBLICATION_PUSH_APPROVED_BRANCH=feat/publish-note
export PUBLICATION_PUSH_APPROVED_BASE="$blog_base"
export PUBLICATION_PUSH_APPROVED_HEAD="$blog_head"
export PUBLICATION_PUSH_APPROVED_CANDIDATE=src/data/blog/public-note.md

runbooks/guarded-publication-push.sh \
  --repo blogs \
  --candidate src/data/blog/public-note.md \
  --base-branch v4 \
  --remote origin \
  --branch feat/publish-note \
  --expected-remote "$blog_remote"
```

Wrapper는 public base branch를 remote에서 다시 받아 SHA로 고정한다. Clean working tree,
exact remote/branch/base/HEAD/candidate approval, candidate만 바뀐 history, candidate/history 검사,
public build, 고정된 `dist`/Pagefind 검사 순서가 모두 통과한 경우에만 정확한 HEAD SHA를
push한다. 실패 메시지는 위반 category만 표시하며 private 본문, path, canary 또는 token 값을
출력하지 않는다. Public build는 기본 300초 뒤 전체 process group을 종료하며, 필요한 경우
승인된 실행에서만 `PUBLICATION_BUILD_TIMEOUT_SEC`로 제한을 조정한다.

승인 없이 일반 `git push`를 실행하지 않는다. Private note와 무관한 기존 공개 글·코드 변경은
이 wrapper의 대상이 아니며 블로그의 기존 branch/PR 가드레일을 따른다.
