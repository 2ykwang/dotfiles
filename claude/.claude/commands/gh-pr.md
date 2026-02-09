---
description: GitHub PR을 분석하고 코드 리뷰를 제공합니다 (user)
argument-hint: <pr-number 또는 URL>
allowed-tools: Bash(gh pr:*), Bash(gh api:*)
---

GitHub Pull Request를 분석한다.

## 입력
$ARGUMENTS

## 지시사항

1. **입력 파싱**:
   - URL 형태 (예: `https://github.com/owner/repo/pull/123`)인 경우: owner/repo와 PR 번호를 추출하여 `-R owner/repo` 옵션 사용
   - 숫자만 입력된 경우: 현재 레포 기준으로 실행

2. **데이터 조회**:
   ```bash
   gh pr view <number> [-R owner/repo] --json title,body,state,commits,files,additions,deletions,author,baseRefName,headRefName,createdAt,mergedAt,isDraft,mergeable,comments,reviews
   ```

   변경된 코드 내용 확인:
   ```bash
   gh pr diff <number> [-R owner/repo]
   ```

3. **분석 및 보고**:
   다음 항목을 포함하여 보고한다:

   ### PR 요약
   - 제목, 상태 (open/merged/closed), 작성자
   - 브랜치: `head` → `base`
   - Draft 여부, Mergeable 상태
   - 생성일 (병합된 경우 병합일)

   ### 변경 사항 개요
   - 변경된 파일 수, 추가/삭제 라인 수
   - 파일별 변경 요약
   - 주요 변경 영역 (기능, 테스트, 설정 등)

   ### 커밋 분석
   - 커밋 목록 및 각 커밋의 목적
   - 커밋 메시지 품질

   ### 댓글 및 논의
   - 주요 논의 포인트 요약
   - 리뷰어 피드백 정리
   - 제기된 우려사항이나 질문
   - 합의된 사항 vs 미해결 사항

   ### 코드 리뷰
   - 코드 품질 평가
   - 잠재적 이슈 (버그, 보안, 성능)
   - 개선 제안
   - 테스트 커버리지 관련 의견
