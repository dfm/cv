use adsabs::prelude::*;

fn main() -> Result<(), AdsError> {
    let client = Ads::from_env()?;

    let docs = client
        .search("author:\"Foreman-Mackey\" AND (doctype:\"article\" OR doctype:\"eprint\")")
        .fl("id,title,author,doi,year,pubdate,pub,volume,page,identifier,doctype,citation_count,bibcode")
        .sort("date")
        .iter_docs().map(|doc|
    {
        // Here I'm just removing HTML encoding since the API will encode
        // characters like '&' as '&amp;', for example. 
        doc.map(|mut doc|{
            doc.title = doc.title.map(|t| {
                t.iter()
                    .map(|t| html_escape::decode_html_entities(t).to_string())
                    .collect::<Vec<_>>()
            });
            doc
        })
    }).collect::<Result<Vec<_>, AdsError>>()?;

    std::fs::write("data/ads.json", serde_json::to_string_pretty(&docs)?)?;
    Ok(())
}
