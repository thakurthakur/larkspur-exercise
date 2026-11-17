# PITCH.md

Six lines and a lever. Your words. The last two are scored.

Built: a Larkspur disruption-care chat agent on the Claude Messages API, with 11 tools for looking up bookings, checking flight status and policy, holding seats and escalating to a human.
Does: looks up the booking, finds out what actually happened to the flight, offers rebooking options that policy allows, holds a seat, and leaves the final booking to the customer's own confirm-click.
Number: 18,198 input tokens per resolved contact (K7PQ2M clean cancellation, 4 turns, 4 tool calls, n=1 run).
Safety check: 7 eval cases, 5 of them hard gates; 3 of 7 pass (42.9%), so the release is BLOCKED by the tone, tool-selection and group-split gates.
Next: write a tone addendum so abusive or legal-threat messages get escalated to a human instead of a normal entitlements rundown.
Still broken: an abusive customer threatening legal action still gets a calm, normal answer instead of being handed to a human.
Lever: intelligence

## Priya asked

Costs:
Wrong:
Runs it:
Left out:
