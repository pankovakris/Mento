import requests
from bs4 import BeautifulSoup
import time
import os
import json
from linkedin_parser import linkedin_check_yc_mention
import re
from config import LINKEDIN_SELECTORS, HEADERS

DATA_FILE = "data/yc_s25_companies.json"


def extract_and_check(linkedin_url):
    """Scrape LinkedIn and format new company entry if it's not in existing data."""
    time.sleep(1)  # For rate limits

    matched, match_info = linkedin_check_yc_mention(linkedin_url)

    time.sleep(2)  # For rate limits

    if matched is None or not matched:
        return None

    try:
        resp = requests.get(linkedin_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        name = soup.find(
            "h1", class_=lambda c: c and LINKEDIN_SELECTORS["tagline"] in c
        )
        short_desc = soup.find(
            "span", class_=lambda c: c and LINKEDIN_SELECTORS["short_description"] in c
        )
        full_desc = soup.find(
            "p", class_=lambda c: c and LINKEDIN_SELECTORS["full_description"] in c
        )

        resp_about = requests.get(linkedin_url, headers=HEADERS, timeout=10)
        soup_about = BeautifulSoup(resp_about.text, "html.parser")
        website = soup_about.find("span", class_=LINKEDIN_SELECTORS["web"])

        return {
            "name": name.get_text(strip=True) if name else "Unknown",
            "description": (
                full_desc.get_text(strip=True)
                if full_desc
                else short_desc.get_text(strip=True) if short_desc else ""
            ),
            "website": website,
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


def save_companies(companies, path="data/yc_s25_companies_deduplicated.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)


def normalize_linkedin_url(url):
    if not url:
        return None
    parts = url.rstrip("/").split("linkedin.com/")
    return parts[1] if len(parts) > 1 else url.rstrip("/")


def add_new_linkedin_companies(linkedin_urls):
    companies = load_existing_companies()

    new_entries = []

    existing_links = {
        normalize_linkedin_url(c["linkedin_url"])
        for c in companies
        if c.get("linkedin_url")
    }

    for url in linkedin_urls:
        normalized = normalize_linkedin_url(url)
        print(normalized, existing_links)
        if normalized in existing_links:
            print(f"Already exists: {url}")
            continue

        print(f"Scraping new company: {url}")
        data = extract_and_check(url)
        if data:
            companies.append(data)
            new_entries.append(data)
            existing_links.add(url)

    save_companies(companies)

    print(f"Added {len(new_entries)} new companies.")


def extract_similar_linkedin_companies():
    """Extract similar companies listed on a LinkedIn company page."""
    links = []
    try:
        companies = load_existing_companies()
        existing_links = {c["linkedin_url"] for c in companies if c.get("linkedin_url")}

        for linkedin_url in existing_links:
            resp = requests.get(linkedin_url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                print(f"Failed to load {linkedin_url}")
                print(resp.text)
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            anchors = soup.find_all("a", LINKEDIN_SELECTORS["anchors"])

            for a in anchors:
                href = a.get("href")
                if (
                    href
                    and "/company/" in href
                    and href.startswith("https://www.linkedin.com/company/")
                ):
                    links.append(href[0:-18])

    except Exception as e:
        print(f"[!] Error while parsing: {e}")
        return list(set(links))

    return list(set(links))


def normalize_name(name):
    if not name:
        return ""
    name = name.lower().strip()
    name = re.sub(r"\(.*?\)", "", name)  # remove (YC S25), (YC), etc.
    name = re.sub(r"[^a-z0-9]", "", name)  # remove non-alphanum
    return name


def deduplicate_and_merge(companies):
    seen = {}
    duplicates_removed = 0

    for company in companies[:]:  # copy to avoid mutation issues
        norm = normalize_name(company["name"])

        if norm not in seen:
            seen[norm] = company
            continue

        primary = seen[norm]
        secondary = company

        if primary.get("yc_profile_url"):
            if not primary.get("linkedin_url") and secondary.get("linkedin_url"):
                primary["linkedin_url"] = secondary["linkedin_url"]
                primary["linkedin_mentions_s25"] = secondary.get(
                    "linkedin_mentions_s25"
                )
                primary["linkedin_match"] = secondary.get("linkedin_match")
        else:
            # swap if secondary has YC profile
            if secondary.get("yc_profile_url"):
                if not secondary.get("linkedin_url") and primary.get("linkedin_url"):
                    secondary["linkedin_url"] = primary["linkedin_url"]
                    secondary["linkedin_mentions_s25"] = primary.get(
                        "linkedin_mentions_s25"
                    )
                    secondary["linkedin_match"] = primary.get("linkedin_match")
                seen[norm] = secondary

        companies.remove(secondary)
        duplicates_removed += 1

    print(f"Deduplication complete. Removed {duplicates_removed} duplicates.")
    return companies


if __name__ == "__main__":
    similar_links = extract_similar_linkedin_companies()
    add_new_linkedin_companies(similar_links)

    companies = load_existing_companies()
    companies_clean = deduplicate_and_merge(companies)
    save_companies(companies_clean)
