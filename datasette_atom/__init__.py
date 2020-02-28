import bleach
from datasette import hookimpl, __version__
from feedgen.feed import FeedGenerator
import hashlib
import html

REQUIRED_COLUMNS = {"atom_id", "atom_updated", "atom_title"}


@hookimpl
def register_output_renderer():
    return {"extension": "atom", "callback": render_atom}


def render_atom(args, data, view_name):
    from datasette.views.base import DatasetteError

    columns = set(data["columns"])
    if not REQUIRED_COLUMNS.issubset(columns):
        raise DatasetteError(
            "SQL query must return columns {}".format(", ".join(REQUIRED_COLUMNS)),
            status=400,
        )
    fg = FeedGenerator()
    fg.generator(
        generator="Datasette",
        version=__version__,
        uri="https://github.com/simonw/datasette",
    )
    sql = data["query"]["sql"]
    fg.id(data["database"] + "/" + hashlib.sha256(sql.encode("utf8")).hexdigest())
    fg.updated(max(row["atom_updated"] for row in data["rows"]))
    title = args.get("_feed_title", sql)
    if data.get("table"):
        title += "/" + data["table"]
    if data.get("human_description_en"):
        title += ": " + data["human_description_en"]
    fg.title(title)
    # And the rows
    for row in reversed(data["rows"]):
        entry = fg.add_entry()
        entry.id(str(row["atom_id"]))
        if "atom_content_html" in columns:
            entry.content(clean(row["atom_content_html"]), type="html")
        elif "atom_content" in columns:
            entry.content(row["atom_content"], type="text")
        entry.updated(row["atom_updated"])
        entry.title(str(row["atom_title"]))
        # atom_link is optional
        if "atom_link" in columns:
            entry.link(href=row["atom_link"])
    return {
        "body": fg.atom_str(pretty=True),
        "content_type": "application/xml; charset=utf-8",
        "status_code": 200,
    }


def clean(html):
    cleaned = bleach.clean(
        html,
        tags=[
            "a",
            "abbr",
            "acronym",
            "b",
            "blockquote",
            "code",
            "em",
            "i",
            "li",
            "ol",
            "strong",
            "ul",
            "pre",
            "p",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "img",
        ],
        attributes={"a": ["href", "title"], "img": ["alt", "src"]},
    )
    return cleaned
