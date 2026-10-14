"""s1 · The agent loop: the model picks a tool, we run it, the result goes back, until it answers."""
import json

from common import MODEL, capture, client, retail_db

DB = retail_db()
TOOLS = {   # two read tools from τ²-bench's retail domain, same names and arguments
    "get_order_details": lambda order_id: DB["orders"].get(order_id, "order not found"),
    "get_product_details": lambda product_id: DB["products"].get(product_id, "product not found"),
}
# The argument descriptions are τ²-bench's own. Without the first one, the model dropped the '#' three times and
# never found the order (raw/s1_agent_loop_vague.json): a tool's description is part of its interface.
SCHEMAS = [{"type": "function", "function": {
    "name": name, "description": f"Look up {what} by its id.",
    "parameters": {"type": "object", "properties": {arg: {"type": "string", "description": hint}}, "required": [arg]}}}
    for name, what, arg, hint in [
        ("get_order_details", "an order", "order_id",
         "The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id."),
        ("get_product_details", "a product and all its variants", "product_id", "The product id, such as '6086499569'. Be careful the product id is different from the item id.")]]


def run(question, max_steps=6):
    llm, steps = client(), []
    messages = [{"role": "system", "content": "You are a retail support agent. Use the tools; never guess."},
                {"role": "user", "content": question}]
    for _ in range(max_steps):                                   # the guard against an endless loop
        msg = llm.chat.completions.create(model=MODEL, messages=messages, tools=SCHEMAS).choices[0].message
        messages.append(msg)
        if not msg.tool_calls:                                   # no tool call: this is the answer
            return msg.content, steps
        for call in msg.tool_calls:                              # act, then observe
            args = json.loads(call.function.arguments)
            result = TOOLS[call.function.name](**args)
            steps.append({"tool": call.function.name, "args": args})
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    return "stopped: step limit reached", steps


if __name__ == "__main__":
    q = "Order #W2611340: what is its status, what colour is the water bottle in it, and which other colours of that bottle are available right now?"
    answer, steps = run(q)
    print(*[f"→ {s['tool']}({s['args']})" for s in steps], answer, sep="\n")
    capture("s1_agent_loop", {"model": MODEL, "order_id_description": SCHEMAS[0]["function"]["parameters"]["properties"]["order_id"]["description"], "question": q, "steps": len(steps), "tool_calls": steps, "answer": answer})
