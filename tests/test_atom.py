import datasette
from datasette.app import Datasette
import urllib.parse
import pytest
import httpx

EXPECTED_ATOM = """
<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>http://localhost/:memory:.atom?sql=%0A++++select%0A++++++++1+as+atom_id%2C%0A++++++++123+as+atom_title%2C%0A++++++++%272019-10-23T21%3A32%3A12-07%3A00%27+as+atom_updated%2C%0A++++++++%27blah+%3Cb%3EBold%3C%2Fb%3E%27+as+atom_content%2C%0A++++++++%27Author%27+as+atom_author_name%2C%0A++++++++%27https%3A%2F%2Fwww.example.com%2F%27+as+atom_author_uri%0A++++union+select%0A++++++++%27atom-id-2%27+as+atom_id%2C%0A++++++++%27title+2%27+as+atom_title%2C%0A++++++++%272019-09-23T21%3A32%3A12-07%3A00%27+as+atom_updated%2C%0A++++++++%27blah%27+as+atom_content%2C%0A++++++++null+as+atom_author_name%2C%0A++++++++null+as+atom_author_uri%3B%0A++++</id>
  <title>
    select
        1 as atom_id,
        123 as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'blah &lt;b&gt;Bold&lt;/b&gt;' as atom_content,
        'Author' as atom_author_name,
        'https://www.example.com/' as atom_author_uri
    union select
        'atom-id-2' as atom_id,
        'title 2' as atom_title,
        '2019-09-23T21:32:12-07:00' as atom_updated,
        'blah' as atom_content,
        null as atom_author_name,
        null as atom_author_uri;
    </title>
  <updated>2019-10-23T21:32:12-07:00</updated>
  <link href="http://localhost/:memory:.atom?sql=%0A++++select%0A++++++++1+as+atom_id%2C%0A++++++++123+as+atom_title%2C%0A++++++++%272019-10-23T21%3A32%3A12-07%3A00%27+as+atom_updated%2C%0A++++++++%27blah+%3Cb%3EBold%3C%2Fb%3E%27+as+atom_content%2C%0A++++++++%27Author%27+as+atom_author_name%2C%0A++++++++%27https%3A%2F%2Fwww.example.com%2F%27+as+atom_author_uri%0A++++union+select%0A++++++++%27atom-id-2%27+as+atom_id%2C%0A++++++++%27title+2%27+as+atom_title%2C%0A++++++++%272019-09-23T21%3A32%3A12-07%3A00%27+as+atom_updated%2C%0A++++++++%27blah%27+as+atom_content%2C%0A++++++++null+as+atom_author_name%2C%0A++++++++null+as+atom_author_uri%3B%0A++++" rel="self"/>
  <generator uri="https://github.com/simonw/datasette" version="{version}">Datasette</generator>
  <entry>
    <id>1</id>
    <title>123</title>
    <updated>2019-10-23T21:32:12-07:00</updated>
    <author>
      <name>Author</name>
      <uri>https://www.example.com/</uri>
    </author>
    <content type="text">blah &lt;b&gt;Bold&lt;/b&gt;</content>
  </entry>
  <entry>
    <id>atom-id-2</id>
    <title>title 2</title>
    <updated>2019-09-23T21:32:12-07:00</updated>
    <content type="text">blah</content>
  </entry>
</feed>
""".strip()

EXPECTED_ATOM_WITH_LINK = """
<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>http://localhost/:memory:.atom?sql=%0A++++select%0A++++++++%27atom-id%27+as+atom_id%2C%0A++++++++%27title%27+as+atom_title%2C%0A++++++++%272019-10-23T21%3A32%3A12-07%3A00%27+as+atom_updated%2C%0A++++++++%27https%3A%2F%2Fwww.niche-museums.com%2F%27+as+atom_link%2C%0A++++++++%27blah%27+as+atom_content%3B%0A++++</id>
  <title>
    select
        'atom-id' as atom_id,
        'title' as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'https://www.niche-museums.com/' as atom_link,
        'blah' as atom_content;
    </title>
  <updated>2019-10-23T21:32:12-07:00</updated>
  <link href="http://localhost/:memory:.atom?sql=%0A++++select%0A++++++++%27atom-id%27+as+atom_id%2C%0A++++++++%27title%27+as+atom_title%2C%0A++++++++%272019-10-23T21%3A32%3A12-07%3A00%27+as+atom_updated%2C%0A++++++++%27https%3A%2F%2Fwww.niche-museums.com%2F%27+as+atom_link%2C%0A++++++++%27blah%27+as+atom_content%3B%0A++++" rel="self"/>
  <generator uri="https://github.com/simonw/datasette" version="{version}">Datasette</generator>
  <entry>
    <id>atom-id</id>
    <title>title</title>
    <updated>2019-10-23T21:32:12-07:00</updated>
    <content type="text">blah</content>
    <link href="https://www.niche-museums.com/" rel="alternate"/>
  </entry>
</feed>
""".strip()

