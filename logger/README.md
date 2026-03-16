Unfortunately, `PermissionRequest` event in Claude Code does not include the
most interesting piece of information - reason why it was triggered. I usually
log this information manually using a helper function, that captures some extra
metadata that makes it easier to combine that information with event log:

```
log_stuff() {
  file="$1"
  echo "____________________________________________________________" >> "$file"
  echo "timestamp: $(date +%s)" >> "$file"
  echo "cwd: $PWD" >> "$file"
  echo >> "$file"
  cat - >> "$file"
  echo >> "$file"
}

alias plog='log_stuff .permission-prompts.log'
```
