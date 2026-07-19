---
name: brew-update
description: 로컬에 설치된 Homebrew 패키지와 이 레포의 Brewfile을 비교하고 동기화한다. 사용자가 "brew 동기화", "Brewfile 정리", "Brewfile 업데이트"를 언급하거나, 패키지를 설치·삭제한 뒤 Brewfile에 반영하려 할 때 사용한다.
allowed-tools: Read, Edit, Bash(brew:*), Bash(bash .claude/skills/brew-update/scripts/brewfile-diff.sh:*)
---

# Brewfile 동기화

설치 상태 수집과 diff 계산은 스크립트가 결정적으로 처리한다.
이 문서는 그 결과를 어떻게 판단하고 Brewfile에 반영할지만 다룬다.

## 1. diff 실행

```bash
bash .claude/skills/brew-update/scripts/brewfile-diff.sh
```

- 출력은 `type name` 라인이 `== ADD ==` / `== REMOVE ==` 두 섹션으로 나뉜다.
- 두 섹션 모두 비어 있으면 "동기화 상태"라고 보고하고 종료한다.
- npm 항목은 비교 대상이 아니다 — 이 머신은 글로벌 패키지를 pnpm으로 설치해서
  `brew bundle dump`가 감지하지 못한다. npm 라인은 수동 관리한다.

## 2. 판단 후 사용자 확인

결과를 유형별 표로 정리해 보여주고, 어떤 항목을 반영할지 확인받는다.
diff는 사실이지만 전부 반영 대상은 아니다:

- `homebrew/*` 기본 탭(core, cask, bundle, services)은 자동 관리되므로 추가를 제안하지 않는다.
- 다른 패키지의 의존성으로 깔린 것으로 보이는 formula(예: expat, pkgconf)는
  `brew uses --installed <name>`으로 확인하고, 의존성이면 추가를 제안하지 않는다.
- REMOVE 후보에 부트스트랩 필수 패키지(git, gh, stow, just)가 있으면
  삭제 시 재설치가 깨진다는 경고를 붙인다.
- mas 항목은 App Store 로그인에 의존하므로 별도로 표시한다.

## 3. Brewfile 반영

승인된 항목만 수정한다:

- 기존 섹션 구조(CLI tools, Dev tools, Productivity 등)와 정렬 순서를 유지한다.
- 새 패키지는 알맞은 섹션에 넣고, 기존 스타일대로 정렬 맞춘 `# 한 줄 설명` 주석을 붙인다.
- 승인되지 않은 라인은 건드리지 않는다.

## 4. 검증

스크립트를 재실행해서 승인된 항목이 diff에서 사라졌는지 확인한다.
남아 있는 항목은 사용자가 반영하지 않기로 한 것과 일치해야 한다.
