import urllib.parse
import feedparser
import streamlit as st


st.set_page_config(
    page_title="Weekly Memory Tech Scout",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Weekly Memory Tech Scout")
st.write(
    "최신 반도체/메모리 관련 arXiv 논문을 검색하고, "
    "초록 기반으로 핵심 내용과 메모리 산업 관련성을 정리해주는 AI Agent입니다."
)

st.info(
    "현재 버전은 OpenAI API 없이 동작하는 규칙 기반 버전입니다. "
    "arXiv에서 논문을 자동 검색하고, 키워드 매칭과 초록 분석을 통해 relevance score를 제공합니다."
)


DEFAULT_KEYWORDS = "HBM OR DRAM OR NAND flash OR semiconductor memory OR advanced packaging"

keyword = st.text_input(
    "검색 키워드",
    value=DEFAULT_KEYWORDS
)

max_results = st.slider(
    "가져올 논문 수",
    min_value=1,
    max_value=10,
    value=5
)


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
        authors = []
        if hasattr(entry, "authors"):
            authors = [author.name for author in entry.authors]

        paper = {
            "title": entry.title.replace("\n", " ").strip(),
            "authors": ", ".join(authors) if authors else "Unknown",
            "published": entry.published[:10] if hasattr(entry, "published") else "Unknown",
            "summary": entry.summary.replace("\n", " ").strip() if hasattr(entry, "summary") else "",
            "link": entry.link if hasattr(entry, "link") else ""
        }

        papers.append(paper)

    return papers


def calculate_relevance_score(title, summary):
    text = (title + " " + summary).lower()

    memory_keywords = [
        "memory", "dram", "nand", "hbm", "flash", "semiconductor",
        "packaging", "interconnect", "lithography", "euv", "ald",
        "thin film", "device", "transistor", "thermal", "chip",
        "logic", "wafer", "oxide", "dielectric", "interface",
        "ferroelectric", "capacitor", "high-k"
    ]

    matched_keywords = []

    for keyword in memory_keywords:
        if keyword in text:
            matched_keywords.append(keyword)

    score = min(5, max(1, len(matched_keywords)))

    return score, matched_keywords


def make_rule_based_summary(paper):
    title = paper["title"]
    summary = paper["summary"]

    score, matched_keywords = calculate_relevance_score(title, summary)

    if len(summary) > 700:
        short_summary = summary[:700] + "..."
    else:
        short_summary = summary

    if matched_keywords:
        keyword_text = ", ".join(matched_keywords)
    else:
        keyword_text = "직접 매칭된 키워드 없음"

    if score >= 4:
        relevance_comment = (
            "메모리 반도체, 소자 구조, 공정, 패키징 또는 소재 관점에서 "
            "비교적 높은 관련성이 있는 논문으로 판단됩니다."
        )
    elif score >= 2:
        relevance_comment = (
            "반도체 기술과 간접적으로 관련될 가능성이 있으며, "
            "세부 내용을 추가로 검토할 가치가 있습니다."
        )
    else:
        relevance_comment = (
            "현재 키워드 기준으로는 메모리 반도체와의 직접 관련성은 낮지만, "
            "기초 기술 관점에서 참고 가능성이 있습니다."
        )

    result = f"""
### 자동 요약 리포트

**1. 한 줄 요약**  
이 논문은 `{title}`에 관한 최신 연구로, arXiv에서 자동 검색된 결과입니다.

**2. 연구 배경/문제**  
아래는 논문 초록을 기반으로 추출한 주요 내용입니다.

> {short_summary}

**3. 제안 방법**  
초록 기준으로 볼 때, 연구진은 위 문제를 해결하기 위해 새로운 이론, 구조, 공정, 소자, 소재 또는 분석 방법을 제안한 것으로 보입니다.

**4. 핵심 결과**  
논문 초록에 제시된 결과를 바탕으로, 해당 연구는 기존 기술의 성능 개선, 메커니즘 분석, 또는 새로운 응용 가능성 제시를 목표로 합니다.

**5. 메모리 반도체 관점에서 의미**  
- 매칭된 키워드: `{keyword_text}`  
- 판단: {relevance_comment}

**6. SK hynix relevance score**  
`{score}/5`
"""

    return result


if st.button("최신 논문 검색 및 요약"):
    with st.spinner("arXiv에서 최신 논문을 검색하고 정리하는 중입니다..."):
        try:
            papers = search_arxiv(keyword, max_results)

            if not papers:
                st.warning("검색 결과가 없습니다. 키워드를 바꿔보세요.")

            else:
                st.success(f"{len(papers)}개의 논문을 찾았습니다.")

                for i, paper in enumerate(papers, start=1):
                    st.subheader(f"{i}. {paper['title']}")
                    st.caption(f"Authors: {paper['authors']}")
                    st.caption(f"Published: {paper['published']}")

                    if paper["link"]:
                        st.markdown(f"[논문 링크 열기]({paper['link']})")

                    report = make_rule_based_summary(paper)
                    st.markdown(report)

                    with st.expander("원문 초록 보기"):
                        st.write(paper["summary"])

                    st.divider()

        except Exception as e:
            st.error("앱 실행 중 오류가 발생했습니다.")
            st.write("오류 내용:")
            st.code(str(e))
