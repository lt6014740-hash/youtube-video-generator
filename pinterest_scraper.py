#!/usr/bin/env python3
"""
Pinterest Meme Scraper — Tim anh meme phu hop voi noi dung bai dang.
Dung Playwright de scrape Pinterest search results.

Su dung:
  from pinterest_scraper import find_meme_images
  images = await find_meme_images("gen z di lam", count=5, output_dir="video/public/images")
"""

import asyncio
import hashlib
import re
from pathlib import Path
from urllib.parse import quote_plus

import httpx


def _decompose_search_keywords(keyword: str) -> list[str]:
    """Boc tach tu khoa dai thanh cac bien the ngan hon de tim anh."""
    stop_words = {
        "tại", "ở", "của", "và", "là", "có", "không", "này", "cho", "với",
        "các", "một", "những", "đã", "đang", "sẽ", "rất", "thì", "mà", "nhưng",
        "nên", "vì", "để", "từ", "theo", "hôm", "nay", "ngày", "về", "trên",
        "mình", "bạn", "mọi", "người", "tôi", "chúng", "ta",
        "tình", "hình", "the", "in", "at", "on", "for", "and",
    }
    variants: list[str] = [keyword]
    words = keyword.lower().split()
    core = [w for w in words if w not in stop_words and len(w) > 1]

    if len(core) >= 3:
        variants.append(" ".join(core))
    if len(core) >= 2:
        for i in range(len(core) - 1):
            pair = f"{core[i]} {core[i+1]}"
            if pair not in variants:
                variants.append(pair)
    for w in core:
        if len(w) >= 3 and w not in variants:
            variants.append(w)
    return variants


