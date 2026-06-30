import os
import urllib.parse
import feedparser
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Weekly Memory Tech Scout", page_icon="🧠")

st.title("🧠 Weekly Memory Tech Scout")
st.write("최신 반도체/메모리 관련 arXiv 논문을 검색하고 한국어로 요약해주는 AI Agent입니다.")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

DEFAULT_KEYWORDS = "HBM OR DRAM OR NAND flash OR semiconductor memory OR advanced packaging"

keyword = st.text_input(
    "검색 키워드",
    value=DEFAULT_KEYWORDS
)

max_results = st.slider("가져올 논문 수", 3, 10, 5)

def search_arxiv(query, max_results=5):
    encoded_query = urllib.parse.quote(query)
    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query=all:{encoded_query}"
        f"&start=0"
        f"&max_results={max_results}"
        f"&sortBy=submittedDate"
        f"&sortOrder=descending"
    )

    feed = feedparser.parse(url)
    papers = []

    for entry in feed.entries:
        papers.append({
            "title": entry.title.replace("\n", " "),
            "authors": ", ".join(author.name for author in entry.authors),
            "published": entry.published[:10],
            "summary": entry.summary.replace("\n", " "),
            "link": entry.link
        })

    return papers

def summarize_paper(paper):
    prompt = f"""
너는 SK하이닉스 입사를 앞둔 반도체 신입 엔지니어를 돕는 AI research scout이다.
아래 논문 초록을 바탕으로 한국어로 간결하게 정리해라.

[논문 제목]
{paper['title']}

[초록]
{paper['summary']}

다음 형식으로 답해라.

1. 한 줄 요약:
2. 연구 배경/문제:
3. 제안 방법:
4. 핵심 결과:
5. 메모리 반도체 관점에서 의미:
6. SK hynix relevance score: 1~5점
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text

if st.button("최신 논문 검색 및 요약"):
    with st.spinner("arXiv에서 논문을 검색하고 요약하는 중입니다..."):
        papers = search_arxiv(keyword, max_results)

        if not papers:
            st.warning("검색 결과가 없습니다. 키워드를 바꿔보세요.")
        else:
            for i, paper in enumerate(papers, start=1):
                st.subheader(f"{i}. {paper['title']}")
                st.caption(f"Authors: {paper['authors']}")
                st.caption(f"Published: {paper['published']}")
                st.markdown(f"[논문 링크]({paper['link']})")

                summary = summarize_paper(paper)
                st.markdown(summary)
                st.divider()
