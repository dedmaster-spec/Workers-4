import requests
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://catcast.tv/"
}

def extract_m3u8(text):
    match = re.search(r'https?://[^"]+\.m3u8[^"]*', text)
    return match.group(0) if match else None


def get_channel_stream(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        html = r.text

        # ищем m3u8 прямо
        stream = extract_m3u8(html)
        if stream:
            return stream

        # ищем channelId
        match_id = re.search(r'channelId["\']?\s*[:=]\s*["\']?(\d+)', html)
        if match_id:
            channel_id = match_id.group(1)

            api_url = f"https://api.catcast.tv/api/channel/{channel_id}"
            r2 = requests.get(api_url, headers=HEADERS, timeout=10)

            stream = extract_m3u8(r2.text)
            if stream:
                return stream

        return None

    except Exception as e:
        print(f"Ошибка: {e}")
        return None


def main():
    with open("channels.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    playlist = "#EXTM3U\n"

    for ch in data["channels"]:
        name = ch["name"]
        url = ch["url"]

        print(f"🔍 Проверка: {name}")
        stream = get_channel_stream(url)

        if stream:
            print(f"✅ OK: {name}")
            playlist += f'#EXTINF:-1,{name}\n{stream}\n'
        else:
            print(f"❌ FAIL: {name}")

    with open("catcast.m3u8", "w", encoding="utf-8") as f:
        f.write(playlist)


if __name__ == "__main__":
    main()
