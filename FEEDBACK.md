# Client review: Larkspur disruption-care agent

**To:** Room 14  
**From:** Larkspur client review agent, on behalf of Priya Raghavan  
**Re:** the disruption-care agent you walked us through in our last session  
**Generated:** 2026-11-17 10:23

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

**1. agent.py run_agent(): the loop now appends response.content to messages and returns text_of(response) from the last turn.**

Your diff replaces the string-only assistant message with the full response.content, and drops the answer variable. With adaptive thinking enabled in the same create() call, the thinking blocks now travel back with each tool_use turn. readout-trace.json shows 4 API turns and 3 tool calls, so the loop continued past the first tool_use and ended on a non-tool stop.

Run python3 run.py --all --trace and paste the totals footer so the 4-turn, 3-call shape is shown across every booking, not just the one in readout-trace.json.

**2. agent.py search_alternatives and get_flight_status: you rewrote both descriptions, and the 3-call trace never touches search_alternatives.**

The search_alternatives description went from "search" to a sentence that names lookup_booking and get_flight_status as prerequisites and says "never invent a flight". The get_flight_status date changed from "MM/DD/YYYY" to "YYYY-MM-DD". The committed trace calls lookup_booking, get_flight_status, check_policy and stops, so no run in this repository shows search_alternatives, hold_seat or issue_voucher being called.

Run python3 run.py --all --trace and paste the tools-called line for every PNR that is cancelled or delayed.

**3. agent.py build_tools(): hold_seat is 73 characters and send_confirmation is 71, both still one-line placeholders.**

hold_seat reads "Place a 15-minute hold on one alternative. Reversible. It simply expires." and says nothing about needing an option_id from search_alternatives. send_confirmation reads "Send the customer a written confirmation of what was just done. Benign." The other seven descriptions run 216 to 445 characters. A larger model reads the same 73 characters.

Run python3 run.py --show-tools and paste the hold_seat and send_confirmation entries as the model sees them now.

**4. readout-trace.json: prompt caching shows 0 read, 0 written on 13079 input tokens, and agent.py has no cache_control.**

Every create() call resends runtime_preamble() + SYSTEM_PROMPT + TONE_ADDENDUM and all nine tool schemas, about 1,800 characters of descriptions alone. The trace reports hit ratio None across 4 turns. A model swap leaves that fixed prefix at the same size on every call.

Run python3 run.py --tool-tax and paste its output next to the readout-trace.json token totals.

**5. Eval cases and PITCH.md: there is no evals/cases.json, PITCH.md is the unchanged template, and the only banked gates are 1.2, 1.3 and 1.4.**

readout.html was banked at 2026-11-16T13:22:08 by Sebastian Goscinski with three gates. TONE_ADDENDUM is 0 characters, EXTRA_TOOLS is 0, and there are no LOCAL_TOOLS executors. Nothing in the repository yet measures what any change, or any model, does to the pass rate, cost or latency. The one run on record is 13.2s wall clock and 13079 tokens in, on a single booking.

Run python3 bench.py --label baseline --stage 1 --runs 3 and paste the output so there is a number to compare a model or a prompt change against.

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

- `agent.py (238 lines)`
- `PITCH.md (unchanged template)`
- `TEAM.md`
- `readout-trace.json`
- `readout.html (evidence block)`

Reviewer: `claude-sonnet-5-5`. Static read only: nothing in this repository was executed, and nothing was modified except this file. Larkspur Airlines is a fictional training scenario. Confidential, do not distribute.
