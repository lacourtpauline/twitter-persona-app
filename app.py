
import streamlit as st
import pandas as pd
import altair as alt
from utils import compute_engagement, get_engagement_string, compute_keyword_engagement
from genai import GenAI

st.set_page_config(page_title="🌌 TweetSynth: Cyber Persona Generator", layout="wide")
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            background-color: #0f0f1a !important;
            color: #f8f8ff !important;
            font-family: 'Orbitron', sans-serif;
        }
        h1, h2, h3 {
            color: #ff0090 !important;
            text-shadow: 0 0 10px #ff0090;
        }
    </style>
""", unsafe_allow_html=True)

genai = GenAI()

st.sidebar.title("🌐 Navigation")
page = st.sidebar.radio("Go to", ["Home", "Keyword Engagement", "Persona Tweet"])

if "df" not in st.session_state:
    st.session_state.df = None
if "engagement_summary" not in st.session_state:
    st.session_state.engagement_summary = None

if page == "Home":
    st.title("🚀 Home - Tweet Analyzer")
    uploaded = st.file_uploader("Upload tweet CSV", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        df = compute_engagement(df)
        st.session_state.df = df
        with st.spinner("Analyzing engagement ..."):
            summary = get_engagement_string(df, genai)
        st.session_state.engagement_summary = summary

        st.subheader("Top Tweets")
        st.dataframe(df[['text', 'engagement']].head(20).rename(columns={"text": "Tweet", "engagement": "Engagement"}))

        st.markdown(f"<div style='margin-top:20px; padding:20px; background:#1c1c2e; border-left:5px solid #00ffe7; border-radius:8px'>{summary}</div>", unsafe_allow_html=True)

elif page == "Keyword Engagement":
    st.title("📊 Keyword Engagement")
    if st.session_state.df is None:
        st.warning("Please upload a tweet CSV on the Home page first.")
    else:
        keywords_string = st.text_input("Keywords (comma-separated)", "")
        if st.button("Analyze") and keywords_string:
            df_keywords = compute_keyword_engagement(st.session_state.df, keywords_string)
            df_long = df_keywords.melt(id_vars=['keyword', 'pvalue_bh'], 
                                       value_vars=['engagement_false', 'engagement_true'],
                                       var_name='has_keyword', value_name='engagement')
            df_long['has_keyword'] = df_long['has_keyword'].map({'engagement_false': 'False', 'engagement_true': 'True'})

            chart = alt.Chart(df_long).mark_bar().encode(
                x=alt.X('keyword:N', title='Keyword'),
                y=alt.Y('engagement:Q', title='Engagement'),
                color='has_keyword:N',
                tooltip=['keyword', 'has_keyword', 'engagement']
            ).properties(title="Keyword Engagement")

            st.altair_chart(chart, use_container_width=True)

            for _, row in df_keywords.iterrows():
                st.caption(f"**{row['keyword']}** p-value (BH): {row['pvalue_bh']:.4f}")

elif page == "Persona Tweet":
    st.title("🤖 Persona Tweet Generator")
    if st.session_state.df is None or st.session_state.engagement_summary is None:
        st.warning("Please upload tweets and analyze engagement first.")
    else:
        topic = st.text_input("Topic (text or URL)")
        if st.button("Create tweet") and topic:
            with st.spinner("Creating tweet..."):
                tweet_html = genai.display_tweet(topic, st.session_state.df, st.session_state.engagement_summary)
            st.markdown(tweet_html, unsafe_allow_html=True)
