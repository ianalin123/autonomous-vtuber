import asyncio
from core.config import settings
from streamer.capture import HeadlessCapture
from streamer.ffmpeg_pipe import FFmpegPipe


async def main() -> None:
    rtmp_url = f"{settings.twitch_rtmp_url}{settings.twitch_stream_key}"
    capture = HeadlessCapture(frontend_url=settings.vtuber_frontend_url)
    pipe = FFmpegPipe(rtmp_url=rtmp_url)
    print("Starting headless capture...")
    await capture.start()
    print("Starting FFmpeg RTMP pipe...")
    pipe.start()
    print(f"Streaming live to Twitch: {settings.twitch_channel}")
    try:
        while True:
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        pipe.stop()
        await capture.stop()


if __name__ == "__main__":
    asyncio.run(main())
