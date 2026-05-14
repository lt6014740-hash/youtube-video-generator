#!/usr/bin/env python3
"""
Auto Threads Video Generator — Tu dong hoan toan
Mo trinh duyet -> Tim kiem Threads -> Thu thap bai dang -> Viet narration -> TTS -> Render video

Su dung:
  # Che do 1: Ket noi Chrome that cua ban (da login Threads) — DU LIEU CHINH XAC NHAT
  # Buoc 1: Mo Chrome voi remote debugging:
  #   Windows: chrome.exe --remote-debugging-port=9222
  #   Mac:     /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222
  #   Linux:   google-chrome --remote-debugging-port=9222
  # Buoc 2: Dang nhap Threads trong Chrome do
  # Buoc 3: Chay script:
  python auto_threads.py "tinh hinh viec lam tai ha noi" --use-chrome

  # Che do 2: Tu dong scrape (khong can login, du lieu han che hon)
  python auto_threads.py "gen z va cong viec"

  # Che do 3: Hien thi browser de dang nhap (luu session cho lan sau)
  python auto_threads.py "drama showbiz hom nay" --show-browser

Phong cach: Threads City — giong ke chuyen do thi, gan gui, trending
"""

import argparse
import asyncio
import json
import random
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# ---------------------------------------------------------------------------
# GEN Z SLANG DICTIONARY
# ---------------------------------------------------------------------------
SLANG_FILE = Path(__file__).parent / "genz_slang.json"
_slang_dict: dict[str, str] = {}


def _load_slang() -> dict[str, str]:
    """Load Gen Z abbreviation dictionary once."""
    global _slang_dict
    if _slang_dict:
        return _slang_dict
    if SLANG_FILE.exists():
        with open(SLANG_FILE, encoding="utf-8") as f:
            data = json.load(f)
        _slang_dict = data.get("abbreviations", {})
    return _slang_dict


def _expand_slang(text: str) -> str:
    """Replace Gen Z abbreviations with full words for TTS readability."""
    slang = _load_slang()
    if not slang:
        return text
    # Sort by length descending so longer matches take priority
    for abbr in sorted(slang, key=len, reverse=True):
        full = slang[abbr]
        # Word-boundary match (case insensitive)
        pattern = r"(?<!\w)" + re.escape(abbr) + r"(?!\w)"
        text = re.sub(pattern, full, text, flags=re.IGNORECASE)
    return text


def _humanize_number(text: str) -> str:
    """Convert number strings like '5K', '3.2K', '1.8M', '554' to Vietnamese speech."""
    def _num_to_vn(match: re.Match) -> str:
        raw = match.group(0)
        suffix = ""
        num_str = raw

        if raw[-1].upper() in ("K", "M"):
            suffix = raw[-1].upper()
            num_str = raw[:-1]

        try:
            num = float(num_str.replace(",", ""))
        except ValueError:
            return raw

        if suffix == "K":
            num *= 1000
        elif suffix == "M":
            num *= 1_000_000

        num = int(num)

        if num >= 1_000_000:
            m = num / 1_000_000
            if m == int(m):
                return f"{int(m)} triệu"
            return f"{m:.1f} triệu"
        elif num >= 1000:
            k = num / 1000
            remainder = num % 1000
            if remainder == 0:
                return f"{int(k)} nghìn"
            elif remainder % 100 == 0:
                return f"{int(k)} nghìn {remainder // 100} trăm"
            else:
                return f"{int(k)} nghìn {remainder}"
        return str(num)

    # Match patterns like 5K, 3.2K, 1.8M, 1,234, etc.
    return re.sub(r"\d[\d,.]*[KMkm]|\d[\d,.]+", _num_to_vn, text)


# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "output"
VIDEO_DIR = ROOT_DIR / "video"
AUDIO_DIR = VIDEO_DIR / "public" / "audio"
BROWSER_STATE_DIR = ROOT_DIR / ".browser-state"
MALE_VOICE = "vi-VN-NamMinhNeural"
MAX_POSTS = 7

# Threads City narration style markers
CITY_OPENERS = [
    "Ê nghe này,",
    "Nói thật nha,",
    "Real talk nè,",
    "Okay vấn đề là,",
    "Ủa wait,",
    "Này nghe đã chưa,",
    "Chờ chút đã,",
    "Hmm interesting,",
    "No cap nha,",
    "Sự thật là,",
]

CITY_CONNECTORS = [
    "mà nói thật",
    "kiểu vibe đó",
    "chill vậy thôi",
    "real talk luôn",
    "vậy đó mọi người",
    "flex dữ chưa",
    "drama ghê",
    "slay quá đi",
    "toxic thiệt",
    "deep ghê",
]

CITY_CLOSERS = [
    "Nghĩ sao comment bên dưới nha!",
    "Ai đồng ý thì like đi!",
    "Vibe nào mọi người?",
    "Real hay fake đây?",
    "Đúng không mọi người?",
    "Ý kiến gì không?",
    "Chill ha!",
    "Slay chưa!",
]

AVATAR_EMOJIS = ["🏙️", "💼", "🔥", "💬", "📱", "🎯", "💡", "🚀", "⚡", "🌟", "💪", "🎭"]
AVATAR_COLORS = [
    "#e94560", "#3b82f6", "#a855f7", "#f59e0b",
    "#06b6d4", "#ec4899", "#10b981", "#f97316",
]
HEADLESS_MODE = True

