from datasette import hookimpl, __version__
from feedgen.feed import FeedGenerator
import hashlib
import html


@hookimpl
def register_output_renderer(datasette):
    return {"extension": "atom", "callback": render_atom}


def render_atom(args, data, view_name):
    # print(args)
    # import json
    # print(json.dumps(data, default=repr, indent=2))
    fg = FeedGenerator()
    fg.generator(generator="Datasette", version=__version__, uri="https://github.com/simonw/datasette")
    sql = data["query"]["sql"]
    fg.id(data["database"] + "/" + hashlib.sha256(sql.encode("utf8")).hexdigest())
    fg.subtitle(sql)
    title = data["database"]
    if data.get("table"):
        title += "/" + data["table"]
    if data.get("human_description_en"):
        title += ": " + data["human_description_en"]
    fg.title(title)
    # And the rows
    for row in data["rows"]:
        entry = fg.add_entry()
        entry.id(repr(list(row)))
        entry.content(build_content(row), type="html")
        entry.title(repr(list(row)))
    if dict(args).get("_rss"):
        # Link is required for RSS:
        fg.link(href="https://example.com/")
        body = fg.rss_str(pretty=True)
    else:
        body = fg.atom_str(pretty=True)
    return {
        "body": body,
        "content_type": "application/xml; charset=utf-8",
        "status_code": 200,
    }


def build_content(row):
    bits = []
    for key, value in row.items():
        if isinstance(value, dict) and {"value", "label"} == set(value.keys()):
            value = '{} <span style="color: #666; font-size: 0.8em">({})</span>'.format(
                html.escape(value["label"]), html.escape(str(value["value"]))
            )
        else:
            value = html.escape(str(value))
        bits.append('<p><strong>{}</strong>: {}</p>'.format(html.escape(str(key)), value))
    return repr('\n'.join(bits))
