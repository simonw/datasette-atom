import datasette
from datasette.app import Datasette
import urllib.parse
import pytest
import httpx

EXPECTED_ATOM = """
<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>:memory:/d765251b024da6156f346354d5ca573b2c8717bc71d82d2e1a2fdd55b9a44215</id>
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
  <id>:memory:/652f6714d6b9efa3657b50fe0ae8cbac13ccefb2ecbdbafe527c6f6fe97556da</id>
  <title>
    select
        'atom-id' as atom_id,
        'title' as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'https://www.niche-museums.com/' as atom_link,
        'blah' as atom_content;
    </title>
  <updated>2019-10-23T21:32:12-07:00</updated>
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
  <id>:memory:/beb5a312c0daa591d04d7dfb5a79eb8bbbcd6f84ebe90cf0345ed8c24bb2ff22</id>
  <title>
    select
        'atom-id' as atom_id,
        'title' as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'https://www.niche-museums.com/' as atom_link,
        '&lt;h2&gt;blah&lt;/h2&gt;&lt;script&gt;alert("bad")&lt;/script&gt;' as atom_content_html;
    </title>
  <updated>2019-10-23T21:32:12-07:00</updated>
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
            "http://localhost/:memory:?" + urllib.parse.urlencode({"sql": "select sqlite_version()"})
        )
    assert b'<a href="/:memory:.json' in response.content
    assert b'<a href="/:memory:.atom' not in response.content