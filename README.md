# Cuppy - A Content Understanding Platform in Python

Cuppy is a work-in progress "content understanding platform in Python". Right now, it supports is limited to some basic extractions
of web content (text/html). Given a list of URLs, cuppy's webparser.py will extract the following:

- title from title tag
- title from og:title
- canonical url from headers (rare in the wild)
- canonical url from link rel='canonical'
- og:url

Results are stored in a sqllite3 database in the urls table.

With --robotstxt Cuppy observe robots.txt to see if it can/cannot fetch the URL. Robots.txt are stored in the robots_txt table and can be refetched from there.


