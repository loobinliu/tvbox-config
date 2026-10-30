#!/usr/bin/env python3
import json, re, urllib.request, os

UPSTREAM = "https://raw.githubusercontent.com/hebijunge/tvbox-config/main/exports/healthy.json"
OUTPUT = "exports/healthy_clean.json"
LIVE_URL = "https://iptv.zsdc.eu.org/udpxy/192.168.1.1:4022"

# 更严格的成人特征
ADULT = re.compile(
    r'18|AV|福利|伦理|色情|无码|成人|黄色|黑丝|诱惑|麻豆|四虎|香蕉|蜜桃|猫爪|暗网|'
    r'pornhub|xvideos|souav|chaturbate|kxgav|msnii|gdlsp|xrbsp|香奶|白嫖|'
    r'美少女|嫖|ikun|IK|成人直播|台湾成人|主播|直播🔞|有码|'
    r'中文字幕|制服|人妻|乱伦|强奸|动漫精品|伦理影片|🔞|大秀|女优|TikTok直播|'
    r'裤佬|酷捞|至尊|安博|易发源|哈TV|蝴蝶影视|国产直播|欧美主播|亚洲主播|'
    r'日韩系列|livex|hsck|rwcr|18liv|18\.txt|✨live|冰茶',
    re.I
)

# 明确要干掉的站点 key / name 片段
BLACKLIST_SITES = [
    "黑色影视", "heiheizy"
]

def is_adult_obj(obj):
    text = json.dumps(obj, ensure_ascii=False)
    if ADULT.search(text):
        return True
    name = str(obj.get("name", "")) + str(obj.get("key", ""))
    if any(b.lower() in name.lower() for b in BLACKLIST_SITES):
        return True
    # 直播源里带 18 / 成人 / 主播 / 🔞 的直接砍
    url = str(obj.get("url", ""))
    if re.search(r'18|成人|主播|🔞|chaturbate|xvideos|pornhub', url, re.I):
        return True
    return False

def main():
    os.makedirs("exports", exist_ok=True)
    print(f"Fetching {UPSTREAM}")
    with urllib.request.urlopen(UPSTREAM, timeout=90) as r:
        data = json.load(r)

    before_sites = len(data.get("sites", []))
    before_parses = len(data.get("parses", []))

    data["sites"]  = [s for s in data.get("sites", [])  if not is_adult_obj(s)]
    data["lives"]  = []
    data["parses"] = [p for p in data.get("parses", []) if not is_adult_obj(p)]

    # 替换为指定的成都电信 IPTV
    data["lives"] = [
        {
            "name": "成都电信IPTV",
            "type": 0,
            "url": LIVE_URL,
            "playerType": 1,
            "epg": "https://epg.zsdc.eu.org/t.xml.gz"
        }
    ]

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"sites  {before_sites} → {len(data['sites'])}")
    print(f"lives  → 1（已替换为成都电信IPTV）")
    print(f"parses {before_parses} → {len(data['parses'])}")

if __name__ == "__main__":
    main()
