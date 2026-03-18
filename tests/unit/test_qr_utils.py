"""Unit tests for shared.qr_utils — QR version and box size calculators."""

from shared.qr_utils import suggest_box_size, suggest_qr_version


class TestSuggestQrVersion:
    def test_short_data_returns_version_1(self):
        assert suggest_qr_version("hello") == 1

    def test_medium_data(self):
        data = "x" * 100
        version = suggest_qr_version(data)
        assert 1 <= version <= 16

    def test_long_data_returns_higher_version(self):
        short_version = suggest_qr_version("hi")
        long_version = suggest_qr_version("x" * 500)
        assert long_version > short_version

    def test_very_long_data_returns_max_version(self):
        version = suggest_qr_version("x" * 10000)
        assert version == 16  # max version in our capacity table


class TestSuggestBoxSize:
    def test_short_data_returns_minimum(self):
        assert suggest_box_size("hello") == 10

    def test_long_data_returns_larger_size(self):
        size = suggest_box_size("x" * 600)
        assert size == 12

    def test_minimum_is_10(self):
        assert suggest_box_size("a") >= 10
