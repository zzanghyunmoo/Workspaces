# Knowledge Base

`docs/kb/`는 merge된 기능의 **현재 동작과 운영 사실**을 티켓에서 분리해 찾을 수 있게
정리하는 로컬 knowledge base다. Notion `디자인 문서 > 기능 현황`과 티켓별 결과 문서가
canonical source이며, 로컬 KB는 merge commit과 canonical 링크를 가진 동기화 사본이다.

## `docs/solutions/`와의 경계

- `docs/kb/`: merge 후 확인된 기능 상태, 사용법, 운영 경계, 현재 제한.
- `docs/solutions/`: 문제를 해결하며 얻은 재사용 가능한 원인·해결법·워크플로 학습.

같은 내용을 복제하지 않는다. 기능의 현재 모습은 KB에, 다시 발생할 문제를 빠르게 해결하는
지식은 solution에 두고 서로 링크한다.

## 파일 규칙

- 경로: `docs/kb/<category>/<YYYY-MM-DD>-<TICKET>-<topic>.md`
- 시작점: `docs/kb/_template.md`
- merge된 PR과 commit, work evidence, Notion 기능 현황, Notion 티켓 문서를 연결한다.
- 코드에서 확인한 현재 동작과 실제 검증 결과만 기록한다.
- 계획이나 미구현 목표는 현재 기능처럼 쓰지 않는다.

`runbooks/compound_workflow_gate.py closeout`은 work evidence의 `kb_paths`가 실제
`docs/kb/` Markdown 문서를 가리키는지, local `HEAD`에 commit됐는지, 필수 frontmatter와
현재 상태·경계·검증·운영 섹션이 work evidence와 일치하는지 확인한다.
