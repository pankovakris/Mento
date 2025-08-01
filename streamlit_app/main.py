# streamlit_app/main.py

import json
import streamlit as st
import pandas as pd

st.set_page_config(page_title="YC S25 Directory", layout="wide")
st.title("🚀 Y Combinator S25 Companies")

try:
    with open(
        "./app/parser/data/yc_s25_companies_deduplicated.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
except FileNotFoundError:
    st.error("No data file found. Run the scraper first.")
    st.stop()

df = pd.DataFrame(data)

if "source" not in df.columns:
    df["source"] = "yc"
df["source"] = df["source"].fillna("yc").replace("nan", "yc")
if "linkedin_mentions_s25" not in df.columns:
    df["linkedin_mentions_s25"] = False
if "linkedin_match" not in df.columns:
    df["linkedin_match"] = None

st.sidebar.header("📊 Filters")
search = st.sidebar.text_input("🔍 Search by name or description")
source_filter = st.sidebar.multiselect(
    "🛠 Source",
    options=sorted(df["source"].unique().tolist()),
    default=sorted(df["source"].unique().tolist()),
)
mention_filter = st.sidebar.radio(
    "🔬 Mentions YC S25 on LinkedIn?", options=["All", "Yes", "No"], index=0
)

filtered_df = df[df["source"].isin(source_filter)]

if mention_filter == "Yes":
    filtered_df = filtered_df[filtered_df["linkedin_mentions_s25"] == True]
elif mention_filter == "No":
    filtered_df = filtered_df[filtered_df["linkedin_mentions_s25"] == False]

if search:
    filtered_df = filtered_df[
        filtered_df["name"].str.contains(search, case=False, na=False)
        | filtered_df["description"].str.contains(search, case=False, na=False)
    ]


st.markdown("### 📈 Stats")
col1, col2, col3 = st.columns(3)
col1.metric("Total Companies", len(df))
col2.metric("Unique from LinkedIn", df[df["source"] == "linkedin"].shape[0])
col3.metric(
    "S25 mentioned on LinkedIn", df[df["linkedin_mentions_s25"] == True].shape[0]
)

st.markdown("### 🗃 All Companies")
st.dataframe(
    filtered_df[
        [
            "name",
            "description",
            "website",
            "yc_profile_url",
            "linkedin_url",
            "linkedin_mentions_s25",
            "source",
        ]
    ],
    use_container_width=True,
)

st.markdown("---")
st.subheader("🔎 Company Cards")

for _, row in filtered_df.iterrows():
    with st.expander(f":star2: {row['name']}"):
        st.write(
            row["description"] if row["description"] else "🫥 No description available."
        )

        st.markdown(
            f"- 🌐 [Website]({row['website']})"
            if row["website"]
            else "- 🌐 Couldn't find the website :("
        )
        st.markdown(
            f"- 💼 [LinkedIn]({row['linkedin_url']})"
            if row["linkedin_url"]
            else "- 💼 Couldn't find the LinkedIn URL :("
        )
        st.markdown(
            f"- 🏷️ [YC Profile]({row['yc_profile_url']})"
            if row["yc_profile_url"]
            else "- 🏷️ YC profile not listed :("
        )

        source_label = row["source"] if row["source"] else "yc"
        if source_label == "yc":
            source_label = "Y Combinator"

        st.markdown(f"- 📦 Source: **{source_label}**")

        if row["linkedin_mentions_s25"] is None:
            if not row["linkedin_url"]:
                st.markdown(
                    "- 🧬 S25 mentioned on LinkedIn: LinkedIn profile not available"
                )
            else:
                st.markdown("- 🧬 S25 mentioned on LinkedIn: Unknown")
        else:
            st.markdown(
                f"- 🧬 S25 mentioned on LinkedIn: **{row['linkedin_mentions_s25']}**"
            )

        match = row.get("linkedin_match")
        if isinstance(match, dict):
            st.markdown(
                f"- 🧠 Matched in **{match['location']}**: _{match['snippet']}_"
            )
