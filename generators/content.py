"""
Creator / Content 도메인 CSV 생성기

creator      :     7,500개
content      :   100,000개  (creator_id, city_id 랜덤 참조)
content_place: 2,000,000개  (content당 20개, 5일 * 4곳)

content.url    : 'https://www.youtube.com/watch?v={id:011d}' (UNIQUE)
content.title  : 유튜브 브이로그 스타일 4가지 패턴 중 하나 (content_id % 4)
                  패턴 0 — "{hook} {city} 찐{type} | {ep}번째 영상 VLOG"
                  패턴 1 — "{city}여행 vlog{ep}. {city} {kw1}과 {kw2}ㅣ{kw3}ㅣ{kw4}"
                  패턴 2 — "{style} {city} {ep}번째 여행{emoji} ㅣ{course}ㅣ{kw1}ㅣ{kw2}ㅣ{kw3}"
                  패턴 3 — "{city} {ep}번째 여행 | {hook} {type}"
                  UNIQUE(creator_id, title) 보장 — 모든 패턴에 ep 포함

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

# ── 제목 생성용 컴포넌트 ──────────────────────────────────────────────────────
_CITY_NAMES = [
    "서울", "부산", "제주", "경주", "강릉", "여수", "전주", "인천",
    "대구", "광주", "대전", "울산", "수원", "춘천", "속초", "통영",
    "거제", "남해", "안동", "포항", "창원", "목포", "순천", "군산",
    "보령", "태안", "평창", "가평", "파주", "담양",
]
_TRAVEL_HOOKS = [
    "오픈런 없이 못먹는", "현지인도 모르는", "혼자서도 충분한",
    "뚜벅이로 즐기는", "sns 난리난", "알짜배기만 모은",
    "찐여행자의", "요즘 핫한", "가성비 최고", "미슐랭 인정한",
    "안 가면 후회하는", "인생샷 건지는",
]
_TRAVEL_STYLES = [
    "나혼자", "친구랑", "커플", "혼자서", "당일치기", "뚜벅이",
]
_CONTENT_TYPES = [
    "맛집 투어🔥", "카페 투어☕", "핫플 탐방✨", "먹방 브이로그",
    "숨은 명소 탐방", "맛집&카페 탐방",
]
_COURSE_TYPES = [
    "당일치기 코스", "1박2일 코스", "2박3일 완벽 코스",
    "뚜벅이 완전정복", "혼여 코스", "가성비 코스",
]
_PLACE_KEYWORDS = [
    "미슐랭 국밥", "갓성비 오마카세", "감성 소품샵", "인생 카페",
    "야경 명소", "로컬 빵집", "혼술 바", "해산물 맛집",
    "고기 맛집", "디저트 카페", "뷰 맛집", "전통 시장",
    "공방 체험", "루프탑 카페", "이자카야", "라멘 맛집",
    "현지 분식", "트렌디 카페", "편집샵 투어", "편의점 성지",
]
_TITLE_EMOJIS = ["🚃", "✈️", "🏖️", "🎒", "🗺️", "🌟", "💫", "🧸", "🍜", "☕"]

_BASE_UPLOAD_DATE = date(2020, 1, 1)
_MAX_OFFSET_DAYS  = (date(2025, 12, 31) - _BASE_UPLOAD_DATE).days

# content_place time_line: 하루 4곳 시간대
_VISIT_TIMES = ["09:00:00", "11:00:00", "13:00:00", "15:00:00"]


def _make_title(content_id: int, city_id: int, ep: int) -> str:
    """
    content_id 별 로컬 RNG를 사용해 전역 random 시퀀스에 영향 없이
    유튜브 브이로그 스타일 제목을 생성한다.
    모든 패턴에 ep가 포함되어 UNIQUE(creator_id, title)을 보장한다.
    """
    rng  = random.Random(content_id * 997 + config.SEED)
    city = _CITY_NAMES[(city_id - 1) % len(_CITY_NAMES)]
    pat  = content_id % 4

    if pat == 0:
        # 예) "오픈런 없이 못먹는 부산 찐맛집 투어🔥 | 3번째 영상 VLOG"
        hook  = rng.choice(_TRAVEL_HOOKS)
        ctype = rng.choice(_CONTENT_TYPES)
        return f"{hook} {city} 찐{ctype} | {ep}번째 영상 VLOG"

    elif pat == 1:
        # 예) "부산여행 vlog3. 부산 미슐랭 국밥과 인생 카페ㅣ야경 명소ㅣ감성 소품샵"
        kws = rng.sample(_PLACE_KEYWORDS, 4)
        return f"{city}여행 vlog{ep}. {city} {kws[0]}과 {kws[1]}ㅣ{kws[2]}ㅣ{kws[3]}"

    elif pat == 2:
        # 예) "나혼자 부산 5번째 여행🚃 ㅣ당일치기 코스ㅣ갓성비 오마카세ㅣ루프탑 카페ㅣ혼술 바"
        style  = rng.choice(_TRAVEL_STYLES)
        emoji  = rng.choice(_TITLE_EMOJIS)
        course = rng.choice(_COURSE_TYPES)
        kws    = rng.sample(_PLACE_KEYWORDS, 3)
        return f"{style} {city} {ep}번째 여행{emoji} ㅣ{course}ㅣ{kws[0]}ㅣ{kws[1]}ㅣ{kws[2]}"

    else:
        # 예) "부산 7번째 여행 | 현지인도 모르는 카페 투어☕"
        hook  = rng.choice(_TRAVEL_HOOKS)
        ctype = rng.choice(_CONTENT_TYPES)
        return f"{city} {ep}번째 여행 | {hook} {ctype}"


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

            title = _make_title(content_id, city_id, ep)
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
