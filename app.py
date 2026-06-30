import os
import urllib.parse
import feedparser
import streamlit as st
# from openai import OpenAI

st.set_page_config(page_title="Weekly Memory Tech Scout", page_icon="🧠")

st.title("🧠 Weekly Memory Tech Scout")
st.write("최신 반도체/메모리 관련 arXiv 논문을 검색하고 한국어로 요약해주는 AI Agent입니다.")

# client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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
    text = paper["summary"]

    memory_keywords = [
        "memory", "DRAM", "NAND", "HBM", "flash", "semiconductor",
        "packaging", "interconnect", "lithography", "EUV", "ALD",
        "thin film", "device", "transistor", "thermal"
    ]

    matched_keywords = [
        kw for kw in memory_keywords
        if kw.lower() in (paper["title"] + " " + text).lower()
    ]

    score = min(5, max(1, len(matched_keywords)))

    short_summary = text[:600] + "..." if len(text) > 600 else text

    return f"""
1. 한 줄 요약:  
이 논문은 "{paper['title']}"에 관한 최신 연구로, 반도체/메모리 기술과의 연관성을 기준으로 선별되었습니다.

2. 연구 배경/문제:  
arXiv 초록에 따르면, 본 연구는 다음과 같은 기술적 문제를 다룹니다.  
{short_summary}

3. 제안 방법:  
초록 기반으로 볼 때, 연구진은 위 문제를 해결하기 위한 새로운 구조, 공정, 소자, 소재 또는 분석 방법을 제안합니다.

4. 핵심 결과:  
논문 초록에 제시된 주요 결과를 바탕으로, 해당 연구는 기존 기술의 성능 개선 또는 이해도 향상을 목표로 합니다.

5. 메모리 반도체 관점에서 의미:  
매칭된 키워드: {", ".join(matched_keywords) if matched_keywords else "직접 매칭된 키워드 없음"}  
이 논문은 메모리 소자, 반도체 공정, 패키징, 박막 또는 열 관리 관점에서 추가 검토할 가치가 있습니다.

6. SK hynix relevance score: {score}/5
"""

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
                st.divider()6. SK hynix relevance score: {score}/5
"""
