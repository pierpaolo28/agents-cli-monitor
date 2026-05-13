"""Web search tools for finding Agents CLI mentions across multiple platforms."""

import json
import re


def detect_agents_cli_patterns(content: str, url: str) -> str:
    """
    Analyze content to detect THIRD-PARTY Agents CLI mentions.

    IMPORTANT: This tool EXCLUDES first-party Google content.
    We only want external coverage and community mentions, not Google's own docs/blogs.

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
    # EXCLUDE first-party Google content - we only want third-party mentions
    first_party_domains = [
        "google.github.io",
        "github.com/google/agents-cli",
        "developers.googleblog.com",
        "docs.cloud.google.com",
        "adk.dev",
        "cloud.google.com",
        "console.cloud.google.com",
        "youtube.com/@GoogleCloudTech",
        "youtube.com/googlecloud",
    ]

    # Check if this is first-party content
    for domain in first_party_domains:
        if domain in url:
            return json.dumps({
                "is_relevant": False,
                "confidence": 0.0,
                "patterns_found": [],
                "reason": f"First-party content excluded: {domain}",
                "threshold_used": 0.3,
            })

    patterns_found = []
    confidence = 0.0

    # Combine content and URL for pattern matching
    combined_text = f"{content} {url}"

    # High confidence patterns (0.5 each) - Clear third-party content about agents-cli
    high_confidence_patterns = [
        (r"agents-cli", "CLI tool name mentioned"),
        (r"Agents CLI", "Agents CLI explicitly mentioned"),
        (r"google-agents-cli", "Package name"),
        # Third-party platforms talking about agents-cli
        (r"medium\.com.*agents.{0,20}cli", "Medium article"),
        (r"infoq\.com.*agents.{0,20}cli", "InfoQ article"),
        (r"habr\.com.*agents.{0,20}cli", "Habr article"),
        (r"dev\.to.*agents.{0,20}cli", "Dev.to article"),
        (r"reddit\.com.*agents.{0,20}cli", "Reddit discussion"),
    ]

    # Medium confidence patterns (0.3 each) - Strong third-party indicators
    medium_confidence_patterns = [
        # Third-party content types
        (r"(tutorial|guide|walkthrough|how.{0,10}to).{0,40}agents.{0,20}cli", "Third-party tutorial"),
        (r"(review|overview|introduction).{0,40}agents.{0,20}cli", "Third-party review/overview"),
        (r"agents-cli\s+(create|deploy|install|playground|eval)", "CLI command usage"),
        (r"uvx google-agents-cli", "Installation command"),
        # YouTube (non-Google channels)
        (r"youtube\.com/watch.*agents", "YouTube video about agents"),
    ]

    # Low confidence patterns (0.2 each) - Supporting evidence
    low_confidence_patterns = [
        (r"(sfeir|codingame|hackernoon|hashnode).*agents", "Tech publication"),
        (r"stackoverflow.*agents.{0,20}cli", "StackOverflow"),
        (r"twitter\.com.*agents.{0,20}cli", "Twitter mention"),
        (r"linkedin\.com.*agents.{0,20}cli", "LinkedIn post"),
    ]

    # Check high confidence patterns
    for pattern, description in high_confidence_patterns:
        if re.search(pattern, combined_text, re.IGNORECASE):
            patterns_found.append(description)
            confidence += 0.4

    # Check medium confidence patterns
    for pattern, description in medium_confidence_patterns:
        if re.search(pattern, combined_text, re.IGNORECASE):
            patterns_found.append(description)
            confidence += 0.2

    # Check low confidence patterns
    for pattern, description in low_confidence_patterns:
        if re.search(pattern, combined_text, re.IGNORECASE):
            patterns_found.append(description)
            confidence += 0.1

    # Cap confidence at 1.0
    confidence = min(confidence, 1.0)

    # Single threshold for all domains
    threshold = 0.3
    is_relevant = confidence >= threshold

    reason = ""
    if is_relevant:
        reason = f"Found {len(patterns_found)} Agents CLI pattern(s): {', '.join(patterns_found[:3])}"
        if len(patterns_found) > 3:
            reason += f" (+{len(patterns_found) - 3} more)"
    else:
        reason = "No significant Agents CLI patterns detected"

    result = {
        "is_relevant": is_relevant,
        "confidence": round(confidence, 2),
        "patterns_found": patterns_found,
        "reason": reason,
        "threshold_used": threshold,
    }

    return json.dumps(result)
