"""Analyzers that score a website's visibility to AI search engines."""

from __future__ import annotations

import json
import re
from bs4 import BeautifulSoup, Comment


# Known AI crawler user-agent tokens
AI_CRAWLERS = [
    "GPTBot",
    "ChatGPT-User",
    "Google-Extended",
    "Anthropic",
    "ClaudeBot",
    "Claude-Web",
    "PerplexityBot",
    "Bytespider",
    "CCBot",
    "Cohere-ai",
    "Meta-ExternalAgent",
    "Amazonbot",
]


def _parse_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


# ---------------------------------------------------------------------------
# 1. Structured Data Analysis
# ---------------------------------------------------------------------------

def analyze_structured_data(html: str) -> dict:
    """Check for Schema.org / JSON-LD / microdata that helps LLMs understand content."""
    soup = _parse_html(html)
    findings = []
    score = 0
    max_score = 30

    # JSON-LD blocks
    jsonld_scripts = soup.find_all("script", {"type": "application/ld+json"})
    jsonld_types = []
    for tag in jsonld_scripts:
        try:
            data = json.loads(tag.string or "")
            if isinstance(data, dict):
                jsonld_types.append(data.get("@type", "Unknown"))
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        jsonld_types.append(item.get("@type", "Unknown"))
        except (json.JSONDecodeError, TypeError):
            pass

    if jsonld_scripts:
        score += 15
        findings.append(f"Found {len(jsonld_scripts)} JSON-LD block(s): {', '.join(jsonld_types)}")
    else:
        findings.append("No JSON-LD structured data found")

    # Microdata
    microdata_items = soup.find_all(attrs={"itemscope": True})
    if microdata_items:
        types = [el.get("itemtype", "untyped") for el in microdata_items[:5]]
        score += 5
        findings.append(f"Found {len(microdata_items)} microdata item(s): {', '.join(types)}")

    # RDFa
    rdfa_items = soup.find_all(attrs={"typeof": True})
    if rdfa_items:
        score += 5
        findings.append(f"Found {len(rdfa_items)} RDFa item(s)")

    # OpenGraph tags
    og_tags = soup.find_all("meta", attrs={"property": re.compile(r"^og:")})
    if og_tags:
        score += 5
        og_names = [t.get("property") for t in og_tags]
        findings.append(f"OpenGraph tags present: {', '.join(og_names)}")
    else:
        findings.append("No OpenGraph tags found")

    return {
        "name": "Structured Data",
        "score": min(score, max_score),
        "max_score": max_score,
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# 2. Content Clarity & Structure
# ---------------------------------------------------------------------------

def analyze_content_structure(html: str) -> dict:
    """Analyze heading hierarchy, lists, tables, FAQ patterns."""
    soup = _parse_html(html)
    findings = []
    score = 0
    max_score = 25

    # Heading hierarchy
    headings = {}
    for level in range(1, 7):
        tags = soup.find_all(f"h{level}")
        if tags:
            headings[f"h{level}"] = len(tags)

    if headings:
        findings.append(f"Heading structure: {headings}")
        if "h1" in headings:
            score += 5
            h1_texts = [h.get_text(strip=True) for h in soup.find_all("h1")]
            findings.append(f"H1: {h1_texts[0][:100]}")
        if "h2" in headings:
            score += 3
    else:
        findings.append("No heading structure found — poor for AI parsing")

    # Lists (LLMs love structured lists)
    ul_count = len(soup.find_all("ul"))
    ol_count = len(soup.find_all("ol"))
    if ul_count + ol_count > 0:
        score += 3
        findings.append(f"Lists found: {ul_count} unordered, {ol_count} ordered")

    # Tables
    tables = soup.find_all("table")
    if tables:
        score += 2
        findings.append(f"Tables found: {len(tables)}")

    # FAQ-like patterns
    faq_signals = 0
    for tag in soup.find_all(["h2", "h3", "h4", "summary", "dt"]):
        text = tag.get_text(strip=True)
        if text.endswith("?") or text.lower().startswith(("how", "what", "why", "when", "where", "who", "can", "does", "is")):
            faq_signals += 1
    if faq_signals >= 3:
        score += 5
        findings.append(f"FAQ-like content detected ({faq_signals} question headings)")
    elif faq_signals > 0:
        score += 2
        findings.append(f"Some question-style headings found ({faq_signals})")
    else:
        findings.append("No FAQ-style content detected")

    # Content length check
    body = soup.find("body")
    text = body.get_text(separator=" ", strip=True) if body else ""
    word_count = len(text.split())
    if word_count > 500:
        score += 4
        findings.append(f"Good content depth: ~{word_count} words")
    elif word_count > 200:
        score += 2
        findings.append(f"Moderate content: ~{word_count} words")
    else:
        findings.append(f"Thin content: ~{word_count} words — LLMs may not have enough to reference")

    # Definition-like patterns (<dl>, <dfn>, or bold+colon patterns)
    definitions = soup.find_all(["dl", "dfn"])
    if definitions:
        score += 3
        findings.append(f"Definition markup found ({len(definitions)} elements)")

    return {
        "name": "Content Structure",
        "score": min(score, max_score),
        "max_score": max_score,
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# 3. Meta & Brand Identity
# ---------------------------------------------------------------------------

def analyze_brand_identity(html: str, url: str) -> dict:
    """Check how clearly the brand/site identifies itself for LLMs."""
    soup = _parse_html(html)
    findings = []
    score = 0
    max_score = 15

    # Title tag
    title = soup.find("title")
    if title and title.get_text(strip=True):
        score += 3
        findings.append(f"Title: \"{title.get_text(strip=True)[:120]}\"")
    else:
        findings.append("No <title> tag found")

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content", "").strip():
        desc = meta_desc["content"].strip()
        score += 4
        findings.append(f"Meta description ({len(desc)} chars): \"{desc[:150]}\"")
        if len(desc) < 50:
            findings.append("Meta description is very short — may not provide enough context for LLMs")
        elif len(desc) > 160:
            findings.append("Meta description is long — may get truncated")
    else:
        findings.append("No meta description — LLMs rely on this for summarization")

    # Canonical URL
    canonical = soup.find("link", attrs={"rel": "canonical"})
    if canonical:
        score += 2
        findings.append(f"Canonical URL set: {canonical.get('href', '')[:100]}")

    # Author / organization
    author_meta = soup.find("meta", attrs={"name": "author"})
    if author_meta and author_meta.get("content"):
        score += 2
        findings.append(f"Author meta: {author_meta['content']}")

    # Site name via OG
    og_site = soup.find("meta", attrs={"property": "og:site_name"})
    if og_site and og_site.get("content"):
        score += 2
        findings.append(f"OG site name: {og_site['content']}")

    # About page link
    about_links = soup.find_all("a", href=re.compile(r"/(about|who-we-are|company)", re.I))
    if about_links:
        score += 2
        findings.append("About/Company page linked from homepage")
    else:
        findings.append("No visible About page link — helps LLMs understand the entity")

    return {
        "name": "Brand Identity",
        "score": min(score, max_score),
        "max_score": max_score,
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# 4. AI Crawler Access
# ---------------------------------------------------------------------------

def analyze_crawler_access(robots_txt: str | None, html: str) -> dict:
    """Check if AI crawlers are allowed or blocked in robots.txt and meta tags."""
    findings = []
    score = 0
    max_score = 15

    soup = _parse_html(html)

    # robots.txt analysis
    if robots_txt is None:
        findings.append("No robots.txt found — AI crawlers have unrestricted access (by default)")
        score += 8
    else:
        blocked = []
        allowed = []
        lines = robots_txt.splitlines()
        current_agent = None

        for line in lines:
            line = line.strip()
            if line.lower().startswith("user-agent:"):
                current_agent = line.split(":", 1)[1].strip()
            elif line.lower().startswith("disallow:") and current_agent:
                path = line.split(":", 1)[1].strip()
                if path == "/" or path == "/*":
                    for crawler in AI_CRAWLERS:
                        if current_agent == "*" or crawler.lower() in current_agent.lower():
                            blocked.append(crawler if current_agent == "*" else current_agent)

        # Check for explicit AI bot blocks
        for crawler in AI_CRAWLERS:
            pattern = re.compile(re.escape(crawler), re.I)
            if pattern.search(robots_txt):
                # Check if it's blocked
                agent_block = re.search(
                    rf"user-agent:\s*{re.escape(crawler)}.*?(?=user-agent:|\Z)",
                    robots_txt,
                    re.I | re.DOTALL,
                )
                if agent_block:
                    block_text = agent_block.group()
                    if re.search(r"disallow:\s*/\s*$", block_text, re.M):
                        blocked.append(crawler)
                    else:
                        allowed.append(crawler)

        blocked = list(set(blocked))
        allowed = list(set(allowed))

        if blocked:
            findings.append(f"AI crawlers BLOCKED: {', '.join(blocked)}")
            # Partial score — blocking some is fine if others are allowed
            score += max(0, 8 - len(blocked) * 2)
        else:
            score += 8
            findings.append("No AI crawlers explicitly blocked in robots.txt")

        if allowed:
            findings.append(f"AI crawlers explicitly allowed: {', '.join(allowed)}")
            score += 2

    # Meta robots tags
    meta_robots = soup.find("meta", attrs={"name": re.compile(r"robots", re.I)})
    if meta_robots:
        content = meta_robots.get("content", "").lower()
        if "noindex" in content:
            score = max(score - 5, 0)
            findings.append("META ROBOTS: noindex set — page won't be indexed by AI search")
        elif "nofollow" in content:
            score = max(score - 2, 0)
            findings.append("META ROBOTS: nofollow set — crawlers won't follow links")
        else:
            findings.append(f"Meta robots: {content}")
    else:
        score += 2
        findings.append("No restrictive meta robots tags")

    # X-Robots-Tag header check happens at report level

    # Check for AI-specific meta tags
    for crawler in AI_CRAWLERS:
        ai_meta = soup.find("meta", attrs={"name": re.compile(crawler, re.I)})
        if ai_meta:
            content = ai_meta.get("content", "")
            findings.append(f"AI-specific meta tag for {crawler}: {content}")

    return {
        "name": "AI Crawler Access",
        "score": min(score, max_score),
        "max_score": max_score,
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# 5. LLM-Friendly Signals
# ---------------------------------------------------------------------------

def analyze_llm_signals(html: str, llms_txt: str | None, sitemap_xml: str | None) -> dict:
    """Check for signals specifically designed for LLM consumption."""
    soup = _parse_html(html)
    findings = []
    score = 0
    max_score = 15

    # llms.txt (proposed standard)
    if llms_txt:
        score += 5
        line_count = len(llms_txt.strip().splitlines())
        findings.append(f"llms.txt found ({line_count} lines) — proactive LLM optimization")
    else:
        findings.append("No llms.txt found — consider creating one (emerging standard for LLM-friendly sites)")

    # Sitemap presence
    if sitemap_xml:
        score += 3
        findings.append("sitemap.xml present — helps AI crawlers discover content")
    else:
        findings.append("No sitemap.xml — AI crawlers may miss pages")

    # Clean semantic HTML (article, main, section, nav, aside)
    semantic_tags = {}
    for tag_name in ["article", "main", "section", "nav", "aside", "header", "footer"]:
        count = len(soup.find_all(tag_name))
        if count:
            semantic_tags[tag_name] = count

    if semantic_tags:
        score += 3
        findings.append(f"Semantic HTML tags: {semantic_tags}")
    else:
        findings.append("No semantic HTML tags (article, main, section) — hurts AI content extraction")

    # aria-label and accessibility (helps LLMs understand interactive elements)
    aria_count = len(soup.find_all(attrs={"aria-label": True}))
    if aria_count > 3:
        score += 2
        findings.append(f"Good accessibility: {aria_count} aria-labels found")

    # Clean text-to-HTML ratio
    body = soup.find("body")
    if body:
        text_len = len(body.get_text(strip=True))
        html_len = len(str(body))
        ratio = text_len / html_len if html_len > 0 else 0
        if ratio > 0.3:
            score += 2
            findings.append(f"Good text/HTML ratio: {ratio:.1%} — content-rich page")
        elif ratio > 0.15:
            findings.append(f"Moderate text/HTML ratio: {ratio:.1%}")
        else:
            findings.append(f"Low text/HTML ratio: {ratio:.1%} — heavy markup may hinder extraction")

    # Check for excessive JavaScript-only content (bad for AI crawlers)
    scripts = soup.find_all("script")
    noscript = soup.find("noscript")
    if len(scripts) > 20 and (not body or len(body.get_text(strip=True)) < 200):
        findings.append("Warning: Page appears JS-heavy with little server-rendered content — AI crawlers may see empty page")
    elif noscript:
        findings.append("Noscript fallback present — good for crawlers without JS")

    return {
        "name": "LLM-Friendly Signals",
        "score": min(score, max_score),
        "max_score": max_score,
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# Run all analyzers
# ---------------------------------------------------------------------------

def run_all_analyzers(page_data: dict) -> list[dict]:
    """Run all analyzers against fetched page data and return results."""
    html = page_data["html"]
    url = page_data["url"]
    robots_txt = page_data.get("robots_txt")
    llms_txt = page_data.get("llms_txt")
    sitemap_xml = page_data.get("sitemap_xml")

    return [
        analyze_structured_data(html),
        analyze_content_structure(html),
        analyze_brand_identity(html, url),
        analyze_crawler_access(robots_txt, html),
        analyze_llm_signals(html, llms_txt, sitemap_xml),
    ]
