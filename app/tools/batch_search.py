"""Batch search tool - runs multiple queries and returns all unique URLs."""

import json

from app.tools.search_grounding import search_with_grounding


def batch_search_agents_cli() -> str:
    """
    Run a comprehensive batch of searches for Agents CLI content.

    This tool executes 25 pre-defined search queries targeting different
    content types and platforms, then returns all unique URLs found.

    The queries cover:
    - Direct brand terms (agents-cli, google agents cli)
    - Platform terms (Gemini Enterprise Agent Platform, ADK)
    - Use cases (tutorials, deployment, quickstart)
    - Content types (docs, videos, news, blogs)

    Returns:
        JSON with all URLs found across all searches:
        {
            "queries_executed": 25,
            "total_urls_found": N,
            "unique_urls": [...],
            "urls_by_query": {...}
        }
    """
    # Comprehensive query set optimized for THIRD-PARTY coverage
    # Focus on community content, not Google's own docs/blogs
    queries = [
        # Direct brand + third-party platforms (8)
        "agents-cli medium",
        "agents-cli medium article",
        "google agents cli medium",
        "agents-cli infoq",
        "agents-cli habr",
        "agents-cli reddit",
        "agents-cli dev.to",
        "agents-cli substack",

        # Tutorials & guides (7)
        "agents-cli tutorial",
        "agents-cli complete guide",
        "agents-cli beginner guide",
        "agents-cli step by step",
        "how to use agents-cli",
        "agents-cli walkthrough",
        "learn agents-cli",

        # YouTube community content (8)
        "agents-cli youtube",
        "agents-cli video",
        "introducing agents-cli",
        "agents-cli demo",
        "agents-cli overview",
        "agents-cli explained",
        "gemini enterprise agent platform video",
        "google agents cli video tutorial",

        # News & articles (8)
        "agents-cli news",
        "agents-cli announcement",
        "google agents cli article",
        "agents-cli review",
        "agents-cli launch",
        "agents-cli release",
        "google cloud agents cli news",
        "agents-cli tech news",

        # Community discussions (5)
        "agents-cli discussion",
        "agents-cli forum",
        "agents-cli questions",
        "agents-cli stackoverflow",
        "agents-cli community",

        # International content (6)
        "agents-cli sfeir",
        "google cloud next 2026 agents-cli",
        "agents-cli français",
        "agents-cli tutorial español",
        "agents-cli 日本語",
        "agents-cli international",
    ]

    all_urls: list[dict[str, str]] = []
    urls_seen = set()
    results_by_query = {}

    for query in queries:
        try:
            result = search_with_grounding(query, follow_redirects=True)
            data = json.loads(result)

            query_urls = []
            if 'results' in data:
                for item in data['results']:
                    url = item.get('url', '')
                    title = item.get('title', '')

                    if url and url not in urls_seen:
                        urls_seen.add(url)
                        all_urls.append({
                            "title": title,
                            "url": url,
                            "domain": item.get('domain', ''),
                            "found_by_query": query
                        })
                        query_urls.append(url)

            results_by_query[query] = {
                "count": len(query_urls),
                "urls": query_urls[:3]  # Sample
            }

        except Exception as e:
            results_by_query[query] = {
                "error": str(e),
                "count": 0
            }

    return json.dumps({
        "queries_executed": len(queries),
        "total_urls_found": len(all_urls),
        "unique_urls": all_urls,
        "results_by_query": results_by_query,
        "summary": f"Executed {len(queries)} searches, found {len(all_urls)} unique URLs"
    }, indent=2)
