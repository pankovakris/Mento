import requests
from bs4 import BeautifulSoup
import os
import json

from .config import LINKEDIN_SELECTORS, HEADERS, YC_TAGS, S25_TAGS


def linkedin_check_yc_mention(linkedin_url):
    try:
        resp = requests.get(linkedin_url, headers=HEADERS, timeout=10)

        if resp.status_code != 200:
            print(f"{linkedin_url} → HTTP {resp.status_code}")
            return None, None

        soup = BeautifulSoup(resp.text, "html.parser")

        text_blocks = []

        tagline = soup.find(
            "h1", class_=lambda c: c and LINKEDIN_SELECTORS["tagline"] in c
        )
        if tagline:
            text_blocks.append(("name", tagline.get_text(strip=True).lower()))

        short_desc = soup.find("span", class_=LINKEDIN_SELECTORS["short_description"])
        if short_desc:
            text_blocks.append(("short_desc", short_desc.get_text(strip=True).lower()))

        full_desc = soup.find(
            "p", class_=lambda c: c and LINKEDIN_SELECTORS["full_description"] in c
        )
        if full_desc:
            text_blocks.append(("full_desc", full_desc.get_text(strip=True).lower()))

        for label, block in text_blocks:
            if not block:
                continue
            mentions_yc = any(tag in block for tag in YC_TAGS)
            mentions_s25 = any(tag in block for tag in S25_TAGS)
            if mentions_yc and mentions_s25:
                return True, {"location": label, "snippet": block}

        return False, None

    except Exception as e:
        print(f"[!] Failed to parse {linkedin_url}: {e}")
        return None, None


def enrich_all_from_json(input_path="data/yc_s25_companies.json"):
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        companies = json.load(f)

    updated = 0
    for company in companies:
        if not company.get("linkedin_url"):
            continue
        if company.get("linkedin_mentions_s25") is not None:
            continue  # Already enriched

        print(f"🔎 Checking {company['name']}...")

        matched, match_info = linkedin_check_yc_mention(company["linkedin_url"])
        if matched is not None:
            company["linkedin_mentions_s25"] = matched
            company["linkedin_match"] = match_info
            updated += 1
            print(f"Result: {matched} @ {match_info}")
        else:
            print(f"Could not determine for {company['name']}")

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)

    print(f"Done. Updated {updated} companies.")


DATA_FILE = "app/parser/data/yc_s25_companies.json"


def extract_and_check(linkedin_url):
    """Scrape LinkedIn and format new company entry if it's not in existing data."""
    matched, match_info = linkedin_check_yc_mention(linkedin_url)

    if matched is None:
        return None  # failed to load

    try:
        resp = requests.get(linkedin_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        name = soup.find("h1", class_=lambda c: c and "top-card-layout__title" in c)
        short_desc = soup.find("span", class_="line-clamp-2")
        full_desc = soup.find("p", class_=lambda c: c and "break-words" in c)

        return {
            "name": name.get_text(strip=True) if name else "Unknown",
            "description": (
                full_desc.get_text(strip=True)
                if full_desc
                else short_desc.get_text(strip=True) if short_desc else ""
            ),
            "website": None,
            "yc_profile_url": None,
            "linkedin_url": linkedin_url,
            "linkedin_mentions_s25": matched,
            "linkedin_match": match_info,
            "source": "linkedin",
        }

    except Exception as e:
        print(f"[!] Failed to parse {linkedin_url} after match: {e}")
        return None


def load_existing_companies(path=DATA_FILE):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_companies(companies, path=DATA_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)


def add_new_linkedin_companies(linkedin_urls):
    companies = load_existing_companies()
    existing_links = {c["linkedin_url"] for c in companies if c.get("linkedin_url")}

    new_entries = []
    for url in linkedin_urls:
        if url in existing_links:
            print(f"Already exists: {url}")
            continue

        print(f"Scraping new company: {url}")
        data = extract_and_check(url)
        if data:
            companies.append(data)
            new_entries.append(data)

    save_companies(companies)

    print(f"Added {len(new_entries)} new companies.")


if __name__ == "__main__":
    enrich_all_from_json()
