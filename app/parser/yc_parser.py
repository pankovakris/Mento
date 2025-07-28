from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import os
import json
import time

from .config import YC_SELECTORS


BASE_URL = "https://www.ycombinator.com/companies?batch=Summer%202025"


def get_rendered_company_links(batch="Summer%202025"):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    driver.get(f"https://www.ycombinator.com/companies?batch={batch}")
    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, YC_SELECTORS["company_link"])
        )
    )

    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

    anchors = driver.find_elements(By.CSS_SELECTOR, YC_SELECTORS["company_link"])
    links = [a.get_attribute("href") for a in anchors]

    driver.quit()
    return links


def parse_company_page(url, driver=None):
    should_close = False
    if driver is None:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)
        should_close = True

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, YC_SELECTORS["name"]))
        )

        name = driver.find_element(By.CSS_SELECTOR, YC_SELECTORS["name"]).text.strip()
        print(name)

        try:
            desc_element = driver.find_element(
                By.CSS_SELECTOR, YC_SELECTORS["description"]
            )
            description = desc_element.text.strip()
        except:
            description = ""

        try:
            website_button = driver.find_element(
                By.CSS_SELECTOR, YC_SELECTORS["website_button"]
            )
            website = website_button.get_attribute("href")
        except:
            website = None

        linkedin_url = None
        social_links = driver.find_elements(By.XPATH, YC_SELECTORS["linkedin_xpath"])
        if social_links:
            linkedin_url = social_links[0].get_attribute("href")

        return {
            "name": name,
            "description": description,
            "website": website,
            "yc_profile_url": url,
            "linkedin_url": linkedin_url,
            "linkedin_mentions_s25": None,
            "source": "Y Combinator",
        }

    except Exception as e:
        print(f"[!] Error parsing {url}: {e}")
        return None

    finally:
        if should_close:
            driver.quit()


def scrape_and_save(output_path="data/yc_s25_companies.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    try:
        links = get_rendered_company_links()
        print(f"Found {len(links)} companies.")

        results = []
        for url in tqdm(links, desc="Parsing company pages"):
            data = parse_company_page(url, driver=driver)
            if data:
                results.append(data)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Saved to {output_path}")

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_and_save()
