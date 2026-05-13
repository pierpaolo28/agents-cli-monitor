"""
Evaluation dataset of known Agents CLI mentions.

This dataset serves as ground truth to test whether the monitoring agent
can successfully discover these mentions through its search capabilities.
"""

from typing import TypedDict


class MentionEntry(TypedDict):
    """Structure for a known mention entry."""
    url: str
    title: str
    category: str  # docs, blog, video, social, article
    date_published: str  # Approximate date if known


# Ground truth dataset of known Agents CLI mentions
KNOWN_MENTIONS: list[MentionEntry] = [
    # === Official Google Documentation ===
    {
        "url": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/agents/quickstart-adk",
        "title": "Build an agent with ADK and Agents CLI",
        "category": "docs",
        "date_published": "2026-04-01",
    },
    {
        "url": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime",
        "title": "Agent Development Kit Runtime",
        "category": "docs",
        "date_published": "2026-04-01",
    },
    {
        "url": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/deploy-an-agent",
        "title": "Deploy an agent with Agents CLI",
        "category": "docs",
        "date_published": "2026-04-01",
    },
    {
        "url": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/agent-garden",
        "title": "Agent Garden - Gemini Enterprise Agent Platform",
        "category": "docs",
        "date_published": "2026-04-01",
    },
    {
        "url": "https://docs.cloud.google.com/gemini/enterprise/docs/register-and-manage-an-adk-agent",
        "title": "Register and manage an ADK agent",
        "category": "docs",
        "date_published": "2026-04-01",
    },
    {
        "url": "https://adk.dev/deploy/agent-runtime/agents-cli/",
        "title": "Agents CLI - Agent Development Kit",
        "category": "docs",
        "date_published": "2026-04-01",
    },
    {
        "url": "https://adk.dev/tutorials/coding-with-ai/#agents-cli",
        "title": "Coding with AI using Agents CLI",
        "category": "docs",
        "date_published": "2026-04-01",
    },

    # === Official Google Blogs ===
    {
        "url": "https://developers.googleblog.com/agents-cli-in-agent-platform-create-to-production-in-one-cli/",
        "title": "Agents CLI in Agent Platform: create to production in one CLI",
        "category": "blog",
        "date_published": "2026-04-15",
    },
    {
        "url": "https://developers.googleblog.com/build-long-running-ai-agents-that-pause-resume-and-never-lose-context-with-adk/",
        "title": "Build long-running AI agents with ADK",
        "category": "blog",
        "date_published": "2026-04-20",
    },

    # === YouTube Videos ===
    {
        "url": "https://www.youtube.com/watch?v=FxnjRYo3fpU",
        "title": "Introducing Agents CLI in Agent Platform",
        "category": "video",
        "date_published": "2026-04-15",
    },
    {
        "url": "https://www.youtube.com/watch?v=LHcjN11nNPU",
        "title": "What is Gemini Enterprise Agent Platform?",
        "category": "video",
        "date_published": "2026-04-15",
    },

    # === Social Media - Official Google ===
    {
        "url": "https://www.linkedin.com/feed/update/urn:li:activity:7452763201487835137/",
        "title": "Google Developers - Agents CLI Launch",
        "category": "social",
        "date_published": "2026-04-15",
    },
    {
        "url": "https://x.com/googledevs/status/2046997468210966754",
        "title": "Google Developers - Agents CLI Announcement",
        "category": "social",
        "date_published": "2026-04-15",
    },
    {
        "url": "https://bsky.app/profile/developers.google.com/post/3mk3xvainxq27",
        "title": "Google Developers - Agents CLI Post",
        "category": "social",
        "date_published": "2026-04-15",
    },

    # === Medium Articles ===
    {
        "url": "https://medium.com/p/3d1eb54263a7",
        "title": "What Is Google agents-cli? Complete Guide",
        "category": "blog",
        "date_published": "2026-04-18",
    },
    {
        "url": "https://medium.com/google-cloud/i-attempted-to-build-a-team-of-agents-to-help-do-my-job-on-google-cloud-agent-platform-with-the-dc99ff03205f",
        "title": "Building a team of agents on Agent Platform",
        "category": "blog",
        "date_published": "2026-04-20",
    },

    # === News Articles ===
    {
        "url": "https://www.infoq.com/news/2026/04/agents-cli-google-cloud/",
        "title": "Agents CLI: Google Cloud Enterprise Agent Platform",
        "category": "article",
        "date_published": "2026-04-16",
    },
    {
        "url": "https://www.sfeir.dev/ia/google-cloud-next-2026-agents-cli-jai-teste-le-nouveau-couteau-suisse-de-google-pour-automatiser-ladlc-de-vos-agents-adk/",
        "title": "Google Cloud NEXT 2026: Agents CLI (French)",
        "category": "article",
        "date_published": "2026-04-17",
    },
    {
        "url": "https://habr.com/en/articles/1029726/",
        "title": "Agents CLI overview (Russian)",
        "category": "article",
        "date_published": "2026-04-19",
    },

    # === Social Media - Community ===
    {
        "url": "https://www.linkedin.com/posts/addyosmani_agents-cli-in-agent-platform-ugcPost-7452851657283096576-ebMH/",
        "title": "Addy Osmani - Agents CLI in Agent Platform",
        "category": "social",
        "date_published": "2026-04-15",
    },
    {
        "url": "https://www.linkedin.com/feed/update/urn:li:activity:7452739566299561986/",
        "title": "LinkedIn - Agents CLI Discussion",
        "category": "social",
        "date_published": "2026-04-15",
    },
    {
        "url": "https://www.linkedin.com/posts/jh91_google-open-sourced-an-agents-command-line-share-7452952380796518400-mi50/",
        "title": "Google open-sourced Agents CLI",
        "category": "social",
        "date_published": "2026-04-15",
    },
    {
        "url": "https://www.linkedin.com/feed/update/urn:li:activity:7452767430017380352/",
        "title": "LinkedIn - Agents CLI Post",
        "category": "social",
        "date_published": "2026-04-15",
    },
    {
        "url": "https://www.linkedin.com/feed/update/urn:li:activity:7452787989971394560/",
        "title": "LinkedIn - Agents CLI Discussion",
        "category": "social",
        "date_published": "2026-04-15",
    },
    {
        "url": "https://www.linkedin.com/feed/update/urn:li:activity:7452843079482667008/",
        "title": "LinkedIn - Agents CLI Post",
        "category": "social",
        "date_published": "2026-04-15",
    },
    {
        "url": "https://www.linkedin.com/feed/update/urn:li:activity:7452911611297599488/",
        "title": "LinkedIn - Agents CLI Discussion",
        "category": "social",
        "date_published": "2026-04-15",
    },
]


def get_known_mentions_by_category() -> dict[str, list[MentionEntry]]:
    """Group known mentions by category."""
    by_category: dict[str, list[MentionEntry]] = {}
    for mention in KNOWN_MENTIONS:
        category = mention["category"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(mention)
    return by_category


def get_known_urls() -> set[str]:
    """Get set of all known URLs for quick lookup."""
    return {mention["url"] for mention in KNOWN_MENTIONS}


# Summary statistics
TOTAL_KNOWN_MENTIONS = len(KNOWN_MENTIONS)
CATEGORIES = {
    "docs": len([m for m in KNOWN_MENTIONS if m["category"] == "docs"]),
    "blog": len([m for m in KNOWN_MENTIONS if m["category"] == "blog"]),
    "video": len([m for m in KNOWN_MENTIONS if m["category"] == "video"]),
    "social": len([m for m in KNOWN_MENTIONS if m["category"] == "social"]),
    "article": len([m for m in KNOWN_MENTIONS if m["category"] == "article"]),
}
