---
description: Analyze and summarize a GitHub Issue
argument-hint: <issue-number or URL>
allowed-tools: Bash(gh issue:*)
---

Analyze the GitHub Issue.

## Input
$ARGUMENTS

## Instructions

1. **Parse Input**:
   - If URL format (e.g., `https://github.com/owner/repo/issues/123`): extract owner/repo and issue number, use `-R owner/repo` option
   - If only a number: run against the current repository

2. **Fetch Data**:
   ```bash
   gh issue view <number> [-R owner/repo] --json title,body,state,labels,comments,author,createdAt,assignees,milestone
   ```

3. **Analyze and Report**:
   Include the following sections:

   ### Issue Summary
   - Title, state (open/closed), author, created date
   - Labels and milestone
   - Assignees

   ### Problem Analysis
   - Core issue summary
   - Reproduction steps or environment info (if available)
   - Related code or error messages (if available)

   ### Comments Summary
   - Key discussion points
   - Proposed solutions
   - Progress status

   ### Suggested Approach
   - Possible resolution strategies
   - Considerations and caveats
