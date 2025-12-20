---
description: GitHub Issue를 분석하고 요약합니다 (user)
argument-hint: <issue-number 또는 URL>
allowed-tools: Bash(gh issue:*)
---

GitHub Issue를 분석한다.

## 입력
$ARGUMENTS

## 지시사항

1. **입력 파싱**:
   - URL 형태 (예: `https://github.com/owner/repo/issues/123`)인 경우: owner/repo와 이슈 번호를 추출하여 `-R owner/repo` 옵션 사용
   - 숫자만 입력된 경우: 현재 레포 기준으로 실행

2. **데이터 조회**:
   ```bash
   gh issue view <number> [-R owner/repo] --json title,body,state,labels,comments,author,createdAt,assignees,milestone
   ```

3. **분석 및 보고**:
   다음 항목을 포함하여 보고한다:

   ### 이슈 요약
   - 제목, 상태 (open/closed), 작성자, 생성일
   - 라벨 및 마일스톤
   - 담당자

   ### 문제 분석
   - 이슈의 핵심 내용 요약
   - 재현 조건이나 환경 정보 (있는 경우)
   - 관련 코드나 에러 메시지 (있는 경우)

   ### 댓글 요약
   - 주요 논의 포인트
   - 제안된 해결책
   - 진행 상황

   ### 해결 방향 제안
   - 가능한 해결 접근법
   - 고려해야 할 사항
