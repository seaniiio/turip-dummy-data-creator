"""
더미데이터 생성 설정값
각 테이블별 행 수와 공통 시드값을 관리합니다.

ACCOUNT_COUNT는 환경변수로 재정의 가능합니다.
  예) ACCOUNT_COUNT=5000 python3 main.py
"""

import os

SEED = 42

# ── Region ──────────────────────────────────────────────────────────────────
COUNTRY_COUNT  = 50
PROVINCE_COUNT = 17
CITY_COUNT     = 250   # COUNTRY_COUNT * 5

# ── Account / Auth ───────────────────────────────────────────────────────────
ACCOUNT_COUNT       = int(os.environ.get("ACCOUNT_COUNT", 10_000))
GUEST_COUNT         = ACCOUNT_COUNT // 2
MEMBER_COUNT        = ACCOUNT_COUNT // 2
TURIP_MEMBER_COUNT  = MEMBER_COUNT // 2
SOCIAL_MEMBER_COUNT = MEMBER_COUNT // 2
REFRESH_TOKEN_COUNT = MEMBER_COUNT

# ── Creator / Content ────────────────────────────────────────────────────────
CONTENT_COUNT       = ACCOUNT_COUNT * 10        # ACCOUNT_COUNT * 10
CREATOR_COUNT       = CONTENT_COUNT // 13       # CONTENT_COUNT / 13
CONTENT_PLACE_COUNT = CONTENT_COUNT * 20        # CONTENT_COUNT * PLACES_PER_CONTENT
PLACES_PER_CONTENT  = 20
DAYS_PER_CONTENT    = 5          # 5일 여행
PLACES_PER_DAY      = 4          # 하루 4곳 (5 * 4 = 20)

# ── Place ────────────────────────────────────────────────────────────────────
CATEGORY_COUNT      = 200
PLACE_COUNT         = CONTENT_COUNT * 17        # CONTENT_COUNT * 17
PLACE_CATEGORY_COUNT = PLACE_COUNT // 3         # PLACE_COUNT / 3

# ── Favorite ─────────────────────────────────────────────────────────────────
# 기본 폴더: account 당 1개
# 커스텀 폴더: account 당 4개 (공유 2 + 개인 2)
DEFAULT_FOLDER_COUNT           = ACCOUNT_COUNT * 1
CUSTOM_SHARED_FOLDER_COUNT     = ACCOUNT_COUNT * 2
CUSTOM_PRIVATE_FOLDER_COUNT    = ACCOUNT_COUNT * 2
FAVORITE_FOLDER_COUNT          = DEFAULT_FOLDER_COUNT + CUSTOM_SHARED_FOLDER_COUNT + CUSTOM_PRIVATE_FOLDER_COUNT

# 개인 폴더 -> OWNER 1명
# 공유 폴더 -> OWNER 1명, MEMBER 3명
MEMBERS_PER_SHARED_FOLDER      = 3
FAVORITE_FOLDER_ACCOUNT_COUNT  = CUSTOM_PRIVATE_FOLDER_COUNT + (1 + MEMBERS_PER_SHARED_FOLDER) * CUSTOM_SHARED_FOLDER_COUNT

# FavoriteContent: 계정당 20개
CONTENTS_PER_ACCOUNT   = 20
FAVORITE_CONTENT_COUNT = ACCOUNT_COUNT * CONTENTS_PER_ACCOUNT

# FavoritePlace: 폴더당 15개
PLACES_PER_FOLDER      = 15
FAVORITE_PLACE_COUNT   = (DEFAULT_FOLDER_COUNT + CUSTOM_SHARED_FOLDER_COUNT + CUSTOM_PRIVATE_FOLDER_COUNT) * PLACES_PER_FOLDER
