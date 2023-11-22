"""this script generates the taxonomies.csv used to populate the Taxonomy Model
"""

import requests

urls = {}


def get_taxon(url: str):
    if url in urls:
        return

    response = requests.get(url).json()
    parents = response["links"].get("parent_taxons", [{"api_url": None}])
    assert len(parents) == 1
    urls[url] = response["details"]["internal_name"], parents[0]["api_url"]
    for child_taxon in response["links"].get("child_taxons", []):
        get_taxon(child_taxon["api_url"])


for level_one_taxon in requests.get("https://www.gov.uk/api/content").json()["links"]["level_one_taxons"]:
    get_taxon(level_one_taxon["api_url"])


with open("taxonomies.csv", "w") as f:
    for url, (name, parent) in urls.items():
        f.write(f'"{url}", "{name}", "{parent}"\n')
