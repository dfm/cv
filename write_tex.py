#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import json
from datetime import date
from operator import itemgetter

__all__ = ["format_pub"]

JOURNAL_MAP = {
    "ArXiv e-prints": "ArXiv",
    "Monthly Notices of the Royal Astronomical Society": "\\mnras",
    "The Astrophysical Journal": "\\apj",
    "The Astronomical Journal": "\\aj",
    "Publications of the Astronomical Society of the Pacific": "\\pasp",
    "IAU General Assembly": "IAU",
    "American Astronomical Society Meeting Abstracts": "AAS",
}


def format_pub(args):
    ind, pub = args
    fmt = "\\item[{{\\color{{numcolor}}\\scriptsize{0}}}] ".format(ind)
    n = [i for i in range(len(pub["authors"]))
         if "Foreman-Mackey, D" in pub["authors"][i]][0]
    pub["authors"][n] = "\\textbf{Foreman-Mackey, Daniel}"
    if len(pub["authors"]) > 5:
        fmt += ", ".join(pub["authors"][:4])
        fmt += ", \etal"
        if n >= 4:
            fmt += "\\ (incl.\\ \\textbf{DFM})"
    elif len(pub["authors"]) > 1:
        fmt += ", ".join(pub["authors"][:-1])
        fmt += ", \\& " + pub["authors"][-1]
    else:
        fmt += pub["authors"][0]

    fmt += ", {0}".format(pub["year"])

    if pub["doi"] is not None:
        fmt += ", \\doi{{{0}}}{{{1}}}".format(pub["doi"], pub["title"])
    else:
        fmt += ", " + pub["title"]

    if not pub["pub"] in [None, "ArXiv e-prints"]:
        fmt += ", " + JOURNAL_MAP.get(pub["pub"].strip("0123456789# "),
                                      pub["pub"])

    if pub["volume"] is not None:
        fmt += ", \\textbf{{{0}}}".format(pub["volume"])

    if pub["page"] is not None:
        fmt += ", {0}".format(pub["page"])

    if pub["arxiv"] is not None:
        fmt += " (\\arxiv{{{0}}})".format(pub["arxiv"])

    if pub["citations"] > 1:
        fmt += " [\\href{{{0}}}{{{1} citations}}]".format(pub["url"],
                                                          pub["citations"])

    return fmt


if __name__ == "__main__":
    with open("pubs.json", "r") as f:
        pubs = json.load(f)
    with open("other_pubs.json", "r") as f:
        other_pubs = json.load(f)
    with open("select_pubs.json", "r") as f:
        select_pubs = json.load(f)
    for p in other_pubs:
        for p1 in pubs:
            if (p1["arxiv"] is not None and p["arxiv"] == p1["arxiv"]) or \
                    p["title"] == p1["title"]:
                p["citations"] = max(p["citations"], p1["citations"])
                pubs.remove(p1)
    pubs = sorted(pubs + other_pubs, key=itemgetter("pubdate"), reverse=True)
    pubs = [p for p in pubs if p["doctype"] in ["article", "eprint"]]
    ref = [p for p in pubs if p["doctype"] == "article"]
    unref = [p for p in pubs if p["doctype"] == "eprint"]

    # Compute citation stats
    npapers = len(ref)
    nfirst = sum(1 for p in pubs if "Foreman-Mackey" in p["authors"][0])
    cites = sorted((p["citations"] for p in pubs), reverse=True)
    ncitations = sum(cites)
    hindex = sum(c >= i for i, c in enumerate(cites))

    summary = (("refereed: {1} / first author: {2} / citations: {3} / "
               "h-index: {4} ({0})")
               .format(date.today(), npapers, nfirst, ncitations, hindex))
    with open("pubs_summary.tex", "w") as f:
        f.write(summary)

    ref = list(map(format_pub, zip(range(len(ref), 0, -1), ref)))
    unref = list(map(format_pub, zip(range(len(unref), 0, -1), unref)))
    with open("pubs_ref.tex", "w") as f:
        f.write("\n\n".join(ref))
    with open("pubs_unref.tex", "w") as f:
        f.write("\n\n".join(unref))

    # Choose the selected publications
    selected = []
    for s in select_pubs:
        k = s["key"]
        v = s["value"]
        for doc in pubs:
            if doc[k] == v:
                selected.append(doc)
                break
    selected = sorted(selected, key=itemgetter("pubdate"), reverse=True)
    selected = list(map(format_pub, zip(range(len(selected), 0, -1),
                                        selected)))
    with open("pubs_select.tex", "w") as f:
        f.write("\n\n".join(selected))
