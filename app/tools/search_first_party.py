"""Search tool for finding Agents CLI mentions on Google's own properties."""

import json
import re


def detect_agents_cli_first_party(content: str, url: str) -> str:
    """
    Analyze content to detect FIRST-PARTY Agents CLI mentions.

    This validates content from Google's own properties:
    - developers.googleblog.com
    - docs.cloud.google.com
    - adk.dev
    - google.github.io/agents-cli

    Args:
        content: The text content to analyze
        url: The URL of the content (for additional context)

    Returns:
        JSON string containing:
        - is_relevant: Boolean indicating if content is about Agents CLI
        - confidence: Confidence score (0.0 to 1.0)
        - patterns_found: List of patterns detected
        - reason: Explanation of why it was flagged
        - threshold_used: The confidence threshold applied
    """
    # ONLY accept first-party Google content (excluding the repo/docs itself)
    first_party_domains = [
        "developers.googleblog.com",
        "docs.cloud.google.com",
        "adk.dev",
    ]

    # Check if this is first-party content
    is_first_party = False
    matched_domain = None
    for domain in first_party_domains:
        if domain in url:
            is_first_party = True
            matched_domain = domain
            break

    if not is_first_party:
        return json.dumps({
            "is_relevant": False,
            "confidence": 0.0,
            "patterns_found": [],
            "reason": "Not a first-party Google domain",
            "threshold_used": 0.3,
        })

    patterns_found = []
    confidence = 0.0

    # Combine content and URL for pattern matching
    combined_text = f"{content} {url}"

    # High confidence patterns (0.5 each) - Clear mentions of agents-cli
    high_confidence_patterns = [
        (r"agents-cli", "CLI tool name mentioned"),
        (r"Agents CLI", "Agents CLI explicitly mentioned"),
        (r"google-agents-cli", "Package name"),
        (r"agents-cli\s+(create|deploy|install|playground|eval)", "CLI command usage"),
    ]

    # Medium confidence patterns (0.3 each) - Agent Platform context
    medium_confidence_patterns = [
        (r"Agent Platform.*CLI", "Agent Platform with CLI context"),
        (r"CLI.*Agent Platform", "CLI with Agent Platform context"),
        (r"command.{0,10}line.{0,10}(tool|interface)", "Command-line tool reference"),
        (r"ADK.*CLI", "ADK with CLI context"),
    ]

    # Check high confidence patterns
    for pattern, description in high_confidence_patterns:
        if re.search(pattern, combined_text, re.IGNORECASE):
            patterns_found.append(description)
            confidence += 0.5

    # Check medium confidence patterns
    for pattern, description in medium_confidence_patterns:
        if re.search(pattern, combined_text, re.IGNORECASE):
            patterns_found.append(description)
            confidence += 0.3

    # Cap confidence at 1.0
    confidence = min(confidence, 1.0)

    # Threshold for first-party content
    threshold = 0.3
    is_relevant = confidence >= threshold

    reason = ""
    if is_relevant:
        reason = f"Found {len(patterns_found)} Agents CLI pattern(s) on {matched_domain}: {', '.join(patterns_found[:3])}"
        if len(patterns_found) > 3:
            reason += f" (+{len(patterns_found) - 3} more)"
    else:
        reason = f"No significant Agents CLI patterns detected on {matched_domain}"

    result = {
        "is_relevant": is_relevant,
        "confidence": round(confidence, 2),
        "patterns_found": patterns_found,
        "reason": reason,
        "threshold_used": threshold,
        "domain": matched_domain,
    }

    return json.dumps(result)
