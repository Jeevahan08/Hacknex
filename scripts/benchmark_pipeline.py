import asyncio
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.services.benchmark_service import benchmark_service

async def run():
    print("=" * 60)
    print(" IndicLive Pipeline Benchmark & Ablation Runner")
    print("=" * 60)
    res = await benchmark_service.run_benchmark(
        source_language="en-IN",
        target_languages=["ta-IN", "hi-IN", "ml-IN"],
        mode="fast"
    )
    print(f"Run ID: {res.run_id}")
    print(f"Source: {res.source_language} -> Targets: {', '.join(res.target_languages)}")
    print("-" * 60)
    print(f"{'Approach':<28} | {'1st Word':<10} | {'Final':<10} | {'Rewrites':<8} | {'Stability'}")
    print("-" * 60)
    for c in res.comparisons:
        print(f"{c.approach:<28} | {c.first_word_latency_ms} ms     | {c.final_latency_ms} ms     | {c.rewrites:<8} | {c.stability_pct}%")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run())
