"""
Favorite 도메인 CSV 생성기

폴더 ID 구간 설계:
  1 ~ 10,000  : 기본 폴더 (account_id 1~10,000, is_default=1, is_shared=0)
  10,001 ~ 20,000 : 공유 커스텀 폴더 1번 (account_id 1~10,000, is_shared=1)
  20,001 ~ 30,000 : 공유 커스텀 폴더 2번 (account_id 1~10,000, is_shared=1)
  30,001 ~ 40,000 : 개인 커스텀 폴더 1번 (account_id 1~10,000, is_shared=0)
  40,001 ~ 50,000 : 개인 커스텀 폴더 2번 (account_id 1~10,000, is_shared=0)

favorite_folder_account:
  - OWNER 50,000개  : 폴더별 1개 (account_id = 폴더 소유 계정)
  - MEMBER 60,000개 : 공유폴더(20,000개) * 3명
    → 총 110,000개

favorite_content: account 10,000개 * 20개 = 200,000개
  UNIQUE(account_id, content_id) 보장 — account별 순번 순환 배정

favorite_place: folder 50,000개 * 15개 = 750,000개
  UNIQUE(favorite_folder_id, place_id) 보장 — folder별 place_id 순번 순환 배정
"""

import csv
import random

import config

random.seed(config.SEED)

_SHARED_FOLDER_NAMES  = ["함께하는 여행 폴더 1", "함께하는 여행 폴더 2"]
_PRIVATE_FOLDER_NAMES = ["나만의 여행 폴더 1", "나만의 여행 폴더 2"]


def generate(output_dir: str) -> None:
    _generate_favorite_folder(output_dir)
    _generate_favorite_folder_account(output_dir)
    _generate_favorite_content(output_dir)
    _generate_favorite_place(output_dir)


def _owner_account_of(folder_id: int) -> int:
    """folder_id → 소유 account_id 계산."""
    if folder_id <= 10_000:                      # 기본 폴더
        return folder_id
    elif folder_id <= 20_000:                    # 공유 커스텀 1
        return folder_id - 10_000
    elif folder_id <= 30_000:                    # 공유 커스텀 2
        return folder_id - 20_000
    elif folder_id <= 40_000:                    # 개인 커스텀 1
        return folder_id - 30_000
    else:                                        # 개인 커스텀 2
        return folder_id - 40_000


def _generate_favorite_folder(output_dir: str) -> None:
    path = f"{output_dir}/favorite_folder.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "is_default", "is_shared"])

        # 기본 폴더 10,000개 (folder_id = account_id)
        for folder_id in range(1, 10_001):
            w.writerow([folder_id, "기본 폴더", 1, 0])

        # 공유 커스텀 폴더 1 (10,001 ~ 20,000)
        for i, folder_id in enumerate(range(10_001, 20_001), 0):
            w.writerow([folder_id, _SHARED_FOLDER_NAMES[0], 0, 1])

        # 공유 커스텀 폴더 2 (20,001 ~ 30,000)
        for folder_id in range(20_001, 30_001):
            w.writerow([folder_id, _SHARED_FOLDER_NAMES[1], 0, 1])

        # 개인 커스텀 폴더 1 (30,001 ~ 40,000)
        for folder_id in range(30_001, 40_001):
            w.writerow([folder_id, _PRIVATE_FOLDER_NAMES[0], 0, 0])

        # 개인 커스텀 폴더 2 (40,001 ~ 50,000)
        for folder_id in range(40_001, 50_001):
            w.writerow([folder_id, _PRIVATE_FOLDER_NAMES[1], 0, 0])

    print(f"  favorite_folder.csv         : {config.FAVORITE_FOLDER_COUNT:,}행")


def _generate_favorite_folder_account(output_dir: str) -> None:
    """
    OWNER : 모든 폴더(1~50,000)에 1개씩 → 50,000개
    MEMBER: 공유 폴더(10,001~30,000, 총 20,000개)에 3명씩 → 60,000개
    UNIQUE(favorite_folder_id, account_id) 보장:
      MEMBER account_id 는 OWNER와 다른 계정 중 랜덤 선택
    """
    path = f"{output_dir}/favorite_folder_account.csv"
    record_id = 1

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "favorite_folder_id", "account_id", "account_role"])

        # OWNER 레코드
        for folder_id in range(1, config.FAVORITE_FOLDER_COUNT + 1):
            owner_account = _owner_account_of(folder_id)
            w.writerow([record_id, folder_id, owner_account, "OWNER"])
            record_id += 1

        # MEMBER 레코드 (공유 폴더만)
        shared_folder_ids = list(range(10_001, 30_001))  # 20,000개
        for folder_id in shared_folder_ids:
            owner_account = _owner_account_of(folder_id)
            # owner 제외 3명 선택 (결정론적: folder_id 기반 오프셋)
            base = (folder_id * 7 + 13) % config.ACCOUNT_COUNT  # 시드 기반 오프셋
            for k in range(config.MEMBERS_PER_SHARED_FOLDER):
                candidate = (base + k * 31) % config.ACCOUNT_COUNT + 1
                # owner 겹치면 한 칸 이동
                if candidate == owner_account:
                    candidate = (candidate % config.ACCOUNT_COUNT) + 1
                w.writerow([record_id, folder_id, candidate, "MEMBER"])
                record_id += 1

    print(f"  favorite_folder_account.csv : {record_id - 1:,}행")


def _generate_favorite_content(output_dir: str) -> None:
    """
    account 10,000개 * 콘텐츠 20개 = 200,000개.
    UNIQUE(account_id, content_id) 보장:
      content_id = (account_id * 20 + offset) % CONTENT_COUNT + 1 로 순환 배정
    """
    path = f"{output_dir}/favorite_content.csv"
    record_id = 1

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "account_id", "content_id", "created_at"])
        for account_id in range(1, config.ACCOUNT_COUNT + 1):
            base_content = (account_id - 1) * config.CONTENTS_PER_ACCOUNT
            for offset in range(config.CONTENTS_PER_ACCOUNT):
                content_id = (base_content + offset) % config.CONTENT_COUNT + 1
                # 찜 날짜: account_id 기반 결정론적 날짜
                day_offset = (account_id + offset * 3) % 365
                created_at = f"2025-{(day_offset // 30) + 1:02d}-{(day_offset % 28) + 1:02d}"
                w.writerow([record_id, account_id, content_id, created_at])
                record_id += 1

    print(f"  favorite_content.csv        : {record_id - 1:,}행")


def _generate_favorite_place(output_dir: str) -> None:
    """
    폴더 50,000개 * 장소 15개 = 750,000개.
    UNIQUE(favorite_folder_id, place_id) 보장:
      place_id = (folder_id * 15 + offset) % PLACE_COUNT + 1 로 순환 배정
    """
    path = f"{output_dir}/favorite_place.csv"
    total = config.FAVORITE_PLACE_COUNT
    record_id = 1

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "favorite_folder_id", "place_id", "favorite_order"])
        for folder_id in range(1, config.FAVORITE_FOLDER_COUNT + 1):
            base_place = (folder_id - 1) * config.PLACES_PER_FOLDER
            for order in range(1, config.PLACES_PER_FOLDER + 1):
                place_id = (base_place + order - 1) % config.PLACE_COUNT + 1
                w.writerow([record_id, folder_id, place_id, order])
                record_id += 1

    print(f"  favorite_place.csv          : {total:,}행")
