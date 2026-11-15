# dotfiles 작업 지침

- `claude/.claude/CLAUDE.md`는 Codex 전역 지침으로도 쓰인다(`codex/.codex/AGENTS.md` 심링크). `@import`처럼 Codex가 해석하지 못하는 문법을 넣지 않는다.
- 언어별 규칙은 `claude/.claude/rules/<언어>.md`에 `paths` frontmatter와 함께 둔다. Codex는 CLAUDE.md `## 코드`의 안내를 보고 직접 읽는다.
- 특정 요청에서만 필요한 절차는 `agents/.agents/skills/<name>/SKILL.md`에 스킬로 두고, `claude/.claude/skills/<name>`에 상대 심링크를 추가한다.
- 에이전트 지침에는 반복 적용할 고정 규칙만 둔다. 조사와 실험 기록은 두지 않는다.
- 지침은 단언형 한두 줄로 쓴다. 경위와 배경 설명은 쓰지 않는다.