# Regex pattern to strip emojis and special Unicode symbols that Edge-TTS cannot pronounce
_EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"  # enclosed chars
    "\U0001f926-\U0001f937"  # supplemental
    "\U00010000-\U0010ffff"  # all other supplementary
    "\u2640-\u2642"  # gender symbols
    "\u2600-\u2B55"  # misc symbols
    "\u200d"  # zero width joiner
    "\ufe0f"  # variation selector
    "]+",
    flags=re.UNICODE,
)


def _clean_text_for_tts(text: str) -> str:
    """Remove emojis and special chars that cause Edge-TTS to fail."""
    cleaned = _EMOJI_RE.sub("", text)
    # Collapse multiple spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if cleaned else "Nội dung bài đăng"


# ---------------------------------------------------------------------------
# THREADS SCRAPER (Playwright)
# ---------------------------------------------------------------------------
USE_CHROME_CDP = False
CDP_URL = "http://localhost:9222"


def _decompose_keywords(topic: str) -> list[str]:
    """Boc tach tu khoa dai thanh cac tu khoa ngan hon.
    VD: 'tình hình việc làm tại hà nội hôm nay'
      -> ['tình hình việc làm tại hà nội hôm nay',
          'việc làm hà nội', 'việc làm', 'hà nội']
    """
    stop_words = {
        "tại", "ở", "của", "và", "là", "có", "không", "này", "cho", "với",
        "các", "một", "những", "đã", "đang", "sẽ", "rất", "thì", "mà", "nhưng",
        "nên", "vì", "để", "từ", "theo", "hôm", "nay", "ngày", "về", "trên",
        "the", "in", "at", "on", "for", "and", "or", "how", "what", "tình", "hình",
    }

    # Full topic first
    variants: list[str] = [topic]

    # Remove stop words to get core keywords
    words = topic.lower().split()
    core = [w for w in words if w not in stop_words and len(w) > 1]

    # Combine core words in groups of 2-3
    if len(core) >= 3:
        variants.append(" ".join(core))
    if len(core) >= 2:
        # Sliding window of 2
        for i in range(len(core) - 1):
            pair = f"{core[i]} {core[i+1]}"
            if pair not in variants:
                variants.append(pair)
    # Individual important words (only if 3+ chars)
    for w in core:
        if len(w) >= 3 and w not in variants:
            variants.append(w)

    return variants


def _is_vietnamese(text: str) -> bool:
    """Check if text contains Vietnamese characters."""
    vn_chars = "àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ"
    text_lower = text.lower()
    vn_count = sum(1 for c in text_lower if c in vn_chars)
    return vn_count >= 2 or any(
        w in text_lower
        for w in ["của", "và", "là", "được", "có", "không", "này", "cho", "với", "các"]
    )


async def scrape_threads(topic: str, max_posts: int = MAX_POSTS) -> list[dict]:
    """Mo trinh duyet, vao Threads search, thu thap bai dang."""
    from playwright.async_api import async_playwright

    print(f"\n[SCRAPER] Mo trinh duyet, tim kiem: '{topic}'")

    posts: list[dict] = []

    async with async_playwright() as p:
        browser = None
        context = None
        page = None
        close_browser = False

        try:
            if USE_CHROME_CDP:
                # --- CHE DO 1: Ket noi Chrome that cua nguoi dung ---
                print(f"[SCRAPER] Ket noi Chrome cua ban tai {CDP_URL}...")
                browser = await p.chromium.connect_over_cdp(CDP_URL)
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                page = await context.new_page()
                close_browser = False

                # Scrape Threads search voi keyword decomposition
                keywords = _decompose_keywords(topic)
                for kw in keywords:
                    if len(posts) >= max_posts:
                        break
                    print(f"[SCRAPER] Tim voi tu khoa: '{kw}'")
                    new_posts = await _scrape_threads_logged_in(page, kw, max_posts - len(posts))
                    posts.extend(new_posts)

            else:
                # --- CHE DO 2/3: Dung browser rieng ---
                BROWSER_STATE_DIR.mkdir(parents=True, exist_ok=True)
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(BROWSER_STATE_DIR),
                    headless=HEADLESS_MODE,
                    viewport={"width": 430, "height": 932},
                    user_agent=(
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                        "Version/17.0 Mobile/15E148 Safari/604.1"
                    ),
                    locale="vi-VN",
                )
                page = await context.new_page()
                close_browser = True

                # Thu Threads search truc tiep (co the da login tu --show-browser)
                search_url = f"https://www.threads.net/search?q={topic}&serp_type=default"
                print(f"[SCRAPER] Truy cap Threads search...")
                await page.goto(search_url, timeout=20000, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)

                body = await page.inner_text("body")
                if "Log in" not in body or len(body) > 1000:
                    # Da login hoac trang co noi dung
                    posts = await _scrape_threads_logged_in(page, topic, max_posts)

                # Neu chua du bai, dung search engine voi keyword decomposition
                if len(posts) < max_posts:
                    keywords = _decompose_keywords(topic)
                    print(f"[SCRAPER] Tim bai qua search engine, {len(keywords)} bien the tu khoa...")
                    visited_profiles: set[str] = set()
                    for kw in keywords:
                        if len(posts) >= max_posts:
                            break
                        print(f"  [SCRAPER] Thu tu khoa: '{kw}'")
                        profile_urls = await _find_threads_profiles_via_search(page, kw)
                        for url in profile_urls:
                            if len(posts) >= max_posts:
                                break
                            if url in visited_profiles:
                                continue
                            visited_profiles.add(url)
                            new_posts = await _scrape_threads_profile(page, url, topic)
                            posts.extend(new_posts)
                            if new_posts:
                                print(f"    {url} -> {len(new_posts)} bai")

        except Exception as e:
            print(f"[SCRAPER] Loi: {e}")

        # Cleanup
        if close_browser and context:
            await context.close()

    # Filter: chi lay bai tieng Viet neu co du
    vn_posts = [p for p in posts if _is_vietnamese(p.get("content", ""))]
    if len(vn_posts) >= 3:
        posts = vn_posts

    # Ensure we have enough posts
    if len(posts) < 3:
        print("[SCRAPER] Khong du bai tu web, tao fallback posts tu chu de...")
        fallback = _generate_fallback_posts(topic, max_posts - len(posts))
        posts.extend(fallback)

    posts = posts[:max_posts]
    print(f"[SCRAPER] Tong: {len(posts)} bai dang")
    return posts


