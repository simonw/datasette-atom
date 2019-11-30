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
* `atom_content` - content that should be shown in the feed. This will be treated as a regular string, so any embedded HTML tags will be escaped when they are displayed.

You can also return an optional `atom_link` column, which will be used as a URL that the entry in the feed links to.

A query that returns these columns can then be returned as an Atom feed by adding the `.atom` extension.

## Example

Here is an example SQL query which generates an Atom feed for new entries on [www.niche-museums.com](https://www.niche-museums.com/):

```sql
select
  'tag:niche-museums.com,' || substr(created, 0, 11) || ':' || id as atom_id,
  name as atom_title,
  created as atom_updated,
  'https://www.niche-museums.com/browse/museums/' || id as atom_link,
  description as atom_content
from
  museums
order by
  created desc
limit 15
```

You can [try the query here](https://www.niche-museums.com/browse?sql=select%0D%0A++%27tag%3Aniche-museums.com%2C%27+%7C%7C+substr%28created%2C+0%2C+11%29+%7C%7C+%27%3A%27+%7C%7C+id+as+atom_id%2C%0D%0A++name+as+atom_title%2C%0D%0A++created+as+atom_updated%2C%0D%0A++%27https%3A%2F%2Fwww.niche-museums.com%2Fbrowse%2Fmuseums%2F%27+%7C%7C+id+as+atom_link%2C%0D%0A++description+as+atom_content%0D%0Afrom%0D%0A++museums%0D%0Aorder+by%0D%0A++created+desc). Here is [the atom feed](https://www.niche-museums.com/browse.atom?sql=select%0D%0A++%27tag%3Aniche-museums.com%2C%27+%7C%7C+substr%28created%2C+0%2C+11%29+%7C%7C+%27%3A%27+%7C%7C+id+as+atom_id%2C%0D%0A++name+as+atom_title%2C%0D%0A++created+as+atom_updated%2C%0D%0A++%27https%3A%2F%2Fwww.niche-museums.com%2Fbrowse%2Fmuseums%2F%27+%7C%7C+id+as+atom_link%2C%0D%0A++description+as+atom_content%0D%0Afrom%0D%0A++museums%0D%0Aorder+by%0D%0A++created+desc) that is generated when you swap in the `.atom` extension.