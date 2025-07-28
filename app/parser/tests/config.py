YC_SELECTORS = {
    "company_link": "a[class*='company']",
    "name": "h1[class*='text-3xl font-bold']",
    "description": "div[class*='prose max-w-full whitespace-pre-line']",
    "website_button": "a[class*='mb-2 whitespace-nowrap md:mb-0']",
    "linkedin_xpath": "//a[contains(@href, 'linkedin.com/company')]",
}

LINKEDIN_SELECTORS = {
    "tagline": "top-card-layout__title",
    "short_description": "line-clamp-2",
    "full_description": "break-words",
    "web": "link-without-visited-state",
    "anchors": {"data-tracking-control-name": "similar-pages"},
}

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}

YC_TAGS = ["yc", "ycombinator", "y combinator"]
S25_TAGS = ["s25", "summer 2025", "summer2025", "2025summer", "2025 summer"]