EXPECTED_ATOM_WITH_HTML = """
<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>http://localhost/:memory:.atom?sql=%0A++++select%0A++++++++%27atom-id%27+as+atom_id%2C%0A++++++++%27title%27+as+atom_title%2C%0A++++++++%272019-10-23T21%3A32%3A12-07%3A00%27+as+atom_updated%2C%0A++++++++%27https%3A%2F%2Fwww.niche-museums.com%2F%27+as+atom_link%2C%0A++++++++%27%3Ch2%3Eblah%3C%2Fh2%3E%3Cscript%3Ealert%28%22bad%22%29%3C%2Fscript%3E%27+as+atom_content_html%3B%0A++++</id>
  <title>
    select
        'atom-id' as atom_id,
        'title' as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'https://www.niche-museums.com/' as atom_link,
        '&lt;h2&gt;blah&lt;/h2&gt;&lt;script&gt;alert("bad")&lt;/script&gt;' as atom_content_html;
    </title>
  <updated>2019-10-23T21:32:12-07:00</updated>
  <link href="http://localhost/:memory:.atom?sql=%0A++++select%0A++++++++%27atom-id%27+as+atom_id%2C%0A++++++++%27title%27+as+atom_title%2C%0A++++++++%272019-10-23T21%3A32%3A12-07%3A00%27+as+atom_updated%2C%0A++++++++%27https%3A%2F%2Fwww.niche-museums.com%2F%27+as+atom_link%2C%0A++++++++%27%3Ch2%3Eblah%3C%2Fh2%3E%3Cscript%3Ealert%28%22bad%22%29%3C%2Fscript%3E%27+as+atom_content_html%3B%0A++++" rel="self"/>
  <generator uri="https://github.com/simonw/datasette" version="{version}">Datasette</generator>
  <entry>
    <id>atom-id</id>
    <title>title</title>
    <updated>2019-10-23T21:32:12-07:00</updated>
    <content type="html">&lt;h2&gt;blah&lt;/h2&gt;&amp;lt;script&amp;gt;alert("bad")&amp;lt;/script&amp;gt;</content>
    <link href="https://www.niche-museums.com/" rel="alternate"/>
  </entry>
</feed>
""".strip()