async def find_meme_images(
    keyword: str,
    count: int = 5,
    output_dir: str | Path = "video/public/images",
) -> list[str]:
    """
    Tim va download anh meme tu Pinterest theo tu khoa.
    Neu tu khoa dai khong co ket qua, tu dong boc tach tu khoa ngan hon.
    Tra ve danh sach duong dan tuong doi (vd: "images/meme_abc123.jpg")
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Try keyword decomposition: long keyword first, then shorter variants
    keyword_variants = _decompose_search_keywords(keyword)
    image_urls: list[str] = []

    for kw in keyword_variants:
        if image_urls:
            break
        image_urls = await _search_pinterest_images(kw, count * 3)
        if not image_urls:
            print(f"  [PINTEREST] '{kw}' -> 0 anh, thu tu khoa ngan hon...")

    if not image_urls:
        # Fallback to Google Images with decomposed keywords
        for kw in keyword_variants:
            if image_urls:
                break
            print(f"  [GOOGLE IMG] Thu: '{kw}'")
            image_urls = await _search_google_images(kw, count * 2)

    downloaded: list[str] = []
    async with httpx.AsyncClient(
        timeout=15.0,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    ) as client:
        for url in image_urls:
            if len(downloaded) >= count:
                break
            try:
                resp = await client.get(url)
                if resp.status_code == 200 and len(resp.content) > 5000:
                    content_type = resp.headers.get("content-type", "")
                    if "image" not in content_type and not url.endswith((".jpg", ".png", ".webp")):
                        continue

                    ext = ".jpg"
                    if "png" in content_type or url.endswith(".png"):
                        ext = ".png"
                    elif "webp" in content_type or url.endswith(".webp"):
                        ext = ".webp"

                    url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
                    filename = f"meme_{url_hash}{ext}"
                    filepath = output_path / filename
                    filepath.write_bytes(resp.content)

                    rel_path = f"images/{filename}"
                    downloaded.append(rel_path)
                    print(f"  [PINTEREST] Downloaded: {filename} ({len(resp.content)//1024}KB)")

            except Exception as e:
                continue

    return downloaded


async def _search_pinterest_images(keyword: str, count: int) -> list[str]:
    """Search Pinterest and extract image URLs."""
    image_urls: list[str] = []

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("  [PINTEREST] Playwright not installed, skipping Pinterest search")
        return []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        try:
            search_url = f"https://www.pinterest.com/search/pins/?q={quote_plus(keyword + ' meme')}"
            print(f"  [PINTEREST] Searching: {keyword}")
            await page.goto(search_url, timeout=20000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            # Scroll to load more images
            for _ in range(2):
                await page.evaluate("window.scrollBy(0, 1000)")
                await page.wait_for_timeout(1500)

            # Extract image URLs from Pinterest pins
            img_elements = await page.query_selector_all("img[src*='pinimg.com']")
            for img in img_elements[:count]:
                src = await img.get_attribute("src") or ""
                if src and "pinimg.com" in src:
                    # Get higher resolution version
                    high_res = re.sub(r"/\d+x/", "/564x/", src)
                    if high_res not in image_urls:
                        image_urls.append(high_res)

            # Also try data-src for lazy-loaded images
            if len(image_urls) < count:
                img_elements = await page.query_selector_all("img[data-src*='pinimg.com']")
                for img in img_elements[:count]:
                    src = await img.get_attribute("data-src") or ""
                    if src and "pinimg.com" in src:
                        high_res = re.sub(r"/\d+x/", "/564x/", src)
                        if high_res not in image_urls:
                            image_urls.append(high_res)

            print(f"  [PINTEREST] Tim thay {len(image_urls)} anh")

        except Exception as e:
            print(f"  [PINTEREST] Loi: {e}")

        await browser.close()

    return image_urls


async def _search_google_images(keyword: str, count: int) -> list[str]:
    """Fallback: search Google Images for meme pictures."""
    image_urls: list[str] = []

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        try:
            query = f"{keyword} meme funny"
            url = f"https://www.google.com/search?q={quote_plus(query)}&tbm=isch&hl=vi"
            await page.goto(url, timeout=15000, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            img_elements = await page.query_selector_all("img[src^='http']")
            for img in img_elements[:count * 2]:
                src = await img.get_attribute("src") or ""
                if src.startswith("http") and "google" not in src and len(src) > 30:
                    if src not in image_urls:
                        image_urls.append(src)

            print(f"  [GOOGLE IMG] Tim thay {len(image_urls)} anh")

        except Exception as e:
            print(f"  [GOOGLE IMG] Loi: {e}")

        await browser.close()

    return image_urls


def extract_keywords(content: str) -> str:
    """Extract search keywords from post content for image search."""
    # Remove common Threads City words that don't help image search
    stop_words = {
        "mình", "của", "và", "là", "được", "có", "không", "này", "cho", "với",
        "các", "một", "những", "đã", "đang", "sẽ", "rất", "thì", "mà", "nhưng",
        "nên", "vì", "để", "từ", "theo", "bạn", "mọi", "người", "nha", "nè",
        "luôn", "quá", "lắm", "ghê", "dữ", "thiệt", "thật", "thế", "vậy",
        "hôm", "nay", "hãy", "tôi", "chúng", "ta",
    }

    words = re.findall(r"[\w]+", content.lower())
    keywords = [w for w in words if w not in stop_words and len(w) > 2]

    # Take top keywords (prioritize nouns/key terms)
    return " ".join(keywords[:5])


async def find_memes_for_posts(
    posts: list[dict],
    output_dir: str | Path = "video/public/images",
) -> list[dict]:
    """
    Tim anh meme phu hop cho tung bai dang.
    Tra ve posts da cap nhat voi postImage.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"\n[MEME] Tim anh meme cho {len(posts)} bai dang...")

    # Collect all keywords first
    all_keywords = []
    for post in posts:
        kw = extract_keywords(post.get("content", ""))
        all_keywords.append(kw)

    # Search for meme images — batch by topic similarity
    # Use the main topic as primary search
    all_images: list[str] = []

    # Search with different keyword sets
    seen_keywords: set[str] = set()
    for kw in all_keywords:
        if kw in seen_keywords or not kw:
            continue
        seen_keywords.add(kw)
        images = await find_meme_images(kw, count=2, output_dir=output_dir)
        all_images.extend(images)

    # Assign images to posts (round-robin if not enough)
    for i, post in enumerate(posts):
        if all_images:
            post["postImage"] = all_images[i % len(all_images)]
        else:
            post["postImage"] = ""

    found = sum(1 for p in posts if p.get("postImage"))
    print(f"[MEME] Gan {found}/{len(posts)} bai co anh meme")

    return posts


# CLI test
if __name__ == "__main__":
    import sys

    keyword = sys.argv[1] if len(sys.argv) > 1 else "gen z việt nam meme"
    print(f"Searching Pinterest for: {keyword}")
    images = asyncio.run(find_meme_images(keyword, count=3))
    print(f"\nDownloaded {len(images)} images:")
    for img in images:
        print(f"  - {img}")
