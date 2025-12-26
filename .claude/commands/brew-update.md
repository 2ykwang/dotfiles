---
description: 로컬 Homebrew 패키지와 Brewfile을 동기화합니다
allowed-tools: Bash(brew *), Read, Edit
---

로컬 머신에 설치된 Homebrew 패키지와 Git 레포의 Brewfile을 비교하여 동기화한다.

## 지시사항

1. **현재 상태 확인**:
   ```bash
   # 현재 설치된 패키지 목록 생성
   brew bundle dump --file=/tmp/current_brewfile --force
   ```

2. **Brewfile 읽기**:
   - dotfiles 레포의 Brewfile 경로: `$ARGUMENTS` (없으면 현재 디렉터리의 Brewfile)
   - `/tmp/current_brewfile`과 기존 Brewfile 비교

3. **차이점 분석**:
   - 새로 설치된 패키지 (로컬에만 있는 것)
   - 삭제된 패키지 (Brewfile에만 있는 것)
   - 각 패키지 유형별로 분류 (tap, brew, cask)

4. **결과 보고**:
   다음 형식으로 보고한다:

   ### 새로 추가된 패키지
   | 유형 | 패키지 | 추가 여부 |
   |------|--------|----------|
   | brew | package-name | 추가 권장 |

   ### 삭제된 패키지
   | 유형 | 패키지 | 삭제 여부 |
   |------|--------|----------|
   | cask | old-app | 삭제 권장 |

5. **사용자 확인 후 업데이트**:
   - 사용자에게 어떤 변경사항을 적용할지 확인
   - 승인된 변경사항만 Brewfile에 반영
   - 기존 Brewfile의 주석과 섹션 구조를 유지
   - 새 패키지는 적절한 섹션에 배치하고 간단한 주석 추가

## 주의사항

- mas (Mac App Store) 패키지는 별도로 표시
- 기존 Brewfile의 정렬 순서와 주석 스타일 유지
- 시스템 필수 패키지(git, gh 등)는 삭제하지 않도록 경고
