"""
Place 도메인 CSV 생성기

category   :       200개
place      : 1,700,000개  (대용량 — 스트리밍 방식)
place_category :  50,000개  (place 1개당 평균 0.03개 → 장소 1,000개당 약 29개)

place.url      : 'https://maps.google.com/maps/place/{id}' (UNIQUE)
place.latitude : 위도  -90 ~ 90
place.longitude: 경도 -180 ~ 180

place_category 할당 전략:
  - category_id : 1 ~ 200 순환
  - place_id    : 1 ~ 50,000 (UNIQUE(place_id, category_id) 보장 — place당 1개만)
"""

import csv
import random

import config

random.seed(config.SEED)

# ── 구글 맵 카테고리 200개 ────────────────────────────────────────────────────
_CATEGORIES = [
    "레스토랑", "카페", "베이커리", "바", "술집", "패스트푸드", "분식집", "이자카야",
    "한식당", "중식당", "일식당", "양식당", "인도음식", "태국음식", "멕시코음식", "베트남음식",
    "해산물 레스토랑", "채식 레스토랑", "뷔페", "푸드코트", "편의점", "마트", "시장",
    "박물관", "미술관", "갤러리", "역사 유적지", "문화센터", "공연장", "극장", "영화관",
    "공원", "국립공원", "자연보호구역", "해변", "산", "강", "호수", "폭포", "동굴",
    "호텔", "게스트하우스", "호스텔", "리조트", "펜션", "캠핑장", "에어비앤비",
    "쇼핑몰", "백화점", "전통시장", "아울렛", "편집샵", "서점", "약국", "면세점",
    "지하철역", "버스터미널", "공항", "기차역", "항구", "렌터카", "주차장",
    "병원", "클리닉", "의원",
    "헬스장", "수영장", "테니스장", "골프장", "스키장", "서핑스쿨", "다이빙센터",
    "테마파크", "놀이공원", "워터파크", "동물원", "식물원", "수족관", "천문대",
    "대학교", "학교", "도서관", "연구소",
    "교회", "성당", "사찰", "모스크", "신사",
    "은행", "ATM", "환전소", "우체국", "경찰서", "소방서",
    "스파", "마사지샵", "네일샵", "헤어살롱", "피부과",
    "사진관", "인쇄소", "세탁소",
    "투어 에이전시", "관광안내소", "투어 버스",
    "와이너리", "양조장", "커피 농장", "차 농장",
    "아이스크림", "디저트샵", "초콜릿샵", "케이크샵",
    "피자", "파스타", "스테이크하우스", "샐러드바", "라멘", "초밥", "타코", "케밥",
    "브런치카페", "루프탑바", "와인바", "칵테일바", "클럽", "노래방", "PC방", "보드게임카페",
    "독서실", "스터디카페", "공유오피스", "전시관", "컨벤션센터",
    "마리나", "요트클럽", "수상스포츠센터", "번지점프", "집라인",
    "트레킹코스", "자전거도로", "조깅코스",
    "야시장", "플리마켓", "팝업스토어",
    "게임센터", "VR체험관", "방탈출카페", "키즈카페",
    "강아지카페", "고양이카페",
    "공방", "도자기 체험", "한복 체험", "전통문화 체험",
    "사우나", "찜질방", "온천",
    "유스호스텔", "산장", "글램핑",
    "팬케이크", "와플카페", "버블티샵", "주스바",
    "편의시설", "공중화장실", "휴게소",
    "전망대", "등대", "성", "궁궐", "왕릉",
    "스케이트장", "볼링장", "당구장", "탁구장", "클라이밍센터",
    "요가스튜디오", "필라테스", "태권도장", "무술도장",
    "승마장", "래프팅", "카약",
    "비치바", "풀바", "루프탑 레스토랑",
    "포장마차", "포차", "호프집",
    "갈비집", "삼겹살집", "냉면집", "설렁탕", "순대국", "해장국",
    "꽃집", "인테리어샵", "가구점",
    "항공사 라운지", "기내식당",
    "크루즈 터미널", "페리 터미널",
    "워킹투어 출발지", "시티투어 버스정류장",
    "관측소", "기상대",
    "소극장", "뮤지컬 극장", "오페라하우스", "콘서트홀",
    "미디어아트관", "과학관", "자연사박물관", "전쟁기념관",
    "국경", "이민국",
    "리조트 수영장", "인피니티풀",
    "해돋이 명소", "야경 명소", "단풍 명소", "벚꽃 명소",
    "포토존", "인스타그램 명소",
    "공항 면세점", "기념품샵",
    "기타",
]  # 229개

_PLACE_TYPES = [
    "광장", "거리", "골목", "공원", "해변", "산", "호수", "폭포", "계곡",
    "마을", "섬", "반도", "항구", "역", "다리", "탑", "성", "궁",
    "사원", "교회", "시장", "쇼핑몰", "박물관", "미술관", "카페", "레스토랑",
]

_ADJECTIVES = [
    "아름다운", "유명한", "인기있는", "숨겨진", "전통", "현대적인", "고즈넉한",
    "활기찬", "조용한", "낭만적인", "이국적인", "자연친화적인",
]


def generate(output_dir: str) -> None:
    _generate_category(output_dir)
    _generate_place(output_dir)
    _generate_place_category(output_dir)


def _generate_category(output_dir: str) -> None:
    path = f"{output_dir}/category.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "name"])
        for i, name in enumerate(_CATEGORIES[:config.CATEGORY_COUNT], 1):
            w.writerow([i, name])
    print(f"  category.csv      : {config.CATEGORY_COUNT}행")


def _generate_place(output_dir: str) -> None:
    """
    170만 행 스트리밍 작성.
    주소 풀(10,000개)에서 순환해 Faker 호출 횟수 최소화.
    """
    from faker import Faker
    fake = Faker("ko_KR")
    Faker.seed(config.SEED)

    # 주소 풀 생성 (10,000개)
    addr_pool = [fake.address().replace("\n", " ") for _ in range(10_000)]

    path = f"{output_dir}/place.csv"
    total = config.PLACE_COUNT
    print_interval = total // 10

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "url", "address", "latitude", "longitude"])
        for i in range(1, total + 1):
            ptype = _PLACE_TYPES[i % len(_PLACE_TYPES)]
            adj   = _ADJECTIVES[i % len(_ADJECTIVES)]
            name  = f"{adj} {ptype} {i}"
            url   = f"https://maps.google.com/maps/place/{i}"
            addr  = addr_pool[i % len(addr_pool)]
            lat   = round(random.uniform(-85.0, 85.0), 7)
            lon   = round(random.uniform(-180.0, 180.0), 7)
            w.writerow([i, name, url, addr, lat, lon])
            if i % print_interval == 0:
                print(f"    place {i:>9,} / {total:,} ({i * 100 // total}%)")
    print(f"  place.csv         : {total:,}행")


def _generate_place_category(output_dir: str) -> None:
    """
    place_id 1 ~ 50,000 에 category_id를 1개씩 부여.
    UNIQUE(place_id, category_id) 자동 보장.
    """
    path = f"{output_dir}/place_category.csv"
    total = config.PLACE_CATEGORY_COUNT
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "place_id", "category_id"])
        for i in range(1, total + 1):
            place_id    = i                                  # 1 ~ 50,000
            category_id = (i % config.CATEGORY_COUNT) + 1   # 1 ~ 200 순환
            w.writerow([i, place_id, category_id])
    print(f"  place_category.csv: {total:,}행")
