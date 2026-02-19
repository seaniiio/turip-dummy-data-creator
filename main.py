"""
Turip 더미데이터 생성기
도메인 의존 순서: Region → Account/Auth → Place → Creator/Content → Favorite
"""

import os
import time

from generators import region, account, place, content, favorite

OUTPUT_DIR = "output"


def _step(number: int, total: int, label: str, fn):
    print(f"[{number}/{total}] {label} 생성 중...")
    t = time.time()
    fn(OUTPUT_DIR)
    print(f"  └─ 완료 ({time.time() - t:.1f}s)\n")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("  Turip Dummy Data Creator")
    print("=" * 50 + "\n")

    steps = [
        ("Region 도메인 (country / province / city)",        region.generate),
        ("Account/Auth 도메인 (account ~ refresh_token)",    account.generate),
        ("Place 도메인 (category / place / place_category)", place.generate),
        ("Content 도메인 (creator / content / content_place)", content.generate),
        ("Favorite 도메인 (folder / folder_account / place / content)", favorite.generate),
    ]

    for i, (label, fn) in enumerate(steps, 1):
        _step(i, len(steps), label, fn)

    print("=" * 50)
    print(f"  완료! CSV 파일 위치: {os.path.abspath(OUTPUT_DIR)}/")
    print("=" * 50)


if __name__ == "__main__":
    main()
