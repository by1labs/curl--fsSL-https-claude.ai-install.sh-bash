"""Generate the final JSON analysis report."""

from __future__ import annotations

import json
from datetime import datetime, timezone


def _grade(pct: float) -> str:
    """Convert percentage to letter grade."""
    if pct >= 90:
        return "A"
    if pct >= 80:
        return "B"
    if pct >= 65:
        return "C"
    if pct >= 50:
        return "D"
    return "F"


def _recommendations(results: list[dict]) -> list[str]:
    """Generate actionable recommendations based on analysis results."""
    recs = []

    for r in results:
        name = r["name"]
        pct = (r["score"] / r["max_score"] * 100) if r["max_score"] > 0 else 0

        if name == "Structured Data" and pct < 50:
            recs.append(
                "Add JSON-LD structured data (Schema.org) to your pages. "
                "Include Organization, WebSite, and page-specific types (Article, Product, FAQ). "
                "This is one of the strongest signals for AI search engines."
            )
        if name == "Structured Data" and pct >= 50 and pct < 80:
            recs.append(
                "Expand your structured data coverage. Add FAQ schema for question-based content "
                "and ensure all key entities have JSON-LD markup."
            )

        if name == "Content Structure" and pct < 50:
            recs.append(
                "Improve content structure: use clear heading hierarchy (H1 > H2 > H3), "
                "add FAQ sections with question headings, and use lists/tables for data. "
                "LLMs extract information most reliably from well-structured content."
            )

        if name == "Brand Identity" and pct < 50:
            recs.append(
                "Strengthen brand signals: add a descriptive meta description (120-155 chars), "
                "set og:site_name, add author metadata, and ensure an About page is linked. "
                "Clear brand identity helps LLMs accurately attribute and recommend your site."
            )

        if name == "AI Crawler Access" and pct < 60:
            recs.append(
                "Review your robots.txt — you may be blocking AI crawlers (GPTBot, ClaudeBot, "
                "PerplexityBot). If you want visibility in AI search, allow these crawlers access. "
                "Check for restrictive meta robots tags as well."
            )

        if name == "LLM-Friendly Signals" and pct < 50:
            recs.append(
                "Add a llms.txt file (see llmstxt.org) describing your site for LLMs. "
                "Ensure you have a sitemap.xml, use semantic HTML (article, main, section), "
                "and keep a good text-to-HTML ratio for easy content extraction."
            )

    if not recs:
        recs.append(
            "Your site scores well across all categories. Continue maintaining structured data, "
            "clear content, and open crawler access to stay visible in AI search results."
        )

    return recs


def generate_report(url: str, page_data: dict, results: list[dict]) -> dict:
    """Build the full JSON report."""
    total_score = sum(r["score"] for r in results)
    total_max = sum(r["max_score"] for r in results)
    overall_pct = (total_score / total_max * 100) if total_max > 0 else 0

    categories = []
    for r in results:
        cat_pct = (r["score"] / r["max_score"] * 100) if r["max_score"] > 0 else 0
        categories.append({
            "name": r["name"],
            "score": r["score"],
            "max_score": r["max_score"],
            "percentage": round(cat_pct, 1),
            "grade": _grade(cat_pct),
            "findings": r["findings"],
        })

    report = {
        "analyzer": "AI Search Analyzer v1.0",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "url": url,
        "final_url": page_data.get("final_url", url),
        "overall": {
            "score": total_score,
            "max_score": total_max,
            "percentage": round(overall_pct, 1),
            "grade": _grade(overall_pct),
        },
        "categories": categories,
        "recommendations": _recommendations(results),
        "ai_crawlers_checked": [
            "GPTBot", "ChatGPT-User", "Google-Extended", "ClaudeBot",
            "PerplexityBot", "CCBot", "Cohere-ai", "Amazonbot",
        ],
    }

    return report


def report_to_json(report: dict, indent: int = 2) -> str:
    """Serialize report to JSON string."""
    return json.dumps(report, indent=indent, ensure_ascii=False)
