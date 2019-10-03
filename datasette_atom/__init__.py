from datasette import hookimpl, __version__
from feedgen.feed import FeedGenerator
import hashlib
import html
import inspect


PARAMETER_NAMES = {"atom_title": "Entry title"}


@hookimpl
def register_output_renderer(datasette):
    return {"extension": "atom", "callback": render_atom}


def render_atom(args, data, view_name):
    request = get_variable_from_stack("request")
    datasette = get_variable_from_stack("ds", True)
    fg = FeedGenerator()
    fg.generator(
        generator="Datasette",
        version=__version__,
        uri="https://github.com/simonw/datasette",
    )
    sql = data["query"]["sql"]
    fg.id(data["database"] + "/" + hashlib.sha256(sql.encode("utf8")).hexdigest())
    fg.subtitle(sql)
    title = data["database"]
    if data.get("table"):
        title += "/" + data["table"]
    if data.get("human_description_en"):
        title += ": " + data["human_description_en"]
    fg.title(title)

    import json

    print(json.dumps(data, default=repr, indent=4))

    # atom:id - for tables, this is the database/table/rowid - but for arbitrary queries
    # we instead use a sha256 of the row contents unless ?_atom_id= is provided

    # atom:updated - if there is an obvious candidate based on column name + content we use
    # that, otherwise we require ?_atom_updated=

    # atom:title - we require ?_atom_title= for this. Later we will try to autodetect it
    atom_title = args.get("_atom_title")
    if not atom_title or atom_title not in data["columns"]:
        return prompt_for_parameters(datasette, ["atom_title"], data["columns"])

    # atom:content - if ?_atom_content= is there, use it - otherwise HTML of all key/pairs

    # And the rows
    for row in data["rows"]:
        entry = fg.add_entry()
        entry.id(repr(list(row)))
        entry.content(build_content(row), type="html")
        entry.title(str(row[atom_title]))
    if dict(args).get("_rss"):
        # Link is required for RSS:
        fg.link(href=request.url)
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
    for key, value in dict(row).items():
        if isinstance(value, dict) and {"value", "label"} == set(value.keys()):
            value = '{} <span style="color: #666; font-size: 0.8em">({})</span>'.format(
                html.escape(value["label"]), html.escape(str(value["value"]))
            )
        else:
            value = html.escape(str(value))
        bits.append(
            "<p><strong>{}</strong>: {}</p>".format(html.escape(str(key)), value)
        )
    return repr("\n".join(bits))


def get_variable_from_stack(name, try_on_self=False):
    # This is a work-around until Datasette is updated to make these
    # objects available to the register_output_renderer render callback
    frame = inspect.currentframe()
    while frame:
        print(frame.f_locals.keys())
        if "self" in frame.f_locals:
            print("  self = ", frame.f_locals["self"])
        if name in frame.f_locals:
            return frame.f_locals[name]
        elif (
            try_on_self
            and "self" in frame.f_locals
            and hasattr(frame.f_locals["self"], name)
        ):
            return getattr(frame.f_locals["self"], name)
        else:
            frame = frame.f_back
    return None


def prompt_for_parameters(datasette, parameters, columns):
    return {
        "body": render_template(
            datasette,
            "configure_atom.html",
            {
                "parameters": parameters,
                "columns": columns,
                "PARAMETER_NAMES": PARAMETER_NAMES,
            },
        ),
        "content_type": "text/html; charset=utf-8",
        "status_code": 400,
    }


def render_template(datasette, template_name, context=None):
    context = context or {}
    template = datasette.jinja_env.select_template([template_name])
    return template.render(context)
