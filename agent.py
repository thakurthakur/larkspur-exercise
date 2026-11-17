"""Larkspur disruption agent. This is the file you build.

It runs right now, and it is wrong in four places. The trace shows each one
before the code does, so read the trace first:

    python3 run.py K7PQ2M --trace

Where you edit:   grep -n '✏' agent.py   (six marks, one per place)
Steps and gates:  https://anthropicpartnerbasecamp.bts.com/
"""
from __future__ import annotations
from typing import Any, Dict, List
from support import mock_backend as backend
from support import (MODEL, SYSTEM_PROMPT, call_local, execute_tool, mcp_client,
                     new_session, next_available_day, record_tool_result,
                     runtime_preamble)

MAX_TOOL_CALLS = 8  # Larkspur's own build capped the loop here; then a human takes over.

TONE_ADDENDUM = ""                       # ✏️ Build 4, step 4.1, intelligence goal
EXTRA_TOOLS: List[Dict[str, Any]] = [   # ✏️ Build 2, step 2.1: schemas for the tools you add
    {
        "name": "seats_left",
        "description": (
            "Look up the free seats left in each cabin of one flight on one date. "
            "Use it when the customer asks whether there is room on a flight, or how many "
            "seats are left, including for a whole party: compare the count with the number "
            "of people the customer says are travelling, which can differ from the passengers "
            "on the booking. "
            "For a question about seats or room, call this first: it is the focused read "
            "for exactly that. get_flight_status is for status, delay and cause, so add it "
            "only when the answer also needs those. "
            "It needs flight_no and date, which you take from lookup_booking "
            "(segment.flight_number and segment.date) or from a search_alternatives option; "
            "never ask the customer for them and never guess them. "
            "Returns {\"seats_left_Y\": n, \"seats_left_J\": n}: Y is main (economy), J is first. "
            "0 means that cabin is full, which is a real answer and not an error. A count "
            "below the party size means the whole party does not fit in that cabin. "
            "If get_flight_status already returned seats_left_Y and seats_left_J for the same "
            "flight and date, do not call this as well. "
            "search_alternatives already reports seats_available on each option, so do not "
            "use this to re-check those. "
            "On failure it returns {\"error\": ...}. 'Flight number ... not found' or "
            "'Date ... not found' means the arguments do not match the data: re-read them "
            "from the booking rather than trying other dates. 'No flight data for ...' means "
            "the date is outside the days the data covers: say you cannot check seats for "
            "that date, and do not retry other dates. An invalid date means fix it "
            "and call again. 'Failed to load flight data' means the data is unavailable: "
            "tell the customer you cannot check seats right now. "
            "Only ever state a seat count this tool returned, never an estimate. The count is "
            "a snapshot, not a reservation: hold_seat is what sets a seat aside."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "flight_no": {
                    "type": "string",
                    "description": "Flight number as it appears on the booking segment, e.g. LK415.",
                },
                "date": {
                    "type": "string",
                    "description": "Local flight date in ISO format YYYY-MM-DD, e.g. 2025-05-08. "
                                   "Not MM/DD/YYYY.",
                },
            },
            "required": ["flight_no", "date"],
        },
    },
]


def seats_left(flight_no: str, date: str) -> Dict[str, Any]:
    """Free seats in each cabin of one flight on one date, read from flights.csv.

    One pass over the rows. It answers with the numbers the data holds, or with an
    {"error": ...} that says which argument did not match; it never fills in a
    default number. call_local() only catches TypeError, so every expected failure
    is returned here and never raised.
    """
    flight_no = str(flight_no).strip().upper()
    date = str(date).strip()

    if not backend.ISO_DATE.match(date):
        return {"error": f"Invalid date '{date}': use ISO format YYYY-MM-DD."}
    if not backend.DATA_HORIZON_START <= date <= backend.DATA_HORIZON_END:
        return {"error": f"No flight data for {date}: the data covers "
                         f"{backend.DATA_HORIZON_START} to {backend.DATA_HORIZON_END}."}

    try:
        rows = backend.load_flights()
    except Exception as exc:  # noqa: BLE001 - the model reads this and can tell the customer
        return {"error": f"Failed to load flight data: {exc}"}

    flight_seen = False
    for row in rows:
        if row["flight_no"] != flight_no:
            continue
        flight_seen = True
        if row["date"] == date:
            return {"flight_no": flight_no, "date": date,
                    "seats_left_Y": row["seats_left_Y"], "seats_left_J": row["seats_left_J"]}

    if flight_seen:
        return {"error": f"Date {date} not found for flight number {flight_no}."}
    return {"error": f"Flight number {flight_no} not found."}


