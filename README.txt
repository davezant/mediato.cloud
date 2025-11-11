# Media Extractor — Open Source Social Media Downloader

Media Extractor is an open-source project designed to fetch direct media links from social media platforms. 
The goal is to provide a simple, free, and trusted tool that helps users extract videos or images without watermarks, popups, ads, or shady downloaders.

✅ What works right now
----------------------
• Instagram — reels, posts, carousels, single videos
• TikTok — direct video extraction, watermark-free, H.264 conversion
• Twitter/X — images, videos, GIFs using Twitter internal fallback
• YouTube — direct video fallback link detection
• Reddit — detects embedded media URL (if present)

🌀 Current limitations
----------------------
• Facebook — partially working (needs reliable media parsing)
• Threads — in progress
• Some posts with protected or private content cannot be processed
• Pages using heavy dynamic obfuscation require better fallback logic
• You need to edit the original yt-dlp-proxy to access better and make it go it way, but i don't remember how

🚧 What needs improvement
-------------------------
• More stable detection for Instagram images
• Better error handling and response formatting
• Async queue to support multiple downloads at the same time
• Better UI for previewing multiple media files
• Add support for downloading media in different resolutions

✨ Possible future features
--------------------------
• Built-in video editor (cut, convert, compress)
• Browser extension to extract media directly from the page
• Batch media downloading
• Desktop version (Electron / Tauri)
• Automatic watermark removal for more platforms
• Upload history and full logs

🤝 Contribute
-------------
This is an open project — feel free to submit pull requests, new platform support, bug fixes, or feature ideas.
Even small improvements are welcome.

Together we can turn this into the most complete media extractor on the internet. 🚀
