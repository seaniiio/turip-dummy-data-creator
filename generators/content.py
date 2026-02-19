"""
Creator / Content 도메인 CSV 생성기

creator      :     7,500개
content      :   100,000개  (creator_id, city_id 랜덤 참조)
content_place: 2,000,000개  (content당 20개, 5일 * 4곳)

content.url    : 'https://www.youtube.com/watch?v={id:011d}' (UNIQUE)
content.title  : '{creator_id}번 크리에이터의 {city_name} 여행 EP.{n}' 형식
                  UNIQUE(creator_id, title) 보장 — 크리에이터별 순번 증가

content_place 구조 (content당 20개):
  visit_day   : 1 ~ 5 (5일 여행)
  visit_order : 1 ~ 4 (하루 4곳)
  time_line   : 09:00 / 11:00 / 13:00 / 15:00
  UNIQUE(content_id, visit_day, visit_order) 자동 보장
"""

import csv
import random
from datetime import date, timedelta

import config

random.seed(config.SEED)

_CHANNEL_ADJECTIVES = [
    "빛나는", "여유로운", "설레는", "즐거운", "행복한", "신나는", "아늑한",
    "특별한", "따뜻한", "자유로운", "달콤한", "감성", "힐링", "로맨틱",
]
_CHANNEL_NOUNS = [
    "여행자", "탐험가", "방랑자", "나그네", "여행러", "트래블러", "여행꾼",
    "바람", "구름", "별빛", "노을", "달빛", "파도", "봄날",
]
_CONTENT_KEYWORDS = [
    "vlog", "여행기", "숨은 맛집", "코스 추천", "현지 가이드",
    "총정리", "여행 꿀팁", "필수 코스", "1박2일", "2박3일", "4박5일",
]

_BASE_UPLOAD_DATE = date(2020, 1, 1)
_MAX_OFFSET_DAYS  = (date(2025, 12, 31) - _BASE_UPLOAD_DATE).days

# content_place time_line: 하루 4곳 시간대
_VISIT_TIMES = ["09:00:00", "11:00:00", "13:00:00", "15:00:00"]


def generate(output_dir: str) -> None:
    _generate_creator(output_dir)
    city_ids = _generate_content(output_dir)   # 반환값 없어도 되지만 아래 사용 안 함
    _generate_content_place(output_dir)


def _generate_creator(output_dir: str) -> None:
    path = f"{output_dir}/creator.csv"
    used_names: set[str] = set()
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "channel_name", "profile_image"])
        for i in range(1, config.CREATOR_COUNT + 1):
            # channel_name UNIQUE 보장: 형용사 + 명사 + 인덱스
            adj  = _CHANNEL_ADJECTIVES[i % len(_CHANNEL_ADJECTIVES)]
            noun = _CHANNEL_NOUNS[i % len(_CHANNEL_NOUNS)]
            name = f"{adj}{noun}{i:04d}"
            used_names.add(name)
            profile = f"https://images.turip.com/creator/{i}.jpg"
            w.writerow([i, name, profile])
    print(f"  creator.csv       : {config.CREATOR_COUNT:,}행")


def _generate_content(output_dir: str) -> None:
    """
    UNIQUE(creator_id, title) 보장:
      creator_id 별로 콘텐츠 순번(ep) 카운터를 관리.
    city_id : 1 ~ 250 랜덤
    """
    path = f"{output_dir}/content.csv"

    # creator당 콘텐츠 순번 추적
    creator_ep: dict[int, int] = {}

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "creator_id", "city_id", "title", "url", "uploaded_date"])
        for content_id in range(1, config.CONTENT_COUNT + 1):
            creator_id = (content_id % config.CREATOR_COUNT) + 1   # 1 ~ 7,500 순환
            city_id    = (content_id % config.CITY_COUNT) + 1       # 1 ~ 250  순환

            ep = creator_ep.get(creator_id, 0) + 1
            creator_ep[creator_id] = ep

            kw    = _CONTENT_KEYWORDS[content_id % len(_CONTENT_KEYWORDS)]
            title = f"도시{city_id} {kw} EP.{ep}"
            url   = f"https://www.youtube.com/watch?v={content_id:011d}"

            offset = random.randint(0, _MAX_OFFSET_DAYS)
            uploaded = _BASE_UPLOAD_DATE + timedelta(days=offset)

            w.writerow([content_id, creator_id, city_id, title, url,
                        uploaded.strftime("%Y-%m-%d")])
    print(f"  content.csv       : {config.CONTENT_COUNT:,}행")


def _generate_content_place(output_dir: str) -> None:
    """
    content 1개당 5일 * 4곳 = 20개 content_place 생성.
    UNIQUE(content_id, visit_day, visit_order) 자동 보장.
    place_id : 1 ~ 1,700,000 순환
    """
    path  = f"{output_dir}/content_place.csv"
    total = config.CONTENT_PLACE_COUNT
    print_interval = total // 10

    cp_id     = 1
    place_max = config.PLACE_COUNT

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "content_id", "place_id", "visit_day", "visit_order", "time_line"])
        for content_id in range(1, config.CONTENT_COUNT + 1):
            for day in range(1, config.DAYS_PER_CONTENT + 1):
                for order in range(1, config.PLACES_PER_DAY + 1):
                    place_id  = (cp_id % place_max) + 1
                    time_line = _VISIT_TIMES[order - 1]
                    w.writerow([cp_id, content_id, place_id, day, order, time_line])
                    if cp_id % print_interval == 0:
                        print(f"    content_place {cp_id:>9,} / {total:,} ({cp_id * 100 // total}%)")
                    cp_id += 1
    print(f"  content_place.csv : {total:,}행")
