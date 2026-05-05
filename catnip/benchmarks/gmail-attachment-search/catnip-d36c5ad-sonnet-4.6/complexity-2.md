---
goal: Python script to find last 3 Gmail emails with attachments
prompt: Create a simple Python script that searches Gmail for emails matching a user-provided query, then returns the last 3 matching emails that have attachments.
complexity: 2
---

## Plan

Use the Gmail MCP tools already available in this session to search for emails matching the user's query, filter those with attachments, and return the 3 most recent.

### Success criteria

- Script accepts a query string from the user (CLI arg or prompt)
- Searches Gmail using the query and filters results to only those with attachments
- Returns details (subject, sender, date) of the last 3 matching emails with attachments
