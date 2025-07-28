# 🚀 YC S25 Directory

A real-time data explorer for companies in **Y Combinator's Summer 2025 (S25)** batch — including official entries and hidden gems discovered through LinkedIn.

---

## 💡 What This Project Does

This project:
- Scrapes companies from the official [Y Combinator Companies Directory](https://www.ycombinator.com/companies?batch=Summer%202025)
- Enriches data by crawling LinkedIn pages to detect whether companies **mention S25 YC affiliation**
- Surfaces **LinkedIn-only startups** not listed on the YC site but that are likely part of the same batch
- Presents everything in a filterable **Streamlit dashboard**

---

## Features

- Parsing of YC’s dynamic company listings
- LinkedIn analysis
- JSON-based data storage
- Rich filtering and search in Streamlit
- Stats: total companies, LinkedIn-only entries, S25 mentions, and more
- Support for adding similar companies via LinkedIn discovery

---

## How It Works

1. `scraper.py`: Scrapes company data from YC.
2. `linkedin_parser.py`: Enriches company profiles with data from LinkedIn.
3. `streamlit_app/main.py`: Visualizes everything.
4. All config and selectors live in `config.py`.

---

## ▶️ Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the Streamlit app
streamlit run streamlit_app/main.py
