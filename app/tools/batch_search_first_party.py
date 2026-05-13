"""Batch search tool for first-party Google content about Agents CLI."""

import json

from app.tools.search_grounding import search_with_grounding


def batch_search_first_party() -> str:
    """
    Search for Agents CLI mentions on Google's own properties.

    Targets first-party domains (EXCLUDING the repo and official docs site):
    - developers.googleblog.com (Google Developer Blog)
    - docs.cloud.google.com (Google Cloud Docs)
    - adk.dev (ADK Documentation)

    Returns:
        JSON with all URLs found across first-party searches:
        {
            "queries_executed": N,
            "total_urls_found": N,
            "unique_urls": [...],
            "urls_by_query": {...}
        }
    """
    queries = [
        # Google Developer Blog
        "agents-cli site:developers.googleblog.com",
        "google agents cli site:developers.googleblog.com",
        "agent development kit CLI site:developers.googleblog.com",

        # Google Cloud Docs
        "agents-cli site:docs.cloud.google.com",
        "google agents cli site:docs.cloud.google.com",
        "agent platform CLI site:docs.cloud.google.com",
        "ADK CLI site:docs.cloud.google.com",
        "gemini enterprise agent platform CLI site:docs.cloud.google.com",

        # ADK Documentation
        "agents-cli site:adk.dev",
        "CLI site:adk.dev",
        "command line site:adk.dev",
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
        "summary": f"Executed {len(queries)} first-party searches, found {len(all_urls)} unique URLs"
    }, indent=2)
