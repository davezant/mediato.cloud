import os

if __name__ == "__main__":
    os.system("pip install -r requirements.txt")
    os.system("pip install -m playwright install")
    os.system("python3 -m yt-dlp-proxy --update")
    
