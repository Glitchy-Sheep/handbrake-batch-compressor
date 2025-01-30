import datetime

from src.handbrake_cli_output_capturer import (
    parse_handbrake_cli_output,
)


class TestHandbrakeCliOutputCapturer:

    def test_with_sufficient_data(self):
        handbrake_cli_output = (
            "Encoding: task 1 of 1, 4.00 % (937.13 fps, avg 955.64 fps, ETA 00h03m22s)"
        )

        progress_info = parse_handbrake_cli_output(handbrake_cli_output)

        assert progress_info.progress == 4.00
        assert progress_info.fps_current == 937.13
        assert progress_info.fps_average == 955.64
        assert progress_info.eta == datetime.timedelta(hours=0, minutes=3, seconds=22)

    def test_completed(self):
        handbrake_cli_output = (
            "Encoding: task 1 of 1, 100.00 % (0 fps, avg 0 fps, ETA 00h00m00s)"
        )

        progress_info = parse_handbrake_cli_output(handbrake_cli_output)

        assert progress_info.progress == 100.00
        assert progress_info.fps_current == 0
        assert progress_info.fps_average == 0
        assert progress_info.eta == datetime.timedelta(hours=0, minutes=0, seconds=0)

    def test_without_statistics(self):
        handbrake_cli_output = "Encoding: task 1 of 1, 12.00 % "

        progress_info = parse_handbrake_cli_output(handbrake_cli_output)

        assert progress_info.progress == 12.00
        assert progress_info.fps_current == None
        assert progress_info.fps_average == None
        assert progress_info.eta == None
