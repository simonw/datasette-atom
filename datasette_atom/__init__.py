import bleach
from datasette import hookimpl, __version__
from feedgen.feed import FeedGenerator
import hashlib
import html

REQUIRED_COLUMNS = {"atom_id", "atom_updated", "atom_title"}


@hookimpl
def register_output_renderer():
    return {"extension": "atom", "render": render_atom, "can_render": can_render_atom}


def render_atom(
    datasette, request, sql, columns, rows, database, table, query_name, view_name, data
):
    from datasette.views.base import DatasetteError

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
    fg.id(request.url)
    fg.link(href=request.url, rel="self")
    fg.updated(max(row["atom_updated"] for row in rows))
    title = request.args.get("_feed_title", sql)
    if table:
        title += "/" + table
    if data.get("human_description_en"):
        title += ": " + data["human_description_en"]
    # If this is a canned query the configured title for that over-rides all others
    if query_name:
        try:
            title = datasette.metadata(database=database)["queries"][query_name][
                "title"
            ]
        except (KeyError, TypeError):
            pass
    fg.title(title)
    # And the rows
    for row in reversed(rows):
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
        if "atom_author_name" in columns and row["atom_author_name"]:
            author = {
                "name": row["atom_author_name"],
            }
            for key in ("uri", "email"):
                colname = "atom_author_{}".format(key)
                if colname in columns and row[colname]:
                    author[key] = row[colname]
            entry.author(author)

    return {
        "body": fg.atom_str(pretty=True),
        "content_type": "application/xml; charset=utf-8",
        "status_code": 200,
    }


def can_render_atom(columns):
    return REQUIRED_COLUMNS.issubset(columns)


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
