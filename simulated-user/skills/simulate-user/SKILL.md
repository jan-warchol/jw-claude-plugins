---
name: simulate-user
description: Activate simulation mode for skill evaluation. Pass one or more knowledge file paths as arguments. Example: /simulate-user spec.md constraints.txt
---

You are executing the /simulate-user skill.

The arguments contain one or more file paths (space-separated). These are the knowledge files the simulated user will draw on when answering the main agent's clarifying questions.

Steps:

1. Parse the file paths from the arguments you received.

2. Write `.simulate-user-config.json` in the current project directory:
   ```json
   {"knowledge_files": ["<path1>", "<path2>", ...], "log_file": "simulate-user-log.jsonl"}
   ```

4. Inform the user that simulation mode is now active. Include:
   - Which knowledge files were loaded
   - That clarifying questions will be answered by the simulated-user subagent
   - That a Q&A log will be written to `simulate-user-log.jsonl`
   - That to deactivate, they should delete `.simulate-user-config.json`

5. Remind yourself: for the rest of this session, when you need to ask clarifying questions before starting a task, do NOT use AskUserQuestion. Instead, compile all your questions and send them to the simulated-user subagent in a single call:

   Agent(subagent_type="simulated-user:simulated-user", prompt="<your numbered questions>")

   Format each question exactly as you would for AskUserQuestion: include a short question followed by predefined answer options. The simulated user will pick the closest matching option — they will not volunteer free-form information.

   Example prompt:
   ```
   1. What platform should the app target?
      Options: a) Web browsers only  b) Mobile only  c) Both web and mobile  d) Other (please specify)

   2. Should the app support dark mode?
      Options: a) Yes, required  b) Nice to have  c) No
   ```

   Include an "Other (please specify)" or equivalent open option only when the answer space is genuinely open-ended. Send all questions in one call. Do not ask the human user anything — all answers come from the simulated user.
