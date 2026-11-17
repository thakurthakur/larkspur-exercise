# Client review: Larkspur disruption-care agent

**To:** Room 14  
**From:** Larkspur client review agent, on behalf of Priya Raghavan  
**Re:** the disruption-care agent you walked us through in our last session  
**Generated:** 2026-11-17 10:07

## Priya's note

> Our vendor says we should just be using your best model.
>
> Why aren't we?
>
> Priya Raghavan, Larkspur Airlines

She sent that before this session opened. She means it. A vendor told her to buy
the biggest model, and she has a number to defend upstairs. Her four questions from
day one are still open. Naming a model answers none of them.

## Still open from day one

| Her question | What she means by it |
| --- | --- |
| **What it costs** | Per resolved contact, against the $6.90 a human contact costs us. |
| **When it is wrong** | The first untrue thing it says, and what happens after that. |
| **Who runs it** | In June, after you have left. |
| **What you left out** | The scope you cut, and why. |

## What the review agent found

Larkspur pointed a review agent at your repository. It read the
code. It did not run your agent, and the only file it changed is this one. Each
item below names the file and the line it is about.

**1. agent.py seats_left: the tool description runs 1822 characters and the other nine run 71 to 445.**

The pod's EXTRA_TOOLS entry for seats_left is more than four times as long as check_policy at 445 characters. It spells out error strings, party-size comparison and when not to call it versus get_flight_status and search_alternatives. The 13079 input tokens in readout-trace.json are re-sent on every one of 4 API turns, and nobody has measured what this one description adds to each.

Run python3 run.py --tool-tax and paste the per-tool token breakdown.

**2. agent.py hold_seat and send_confirmation descriptions are 73 and 71 characters and the pod's diff does not touch them.**

hold_seat reads "Place a 15-minute hold on one alternative. Reversible. It simply expires." It says nothing about which tool produces the option_id it requires. The diff rewrote search_alternatives and get_flight_status and added seats_left, and left these two as they shipped. The committed run called lookup_booking, get_flight_status and check_policy only, so neither tool has been exercised on the wire.

Run python3 run.py --all --trace and paste the totals footer plus the tool order for any booking that reaches hold_seat.

**3. agent.py run_agent: the diff changed the loop to append response.content and return text_of(response) after the loop ends.**

The shipped loop appended text_of(response) as the assistant turn and kept an answer variable from the previous turn. Yours appends the full content blocks, which is what thinking={"type": "adaptive"} needs to carry through tool_use turns. readout-trace.json shows thinking seen on the wire: True across 4 turns, 3 tool calls, and the stop at MAX_TOOL_CALLS = 8 has not been hit. You can claim a multi-turn loop that completes, on one booking.

Run python3 run.py --all --trace and paste the totals footer so the loop is shown on more than one booking shape.

**4. readout-trace.json shows prompt caching at 0 read, 0 written, and agent.py contains no cache_control.**

The committed run sent 13079 tokens in over 4 API turns with hit ratio None. A bigger model would be billed on those same uncached tokens at a higher rate. Priya's question about model choice has no baseline yet because no before and after exists. PITCH.md has no Number line and no Lever filled in.

Run python3 bench.py --label before --stage 1 --runs 3, then python3 bench.py --compare before after after the change, and paste the compare output.

**5. TONE_ADDENDUM in agent.py is 0 characters and there is no evals/cases.json, so no case in this repo tests the agent's behavior.**

Banked gates in readout.html are 1.2, 1.3, 1.4 only. Nothing under 2.x, 3.1 or 4.1 is banked, and the seats_left tool added in your diff has no gate behind it. Several given files, including verify.py, eval_harness.py and bench.py, differ from the shipped pack, so a number from them needs the diff behind it before it is quoted.

Run python3 verify.py 2.1 and paste its output, and list which given files you edited and why.

## Your four answers

The four lines under `## Priya asked` in your PITCH.md are still empty. They
are one line each and they are not a coding job: cost, what happens when it is
wrong, who runs it in June, and what you left out. Whoever on your side is not
editing agent.py is the right person to write them, and they are the four
things I will ask about first.

## Before our next meeting

> Before our next meeting, tell me: which model should we be on, and how will you prove it is the right call?
>
> Priya Raghavan, Larkspur Airlines

Bring two things. A recommendation, and the measurement behind it. If the model is
not the problem, say so, and bring the number that shows it.

## What this review read

- `agent.py (327 lines)`
- `PITCH.md`
- `TEAM.md`
- `readout-trace.json`
- `readout.html (evidence block)`
- given files that differ from the shipped pack: `verify.py`, `eval_harness.py`, `bench.py`, `readout.py`, `setup.py`, `pod_sync.py`, `run.py`, `review.py`, `support/__init__.py`, `support/client.py`, `support/data.py`, `support/models.py`, `support/tools.py`, `support/trace.py`, `support/offline.py`, `support/mock_backend.py`, `support/mcp_client.py`, `support/mcp_server.py`, `support/mcp_selftest.py`, `support/access.py`, `support/keyscan.py`, `support/review.py`

Reviewer: `claude-sonnet-5-5`. Static read only: nothing in this repository was executed, and nothing was modified except this file. Larkspur Airlines is a fictional training scenario. Confidential, do not distribute.
