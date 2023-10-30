import datetime

import humanize
import jinja2
from django.templatetags.static import static
from django.urls import reverse
from markdown_it import MarkdownIt

# `js-default` setting required to sanitize inputs
# https://markdown-it-py.readthedocs.io/en/latest/security.html
markdown_converter = MarkdownIt("js-default")


def is_in(value, list):
    return value in list


def url(path, *args, **kwargs):
    assert not (args and kwargs)
    return reverse(path, args=args, kwargs=kwargs)


def remove_query_param(query_dict, key_to_change, value_to_change):
    qd = query_dict.copy()
    if value_to_change in qd.getlist(key_to_change):
        updated_values = qd.pop(key_to_change)
        updated_values.remove(value_to_change)
        qd.setlistdefault(key_to_change, updated_values)
    if key_to_change != 'page':
        qd.__setitem__('page', 1)
    return qd.urlencode()


def markdown(text, cls=None):
    """
    Converts the given text into markdown.
    The `replace` statement replaces the outer <p> tag with one that contains the given class, otherwise the markdown
    ends up double wrapped with <p> tags.
    Args:
        text: The text to convert to markdown
        cls (optional): The class to apply to the outermost <p> tag surrounding the markdown

    Returns:
        Text converted to markdown
    """
    html = markdown_converter.render(text).strip()
    html = html.replace("<p>", f'<p class="{cls or ""}">', 1).replace("</p>", "", 1)
    return html


def humanize_timedelta(minutes=0, hours_limit=200, too_large_msg=""):
    if minutes > (hours_limit * 60):
        if not too_large_msg:
            return f"More than {hours_limit} hours"
        else:
            return too_large_msg
    else:
        delta = datetime.timedelta(minutes=minutes)
        return humanize.precisedelta(delta, minimum_unit="minutes")


def environment(**options):
    extra_options = dict()
    env = jinja2.Environment(  # nosec B701
        **{
            "autoescape": True,
            **options,
            **extra_options,
        }
    )
    env.globals.update(
        {
            "static": static,
            "is_in": is_in,
            "url": url,
            "remove_query_param": remove_query_param,
            "humanize_timedelta": humanize_timedelta,
        }
    )
    return env
