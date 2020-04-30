# datasette-atom

[![PyPI](https://img.shields.io/pypi/v/datasette-atom.svg)](https://pypi.org/project/datasette-atom/)
[![CircleCI](https://circleci.com/gh/simonw/datasette-atom.svg?style=svg)](https://circleci.com/gh/simonw/datasette-atom)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-atom/blob/master/LICENSE)

Datasette plugin that adds support for generating [Atom feeds](https://validator.w3.org/feed/docs/atom.html) with the results of a SQL query.

## Installation

Install this plugin in the same environment as Datasette to enable the `.atom` output extension.

    $ pip install datasette-atom

## Usage

To create an Atom feed you need to define a custom SQL query that returns a required set of columns:

* `atom_id` - a unique ID for each row. [This article](https://web.archive.org/web/20080211143232/http://diveintomark.org/archives/2004/05/28/howto-atom-id) has suggestions about ways to create these IDs.
* `atom_title` - a title for that row.
* `atom_updated` - an [RFC 3339](http://www.faqs.org/rfcs/rfc3339.html) timestamp representing the last time the entry was modified in a significant way. This can usually be the time that the row was created.

The following columns are optional:

* `atom_content` - content that should be shown in the feed. This will be treated as a regular string, so any embedded HTML tags will be escaped when they are displayed.
* `atom_content_html` - content that should be shown in the feed. This will be treated as an HTML string, and will be sanitized using [Bleach](https://github.com/mozilla/bleach) to ensure it does not have any malicious code in it before being returned as part of a `<content type="html">` Atom element. If both are provided, this will be used in place of `atom_content`.
* `atom_link` - a URL that should be used as the link that the feed entry points to.
* `atom_author_name` - the name of the author of the entry. If you provide this you can also provide `atom_author_uri` and `atom_author_email` with a URL and e-mail address for that author.

A query that returns these columns can then be returned as an Atom feed by adding the `.atom` extension.

## Example

Here is an example SQL query which generates an Atom feed for new entries on [www.niche-museums.com](https://www.niche-museums.com/):

```sql
select
  'tag:niche-museums.com,' || substr(created, 0, 11) || ':' || id as atom_id,
  name as atom_title,
  created as atom_updated,
  'https://www.niche-museums.com/browse/museums/' || id as atom_link,
  coalesce(
    '<img src="' || photo_url || '?w=800&amp;h=400&amp;fit=crop&amp;auto=compress">',
    ''
  ) || '<p>' || description || '</p>' as atom_content_html
from
  museums
order by
  created desc
limit
  15
```

You can try this query by [pasting it in here](https://www.niche-museums.com/browse) - then click the `.atom` link to see it as an Atom feed.
