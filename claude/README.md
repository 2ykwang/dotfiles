# Claude Code 설정

dotfiles로 관리하는 Claude Code 설정 및 커스텀 커맨드.

## 구조

```
claude/
├── CLAUDE.md              # 전역 메모리 (개인 설정)
├── settings.json          # Claude Code 설정
├── statusline-command.sh  # 상태바 연동 스크립트
├── commands/              # 커스텀 슬래시 커맨드
│   ├── gh-issue.md        # /gh-issue - GitHub 이슈 분석
│   ├── gh-pr.md           # /gh-pr - PR 분석 및 코드 리뷰
│   ├── gh-review.md       # /gh-review - PR 리뷰 요약
│   └── gh-check-duplicate-issues.md  # /gh-check-duplicate-issues - 중복 이슈 확인
└── README.md
```

## 설치

`setup.sh` 스크립트가 `~/.claude/`에서 이 디렉토리로 심볼릭 링크를 생성한다:

```bash
~/.claude/CLAUDE.md             → dotfiles/claude/CLAUDE.md
~/.claude/settings.json         → dotfiles/claude/settings.json
~/.claude/statusline-command.sh → dotfiles/claude/statusline-command.sh
~/.claude/commands/             → dotfiles/claude/commands/
```

## 커스텀 커맨드

| 커맨드 | 설명 |
|--------|------|
| `/gh-issue <번호\|URL>` | GitHub 이슈 분석 및 요약 |
| `/gh-pr <번호\|URL>` | PR 분석 및 코드 리뷰 제공 |
| `/gh-review <번호\|URL>` | PR 리뷰 코멘트 요약 |
| `/gh-check-duplicate-issues <번호\|URL>` | 중복 이슈 여부 확인 |

## 전역 메모리 (CLAUDE.md)

모든 프로젝트에 적용되는 개인 설정:

- 응답 언어
- 커뮤니케이션 스타일
- 코드 리뷰 선호사항
- 테스트 관행
