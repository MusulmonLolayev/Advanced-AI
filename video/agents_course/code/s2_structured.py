"""s2 · Structured output: the model must fill a JSON Schema; we
validate it and send errors back for a retry."""
import json

from jsonschema import ValidationError, validate

from common import MODEL, capture, client, retail_db

DB = retail_db()
RETURN = {"type": "object", "additionalProperties": False,
          "required": ["order_id", "item_ids", "reason"],
          "properties": {
              "order_id": {"type": "string", "pattern": "^#W[0-9]{7}$"},
              "item_ids": {"type": "array", "items": {"type": "string"},
                           "minItems": 1},
              "reason": {"enum": ["damaged", "wrong_item",
                                  "no_longer_needed"]}}}
TOOL = [{"type": "function", "function": {
    "name": "submit_return", "parameters": RETURN,
    "description": "File a return request for items of one delivered"
                   " order."}}]


def check(req):
    """Schema first, then the facts the schema cannot know: the items
    must belong to that order."""
    validate(req, RETURN)
    items = {i["item_id"]: i["name"]
             for i in DB["orders"][req["order_id"]]["items"]}
    # an actionable error lists the valid choices; naming the problem
    # alone failed 3 times (raw/s2_structured_unhelpful.json)
    if bad := [i for i in req["item_ids"] if i not in items]:
        raise ValidationError(
            f"item ids {bad} are not in {req['order_id']}; "
            f"its items are {items}")


def extract(text, tries=3):
    llm, log = client(), []
    messages = [{"role": "system", "content": "Turn the customer "
                 "message into one submit_return call."},
                {"role": "user", "content": text}]
    for _ in range(tries):
        # DeepSeek's thinking mode refuses a forced tool_choice, so a
        # plain reply is sent back as an error too
        msg = llm.chat.completions.create(model=MODEL,
            messages=messages, tools=TOOL).choices[0].message
        if not msg.tool_calls:
            log.append({"request": None, "error": "answered in text "
                        "instead of calling submit_return"})
            messages += [msg, {"role": "user", "content": "Call "
                               "submit_return; do not answer in text."}]
            continue
        call = msg.tool_calls[0]
        req = json.loads(call.function.arguments)
        try:
            check(req)
            log.append({"request": req, "error": None})
            return req, log
        except ValidationError as e:  # say exactly what was wrong
            log.append({"request": req, "error": e.message})
            messages += [msg, {
                "role": "tool", "tool_call_id": call.id,
                "content": f"Invalid: {e.message}. Try again."}]
    return None, log


if __name__ == "__main__":
    order = DB["orders"]["#W2611340"]
    text = (f"Hi, order #W2611340 arrived but the "
            f"{order['items'][0]['name'].lower()} is cracked. "
            f"Product {order['items'][0]['product_id']}. "
            f"I want to send it back.")
    req, log = extract(text)
    for i, t in enumerate(log, 1):
        print(f"try {i}: {t['request']}  "
              f"{'OK' if not t['error'] else 'invalid: ' + t['error']}")
    capture("s2_structured", {
        "model": MODEL, "message": text, "tries": log,
        "valid": req is not None,
        "invalid_first_try": log[0]["error"] is not None,
        "recovered": req is not None and log[0]["error"] is not None})
