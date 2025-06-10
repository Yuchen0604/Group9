import pandas as pd
import os
import re
import requests
from bs4 import UnicodeDammit, BeautifulSoup

# Multiple Wikipedia page URLs (including other languages)
urls = [
    "https://en.wikipedia.org/wiki/Seven_Summits",
    "https://en.wikipedia.org/wiki/Eight-thousander",
    "https://en.wikipedia.org/wiki/List_of_mountains_of_the_Alps_over_4000_metres",
    "https://en.wikipedia.org/wiki/Lists_of_earthquakes",
    "https://en.wikipedia.org/wiki/Highest_unclimbed_mountain#List_of_highest_unclimbed_peaks",
    "https://en.wikipedia.org/wiki/List_of_highest_mountains_on_Earth",
    "https://en.wikipedia.org/wiki/Lakes_of_Titan",
    "https://en.wikipedia.org/wiki/List_of_largest_lakes_of_Europe",
    "https://en.wikipedia.org/wiki/List_of_lakes_by_area",
    # You can continue adding more URLs
]




# Languages to include (use ISO 639-1 codes)
desired_languages = ['en', 'zh', 'de', 'it', 'nl', 'et']  # English, Chinese, German, Italian, Dutch, Estonian

# Helper function: convert URL to a valid folder name
def url_to_folder_name(url):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', url.split("/wiki/")[-1])

# Helper function: get URLs of the same Wikipedia entity in other languages
def get_language_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        lang_links = soup.select("li.interlanguage-link > a")
        return {
            link.get("hreflang"): ("https:" + link["href"] if link["href"].startswith("//") else link["href"])
            for link in lang_links
            if link.has_attr("href") and link.get("hreflang") in desired_languages
        }
    except Exception as e:
        print(f"Failed to fetch language links for {url}: {e}")
        return {}

log_entries = []
successful_entities = []

# Process each entity and its language versions
for base_url in urls:
    entity_folder = url_to_folder_name(base_url)
    os.makedirs(entity_folder, exist_ok=True)

    language_urls = {"en": base_url}  # include original English page
    language_urls.update(get_language_links(base_url))

    found_languages = 0

    for lang in desired_languages:
        lang_url = language_urls.get(lang)
        lang_folder = os.path.join(entity_folder, lang)
        os.makedirs(lang_folder, exist_ok=True)

        if not lang_url:
            log_entries.append(f"[MISSING] {entity_folder} - Language '{lang}' page not found.")
            continue

        try:
            print(f"Processing URL: {lang_url} ({lang})")
            response = requests.get(lang_url)
            response.raise_for_status()
            html = UnicodeDammit(response.content).unicode_markup
            tables = pd.read_html(html)
            log_entries.append(f"[OK] {entity_folder} - {lang}: {len(tables)} tables found")

            for i, table in enumerate(tables):
                filename = os.path.join(lang_folder, f"table_{i+1}.csv")
                table.to_csv(filename, index=False)
                print(f"Saved: {filename}")

            found_languages += 1

        except Exception as e:
            log_entries.append(f"[ERROR] {entity_folder} - {lang}: {e}")
            print(f"Failed to process: {lang_url}\nError: {e}")

    if found_languages >= 3:
        successful_entities.append(base_url)

# Save log file
with open("wikipedia_scrape_log.txt", "w", encoding="utf-8") as log_file:
    log_file.write("\n".join(log_entries))
    log_file.write("\n\n")
    log_file.write(f"Total entities with at least 3 language pages: {len(successful_entities)}\n")
    log_file.write("Entities meeting the criteria:\n")
    log_file.write("\n".join(successful_entities))

print("\nLog written to wikipedia_scrape_log.txt")
