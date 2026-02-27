import subprocess
from typing import Optional


class FFmpegPipe:
    def __init__(self, rtmp_url: str, width: int = 1280, height: int = 720, fps: int = 30) -> None:
        self._rtmp_url = rtmp_url
        self._width = width
        self._height = height
        self._fps = fps
        self._process: Optional[subprocess.Popen] = None

    def build_command(self) -> list[str]:
        return [
            "ffmpeg", "-y",
            "-f", "x11grab",
            "-r", str(self._fps),
            "-s", f"{self._width}x{self._height}",
            "-i", ":99",
            "-f", "pulse",
            "-i", "default",
            "-vcodec", "libx264",
            "-preset", "veryfast",
            "-b:v", "2500k",
            "-maxrate", "2500k",
            "-bufsize", "5000k",
            "-acodec", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-f", "flv",
            self._rtmp_url,
        ]

    def start(self) -> None:
        self._process = subprocess.Popen(
            self.build_command(),
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

    def stop(self) -> None:
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None
