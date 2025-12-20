---
description: Summarize review comments on a GitHub PR
argument-hint: <pr-number or URL>
allowed-tools: Bash(gh pr:*), Bash(gh api:*)
---

Summarize the GitHub Pull Request reviews.

## Input
$ARGUMENTS

## Instructions

1. **Parse Input**:
   - If URL format (e.g., `https://github.com/owner/repo/pull/123`): extract owner/repo and PR number, use `-R owner/repo` option
   - If only a number: run against the current repository

2. **Fetch Data**:
   ```bash
   gh pr view <number> [-R owner/repo] --json reviews,comments,reviewDecision,reviewRequests,title,state
   ```

   For detailed review comments:
   ```bash
   gh api repos/{owner}/{repo}/pulls/{number}/comments
   ```

3. **Analyze and Report**:
   Include the following sections:

   ### PR Status
   - Title, state
   - Review decision (APPROVED, CHANGES_REQUESTED, REVIEW_REQUIRED, etc.)
   - Requested reviewers list

   ### Feedback by Reviewer
   For each reviewer:
   - Review status (approved/changes requested/commented)
   - Summary of key feedback

   ### Key Discussion Points
   - Repeatedly mentioned issues
   - Important design/implementation discussions
   - Agreed items vs. unresolved items

   ### Unresolved Comments
   - List of unresolved review comments
   - Core content of each comment

   ### Recommended Actions
   - Items to resolve before merging
   - Prioritized list
