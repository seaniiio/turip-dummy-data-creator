"""
더미데이터 생성 설정값
각 테이블별 행 수와 공통 시드값을 관리합니다.
"""

SEED = 42

# ── Region ──────────────────────────────────────────────────────────────────
COUNTRY_COUNT  = 50
PROVINCE_COUNT = 17
CITY_COUNT     = 250   # COUNTRY_COUNT * 5

# ── Account / Auth ───────────────────────────────────────────────────────────
ACCOUNT_COUNT       = 10_000
GUEST_COUNT         = 5_000   # account_id 1 ~ 5,000
MEMBER_COUNT        = 5_000   # account_id 5,001 ~ 10,000
TURIP_MEMBER_COUNT  = 2_500   # member_id 1 ~ 2,500
SOCIAL_MEMBER_COUNT = 2_500   # member_id 2,501 ~ 5,000
REFRESH_TOKEN_COUNT = 5_000   # member_id 1 ~ 5,000 각 1개

# ── Place ────────────────────────────────────────────────────────────────────
CATEGORY_COUNT      = 200
PLACE_COUNT         = 1_700_000
PLACE_CATEGORY_COUNT = 50_000

# ── Creator / Content ────────────────────────────────────────────────────────
CREATOR_COUNT       = 7_500
CONTENT_COUNT       = 100_000
CONTENT_PLACE_COUNT = 2_000_000  # CONTENT_COUNT * 20
PLACES_PER_CONTENT  = 20
DAYS_PER_CONTENT    = 5          # 5일 여행
PLACES_PER_DAY      = 4          # 하루 4곳 (5 * 4 = 20)

# ── Favorite ─────────────────────────────────────────────────────────────────
# 기본 폴더: account 10,000개 당 1개 = 10,000
# 커스텀 폴더: account 당 4개 (공유 2 + 개인 2) = 40,000
# 합계: 50,000
FAVORITE_FOLDER_COUNT          = 50_000
DEFAULT_FOLDER_COUNT           = 10_000   # id 1 ~ 10,000
CUSTOM_SHARED_FOLDER_COUNT     = 20_000   # id 10,001 ~ 30,000 (account당 2개)
CUSTOM_PRIVATE_FOLDER_COUNT    = 20_000   # id 30,001 ~ 50,000 (account당 2개)

# OWNER 50,000 + 공유폴더(20,000) 당 MEMBER 3명 = 110,000
FAVORITE_FOLDER_ACCOUNT_COUNT  = 110_000
MEMBERS_PER_SHARED_FOLDER      = 3

FAVORITE_CONTENT_COUNT = 200_000   # account 10,000 * 20
CONTENTS_PER_ACCOUNT   = 20

FAVORITE_PLACE_COUNT   = 750_000   # folder 50,000 * 15
PLACES_PER_FOLDER      = 15
