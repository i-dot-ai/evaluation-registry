import pytest

from evaluation_registry import jinja2


def test_convert_markdown_sanitises_html():
    dodgy_html = '<script>alert("Oops! This is a malicious script.");</script>'
    converted_markdown = jinja2.markdown(dodgy_html)
    assert "<script>" not in converted_markdown, converted_markdown


def test_convert_markdown():
    markdown_text = "**I am bold**"
    expected = "<p><strong>I am bold</strong></p>"
    actual = jinja2.markdown(markdown_text)
    assert actual == expected, actual


@pytest.mark.parametrize(
    "time_delta, minutes, hours_limit, too_large_msg",
    [
        ("0 minutes", 0, 0, ""),
        ("10 hours and 9 minutes", 609, 200, ""),
        ("More than 200 hours", 13000, 200, ""),
        ("More than 2 hours", 609, 2, ""),
        ("too long", 301, 2, "too long"),
    ],
)
def test_humanize_timedelta(time_delta, minutes, hours_limit, too_large_msg):
    actual = jinja2.humanize_timedelta(minutes, hours_limit, too_large_msg)
    assert actual == time_delta, actual
