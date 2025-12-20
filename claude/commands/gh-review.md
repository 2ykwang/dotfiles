---
description: GitHub PR의 리뷰 내용을 요약합니다 (user)
argument-hint: <pr-number 또는 URL>
allowed-tools: Bash(gh pr:*), Bash(gh api:*)
---

GitHub Pull Request의 리뷰를 요약한다.

## 입력
$ARGUMENTS

## 지시사항

1. **입력 파싱**:
   - URL 형태 (예: `https://github.com/owner/repo/pull/123`)인 경우: owner/repo와 PR 번호를 추출하여 `-R owner/repo` 옵션 사용
   - 숫자만 입력된 경우: 현재 레포 기준으로 실행

2. **데이터 조회**:
   ```bash
   gh pr view <number> [-R owner/repo] --json reviews,comments,reviewDecision,reviewRequests,title,state
   ```

   상세 리뷰 코멘트:
   ```bash
   gh api repos/{owner}/{repo}/pulls/{number}/comments
   ```

3. **분석 및 보고**:
   다음 항목을 포함하여 보고한다:

   ### PR 현황
   - 제목, 상태
   - 리뷰 결정 (APPROVED, CHANGES_REQUESTED, REVIEW_REQUIRED 등)
   - 요청된 리뷰어 목록

   ### 리뷰어별 피드백
   각 리뷰어에 대해:
   - 리뷰 상태 (승인/변경 요청/코멘트)
   - 주요 피드백 내용 요약

   ### 주요 논의 포인트
   - 반복적으로 언급된 이슈
   - 중요한 설계/구현 논의
   - 합의된 사항과 미합의 사항

   ### 미해결 코멘트
   - 아직 해결되지 않은 리뷰 코멘트 목록
   - 각 코멘트의 핵심 내용

   ### 권장 액션
   - PR 병합 전 해결해야 할 사항
   - 우선순위별 정리
