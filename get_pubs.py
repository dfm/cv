#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import json
from operator import itemgetter

import ads
from utf8totex import utf8totex

__all__ = ["get_papers"]


def get_papers(author):
    papers = list(ads.SearchQuery(
        author=author,
        fl=["id", "title", "author", "doi", "year", "pubdate", "pub",
            "volume", "page", "identifier", "doctype", "citation_count",
            "bibcode"],
        max_pages=100,
    ))
    dicts = []
    for paper in papers:
        aid = [":".join(t.split(":")[1:]) for t in paper.identifier
               if t.startswith("arXiv:")]
        for t in paper.identifier:
            if len(t.split(".")) != 2:
                continue
            try:
                list(map(int, t.split(".")))
            except ValueError:
                pass
            else:
                aid.append(t)
        try:
            page = int(paper.page[0])
        except (ValueError, TypeError):
            page = None
            if paper.page is not None and paper.page[0].startswith("arXiv:"):
                aid.append(":".join(paper.page[0].split(":")[1:]))
        dicts.append(dict(
            doctype=paper.doctype,
            authors=list(map(utf8totex, paper.author)),
            year=paper.year,
            pubdate=paper.pubdate,
            doi=paper.doi[0] if paper.doi is not None else None,
            title=utf8totex(paper.title[0]),
            pub=paper.pub,
            volume=paper.volume,
            page=page,
            arxiv=aid[0] if len(aid) else None,
            citations=(paper.citation_count
                       if paper.citation_count is not None else 0),
            url="http://adsabs.harvard.edu/abs/" + paper.bibcode,
        ))
    return sorted(dicts, key=itemgetter("pubdate"), reverse=True)


if __name__ == "__main__":
    papers = get_papers("Foreman-Mackey")
    with open("pubs.json", "w") as f:
        json.dump(papers, f, sort_keys=True, indent=2, separators=(",", ": "))
