import asyncio
import re
from urllib.parse import urlparse
from pathlib import Path

cookie_dir = Path("cache/")

class SocialMedia:
    def __init__(self, url: str, headless: bool = True):
        self.url = url
        self.headless = headless

    def get_domain(self):
        return urlparse(self.url).netloc.lower()


class Facebook(SocialMedia):
    async def get_post_media(self):
        raise Exception("Not Implemented")


class Twitter(SocialMedia):
    async def get_post_media(self):
        return self.url.replace("x.com", "dl.fxtwitter.com")


class Threads(SocialMedia):
    async def get_post_media(self):
        raise Exception("Not Implemented")

class Instagram(SocialMedia):
    async def get_post_media(self):
        from playwright.async_api import async_playwright
        self.url = self.url.replace("/reels/", "/reel/")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                page = await browser.new_page()
                await page.goto(self.url, timeout=60000)
                await page.wait_for_selector("article, video", timeout=10000)

                reels_video = await page.eval_on_selector_all("video", "els => els.map(e => e.src)")
                post_media = await page.eval_on_selector_all("article img, article video", "els => els.map(e => e.src)")

                await browser.close()
                media = reels_video or post_media
                return media[0] if len(media) == 1 else media or "Nenhuma mídia encontrada."
        except Exception as e:
            return f"Instagram error: {e}"


class TikTok(SocialMedia):
    async def get_post_media(self):
        import json
        import asyncio
        import shutil
        import os
        import subprocess
        from pathlib import Path
        from yt_dlp import YoutubeDL
        
        cookie_dir = Path("cache")
        json_cookie_path = cookie_dir / "tiktok_cookies.json"
        netscape_cookie_path = cookie_dir / "tiktok_cookies_netscape.txt"
        static_files_dir = Path("static/files")
        static_files_dir.mkdir(parents=True, exist_ok=True)

        def json_to_netscape(json_file, output_file):
            with open(json_file, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# Format: domain\tflag\tpath\tsecure\texpiration\tname\tvalue\n")
                for cookie in cookies:
                    domain = cookie["domain"]
                    flag = "TRUE" if domain.startswith(".") else "FALSE"
                    path = cookie["path"]
                    secure = "TRUE" if cookie.get("secure") else "FALSE"
                    expires = cookie.get("expires", 0)
                    name = cookie["name"]
                    value = cookie["value"]
                    f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")

        json_to_netscape(json_cookie_path, netscape_cookie_path)

        ydl_opts = {
            "quiet": True,
            "cookiefile": str(netscape_cookie_path),
            "noplaylist": True,
            "outtmpl": "%(id)s.%(ext)s",
            "merge_output_format": "mp4",  # final container
            "format": "bestvideo+bestaudio/best"  # allow any codec, we will re-encode if needed
        }

        def extract_and_move():
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                filename = ydl.prepare_filename(info)

            temp_file = Path(filename)
            destination = static_files_dir / temp_file.name

            shutil.move(temp_file, destination)
            
            vcodec = None
            for f in info.get("formats", []):
                if f.get("format_id") == info.get("format_id"):
                    vcodec = f.get("vcodec")
                    break
            if not vcodec:
                vcodec = info.get("vcodec")

            if vcodec and not vcodec.startswith("avc1"):
                # Convert to H.264
                converted_path = static_files_dir / (destination.stem + "_h264.mp4")
                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", str(destination),
                    "-c:v", "libx264",
                    "-crf", "23",
                    "-preset", "fast",
                    "-c:a", "copy",
                    str(converted_path)
                ], check=True)

                os.remove(destination)
                converted_path.rename(destination)

            return f"/static/files/{destination.name}"

        return await asyncio.to_thread(extract_and_move)



class YouTube(SocialMedia):
    _safe_counter = 0

    async def get_post_media(self):
         proc = await asyncio.create_subprocess_exec(
           "python3", "-m", "yt_dlp_proxy", "-g", "-q", self.url, "-f", "best", "--no-playlist", "--get-description",
             stdout=asyncio.subprocess.PIPE,
             stderr=asyncio.subprocess.PIPE
         )
         stdout, _ = await proc.communicate()
         string_cmd = stdout.decode("utf-8")
         if "Provided to YouTube" and "Auto-generated" in string_cmd:
           raise Exception("Protected Content By Youtube")
         url_yt = re.findall(r'https?://[^\s"]*?source=youtube[^\s"]*', string_cmd)
         print(stdout)
         YouTube._safe_counter += 1
         if YouTube._safe_counter >= 4:
             await asyncio.create_subprocess_exec("python3", "-m", "yt_dlp_proxy", "--update")
             YouTube._safe_counter = 0

         return str(url_yt[0]) if url_yt else None


class LinkedIn(SocialMedia):
    async def get_post_media(self):
        raise Exception("Not Implemented")


class Pinterest(SocialMedia):
    async def get_post_media(self):
        raise Exception("Not Implemented")


class Reddit(SocialMedia):
    async def get_post_media(self):
        try:
            import praw

            def fetch():
                reddit = praw.Reddit(
                    client_id="Mediato",
                    client_secret="	WxF9JudKbCy_vt3TPohHN6EDBD7zhw",
                    user_agent="Mozilla/5.0 (platform; rv:gecko-version) Gecko/gecko-trail Firefox/firefox-version"
                )
                match = re.search(r"comments/([a-z0-9]+)/", self.url)
                if not match:
                    return "Invalid Reddit URL"
                submission = reddit.submission(id=match.group(1))
                if submission.is_video and submission.media:
                    return submission.media['reddit_video']['fallback_url']
                return submission.url or "Nenhuma mídia encontrada."

            return await asyncio.to_thread(fetch)
        except Exception as e:
            return f"Reddit error: {e}"


def get_social_media_class(url):
    domain = urlparse(url).netloc.lower()
    if "instagram.com" in domain:
        return Instagram
    elif "facebook.com" in domain:
        return Facebook
    elif "twitter.com" in domain or "x.com" in domain:
        return Twitter
    elif "threads.com" in domain:
        return Threads
    elif "tiktok.com" in domain:
        return TikTok
    elif "youtube.com" in domain or "youtu.be" in domain:
        return YouTube
    elif "linkedin.com" in domain:
        return LinkedIn
    elif "pinterest.com" in domain:
        return Pinterest
    elif "reddit.com" in domain:
        return Reddit
    return None

