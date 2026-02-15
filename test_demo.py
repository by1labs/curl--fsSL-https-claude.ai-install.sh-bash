"""Demo test script — simulates analyzing a website with sample HTML."""

import json
from ai_search_analyzer.analyzers import run_all_analyzers
from ai_search_analyzer.report import generate_report, report_to_json

# ── Sample 1: Well-optimized site ──────────────────────────────────────────

GOOD_SITE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Acme Cloud — Modern Infrastructure for Developers</title>
    <meta name="description" content="Acme Cloud provides scalable cloud infrastructure, APIs, and developer tools trusted by 50,000+ companies worldwide. Deploy in seconds, scale without limits.">
    <meta name="author" content="Acme Cloud Inc.">
    <meta property="og:title" content="Acme Cloud — Modern Infrastructure for Developers">
    <meta property="og:description" content="Scalable cloud infrastructure trusted by 50,000+ companies.">
    <meta property="og:site_name" content="Acme Cloud">
    <meta property="og:type" content="website">
    <meta property="og:image" content="https://acmecloud.com/og-image.png">
    <link rel="canonical" href="https://acmecloud.com/">
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Acme Cloud",
        "url": "https://acmecloud.com",
        "logo": "https://acmecloud.com/logo.png",
        "description": "Modern cloud infrastructure for developers",
        "sameAs": [
            "https://twitter.com/acmecloud",
            "https://linkedin.com/company/acmecloud"
        ]
    }
    </script>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "What is Acme Cloud?",
                "acceptedAnswer": {"@type": "Answer", "text": "Acme Cloud is a developer-first cloud platform."}
            },
            {
                "@type": "Question",
                "name": "How much does it cost?",
                "acceptedAnswer": {"@type": "Answer", "text": "Plans start at $0 with pay-as-you-go pricing."}
            }
        ]
    }
    </script>
</head>
<body>
    <header>
        <nav aria-label="Main navigation">
            <a href="/">Acme Cloud</a>
            <a href="/products">Products</a>
            <a href="/pricing">Pricing</a>
            <a href="/docs">Documentation</a>
            <a href="/about">About Us</a>
            <a href="/blog">Blog</a>
        </nav>
    </header>
    <main>
        <section aria-label="Hero">
            <h1>Build anything. Scale everything.</h1>
            <p>Acme Cloud gives developers the infrastructure they need to ship fast and scale without limits. Trusted by 50,000+ companies from startups to Fortune 500.</p>
        </section>

        <section aria-label="Features">
            <h2>Why developers choose Acme Cloud</h2>
            <ul>
                <li><strong>Global Edge Network:</strong> Deploy to 200+ locations worldwide</li>
                <li><strong>Auto-scaling:</strong> Handle traffic spikes automatically</li>
                <li><strong>Developer-first APIs:</strong> Clean, well-documented REST and GraphQL APIs</li>
                <li><strong>99.99% Uptime SLA:</strong> Enterprise-grade reliability</li>
            </ul>
        </section>

        <section aria-label="Products">
            <h2>Our Products</h2>
            <article>
                <h3>Acme Compute</h3>
                <p>Serverless functions and containers that scale to zero. Pay only for what you use.</p>
            </article>
            <article>
                <h3>Acme Database</h3>
                <p>Managed PostgreSQL, Redis, and vector databases with automatic backups and replication.</p>
            </article>
            <article>
                <h3>Acme Storage</h3>
                <p>Object storage with global CDN. Store and serve files at any scale.</p>
            </article>
        </section>

        <section aria-label="FAQ">
            <h2>Frequently Asked Questions</h2>
            <h3>What is Acme Cloud?</h3>
            <p>Acme Cloud is a developer-first cloud platform offering compute, storage, and database services.</p>
            <h3>How do I get started?</h3>
            <p>Sign up for free at acmecloud.com. No credit card required. Deploy your first app in under 5 minutes.</p>
            <h3>What programming languages are supported?</h3>
            <p>We support Node.js, Python, Go, Rust, Java, Ruby, PHP, and any language that runs in containers.</p>
            <h3>Can I migrate from AWS or GCP?</h3>
            <p>Yes! We offer free migration assistance and compatibility layers for common AWS and GCP services.</p>
            <h3>Is there an SLA?</h3>
            <p>Yes, all paid plans include a 99.99% uptime SLA with financial credits for any downtime.</p>
        </section>

        <section aria-label="Comparison">
            <h2>How we compare</h2>
            <table>
                <thead>
                    <tr><th>Feature</th><th>Acme Cloud</th><th>AWS</th><th>GCP</th></tr>
                </thead>
                <tbody>
                    <tr><td>Deploy time</td><td>< 10 seconds</td><td>Minutes</td><td>Minutes</td></tr>
                    <tr><td>Free tier</td><td>Generous</td><td>Limited</td><td>Limited</td></tr>
                    <tr><td>Pricing</td><td>Simple</td><td>Complex</td><td>Complex</td></tr>
                </tbody>
            </table>
        </section>
    </main>
    <footer>
        <p>&copy; 2026 Acme Cloud Inc. All rights reserved.</p>
        <nav aria-label="Footer navigation">
            <a href="/privacy">Privacy</a>
            <a href="/terms">Terms</a>
            <a href="/security">Security</a>
        </nav>
    </footer>