async def _scrape_threads_logged_in(page, topic: str, max_posts: int) -> list[dict]:
    """Scrape Threads search results khi da dang nhap."""
    posts: list[dict] = []

    # Neu chua o trang search, navigate toi
    current_url = page.url
    if "threads.net/search" not in current_url:
        search_url = f"https://www.threads.net/search?q={topic}&serp_type=default"
        await page.goto(search_url, timeout=20000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

    # Scroll de load them bai
    for i in range(5):
        await page.evaluate("window.scrollBy(0, 800)")
        await page.wait_for_timeout(1500)

    body_text = await page.inner_text("body")
    lines = [l.strip() for l in body_text.split("\n") if l.strip()]

    skip_patterns = {
        "log in", "sign up", "follow", "followers", "following",
        "translate", "say more", "privacy", "terms", "about",
        "đăng nhập", "đăng ký", "xem thêm", "điều khoản",
        "threads", "replies", "reposts", "mention", "media",
        "verified", "search", "home",
    }

    # Parse posts: look for patterns username -> timestamp -> content
    current_username = None
    for line in lines:
        if len(posts) >= max_posts:
            break
        lower = line.lower().strip()

        # Skip UI/nav text
        if any(sw in lower for sw in skip_patterns):
            continue
        if len(line) < 5 or line.startswith("http"):
            continue
        if re.match(r"^[\d,.\s]+$", line):
            continue

        # Detect username (short, no spaces, or @mention)
        if (len(line) < 25 and " " not in line and "." in line) or line.startswith("@"):
            current_username = line.lstrip("@").strip()
            continue

        # Detect time ago pattern
        if re.match(r"^\d+[hdmswn]$", line) or line in ("Just now", "vừa xong"):
            continue

        # Substantial content line = a post
        if len(line) > 25:
            username = current_username or "threads_user"
            posts.append({
                "username": username[:25],
                "content": line[:300],
                "likes": random.randint(50, 8000),
                "comments": random.randint(5, 500),
                "reposts": random.randint(2, 200),
            })
            current_username = None

    print(f"[SCRAPER] Threads search: {len(posts)} bai dang")
    return posts


async def _find_threads_profiles_via_search(page, topic: str) -> list[str]:
    """Search engines to find Threads profile/post URLs related to topic."""
    profile_urls: list[str] = []
    seen: set[str] = set()

    # Try multiple search engines
    searches = [
        f"https://html.duckduckgo.com/html/?q=site%3Athreads.net+{topic.replace(' ', '+')}",
        f"https://www.google.com/search?q=site:threads.net+{topic.replace(' ', '+')}&hl=vi&num=15",
    ]

    for search_url in searches:
        if len(profile_urls) >= 6:
            break
        try:
            engine = "DuckDuckGo" if "duckduckgo" in search_url else "Google"
            print(f"[SCRAPER] {engine}: threads.net {topic}")
            await page.goto(search_url, timeout=15000, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            # Extract all links on page
            all_links = await page.query_selector_all("a")
            for link in all_links:
                href = await link.get_attribute("href") or ""
                # Find threads.net profile or post URLs
                match = re.search(
                    r"(https?://(?:www\.)?threads\.(?:net|com)/@[\w.]+)(/post/[\w]+)?",
                    href,
                )
                if match:
                    url = match.group(0)
                    base = match.group(1)
                    if base not in seen:
                        seen.add(base)
                        profile_urls.append(url)
            print(f"  -> {len(profile_urls)} link Threads")
        except Exception as e:
            print(f"  -> Loi: {e}")

    return profile_urls[:8]


async def _scrape_threads_profile(page, url: str, topic: str) -> list[dict]:
    """Visit a public Threads profile/post page and extract posts."""
    posts: list[dict] = []

    try:
        await page.goto(url, timeout=15000, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Scroll to load content
        for _ in range(2):
            await page.evaluate("window.scrollBy(0, 600)")
            await page.wait_for_timeout(1000)

        body_text = await page.inner_text("body")
        lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        # Extract username from URL
        username_match = re.search(r"@([\w.]+)", url)
        username = username_match.group(1) if username_match else "threads_user"

        # Filter for substantial content lines
        skip_words = {
            "log in", "sign up", "follow", "followers", "following",
            "threads", "replies", "media", "reposts", "mention",
            "translate", "say more", "privacy", "terms",
            "đăng nhập", "hãy đăng nhập", "xem thêm", "đăng ký",
            "your favorite", "christmas", "instagram",
        }

        content_lines = []
        for line in lines:
            lower = line.lower().strip()
            if (
                len(line) > 30
                and not any(sw in lower for sw in skip_words)
                and not line.startswith("http")
                and not re.match(r"^[\d,.\s]+$", line)
                and not re.match(r"^\d{2}/\d{2}/\d{2}$", line)
            ):
                content_lines.append(line)

        # Take the best content lines as posts
        topic_lower = topic.lower()
        topic_words = set(topic_lower.split())

        # Sort by relevance to topic
        def relevance(text: str) -> int:
            t = text.lower()
            return sum(1 for w in topic_words if w in t)

        content_lines.sort(key=relevance, reverse=True)

        for content in content_lines[:3]:
            if len(content) > 30:
                posts.append({
                    "username": username,
                    "content": content[:250],
                    "likes": random.randint(50, 5000),
                    "comments": random.randint(5, 300),
                    "reposts": random.randint(2, 150),
                })

    except Exception as e:
        print(f"  [SCRAPER] Loi khi doc {url}: {e}")

    return posts


async def _extract_threads_posts(page, max_posts: int) -> list[dict]:
    """Extract posts from a Threads page (search or profile)."""
    posts: list[dict] = []

    for _ in range(3):
        await page.evaluate("window.scrollBy(0, 800)")
        await page.wait_for_timeout(1000)

    body_text = await page.inner_text("body")
    lines = [l.strip() for l in body_text.split("\n") if l.strip()]

    skip_words = {
        "log in", "sign up", "follow", "followers", "following",
        "threads", "translate", "say more", "privacy", "terms",
    }

    for line in lines:
        if len(posts) >= max_posts:
            break
        lower = line.lower()
        if (
            len(line) > 40
            and not any(sw in lower for sw in skip_words)
            and not line.startswith("http")
        ):
            posts.append({
                "username": "threads_user",
                "content": line[:250],
                "likes": random.randint(50, 5000),
                "comments": random.randint(5, 300),
                "reposts": random.randint(2, 150),
            })

    return posts


async def scrape_thread_comments(url: str, max_comments: int = 10) -> tuple[dict, list[dict]]:
    """Scrape binh luan noi bat tu 1 URL bai viet Threads cu the.
    Tra ve (original_post, sorted_comments_by_likes).
    """
    from playwright.async_api import async_playwright

    # Normalize URL
    url = url.replace("threads.com", "threads.net")
    if not url.startswith("http"):
        url = "https://" + url

    print(f"\n[SCRAPER] Mo bai viet: {url}")

    original_post: dict = {}
    comments: list[dict] = []

    async with async_playwright() as p:
        browser = None
        context = None
        page = None

        try:
            if USE_CHROME_CDP:
                browser = await p.chromium.connect_over_cdp(CDP_URL)
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                page = await context.new_page()
            else:
                BROWSER_STATE_DIR.mkdir(parents=True, exist_ok=True)
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(BROWSER_STATE_DIR),
                    headless=HEADLESS_MODE,
                    viewport={"width": 1280, "height": 900},
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    locale="vi-VN",
                )
                page = await context.new_page()

            await page.goto(url, timeout=25000, wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)

            # Scroll to load more comments
            for _ in range(6):
                await page.evaluate("window.scrollBy(0, 800)")
                await page.wait_for_timeout(1200)

            # Parse comments from body text (works reliably in headless)
            body_text = await page.inner_text("body")
            lines = [l.strip() for l in body_text.split("\n") if l.strip()]

            # Also get username links in order for reliable username extraction
            all_user_links = await page.query_selector_all("a[href^='/@']")
            ordered_usernames: list[str] = []
            for link in all_user_links:
                href = await link.get_attribute("href") or ""
                uname = href.strip("/").lstrip("@")
                # Filter out post/media links — only keep pure profile links
                if uname and "/" not in uname and uname not in ("search", "login"):
                    if uname not in ordered_usernames or len(ordered_usernames) < 3:
                        ordered_usernames.append(uname)

            # State machine to parse text blocks
            skip_words = {
                "thread", "log in", "sign up", "translate", "privacy",
                "terms", "say more", "continue with", "related threads",
                "lượt xem", "tác giả", "report", "cookies", "© 2026",
            }

            current_username = None
            username_idx = 0
            entries: list[dict] = []
            i = 0

            while i < len(lines):
                line = lines[i]
                lower = line.lower().strip()

                # Skip UI text
                if any(sw in lower for sw in skip_words):
                    i += 1
                    continue

                # Detect username: short text with dots/underscores, no spaces
                is_username = (
                    len(line) < 30
                    and " " not in line
                    and ("." in line or "_" in line)
                    and not line.startswith("http")
                    and not re.match(r"^[\d,./]+$", line)
                )

                if is_username:
                    current_username = line.lstrip("@").strip()
                    i += 1
                    # Skip timestamp line (e.g., "09/02/2026" or "1d")
                    if i < len(lines) and re.match(r"^[\d/]+$|^\d+[hdmswn]$", lines[i].strip()):
                        i += 1
                    # Skip "· Tác giả" line
                    if i < len(lines) and "tác giả" in lines[i].lower():
                        i += 1
                    continue

                # Skip pure number lines (engagement counts like "3K", "426", "554", etc.)
                if re.match(r"^[\d,.]+[KMkm]?$", line):
                    i += 1
                    continue

                # Skip date-like lines
                if re.match(r"^\d{2}/\d{2}/\d{2,4}$", line):
                    i += 1
                    continue

                # Content line: substantial text = a comment
                if len(line) > 10:
                    username = current_username or (
                        ordered_usernames[username_idx]
                        if username_idx < len(ordered_usernames)
                        else "threads_user"
                    )

                    # Collect engagement numbers that follow
                    likes = 0
                    cmt_count = 0
                    j = i + 1
                    nums_found: list[int] = []
                    while j < len(lines) and len(nums_found) < 4:
                        nl = lines[j].strip()
                        if re.match(r"^[\d,.]+[KMkm]?$", nl):
                            nums_found.append(_parse_count(nl))
                            j += 1
                        else:
                            break

                    if nums_found:
                        likes = nums_found[0]
                    if len(nums_found) > 1:
                        cmt_count = nums_found[1]

                    entries.append({
                        "username": username[:25],
                        "content": line[:300],
                        "likes": likes,
                        "comments": cmt_count,
                        "reposts": 0,
                    })
                    current_username = None
                    username_idx += 1
                    i = j  # skip past the numbers
                    continue

                i += 1

            if entries:
                original_post = entries[0]
                seen_content: set[str] = set()
                for entry in entries[1:]:
                    ck = entry["content"][:50]
                    if ck in seen_content:
                        continue
                    seen_content.add(ck)
                    comments.append(entry)
                print(f"[SCRAPER] Tim thay {len(entries)} entries tu trang")

        except Exception as e:
            print(f"[SCRAPER] Loi: {e}")

        if context and not USE_CHROME_CDP:
            await context.close()

    # Sort by likes descending
    comments.sort(key=lambda c: c.get("likes", 0), reverse=True)
    comments = comments[:max_comments]

    print(f"[SCRAPER] Bai goc: @{original_post.get('username', '?')}")
    print(f"[SCRAPER] {len(comments)} binh luan noi bat (sap xep theo likes)")
    for c in comments[:5]:
        print(f"  @{c['username']} ({c['likes']} likes): {c['content'][:50]}...")

    return original_post, comments


def _parse_count(text: str) -> int:
    """Parse '3K', '1.2K', '554' into int."""
    text = text.strip().replace(",", "")
    if not text:
        return 0
    if text.upper().endswith("K"):
        return int(float(text[:-1]) * 1000)
    if text.upper().endswith("M"):
        return int(float(text[:-1]) * 1000000)
    try:
        return int(text)
    except ValueError:
        return 0


def _generate_fallback_posts(topic: str, count: int) -> list[dict]:
    """Generate topic-specific posts when scraping fails (Threads City style)."""

    # Threads City style — realistic, opinionated, Gen Z voice
    templates = [
        "Nói thật {topic} đang là vấn đề nóng, ai cũng bàn tán. Mình theo dõi mấy ngày rồi thấy nhiều ý kiến hay phết",
        "Update nhanh về {topic} cho ai chưa biết: Tình hình thay đổi khá nhiều so với tuần trước. Mọi người nên cập nhật!",
        "Có ai đang gặp vấn đề với {topic} không? Mình chia sẻ kinh nghiệm thực tế của bản thân nè, hy vọng giúp ích",
        "Hot take: {topic} không hẳn như mọi người đang nghĩ đâu. Cùng phân tích khách quan xem sao",
        "Tổng hợp những gì đang diễn ra với {topic}. Save post này lại để đọc kỹ nhé mọi người!",
        "Mình vừa trải nghiệm thực tế về {topic}. Nói thật là bất ngờ, không như trên mạng nói",
        "Góc nhìn từ người trong cuộc về {topic}: Thực tế khác xa với những gì truyền thông đưa tin",
        "Thread này mình viết cho ai đang quan tâm tới {topic}. Phân tích chi tiết từ A đến Z luôn",
        "Drama mới về {topic}: Cộng đồng đang chia rẽ thành 2 phe. Bạn thuộc phe nào?",
        "Chia sẻ thông tin hữu ích về {topic} mà ít người biết. Ai cần thì inbox mình tư vấn thêm nha",
    ]

    usernames = [
        "city.vibes", "hanoi.real.talk", "vn.threads.daily",
        "urban.pulse", "street.stories.vn", "trending.city",
        "real.talk.hn", "daily.threads.vn", "gen.z.city",
        "saigon.talks",
    ]

    posts = []
    random.shuffle(templates)
    random.shuffle(usernames)

    for i in range(min(count, len(templates))):
        posts.append({
            "username": usernames[i % len(usernames)],
            "content": templates[i].format(topic=topic),
            "likes": random.randint(200, 10000),
            "comments": random.randint(20, 600),
            "reposts": random.randint(10, 300),
        })

    return posts


# ---------------------------------------------------------------------------
# THREADS CITY NARRATION GENERATOR
# ---------------------------------------------------------------------------
def generate_city_narration(post: dict, index: int, total: int) -> str:
    """Generate Threads City style narration for a post."""
    content = post["content"]
    username = post["username"]
    likes = post.get("likes", 0)
    comments = post.get("comments", 0)

    opener = CITY_OPENERS[index % len(CITY_OPENERS)]
    connector = CITY_CONNECTORS[index % len(CITY_CONNECTORS)]

    # Shorten content for narration
    short_content = content[:100].rstrip(".")
    if len(content) > 100:
        short_content += "..."

    # Build narration based on engagement
    if likes > 3000:
        engagement = f"Bài này {likes:,} likes, viral dữ luôn"
    elif likes > 1000:
        engagement = f"{likes:,} likes rồi, hot phết"
    elif comments > 100:
        engagement = f"{comments} bình luận, bàn luận sôi nổi ghê"
    else:
        engagement = f"Mọi người react mạnh lắm"

    # Different narration patterns
    patterns = [
        f"{opener} @{username} vừa đăng: {short_content}. {engagement}, {connector}.",
        f"{opener} bài của @{username} đang gây chú ý: {short_content}. {engagement}!",
        f"Tiếp theo từ @{username}, {connector}: {short_content}. {engagement}.",
        f"{opener} @{username} chia sẻ, {short_content}. {engagement}, đúng không nè!",
        f"@{username} có góc nhìn hay: {short_content}. {engagement}, {connector}!",
    ]

    narration = patterns[index % len(patterns)]

    # Add closer for last post
    if index == total - 1:
        closer = random.choice(CITY_CLOSERS)
        narration += f" {closer}"

    return narration


def _extract_meme_keyword(content: str) -> str:
    """Extract 2-3 core keywords from comment content for meme search."""
    stop_words = {
        "mình", "của", "và", "là", "được", "có", "không", "này", "cho", "với",
        "các", "một", "những", "đã", "đang", "sẽ", "rất", "thì", "mà", "nhưng",
        "nên", "vì", "để", "từ", "theo", "bạn", "mọi", "người", "nha", "nè",
        "luôn", "quá", "lắm", "ghê", "dữ", "thiệt", "thật", "thế", "vậy",
        "hôm", "nay", "hãy", "tôi", "chúng", "trên", "đó", "cái", "ông",
        "bà", "anh", "chị", "em", "mấy", "tui", "ổng", "nào", "trường",
    }
    words = re.findall(r"[\w]+", content.lower())
    core = [w for w in words if w not in stop_words and len(w) > 2]
    return " ".join(core[:3]) if core else "funny"


def _generate_url_intro(original_post: dict) -> str:
    """Generate intro narration for URL comment video. No username."""
    content = original_post.get("content", "")[:100]
    likes = original_post.get("likes", 0)
    comments = original_post.get("comments", 0)

    content = _expand_slang(content)
    content = _humanize_number(content)
    likes_text = _humanize_number(str(likes))
    comments_text = _humanize_number(str(comments))

    intros = [
        f"Nóng nè! Bài viết: \"{content}\". "
        f"{likes_text} likes và {comments_text} bình luận, xem mọi người nói gì nha!",
        f"Hot trên Threads! \"{content}\". "
        f"Viral dữ luôn với {likes_text} likes. Cùng đọc bình luận nổi bật!",
        f"Bài viết đang gây sốt: \"{content}\". "
        f"Cộng đồng Threads bùng nổ với {comments_text} bình luận. Check ngay!",
    ]
    return random.choice(intros)


def _generate_comment_narration(post: dict, index: int, total: int) -> str:
    """Generate narration for a specific comment in URL mode.
    Rules: no username, humanize numbers, expand slang, read content as-is."""
    content = post.get("content", "")[:200]
    likes = post.get("likes", 0)

    # Expand slang and humanize numbers in content
    content = _expand_slang(content)
    content = _humanize_number(content)

    # Humanize like count
    if likes > 500:
        engagement = f". Bình luận này có {_humanize_number(str(likes))} likes"
    elif likes > 100:
        engagement = f". {_humanize_number(str(likes))} likes"
    else:
        engagement = ""

    # Simple narration: just read the content, minimal filler
    narration = content + engagement

    if index == total - 1:
        closer = random.choice(CITY_CLOSERS)
        narration += f". {closer}"

    return narration


def generate_intro_narration(topic: str) -> str:
    """Generate intro narration for the video."""
    intros = [
        f"Yo mọi người! Hôm nay Threads đang nóng với chủ đề: {topic}. Cùng xem mọi người nói gì nha!",
        f"Chào mọi người! Trending trên Threads hôm nay: {topic}. Nhiều góc nhìn hay lắm, cùng xem!",
        f"Real talk nè! {topic} đang được bàn tán rất nhiều trên Threads. Mình tổng hợp lại cho mọi người!",
    ]
    return random.choice(intros)


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------
async def main():
    parser = argparse.ArgumentParser(
        description="Auto Threads Video — Tu dong scrape + render video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Vi du:
              python auto_threads.py "tinh hinh viec lam tai ha noi"
              python auto_threads.py "gen z va cong viec"
              python auto_threads.py --url "https://www.threads.com/@user/post/ABC123"
        """),
    )
    parser.add_argument("topic", nargs="?", default=None,
                        help="Chu de tim kiem tren Threads (bo qua neu dung --url)")
    parser.add_argument("--url", type=str, default=None,
                        help="URL bai viet Threads — lay binh luan noi bat")
    parser.add_argument("--posts", type=int, default=MAX_POSTS, help="So bai dang (mac dinh 7)")
    parser.add_argument("--voice", default=MALE_VOICE, help="Giong TTS")
    parser.add_argument("--template", default="threads", choices=["threads", "historical"],
                        help="Template video (mac dinh: threads)")
    parser.add_argument("--no-music", action="store_true", help="Khong dung nhac nen")
    parser.add_argument("--no-meme", action="store_true",
                        help="Khong tim anh meme tu Pinterest")
    parser.add_argument("--show-browser", action="store_true",
                        help="Hien thi trinh duyet (de dang nhap Threads)")
    parser.add_argument("--use-chrome", action="store_true",
                        help="Ket noi Chrome that cua ban (da login Threads)")
    parser.add_argument("--cdp-port", type=int, default=9222,
                        help="Port Chrome remote debugging (mac dinh 9222)")
    args = parser.parse_args()

    if not args.url and not args.topic:
        parser.error("Can topic hoac --url")

    # Pass flags to scraper
    global HEADLESS_MODE, USE_CHROME_CDP, CDP_URL
    HEADLESS_MODE = not args.show_browser
    USE_CHROME_CDP = args.use_chrome
    CDP_URL = f"http://localhost:{args.cdp_port}"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    url_mode = bool(args.url)
    topic = args.topic or "Threads comments"
    safe_topic = re.sub(r"[^\w\s]", "", topic).replace(" ", "_")[:30]

    mode = "URL comments" if url_mode else (
        "Chrome CDP (da login)" if USE_CHROME_CDP else "Show browser" if not HEADLESS_MODE else "Auto scrape")
    print("=" * 60)
    print(f"  AUTO THREADS VIDEO GENERATOR")
    if url_mode:
        print(f"  URL: {args.url}")
    else:
        print(f"  Chu de: {topic}")
    print(f"  Che do: {mode}")
    print(f"  Phong cach: Threads City")
    print("=" * 60)

    if url_mode:
        # --- URL MODE: Scrape comments from a specific post ---
        print("\n[1/5] Lay binh luan noi bat tu bai viet...")
        original_post, comments = await scrape_thread_comments(args.url, max_comments=args.posts)

        if not original_post:
            print("[ERROR] Khong lay duoc bai viet goc!")
            return

        # Use original post content as topic
        topic = original_post.get("content", "Threads discussion")[:60]
        safe_topic = re.sub(r"[^\w\s]", "", topic).replace(" ", "_")[:30]

        posts = comments if comments else []

        if len(posts) < 3:
            print(f"[WARNING] Chi lay duoc {len(posts)} binh luan, them fallback...")

        # --- Step 2: Find meme for each comment ---
        if not args.no_meme:
            print("\n[2/5] Tim anh meme phu hop tung binh luan...")
            from pinterest_scraper import find_meme_images
            img_dir = ROOT_DIR / "video" / "public" / "images"
            img_dir.mkdir(parents=True, exist_ok=True)
            for i, post in enumerate(posts):
                kw = _extract_meme_keyword(post.get("content", ""))
                print(f"  [{i+1}] '{kw}' -> ", end="", flush=True)
                images = await find_meme_images(kw + " meme", count=1, output_dir=img_dir)
                if images:
                    post["memeImage"] = images[0]
                    print(f"OK ({images[0]})")
                else:
                    post["memeImage"] = ""
                    print("(khong tim thay)")
        else:
            print("\n[2/5] Bo qua tim anh meme (--no-meme)")

        # --- Step 3: Generate narrations for comments ---
        print("\n[3/5] Viet kich ban Threads City style...")
        intro_narration = _generate_url_intro(original_post)
        for i, post in enumerate(posts):
            post["narration"] = _generate_comment_narration(post, i, len(posts))
            post["timeAgo"] = post.get("timeAgo", random.choice(["1 giờ", "2 giờ", "3 giờ"]))
            post["hasReplies"] = post.get("comments", 0) > 0
            post["avatarEmoji"] = AVATAR_EMOJIS[i % len(AVATAR_EMOJIS)]
            post["avatarColor"] = AVATAR_COLORS[i % len(AVATAR_COLORS)]
            print(f"  [{i+1}] @{post['username']}: {post['narration'][:60]}...")

        # Add intro (original post) as first entry
        intro_post = {
            "username": original_post.get("username", "threads.city"),
            "timeAgo": "vừa xong",
            "content": original_post.get("content", topic),
            "likes": original_post.get("likes", 0),
            "comments": original_post.get("comments", 0),
            "reposts": original_post.get("reposts", 0),
            "hasReplies": True,
            "avatarEmoji": "🔥",
            "avatarColor": "#e94560",
            "narration": intro_narration,
        }
        all_posts = [intro_post] + posts

    else:
        # --- TOPIC MODE (existing behavior) ---
        # --- Step 1: Scrape posts ---
        print("\n[1/5] Thu thap bai dang tu Threads...")
        posts = await scrape_threads(topic, max_posts=args.posts)

        # --- Step 2: Find meme images from Pinterest ---
        if not args.no_meme:
            print("\n[2/5] Tim anh meme tu Pinterest...")
            from pinterest_scraper import find_memes_for_posts
            posts = await find_memes_for_posts(posts, output_dir=ROOT_DIR / "video" / "public" / "images")
        else:
            print("\n[2/5] Bo qua tim anh meme (--no-meme)")

        # --- Step 3: Generate narrations ---
        print("\n[3/5] Viet kich ban Threads City style...")
        intro_narration = generate_intro_narration(topic)
        for i, post in enumerate(posts):
            post["narration"] = generate_city_narration(post, i, len(posts))
            post["timeAgo"] = random.choice(["1 giờ", "2 giờ", "3 giờ", "5 giờ", "8 giờ", "12 giờ"])
            post["hasReplies"] = True
            post["avatarEmoji"] = AVATAR_EMOJIS[i % len(AVATAR_EMOJIS)]
            post["avatarColor"] = AVATAR_COLORS[i % len(AVATAR_COLORS)]
            print(f"  [{i+1}] @{post['username']}: {post['narration'][:60]}...")

        # Add intro as first "post"
        intro_post = {
            "username": "threads.city",
            "timeAgo": "vừa xong",
            "content": f"🔥 TRENDING: {topic.upper()}\n\nCùng xem cộng đồng Threads đang nói gì!",
            "likes": random.randint(5000, 20000),
            "comments": random.randint(500, 2000),
            "reposts": random.randint(200, 1000),
            "hasReplies": True,
            "avatarEmoji": "🏙️",
            "avatarColor": "#e94560",
            "narration": intro_narration,
        }
        all_posts = [intro_post] + posts

    # --- Step 4: Generate TTS audio ---
    print("\n[4/5] Tao audio TTS...")
    from backend.app.tts_service import synthesize_edge_tts

    posts_data = []
    for i, post in enumerate(all_posts):
        print(f"  Audio {i+1}/{len(all_posts)}: @{post['username']}")
        clean_narration = _clean_text_for_tts(post["narration"])
        try:
            audio_file, duration = await synthesize_edge_tts(
                text=clean_narration,
                language="vi",
                voice=args.voice,
            )
        except Exception as e:
            print(f"    [WARN] TTS loi, thu lai voi text don gian: {e}")
            fallback_text = _clean_text_for_tts(post.get("content", "")[:100])
            try:
                audio_file, duration = await synthesize_edge_tts(
                    text=fallback_text,
                    language="vi",
                    voice=args.voice,
                )
            except Exception:
                audio_file, duration = await synthesize_edge_tts(
                    text="Nội dung bài đăng tiếp theo trên Threads",
                    language="vi",
                    voice=args.voice,
                )
        filename = Path(audio_file).name
        shutil.copy2(audio_file, AUDIO_DIR / filename)

        has_meme = bool(post.get("memeImage"))
        meme_dur = 3.0 if has_meme else 0
        has_post_image = bool(post.get("postImage"))
        dur = max(duration + (2.5 if has_post_image else 1.5) + meme_dur, 5.0)
        posts_data.append({
            "username": post["username"],
            "timeAgo": post["timeAgo"],
            "content": post["content"],
            "likes": post.get("likes", 0),
            "comments": post.get("comments", 0),
            "reposts": post.get("reposts", 0),
            "hasReplies": post.get("hasReplies", False),
            "avatarEmoji": post.get("avatarEmoji", "💬"),
            "avatarColor": post.get("avatarColor", "#444"),
            "postImage": post.get("postImage", ""),
            "memeImage": post.get("memeImage", ""),
            "memeDuration": meme_dur,
            "audioFile": f"audio/{filename}",
            "durationInSeconds": dur,
        })
        print(f"    -> {duration:.1f}s")

    total_duration = sum(p["durationInSeconds"] for p in posts_data)

    # --- Step 5: Render video ---
    print(f"\n[5/5] Render video...")

    bgm_path = AUDIO_DIR / "background-music.mp3"
    has_bgm = bgm_path.exists() and not args.no_music

    props = {
        "posts": posts_data,
        "totalDurationInSeconds": total_duration,
        "fps": 30,
        "width": 1920,
        "height": 1080,
    }

    if has_bgm:
        props["backgroundMusic"] = "audio/background-music.mp3"
        props["backgroundMusicVolume"] = 0.15

    props_file = str(OUTPUT_DIR / f"auto_props_{safe_topic}.json")
    with open(props_file, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    output_file = str(OUTPUT_DIR / f"auto_threads_{safe_topic}.mp4")
    print(f"  Output: {output_file}")
    print(f"  So bai dang: {len(posts_data)}")
    print(f"  Thoi luong: {total_duration:.1f}s")
    print(f"  Nhac nen: {'Co' if has_bgm else 'Khong'}")

    result = subprocess.run(
        [
            "npx", "remotion", "render",
            "ThreadsScrollVideo",
            "--props", props_file,
            "--output", output_file,
            "--codec", "h264",
        ],
        cwd=str(VIDEO_DIR),
        capture_output=True, text=True, timeout=600,
    )

    if result.returncode != 0:
        print(f"STDERR: {result.stderr}")
        print(f"STDOUT: {result.stdout}")
        raise RuntimeError(f"Render that bai: {result.stderr}")

    # --- Result ---
    import os
    file_size = os.path.getsize(output_file) / (1024 * 1024)

    print(f"\n{'=' * 60}")
    print(f"  VIDEO HOAN THANH!")
    print(f"  File: {output_file}")
    print(f"  Kich thuoc: {file_size:.1f}MB")
    print(f"  Thoi luong: {total_duration:.1f}s")
    print(f"  So bai dang: {len(posts_data)}")
    print(f"  Chu de: {topic}")
    print(f"  Phong cach: Threads City")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
