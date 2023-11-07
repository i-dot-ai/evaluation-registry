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
    "time_delta, args",
    [
        ("0 minutes", {}),
        ("10 hours and 9 minutes", {"minutes": 609}),
        ("More than 200 hours", {"minutes": 13000}),
        ("More than 2 hours", {"minutes": 609, "hours_limit": 2}),
        ("too long", {"minutes": 609, "hours_limit": 2, "too_large_msg": "too long"}),
    ],
)
def test_humanize_timedelta(time_delta, args):
    actual = jinja2.humanize_timedelta(**args)
    assert actual == time_delta, actual
