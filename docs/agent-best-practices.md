# macinput agent best practices

Language: [English](agent-best-practices.md) | [中文](agent-best-practices.zh-CN.md)

## Core workflow

The safe default loop is:

1. Capture a screenshot.
2. Inspect the screenshot.
3. Perform one atomic action.
4. Capture a new screenshot.
5. Reassess before the next action.

This project is intentionally primitive: it gives the agent control, not perception. The agent must provide the perception and decision-making layer.

## Recommended action policy

### Observe before action

Never click on an unfamiliar screen without first taking a screenshot.

### One mutation at a time

Avoid long speculative chains such as:

- click
- type
- press enter
- click again

Instead, insert a screenshot after each meaningful mutation.

### Revalidate coordinates

Coordinates become stale whenever:

- a window moves
- scrolling occurs
- a dialog opens
- the active Space or monitor changes

### Keep text small

Only type the text needed for the current task step. Large generated text increases the chance of input mistakes and accidental disclosure.

If a focused control does not reliably accept `type_text_input`, switch to `paste_text_input` instead of retrying the same direct typing path.

### Use screenshots as ephemeral artifacts

Read them, use them, then clean them up.

## Failure handling

Stop and reassess when:

- the new screenshot differs from expectation
- the target control is not visible
- an app presents a permission dialog or modal
- keyboard focus is ambiguous

Do not recover by guessing.

## Recommended prompt strategy for host agents

Tell the agent explicitly:

- always take a screenshot before the first action
- always re-screenshot after state changes
- never rely on old coordinates
- never input secrets unless the user explicitly requested it
- stop on uncertainty

The server already provides `ui_action_protocol`, `macinput://overview`, `macinput://best-practices`, and `macinput://permissions`. Hosts should expose these to their planner when possible.
