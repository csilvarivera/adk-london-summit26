# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import io
import pytest
from unittest.mock import patch, MagicMock

from app.tools import (
    wikipedia_search_tool,
    text_summarizer_tool,
    google_news_api_tool,
    sentiment_analysis_tool,
    arxiv_search_tool,
    pdf_scraper_tool
)


def test_text_summarizer_tool() -> None:
    """Tests the text summarizer tool under various text lengths."""
    # Simple short text
    assert text_summarizer_tool("Short text.") == "- Short text"
    
    # Standard multi-sentence text
    long_text = (
        "Quantum computing is a rapidly-emerging technology. "
        "It harnesses the laws of quantum mechanics to solve problems too complex for classical computers. "
        "These machines are very different from the classical computers that have been around for decades. "
        "Quantum superposition and entanglement are the key drivers. "
        "In conclusion, it will revolutionize many scientific industries."
    )
    summary = text_summarizer_tool(long_text)
    assert "- Quantum computing is a rapidly-emerging technology." in summary
    assert "- In conclusion, it will revolutionize many scientific industries." in summary


def test_sentiment_analysis_tool() -> None:
    """Tests sentiment analysis polarity calculations and categories."""
    # Positive
    pos_res = sentiment_analysis_tool([
        "We achieved an excellent breakthrough today",
        "It is a strong and promising innovation"
    ])
    assert pos_res["sentiment"] == "Positive"
    assert pos_res["polarity_score"] > 0.0
    
    # Negative
    neg_res = sentiment_analysis_tool([
        "The project is a major crisis and a failure",
        "We worry about the risk and limitations"
    ])
    assert neg_res["sentiment"] == "Negative"
    assert neg_res["polarity_score"] < 0.0
    
    # Neutral
    neu_res = sentiment_analysis_tool(["The table is white", "Standard routine operation"])
    assert neu_res["sentiment"] == "Neutral"
    assert neu_res["polarity_score"] == 0.0


@patch("urllib.request.urlopen")
def test_wikipedia_search_tool_success(mock_urlopen: MagicMock) -> None:
    """Tests wikipedia search tool returns structured results on success."""
    # Mocking urllib urlopen response
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "query": {
            "search": [
                {
                    "title": "Quantum Computing",
                    "pageid": 12345,
                    "snippet": "Quantum computing is a <span class=\"searchmatch\">field</span> of study.",
                    "wordcount": 2500
                }
            ]
        }
    }).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    res = wikipedia_search_tool("Quantum Computing")
    assert res["status"] == "success"
    assert res["query"] == "Quantum Computing"
    assert len(res["results"]) == 1
    assert res["results"][0]["title"] == "Quantum Computing"
    # Verify search HTML span is stripped
    assert res["results"][0]["snippet"] == "Quantum computing is a field of study."


@patch("urllib.request.urlopen")
def test_wikipedia_search_tool_error(mock_urlopen: MagicMock) -> None:
    """Tests wikipedia search tool handles network failures gracefully."""
    mock_urlopen.side_effect = Exception("Connection Timeout")
    res = wikipedia_search_tool("Error Topic")
    assert res["status"] == "error"
    assert "Wikipedia search failed" in res["message"]


@patch("urllib.request.urlopen")
def test_google_news_api_tool_success(mock_urlopen: MagicMock) -> None:
    """Tests google news rss parser handles XML payloads cleanly."""
    rss_payload = """<rss version="2.0">
      <channel>
        <title>Google News search results</title>
        <item>
          <title>Breaking News Headline - TechSource</title>
          <link>https://techsource.com/breaking-news</link>
          <pubDate>Sun, 07 Jun 2026 12:00:00 GMT</pubDate>
          <source>TechSource</source>
        </item>
      </channel>
    </rss>"""
    
    mock_response = MagicMock()
    mock_response.read.return_value = rss_payload.encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    res = google_news_api_tool("Quantum")
    assert res["status"] == "success"
    assert len(res["articles"]) == 1
    assert res["articles"][0]["title"] == "Breaking News Headline - TechSource"
    assert res["articles"][0]["source"] == "TechSource"


@patch("urllib.request.urlopen")
def test_arxiv_search_tool_success(mock_urlopen: MagicMock) -> None:
    """Tests arXiv RSS parser reads feed and extracts author, pdf links, and dates."""
    arxiv_payload = """<feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <title>Quantum Supremacy Using Linear Optics</title>
        <summary>This paper presents theoretical formulations for quantum supremacy.</summary>
        <published>2026-05-15T08:00:00Z</published>
        <link href="http://arxiv.org/pdf/2605.12345" title="pdf" rel="related" />
        <author>
          <name>Dr. Alice Smith</name>
        </author>
        <author>
          <name>Prof. Bob Jones</name>
        </author>
      </entry>
    </feed>"""
    
    mock_response = MagicMock()
    mock_response.read.return_value = arxiv_payload.encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    res = arxiv_search_tool("quantum supremacy")
    assert res["status"] == "success"
    assert len(res["papers"]) == 1
    paper = res["papers"][0]
    assert paper["title"] == "Quantum Supremacy Using Linear Optics"
    assert "Dr. Alice Smith" in paper["authors"]
    assert "Prof. Bob Jones" in paper["authors"]
    assert paper["pdf_url"] == "http://arxiv.org/pdf/2605.12345"


def test_pdf_scraper_tool() -> None:
    """Tests pdf scraper dummy extraction and validation."""
    err_res = pdf_scraper_tool("")
    assert err_res["status"] == "error"
    
    success_res = pdf_scraper_tool("http://arxiv.org/pdf/2605.12345")
    assert success_res["status"] == "success"
    assert "methodology_type" in success_res["findings"]
