#!/usr/bin/env python3
"""
Auto Threads Video Generator — Tu dong hoan toan
Mo trinh duyet -> Tim kiem Threads -> Thu thap bai dang -> Viet narration -> TTS -> Render video

Su dung:
  python auto_threads.py "tinh hinh viec lam tai ha noi hom nay"
  python auto_threads.py "gen z va chuyen di lam"
  python auto_threads.py "drama showbiz hom nay"

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


# ---------------------------------------------------------------------------
# THREADS SCRAPER (Playwright)
# ---------------------------------------------------------------------------
async def scrape_threads(topic: str, max_posts: int = MAX_POSTS) -> list[dict]:
    """Mo trinh duyet, vao Threads search, thu thap bai dang."""
    from playwright.async_api import async_playwright

    print(f"\n[SCRAPER] Mo trinh duyet, tim kiem: '{topic}'")

    posts: list[dict] = []

    async with async_playwright() as p:
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

        try:
            # Strategy 1: Search engines for Threads profiles related to topic
            profile_urls = await _find_threads_profiles_via_search(page, topic)

            # Strategy 2: Visit each public Threads profile and extract posts
            for url in profile_urls:
                if len(posts) >= max_posts:
                    break
                new_posts = await _scrape_threads_profile(page, url, topic)
                posts.extend(new_posts)
                print(f"  [SCRAPER] {url} -> {len(new_posts)} bai")

            # Strategy 3: Try Threads search directly
            if len(posts) < 3:
                print("[SCRAPER] Thu Threads search truc tiep...")
                search_url = f"https://www.threads.net/search?q={topic}&serp_type=default"
                await page.goto(search_url, timeout=20000, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                direct_posts = await _extract_threads_posts(page, max_posts)
                posts.extend(direct_posts)

        except Exception as e:
            print(f"[SCRAPER] Loi: {e}")

        await context.close()

    # Ensure we have enough posts
    if len(posts) < 3:
        print("[SCRAPER] Khong du bai tu web, tao fallback posts tu chu de...")
        fallback = _generate_fallback_posts(topic, max_posts - len(posts))
        posts.extend(fallback)

    posts = posts[:max_posts]
    print(f"[SCRAPER] Tong: {len(posts)} bai dang")
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
              python auto_threads.py "drama showbiz hom nay"
        """),
    )
    parser.add_argument("topic", help="Chu de tim kiem tren Threads")
    parser.add_argument("--posts", type=int, default=MAX_POSTS, help="So bai dang (mac dinh 7)")
    parser.add_argument("--voice", default=MALE_VOICE, help="Giong TTS")
    parser.add_argument("--template", default="threads", choices=["threads", "historical"],
                        help="Template video (mac dinh: threads)")
    parser.add_argument("--no-music", action="store_true", help="Khong dung nhac nen")
    parser.add_argument("--show-browser", action="store_true",
                        help="Hien thi trinh duyet (de dang nhap Threads)")
    args = parser.parse_args()

    # Pass headless flag to scraper
    global HEADLESS_MODE
    HEADLESS_MODE = not args.show_browser

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    topic = args.topic
    safe_topic = re.sub(r"[^\w\s]", "", topic).replace(" ", "_")[:30]

    print("=" * 60)
    print(f"  AUTO THREADS VIDEO GENERATOR")
    print(f"  Chu de: {topic}")
    print(f"  Phong cach: Threads City")
    print("=" * 60)

    # --- Step 1: Scrape posts ---
    print("\n[1/4] Thu thap bai dang tu Threads...")
    posts = await scrape_threads(topic, max_posts=args.posts)

    # --- Step 2: Generate narrations ---
    print("\n[2/4] Viet kich ban Threads City style...")
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

    # --- Step 3: Generate TTS audio ---
    print("\n[3/4] Tao audio TTS...")
    from backend.app.tts_service import synthesize_edge_tts

    posts_data = []
    for i, post in enumerate(all_posts):
        print(f"  Audio {i+1}/{len(all_posts)}: @{post['username']}")
        audio_file, duration = await synthesize_edge_tts(
            text=post["narration"],
            language="vi",
            voice=args.voice,
        )
        filename = Path(audio_file).name
        shutil.copy2(audio_file, AUDIO_DIR / filename)

        dur = max(duration + 1.5, 5.0)
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
            "audioFile": f"audio/{filename}",
            "durationInSeconds": dur,
        })
        print(f"    -> {duration:.1f}s")

    total_duration = sum(p["durationInSeconds"] for p in posts_data)

    # --- Step 4: Render video ---
    print(f"\n[4/4] Render video...")

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