@pytest.mark.asyncio
async def test_incorrect_sql_returns_400():
    app = Datasette([], immutables=[], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get(
            "http://localhost/:memory:.atom?sql=select+sqlite_version()"
        )
    assert 400 == response.status_code
    assert b"SQL query must return columns" in response.content


@pytest.mark.asyncio
async def test_atom_for_valid_query():
    sql = """
    select
        1 as atom_id,
        123 as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'blah <b>Bold</b>' as atom_content,
        'Author' as atom_author_name,
        'https://www.example.com/' as atom_author_uri
    union select
        'atom-id-2' as atom_id,
        'title 2' as atom_title,
        '2019-09-23T21:32:12-07:00' as atom_updated,
        'blah' as atom_content,
        null as atom_author_name,
        null as atom_author_uri;
    """
    app = Datasette([], immutables=[], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get(
            "http://localhost/:memory:.atom?" + urllib.parse.urlencode({"sql": sql})
        )
    assert 200 == response.status_code
    assert "application/xml; charset=utf-8" == response.headers["content-type"]
    assert (
        EXPECTED_ATOM.format(version=datasette.__version__)
        == response.content.decode("utf-8").strip()
    )


@pytest.mark.asyncio
async def test_atom_with_optional_link():
    sql = """
    select
        'atom-id' as atom_id,
        'title' as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'https://www.niche-museums.com/' as atom_link,
        'blah' as atom_content;
    """
    app = Datasette([], immutables=[], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get(
            "http://localhost/:memory:.atom?" + urllib.parse.urlencode({"sql": sql})
        )
    assert 200 == response.status_code
    assert "application/xml; charset=utf-8" == response.headers["content-type"]
    assert (
        EXPECTED_ATOM_WITH_LINK.format(version=datasette.__version__)
        == response.content.decode("utf-8").strip()
    )


@pytest.mark.asyncio
async def test_atom_with_bad_html():
    sql = """
    select
        'atom-id' as atom_id,
        'title' as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'https://www.niche-museums.com/' as atom_link,
        '<h2>blah</h2><script>alert("bad")</script>' as atom_content_html;
    """
    app = Datasette([], immutables=[], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get(
            "http://localhost/:memory:.atom?" + urllib.parse.urlencode({"sql": sql})
        )
    assert 200 == response.status_code
    assert "application/xml; charset=utf-8" == response.headers["content-type"]
    assert (
        EXPECTED_ATOM_WITH_HTML.format(version=datasette.__version__)
        == response.content.decode("utf-8").strip()
    )


@pytest.mark.asyncio
async def test_atom_link_only_shown_for_correct_queries():
    sql = """
    select
        'atom-id' as atom_id,
        'title' as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'https://www.niche-museums.com/' as atom_link,
        '<h2>blah</h2><script>alert("bad")</script>' as atom_content_html;
    """
    app = Datasette([], immutables=[], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get(
            "http://localhost/:memory:?" + urllib.parse.urlencode({"sql": sql})
        )
    assert 200 == response.status_code
    assert "text/html; charset=utf-8" == response.headers["content-type"]
    assert b'<a href="/:memory:.atom' in response.content
    # But with a different query that link is not shown:
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get(
            "http://localhost/:memory:?"
            + urllib.parse.urlencode({"sql": "select sqlite_version()"})
        )
    assert b'<a href="/:memory:.json' in response.content
    assert b'<a href="/:memory:.atom' not in response.content


@pytest.mark.asyncio
async def test_atom_from_titled_canned_query():
    sql = """
    select
        'atom-id' as atom_id,
        'title' as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'https://www.niche-museums.com/' as atom_link,
        'blah' as atom_content;
    """
    app = Datasette(
        [],
        immutables=[],
        memory=True,
        metadata={
            "databases": {
                ":memory:": {"queries": {"feed": {"sql": sql, "title": "My atom feed"}}}
            }
        },
    ).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/:memory:/feed.atom")
    assert 200 == response.status_code
    assert "application/xml; charset=utf-8" == response.headers["content-type"]
    xml = response.content.decode("utf-8")
    assert "<title>My atom feed</title>" in xml


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "config,should_allow",
    [
        (True, True),
        (False, False),
        ({":memory:": ["latest"]}, True),
        ({":memory:": ["notlatest"]}, False),
    ],
)
async def test_allow_unsafe_html_in_canned_queries(config, should_allow):
    sql = """
    select
        'atom-id' as atom_id,
        'title' as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'https://www.niche-museums.com/' as atom_link,
        '<iframe>An iframe!</iframe>' as atom_content_html;
    """
    metadata = {
        "databases": {
            ":memory:": {"queries": {"latest": {"sql": sql}}},
        },
        "plugins": {"datasette-atom": {"allow_unsafe_html_in_canned_queries": config}},
    }
    app = Datasette(
        [],
        immutables=[],
        memory=True,
        metadata=metadata,
    ).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/:memory:/latest.atom")
    assert 200 == response.status_code
    assert "application/xml; charset=utf-8" == response.headers["content-type"]
    if should_allow:
        assert (
            '<content type="html">&lt;iframe&gt;An iframe!&lt;/iframe&gt;</content>'
            in response.text
        )
    else:
        assert (
            '<content type="html">&amp;lt;iframe&amp;gt;An iframe!&amp;lt;/iframe&amp;gt;</content>'
            in response.text
        )