</body>
</html>
"""

GOOD_SITE_ROBOTS = """User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

Sitemap: https://acmecloud.com/sitemap.xml
"""

GOOD_SITE_LLMS = """# Acme Cloud
> Modern cloud infrastructure for developers

Acme Cloud provides scalable compute, storage, and database services.

## Products
- Acme Compute: Serverless functions and containers
- Acme Database: Managed PostgreSQL, Redis, vector DB
- Acme Storage: Object storage with global CDN

## Docs
- [API Reference](https://acmecloud.com/docs/api)
- [Getting Started](https://acmecloud.com/docs/quickstart)
"""

GOOD_SITE_SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://acmecloud.com/</loc></url>
  <url><loc>https://acmecloud.com/products</loc></url>
  <url><loc>https://acmecloud.com/pricing</loc></url>
  <url><loc>https://acmecloud.com/docs</loc></url>
</urlset>
"""


# ── Sample 2: Poorly optimized site ────────────────────────────────────────

BAD_SITE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Home</title>
</head>
<body>
    <div id="app">
        <div class="nav">
            <span>MyStartup</span>
            <span>Login</span>
        </div>
        <div class="hero">
            <div class="big-text">Welcome</div>
            <div class="sub-text">We do things.</div>
        </div>
        <div class="content">
            <div class="card">Feature 1</div>
            <div class="card">Feature 2</div>
            <div class="card">Feature 3</div>
        </div>
    </div>
    <script src="/bundle.js"></script>
    <script src="/vendor.js"></script>
    <script src="/analytics.js"></script>
</body>
</html>
"""

BAD_SITE_ROBOTS = """User-agent: *
Disallow: /

User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: PerplexityBot
Disallow: /

User-agent: CCBot
Disallow: /
"""


# ── Run the analysis ───────────────────────────────────────────────────────

def analyze_sample(name: str, html: str, robots: str | None, llms: str | None, sitemap: str | None):
    url = f"https://{name.lower().replace(' ', '')}.com"
    page_data = {
        "ok": True,
        "url": url,
        "final_url": url,
        "base_url": url,
        "status_code": 200,
        "headers": {},
        "html": html,
        "robots_txt": robots,
        "llms_txt": llms,
        "sitemap_xml": sitemap,
    }

    results = run_all_analyzers(page_data)
    report = generate_report(url, page_data, results)
    return report


if __name__ == "__main__":
    print("=" * 70)
    print("  DEMO: AI Search Analyzer — Well-Optimized Site (Acme Cloud)")
    print("=" * 70)
    report1 = analyze_sample("Acme Cloud", GOOD_SITE_HTML, GOOD_SITE_ROBOTS, GOOD_SITE_LLMS, GOOD_SITE_SITEMAP)
    print(report_to_json(report1))

    print("\n")
    print("=" * 70)
    print("  DEMO: AI Search Analyzer — Poorly Optimized Site (MyStartup)")
    print("=" * 70)
    report2 = analyze_sample("MyStartup", BAD_SITE_HTML, BAD_SITE_ROBOTS, None, None)
    print(report_to_json(report2))
