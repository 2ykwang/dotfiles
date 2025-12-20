---
description: Analyze a GitHub PR and provide code review
argument-hint: <pr-number or URL>
allowed-tools: Bash(gh pr:*), Bash(gh api:*)
---

Analyze the GitHub Pull Request.

## Input
$ARGUMENTS

## Instructions

1. **Parse Input**:
   - If URL format (e.g., `https://github.com/owner/repo/pull/123`): extract owner/repo and PR number, use `-R owner/repo` option
   - If only a number: run against the current repository

2. **Fetch Data**:
   ```bash
   gh pr view <number> [-R owner/repo] --json title,body,state,commits,files,additions,deletions,author,baseRefName,headRefName,createdAt,mergedAt,isDraft,mergeable,comments,reviews
   ```

   To view the changed code:
   ```bash
   gh pr diff <number> [-R owner/repo]
   ```

3. **Analyze and Report**:
   Include the following sections:

   ### PR Summary
   - Title, state (open/merged/closed), author
   - Branch: `head` → `base`
   - Draft status, mergeable state
   - Created date (merge date if merged)

   ### Changes Overview
   - Number of files changed, lines added/deleted
   - Summary of changes per file
   - Main areas affected (features, tests, config, etc.)

   ### Commit Analysis
   - List of commits and their purposes
   - Commit message quality

   ### Comments and Discussion
   - Summary of key discussion points
   - Reviewer feedback summary
   - Raised concerns or questions
   - Agreed items vs. unresolved items

   ### Code Review
   - Code quality assessment
   - Potential issues (bugs, security, performance)
   - Improvement suggestions
   - Test coverage observations
