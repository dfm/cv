# Dan Foreman-Mackey's CV

[![Auto update](https://github.com/dfm/cv/workflows/Auto%20update/badge.svg)](https://github.com/dfm/cv/actions?query=workflow%3A%22Auto+update%22) [![Latest PDF](https://img.shields.io/badge/pdf-latest-orange.svg)](https://docs.google.com/viewer?url=https://github.com/dfm/cv/raw/main-pdf/cv_pubs.pdf)

Licensed under [Creative Commons Attribution](http://creativecommons.org/licenses/by/4.0/)

<hr>

$if(titleblock)$
$titleblock$

$endif$
$for(header-includes)$
$header-includes$

$endfor$
$for(include-before)$
$include-before$

$endfor$
$if(toc)$
$table-of-contents$

$endif$
$body$
$for(include-after)$

$include-after$
$endfor$
