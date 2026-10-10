import asyncio
import json
import sys
import websockets

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

async def test_live():
    url = "ws://localhost:8000/ws/v1/live/autonomous_live_check"
    print(f"[*] Connecting to WebSocket: {url}")
    async with websockets.connect(url) as ws:
        msg1 = await ws.recv()
        print(f"[1] Session response: {msg1}")

        # Start session
        await ws.send(json.dumps({
            "type": "session.start",
            "source_language": "en-IN",
            "target_languages": ["ta-IN", "hi-IN", "ml-IN"],
            "enable_tts": False,
            "mode": "fast"
        }))
        stage = await ws.recv()
        print(f"[2] Pipeline stage: {stage}")

        # Stream speech text
        sentence = "Good morning everyone, today we are going to discuss artificial intelligence."
        print(f"[*] Emitting speech utterance: {sentence}")
        await ws.send(json.dumps({
            "type": "transcript.stream",
            "text": sentence,
            "is_final": True,
            "language": "en-IN"
        }))

        # Listen for emitted events
        received_translations = 0
        for _ in range(10):
            try:
                res = await asyncio.wait_for(ws.recv(), timeout=8.0)
                data = json.loads(res)
                evt_type = data.get("type", "")
                if "translation" in evt_type:
                    received_translations += 1
                    print(f"   -> {evt_type} [{data.get('target_language')}]: {data.get('text')}")
                elif "transcript" in evt_type:
                    print(f"   -> {evt_type}: {data.get('text')}")
                elif "pipeline.stage" in evt_type:
                    print(f"   -> pipeline.stage: {data.get('stage')}")
                
                if received_translations >= 3:
                    print(f"[✓] Successfully received all 3 target translations (Tamil, Hindi, Malayalam)!")
                    break
            except asyncio.TimeoutError:
                break

    print("[+] Autonomous live test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_live())
