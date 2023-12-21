"""this script generates the taxonomies.csv used to populate the Taxonomy Model
"""

import requests

urls = {}
level_two_taxons = []


def code_from_base_path(dict):
    return dict["base_path"][1:] if dict.get("base_path") else None


def get_taxon(url: str, is_first_level: bool = False):
    if url in urls:
        return

    response = requests.get(url).json()
    parents = response["links"].get("parent_taxons", [{"base_path": None}])
    assert len(parents) == 1
    urls[code_from_base_path(response)] = response["details"]["internal_name"], code_from_base_path(parents[0])
    if is_first_level:
        for child_taxon in response["links"].get("child_taxons", []):
            level_two_taxons.append(child_taxon)


for level_one_taxon in requests.get("https://www.gov.uk/api/content").json()["links"]["level_one_taxons"]:
    get_taxon(level_one_taxon["api_url"], is_first_level=True)

for level_two_taxon in level_two_taxons:
    get_taxon(level_two_taxon["api_url"])

with open("taxonomies.csv", "w") as f:
    f.write('"code", "display", "parent"\n')
    for url, (name, parent) in urls.items():
        f.write(f'"{url}", "{name}", "{parent}"\n')
