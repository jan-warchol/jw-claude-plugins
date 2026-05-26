---
name: iterative-spec-writing
description: >
  Write a spec through an iterative workflow.
  Stores all intermediate files in .catnip/<timestamp>-<slug>/ in the project directory.
---

Orchestrate iterative spec writing for a user request.

## Required inputs

Collect before proceeding:

- **request**: the user's request (ask if not provided as skill argument)

## Setup

1. Choose a 3–8 word slug from the request: lowercase words joined with hyphens
   (e.g. `oauth-token-refresh`).
2. Create the process directory:
   ```
   .catnip/<YYYYMMDDTHHMMSS>-<slug>/
   ```
   where the timestamp is the current local time in `YYYYMMDDTHHMMSS` format.
3. Write `metadata.json` in that directory:
   ```json
   {
     "user_request": "<user request copied verbatim>",
   }
   ```

## Preparing tasks

After setup is ready, prepare tasks for running workflow steps using TaskCreate tool. Prepare following tasks:

```json
 {
  "subject": "Prepare draft",
  "description": "Run skill: `/catnip:01-draft-spec <process directory path> <user request>`.",
  "metadata": {
     "slug": <slug>,
     "user_request": <user request>,
     "process_dir": <process directory path> 
  }
};
```

```json
 {
  "subject": "Prepare draft",
  "description": "Run skill: `/catnip:02-enrich-spec <process directory path>`.",
  "metadata": {
     "slug": <slug>,
     "process_dir": <process directory path> 
  }
};
```

```json
 {
  "subject": "Prepare draft",
  "description": "Run skill: `/catnip:03-reorganize-spec <process directory path>`.",
  "metadata": {
     "slug": <slug>,
     "process_dir": <process directory path> 
  }
};
```

```json
 {
  "subject": "Prepare draft",
  "description": "Run skill: `/catnip:04-compress-spec <process directory path>`.",
  "metadata": {
     "slug": <slug>,
     "process_dir": <process directory path> 
  }
};
```

```json
 {
  "subject": "Wrap up the spec",
  "description": "Run skill: `/catnip:05-wrap-up-spec <process directory path>`.",
  "metadata": {
     "slug": <slug>,
     "process_dir": <process directory path> 
  }
};
```

## Start working on the tasks

Execute tasks one by one in the specified order. The tasks and dedicated skills contain all the necessary information.

Focus on each of the tasks separately - trust the process.
