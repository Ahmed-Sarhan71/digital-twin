"""Ad-hoc check, no fixtures: uv run python test_server.py"""
import asyncio, os, sys, types

os.environ["DEEPSEEK_MODEL"] = "deepseek-v4-flash"

# persona files load for real; fall back to stubs only if they're missing
try:
    import context, resources
except Exception as e:
    print("resources/context unloadable (%s) -> stubbing" % e)
    res = types.ModuleType("resources")
    res.linkedin = res.summary = res.style = "..."
    res.facts = {"full_name": "Ahmed Sarhan", "name": "Ahmed"}
    ctx = types.ModuleType("context")
    ctx.prompt = lambda: "persona"
    sys.modules["resources"], sys.modules["context"] = res, ctx
else:
    assert resources.facts["name"] and resources.summary and resources.style and resources.linkedin
    assert len(context.prompt()) > 1000

import server  # used to crash here: OpenAI() with no OPENAI_API_KEY

assert "deepseek" in str(server.client.base_url)
assert server.client.api_key == os.getenv("DEEPSEEK_API_KEY")
assert server.MODEL == "deepseek-v4-flash"

seen = {}


class Fake:
    def create(self, **kw):
        seen.update(kw)
        return type("R", (), {"choices": [type("C", (), {"message": type("M", (), {"content": "ok"})()})()]})()


server.client.chat = type("X", (), {"completions": Fake()})()

sid = "hermes-check-tmp"
assert asyncio.run(server.chat(server.ChatRequest(message="hi", session_id=sid))).response == "ok"
assert seen["model"] == "deepseek-v4-flash"
assert seen["messages"][-1] == {"role": "user", "content": "hi"}

seen.clear()  # second turn replays history from ../memory/<sid>.json
asyncio.run(server.chat(server.ChatRequest(message="again", session_id=sid)))
assert seen["messages"][-2]["content"] == "ok", seen["messages"]

for f in __import__("pathlib").Path("../memory").glob(f"{sid}*"): f.unlink()
print("PASS: base", server.client.base_url, "model", seen["model"])
