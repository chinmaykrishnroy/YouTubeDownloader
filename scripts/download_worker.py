"""Run one cancellable download process; stdout carries only private job updates."""
import asyncio
import contextlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import main


async def run():
    job = json.loads(sys.stdin.readline())
    main.jobs[job["id"]] = job
    output = sys.stdout

    async def publish(message, owner=None):
        current = main.jobs.get(job["id"])
        if current:
            output.write(json.dumps(main.public_job(current)) + "\n")
            output.flush()

    main.broadcast = publish
    # Keep yt-dlp/metadata console output out of the JSON event stream.
    with contextlib.redirect_stdout(sys.stderr):
        await asyncio.to_thread(
            main.run_download, job["id"], job["url"], job["format"],
            job["quality"], job["title"], asyncio.get_running_loop(),
        )
        await publish({})


if __name__ == "__main__":
    asyncio.run(run())
