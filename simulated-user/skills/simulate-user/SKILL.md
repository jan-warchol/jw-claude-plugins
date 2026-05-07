---
name: simulate-user
description: Activate simulation mode for skill evaluation. Pass one or more knowledge file paths as arguments. Example: /simulate-user spec.md constraints.txt
---

You are executing the /simulate-user skill.

The arguments contain one or more file paths (space-separated). These are the knowledge files the simulated user will draw on when answering the main agent's clarifying questions.

Steps:

1. Parse the file paths from the arguments you received.

2. For each path, verify it exists and is readable (use the Read tool). If any path does not exist or cannot be read, report the specific error and stop without writing the config file.

3. Write `.simulate-user-config.json` in the current project directory:
   ```json
   {"knowledge_files": ["<path1>", "<path2>", ...], "log_file": "simulate-user-log.jsonl"}
   ```

4. Inform the user that simulation mode is now active. Include:
   - Which knowledge files were loaded
   - That clarifying questions will be answered by the simulated-user subagent
   - That a Q&A log will be written to `simulate-user-log.jsonl`
   - That to deactivate, they should delete `.simulate-user-config.json`

5. Remind yourself: for the rest of this session, when you need to ask clarifying questions before starting a task, do NOT use AskUserQuestion. Instead, compile all your questions and send them to the simulated-user subagent in a single call:

   Agent(subagent_type="simulated-user", prompt="<all your questions, clearly numbered>")

   The subagent will answer each question. Do not ask the human user anything — all answers come from the simulated user.
