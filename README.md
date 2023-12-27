# Cuppy - A Content Understanding Platform in Python

## Overview

Cuppy is a work-in progress "content understanding platform in Python". Right now, it supports is limited to some basic extractions
of web content (text/html). Given a list of URLs, cuppy's webparser.py will extract the following:

- title from title tag
- title from og:title
- canonical url from headers (rare in the wild)
- canonical url from link rel='canonical'
- og:url
- og:title
- description (from meta name="description")

Results are stored in a sqllite3 database in the urls table. For efficiency Cuppy supports etags to see if the content has been modified.

With -r or --robotstxt Cuppy observes robots.txt to see if it can/cannot fetch the URL. Robots.txt are stored in the robots_txt table and can be refetched from there.

With -f or --force, Cuppy will ignore etag when requesting content, forcing a refresh when possibly the content would be unmodified on the server vs. the cached version.

## Requirements

- Python 3.8+
- requirements.txt: requests, protego