LOCAL_TOOLS: Dict[str, Any] = {         # ✏️ Build 2, step 2.1: the functions behind them
    "seats_left": seats_left,
}


def text_of(response) -> str:
    """Given. The last non-empty text block, never content[0]."""
    texts = [b.text for b in response.content if getattr(b, "type", None) == "text" and b.text]
    return texts[-1] if texts else ""


def tool_results(response) -> List[Dict[str, Any]]:
    """Given. Runs every tool_use block and packages the results the way the
    API expects them back. A tool can live in three places: the MCP server,
    LOCAL_TOOLS, or support/tools.py."""
    # three branches, no try/except in this file: mcp_client.call_remote() and
    # support.call_local() answer with an error dict instead of raising, and both
    # record what came back on the trace
    results = []
    for block in response.content:
        if getattr(block, "type", None) != "tool_use":
            continue
        if block.name in mcp_client.tool_names:
            output = mcp_client.call_remote(block.name, block.input)
        elif block.name in LOCAL_TOOLS:
            output = call_local(LOCAL_TOOLS[block.name], block.name, block.input)
        else:
            output = execute_tool(block.name, block.input)
        results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": str(output),
        })
    return results


def run_agent(pnr: str, last_name: str, message: str) -> str:            # ✏️ Build 1, step 1.2
    """Run the tool loop until Claude stops asking for tools. Return its final text."""
    client, tracer = new_session()
    tools = tool_list()
    messages = [
        {"role": "user", "content": f"PNR {pnr}, last name {last_name}. {message}"},
    ]

    response = client.messages.create(
        model=MODEL, max_tokens=4096, system=runtime_preamble() + SYSTEM_PROMPT + TONE_ADDENDUM,
        thinking={"type": "adaptive"}, tools=tools, messages=messages,
    )

    turns = 1
    while response.stop_reason == "tool_use" and turns < MAX_TOOL_CALLS:
        results = tool_results(response)
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": results})
        response = client.messages.create(
            model=MODEL, max_tokens=4096, system=runtime_preamble() + SYSTEM_PROMPT + TONE_ADDENDUM,
            thinking={"type": "adaptive"}, tools=tools, messages=messages,
        )
        turns += 1

    return text_of(response)


def tool_list() -> List[Dict[str, Any]]:                   # ✏️ Build 2, step 2.2
    """Given. Exactly what Claude is offered on every turn; run.py --show-tools
    prints this list."""
    return build_tools() + EXTRA_TOOLS


