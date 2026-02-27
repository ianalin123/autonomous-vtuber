import pytest
from unittest.mock import patch, MagicMock
from streamer.ffmpeg_pipe import FFmpegPipe


def test_ffmpeg_pipe_constructs_rtmp_command():
    pipe = FFmpegPipe(rtmp_url="rtmp://live.twitch.tv/app/testkey")
    cmd = pipe.build_command()
    assert "rtmp://live.twitch.tv/app/testkey" in cmd
    assert "libx264" in cmd
    assert "aac" in cmd


def test_ffmpeg_pipe_start_spawns_subprocess():
    pipe = FFmpegPipe(rtmp_url="rtmp://live.twitch.tv/app/testkey")
    with patch("streamer.ffmpeg_pipe.subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock()
        pipe.start()
        mock_popen.assert_called_once()


def test_ffmpeg_pipe_stop_terminates_process():
    pipe = FFmpegPipe(rtmp_url="rtmp://live.twitch.tv/app/testkey")
    mock_proc = MagicMock()
    pipe._process = mock_proc
    pipe.stop()
    mock_proc.terminate.assert_called_once()
    assert pipe._process is None
