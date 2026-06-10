# CATNIP

**Complexity-Aware Task Navigation and Intelligent Planning**

A Claude Code plugin with a goal of producing better specifications than base Claude Code.

## Installation

First, register the marketplace. Assuming you have SSH authentication configured:

```
/plugin marketplace add git@github.com:jan-warchol/jw-claude-plugins.git
```

Then install the plugin itself:

```
/plugin install catnip@jan-warchol-plugins
```

## Overview

**Problem statement:** plans created by Claude Code are often too verbose, and yet they can miss
important sections (assumptions, risks, verifiable criteria, etc.) or fail to clarify crucial
design decisions with the user.

**What doesn’t work:** Simply listing everything that should be included will result in bloated
plans. Similarly, instructing the agent to
[“ask questions until a common understanding is reached”](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md)
is overkill (too many questions).

**Constraints:**

- The plugin cannot be too rigid \- models will get smarter, so enforcing a strict structure would
  backfire (holding future agents back)
- Size limit: I hope to get the complete solution (skill instructions \+ accompanying hooks)
  within 2000 lines, preferably much less (3000 _words_).
