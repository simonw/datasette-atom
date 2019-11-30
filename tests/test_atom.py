from .utils import make_app_client
import datasette
import urllib.parse

EXPECTED_ATOM = """
<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>:memory:/051e4d600fc8678005e17f13e1b4065a14833423d0da19f4f34aaeab87822cd4</id>
  <title>
    select
        'atom-id' as atom_id,
        'title' as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'blah' as atom_content
    union select
        'atom-id-2' as atom_id,
        'title 2' as atom_title,
        '2019-09-23T21:32:12-07:00' as atom_updated,
        'blah' as atom_content;
    </title>
  <updated>2019-10-23T21:32:12-07:00</updated>
  <generator uri="https://github.com/simonw/datasette" version="{version}">Datasette</generator>
  <entry>
    <id>atom-id</id>
    <title>title</title>
    <updated>2019-10-23T21:32:12-07:00</updated>
    <content type="text">blah</content>
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


def test_incorrect_sql_returns_400():
    app = make_app_client()
    response = app.get("/:memory:.atom?sql=select+sqlite_version()")
    assert 400 == response.status
    assert "SQL query must return columns" in response.text


def test_atom_for_valid_query():
    sql = """
    select
        'atom-id' as atom_id,
        'title' as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'blah' as atom_content
    union select
        'atom-id-2' as atom_id,
        'title 2' as atom_title,
        '2019-09-23T21:32:12-07:00' as atom_updated,
        'blah' as atom_content;
    """
    app = make_app_client()
    response = app.get("/:memory:.atom?" + urllib.parse.urlencode({"sql": sql}))
    assert 200 == response.status
    assert "application/xml; charset=utf-8" == response.headers["content-type"]
    assert EXPECTED_ATOM.format(version=datasette.__version__) == response.text.strip()


def test_atom_with_optional_link():
    sql = """
    select
        'atom-id' as atom_id,
        'title' as atom_title,
        '2019-10-23T21:32:12-07:00' as atom_updated,
        'https://www.niche-museums.com/' as atom_link,
        'blah' as atom_content;
    """
    app = make_app_client()
    response = app.get("/:memory:.atom?" + urllib.parse.urlencode({"sql": sql}))
    assert 200 == response.status
    assert "application/xml; charset=utf-8" == response.headers["content-type"]
    assert (
        EXPECTED_ATOM_WITH_LINK.format(version=datasette.__version__)
        == response.text.strip()
    )
