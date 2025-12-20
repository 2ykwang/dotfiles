---
description: Check if an issue is a duplicate and find related issues/PRs
argument-hint: <issue-number or GitHub URL>
allowed-tools: Bash(gh issue:*), Bash(gh search:*), Bash(gh pr:*), Bash(gh api:*), Bash(gh repo:*)
---

이슈 $ARGUMENTS를 분석하여 중복 여부와 관련 이슈/PR을 찾는다.

**입력 형식**: 이슈 번호(예: `749`) 또는 GitHub URL(예: `https://github.com/owner/repo/issues/749`)
- URL인 경우: URL에서 `owner/repo`를 추출하여 `--repo` 플래그에 사용
- 번호만 있는 경우: 현재 레포 기준 (`gh repo view --json nameWithOwner -q .nameWithOwner`)

## Step 1: 현재 이슈 상세 확인

`gh issue view $ARGUMENTS --json number,title,body,labels,author,createdAt,comments`
- URL이면 그대로 사용, 번호면 `--repo {owner/repo}` 추가

- 제목과 본문에서 핵심 키워드 추출
- 댓글에서 이미 진행 중인 논의, 언급된 관련 이슈/PR 확인
- 이슈 종류 파악 (버그 리포트 / 기능 요청 / 질문 / 기타)
- 에러 메시지, 스택 트레이스, 특정 파일명 등 구체적인 정보 메모

## Step 2: 다각도 검색 전략

단일 검색으로는 부족하므로 여러 방식으로 검색한다:

### 2-1. 키워드 기반 검색 (최소 2-3개 변형)

`--repo {owner/repo}` 부분은 URL에서 추출했거나 현재 레포 사용.

```bash
gh search issues "<원본 키워드>" --repo {owner/repo} --limit 20
gh search issues "<동의어 키워드>" --repo {owner/repo} --limit 20
gh search issues "<에러코드 또는 파일명>" --repo {owner/repo} --limit 15
```

예시:
- 원본: "login fails" → 동의어: "authentication error", "sign in broken"
- 원본: "500 error" → 관련어: "internal server error", "server crash"

### 2-2. PR도 검색
```bash
gh search prs "<키워드>" --repo {owner/repo} --limit 15
```

### 2-3. 라벨 기반 검색 (라벨이 있는 경우)
```bash
gh issue list --label "<관련 라벨>" --state all --limit 20 --json number,title,state --repo {owner/repo}
```

### 2-4. 크로스 레퍼런스 확인
```bash
gh api repos/{owner}/{repo}/issues/{issue-number}/timeline --jq '.[] | select(.event == "cross-referenced")'
```

## Step 3: 후보 이슈 상세 분석

검색 결과에서 유사해 보이는 이슈들(최소 상위 5-10개)을 `gh issue view <번호> --repo {owner/repo} --json number,title,body,state,comments`로 상세 확인:

- 단순히 제목만 비슷한 것인지, 실제 내용도 같은 문제인지 판단
- 같은 root cause를 가리키는지 확인
- 이미 해결되었는지 (closed 상태 + 해결 코멘트) 확인
- 댓글에서 해결책 논의, 관련 PR 언급 여부 확인

## Step 4: 중복 판단 기준

다음 중 하나라도 해당하면 **중복**으로 판단:

| 기준 | 예시 |
|------|------|
| 같은 버그/에러 | 같은 에러 메시지, 같은 재현 조건 |
| 같은 기능 요청 | 워딩은 다르지만 원하는 기능이 동일 |
| 같은 질문 | 다르게 물어봤지만 같은 내용을 묻고 있음 |
| 같은 root cause | 증상은 다르게 보고되었지만 원인이 같음 |

**중복 아님** 판단 기준:
- 비슷한 영역이지만 다른 구체적 문제
- 같은 기능에 대한 다른 관점의 요청
- 이전 이슈가 해결되었고, 이번에는 regression인 경우

## Step 5: 결과 출력

**URL 형식**:
- 이슈: `https://github.com/{owner}/{repo}/issues/{number}`
- PR: `https://github.com/{owner}/{repo}/pull/{number}`

### 중복 발견 시
```
중복 이슈 발견

원본 이슈: #123 - "제목"
상태: Open / Closed
링크: https://github.com/{owner}/{repo}/issues/123
유사도 근거:
  - 같은 에러 메시지 "XXX" 보고
  - 동일한 재현 조건 (A 후 B 수행 시 발생)
  - 같은 컴포넌트(파일) 관련

권장 액션:
  - 이 이슈에 "#123 과 중복입니다" 코멘트 추가
  - duplicate 라벨 추가
  - 이슈 닫기 고려
```

### 관련 이슈/PR 발견 시 (중복은 아니지만 연관됨)
```
관련 항목 발견

관련 이슈:
  - #456 - "제목" (관련성: 같은 모듈 관련 다른 버그)
    - https://github.com/{owner}/{repo}/issues/456
  - #789 - "제목" (관련성: 비슷한 기능 요청이지만 스코프 다름)
    - https://github.com/{owner}/{repo}/issues/789

관련 PR:
  - #101 - "제목" (상태: Open, 이 이슈와 관련된 수정 진행 중)
    - https://github.com/{owner}/{repo}/pull/101
  - #102 - "제목" (상태: Merged, 참고할만한 이전 수정)
    - https://github.com/{owner}/{repo}/pull/102
```

### 중복/관련 없음
```
중복 없음

검색 요약:
  - 검색된 이슈 수: N개
  - 상세 확인한 이슈: M개
  - 판단: 새로운 이슈로 보임

추천 라벨: bug / feature-request / question / 등
```

## 추가 액션 (선택)

중복 발견 시 댓글 제안:
- 이슈 링크 출력
- 제안 댓글 텍스트: "이 이슈는 #원본번호 와 중복으로 보입니다. 해당 이슈를 참고해주세요."
