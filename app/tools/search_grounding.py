"""Search using Google Search Grounding and resolve redirect URLs."""

import json
import os
import re

import httpx
from google import genai
from google.genai import types


def search_with_grounding(query: str, follow_redirects: bool = True) -> str:
    """
    Search using Gemini with Google Search grounding and resolve redirect URLs.

    Google Search Grounding returns redirect URLs for privacy. This tool
    optionally follows those redirects to get the actual URLs.

    Args:
        query: Search query
        follow_redirects: If True, follow redirect URLs to get real URLs (default: True)

    Returns:
        JSON with search results including resolved URLs
    """
    try:
        # Initialize Gemini client
        client = genai.Client(
            vertexai=True,
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        )

        # Call Gemini with Google Search grounding
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Search the web for: {query}\n\nList the top results you find with their titles and sources.",
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                response_modalities=["TEXT"],
            )
        )

        # Extract real titles from Gemini's text response
        # Format can be: * **Title:** actual title  or  1. **Title** - Source
        text_titles = []
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content:
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        # Try pattern 1: * **Title:** Actual Title
                        pattern1 = r'\*\*Title:\*\*\s+([^\n]+)'
                        matches1 = re.findall(pattern1, part.text)

                        # Try pattern 2: * **Title** or 1. **Title** (without colon)
                        pattern2 = r'(?:\d+\.|\*)\s+\*\*(?!Title:)([^*]+)\*\*'
                        matches2 = re.findall(pattern2, part.text)

                        # Use whichever pattern found more results
                        if len(matches1) > len(matches2):
                            text_titles.extend(matches1)
                        else:
                            text_titles.extend(matches2)

        # Extract URLs from grounding_chunks
        urls = []
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                gm = candidate.grounding_metadata

                if hasattr(gm, 'grounding_chunks') and gm.grounding_chunks:
                    for idx, chunk in enumerate(gm.grounding_chunks):
                        if hasattr(chunk, 'web') and chunk.web:
                            redirect_url = getattr(chunk.web, 'uri', '')
                            domain = getattr(chunk.web, 'domain', '')

                            # Use title from text response if available, else domain
                            title = text_titles[idx] if idx < len(text_titles) else domain

                            if not redirect_url:
                                continue

                            # Try to resolve redirect to real URL
                            real_url = redirect_url
                            if follow_redirects and redirect_url.startswith('https://vertexaisearch.cloud.google.com'):
                                try:
                                    with httpx.Client(follow_redirects=True, timeout=5.0) as http_client:
                                        resp = http_client.head(redirect_url)
                                        real_url = str(resp.url)
                                except Exception:
                                    # If redirect fails, use domain to construct likely URL
                                    if domain:
                                        real_url = f"https://{domain}"

                            urls.append({
                                "title": title,
                                "url": real_url,
                                "domain": domain,
                                "redirect_url": redirect_url if redirect_url != real_url else None
                            })

        return json.dumps({
            "query": query,
            "results_count": len(urls),
            "results": urls,
            "follow_redirects_enabled": follow_redirects
        })

    except Exception as e:
        return json.dumps({
            "error": "Search failed",
            "message": str(e),
            "hint": "Check GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION env vars",
            "results": []
        })
