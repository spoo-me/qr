"""Unit tests for shared.color — color parsing utilities."""

import pytest

from errors import ValidationError
from shared.color import parse_color


class TestParseColor:
    """Tests for parse_color()."""

    def test_named_color_black(self):
        assert parse_color("black") == (0, 0, 0)

    def test_named_color_white(self):
        assert parse_color("white") == (255, 255, 255)

    def test_named_color_case_insensitive(self):
        assert parse_color("RED") == (255, 0, 0)
        assert parse_color("Blue") == (0, 0, 255)

    def test_named_color_transparent(self):
        assert parse_color("transparent") == "transparent"

    def test_hex_color_with_hash(self):
        assert parse_color("#FF0000") == (255, 0, 0)
        assert parse_color("#00ff00") == (0, 255, 0)

    def test_hex_color_without_hash(self):
        assert parse_color("0000FF") == (0, 0, 255)

    def test_rgb_with_prefix(self):
        assert parse_color("rgb(128,64,32)") == (128, 64, 32)

    def test_rgb_with_spaces(self):
        assert parse_color("rgb(128, 64, 32)") == (128, 64, 32)

    def test_tuple_format(self):
        assert parse_color("(106,26,76)") == (106, 26, 76)

    def test_tuple_format_with_spaces(self):
        assert parse_color("(255, 255, 255)") == (255, 255, 255)

    def test_invalid_hex_too_short(self):
        with pytest.raises(ValidationError):
            parse_color("#FFF")

    def test_invalid_format(self):
        with pytest.raises(ValidationError):
            parse_color("not-a-color")

    def test_invalid_rgb_too_many_values(self):
        with pytest.raises(ValidationError):
            parse_color("rgb(1,2,3,4)")

    def test_invalid_tuple_too_few_values(self):
        with pytest.raises(ValidationError):
            parse_color("(1,2)")

    def test_rgb_channel_out_of_range(self):
        with pytest.raises(ValidationError):
            parse_color("rgb(999,0,0)")

    def test_rgb_negative_channel(self):
        with pytest.raises(ValidationError):
            parse_color("rgb(-1,0,0)")

    def test_tuple_channel_out_of_range(self):
        with pytest.raises(ValidationError):
            parse_color("(256,0,0)")