# ──────────────────────────────────────────────────────────────────────────────
# Below this line: what Claude is told about each tool. Step 1.3.
# The functions these describe are written and correct, in support/tools.py.
# ──────────────────────────────────────────────────────────────────────────────
def build_tools() -> List[Dict[str, Any]]:                 # ✏️ Build 1, step 1.3
    """Anthropic-shaped schemas: name, description, input_schema. What Claude is
    told about each of the nine tools, and all it is ever told."""
    return [
        {
            "name": "lookup_booking",
            "description": (
                "Retrieve a Larkspur reservation from Altura by confirmation code (PNR) "
                "and the passenger's last name. Both are required to prevent a lookup on "
                "a guessed PNR. Returns fare family, loyalty tier, the segment that needs "
                "attention, and any group/partner/minor/SSR flags relevant to scope."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"pnr": {"type": "string"}, "last_name": {"type": "string"}},
                "required": ["pnr", "last_name"],
            },
        },
        {
            "name": "get_flight_status",
            "description": (
                "Look up a Larkspur or Larkspur Link flight's current OpsFeed status for "
                "one local date: status, delay minutes, and cause. Use this before telling "
                "a customer anything about a flight's timing; never state it from memory."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "flight_no": {
                        "type": "string",
                        "description": "Flight number exactly as in the booking segment.",
                    },
                    "date": {
                        "type": "string",
                        "description": "Local departure date, YYYY-MM-DD, exactly as returned in the booking segment.",
                    },
                },
                "required": ["flight_no", "date"],
            },
        },
        {
            "name": "search_alternatives",
            "description": (
                "Find alternative Larkspur flights for the disrupted segment on this "
                "booking. Use it after lookup_booking and get_flight_status show the "
                "segment is cancelled or significantly delayed, and before offering the "
                "customer any rebooking. Returns a list of options, each with an "
                "option_id; pass the chosen option_id to hold_seat. Only offer options "
                "this tool returned; never invent a flight."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"pnr": {"type": "string"}},
                "required": ["pnr"],
            },
        },
        {
            "name": "check_policy",
            "description": (
                "Resolve what Larkspur owes this customer for the disruption: rebooking "
                "waiver, refund path, meal/hotel/ground care, goodwill eligibility and cap, "
                "and any escalation triggers. cause_code, delay_minutes and status describe "
                "what get_flight_status told you; fare_family, loyalty_tier and whether this "
                "is overnight are looked up from the booking, not asked of you. Every "
                "response carries a policy_row_id. Cite it if you reference this decision "
                "again."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "pnr": {"type": "string"},
                    "cause_code": {"type": "string", "enum": ["WX", "ATC", "MX", "CREW", "SEC"]},
                    "delay_minutes": {"type": "integer"},
                    "status": {"type": "string", "enum": ["ON_TIME", "DELAYED", "CANCELLED", "DIVERTED"]},
                    "wait_minutes_for_alternative": {"type": "integer"},
                    "chosen_option_id": {"type": "string"},
                },
                "required": ["pnr", "cause_code", "delay_minutes", "status"],
            },
        },
        {
            "name": "hold_seat",
            "description": "Place a 15-minute hold on one alternative. Reversible. It simply expires.",
            "input_schema": {
                "type": "object",
                "properties": {"option_id": {"type": "string"}, "pnr": {"type": "string"}},
                "required": ["option_id", "pnr"],
            },
        },
        {
            "name": "confirm_rebooking",
            "description": (
                "Finalize a held seat. Irreversible. Requires a confirmation_token that "
                "only the customer's own Confirm-click can produce. You cannot supply it "
                "yourself, and 'the customer said yes' in chat does not substitute for it."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"hold_id": {"type": "string"}, "confirmation_token": {"type": "string"}},
                "required": ["hold_id", "confirmation_token"],
            },
        },
        {
            "name": "issue_voucher",
            "description": (
                "Issue a meal, ground, hotel, or goodwill voucher. Auto-approves within the "
                "policy's threshold for that type; above it, returns a pending status for a "
                "human. It does not fail. Always pass the policy_row_id that made it eligible."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "voucher_type": {"type": "string", "enum": ["meal", "ground", "hotel", "goodwill"]},
                    "amount_usd": {"type": "number"},
                    "pnr": {"type": "string"},
                    "policy_row_id": {"type": "string"},
                },
                "required": ["voucher_type", "amount_usd", "pnr", "policy_row_id"],
            },
        },
        {
            "name": "escalate_to_human",
            "description": (
                "Hand this conversation to a human, with your reasoning attached. Use for "
                "groups, partner segments, unaccompanied minors, refunds, or anything else "
                "out of scope. This is the correct outcome for those cases, not a failure."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "pnr": {"type": "string"}, "reason": {"type": "string"},
                    "summary_for_human": {"type": "string"}, "queue": {"type": "string"},
                },
                "required": ["pnr", "reason", "summary_for_human"],
            },
        },
        {
            "name": "send_confirmation",
            "description": "Send the customer a written confirmation of what was just done. Benign.",
            "input_schema": {
                "type": "object",
                "properties": {"pnr": {"type": "string"}, "message": {"type": "string"}},
                "required": ["pnr", "message"],
            },
        },
    ]
