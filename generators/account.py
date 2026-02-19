"""
Account / Auth 도메인 CSV 생성기

ID 구간 설계:
  account    : 1 ~ 10,000
  guest      : account_id 1 ~ 5,000     (guest.id = account_id)
  member     : account_id 5,001 ~ 10,000 (member.id = 1 ~ 5,000)
  turip_member  : member_id 1 ~ 2,500
  social_member : member_id 2,501 ~ 5,000
  refresh_token : member_id 1 ~ 5,000 각 1개

account.role  : 모두 'USER'
account.nickname : '여행자_XXXXX' (5자리 인덱스, UNIQUE 보장)

turip_member.login_password : BCrypt 더미 해시 (전체 동일)
social_member.provider      : GOOGLE(홀수) / KAKAO(짝수)
refresh_token.device_fid    : member_id 기반 UUID 형식 문자열
"""

import csv
import hashlib
import random
from datetime import datetime, timedelta

import config

random.seed(config.SEED)

# 더미 BCrypt 해시 ("password123" 기준, 실제 앱에서 로그인 불가 — 의도된 동작)
_BCRYPT_DUMMY = "$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy"

_BASE_DATE = datetime(2025, 1, 1)


def generate(output_dir: str) -> None:
    _generate_account(output_dir)
    _generate_guest(output_dir)
    _generate_member(output_dir)
    _generate_turip_member(output_dir)
    _generate_social_member(output_dir)
    _generate_refresh_token(output_dir)


def _generate_account(output_dir: str) -> None:
    path = f"{output_dir}/account.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "role", "nickname"])
        for i in range(1, config.ACCOUNT_COUNT + 1):
            w.writerow([i, "USER", f"여행자_{i:05d}"])
    print(f"  account.csv       : {config.ACCOUNT_COUNT}행")


def _generate_guest(output_dir: str) -> None:
    """
    account_id 1 ~ 5,000 을 guest로 매핑.
    device_fid : 'device-{account_id:08d}' (UNIQUE 보장)
    """
    path = f"{output_dir}/guest.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "account_id", "device_fid"])
        for i in range(1, config.GUEST_COUNT + 1):
            account_id = i
            w.writerow([i, account_id, f"device-{account_id:08d}"])
    print(f"  guest.csv         : {config.GUEST_COUNT}행")


def _generate_member(output_dir: str) -> None:
    """
    account_id 5,001 ~ 10,000 을 member로 매핑.
    member.id   = 1 ~ 5,000
    email       = 'member_{id:05d}@turip.com' (UNIQUE 보장)
    """
    path = f"{output_dir}/member.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "account_id", "email", "is_first_login"])
        for member_id in range(1, config.MEMBER_COUNT + 1):
            account_id = config.GUEST_COUNT + member_id  # 5,001 ~ 10,000
            email = f"member_{member_id:05d}@turip.com"
            is_first_login = 0  # 로그인 기록 있음 (refresh_token 있으므로)
            w.writerow([member_id, account_id, email, is_first_login])
    print(f"  member.csv        : {config.MEMBER_COUNT}행")


def _generate_turip_member(output_dir: str) -> None:
    """
    member_id 1 ~ 2,500 을 자체 로그인으로 처리.
    login_id       : 'turip_{member_id:05d}' (5-20자, UNIQUE)
    login_password : BCrypt 더미 해시 (모두 동일)
    """
    path = f"{output_dir}/turip_member.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "member_id", "login_id", "login_password"])
        for i in range(1, config.TURIP_MEMBER_COUNT + 1):
            member_id = i
            login_id = f"turip_{member_id:05d}"
            w.writerow([i, member_id, login_id, _BCRYPT_DUMMY])
    print(f"  turip_member.csv  : {config.TURIP_MEMBER_COUNT}행")


def _generate_social_member(output_dir: str) -> None:
    """
    member_id 2,501 ~ 5,000 을 소셜 로그인으로 처리.
    provider    : 홀수 member_id → GOOGLE, 짝수 → KAKAO
    provider_id : '{provider}_{member_id:010d}' (UNIQUE per provider 보장)
    """
    path = f"{output_dir}/social_member.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "member_id", "provider", "provider_id"])
        for i in range(1, config.SOCIAL_MEMBER_COUNT + 1):
            member_id = config.TURIP_MEMBER_COUNT + i  # 2,501 ~ 5,000
            provider = "GOOGLE" if member_id % 2 == 1 else "KAKAO"
            provider_id = f"{provider.lower()}_{member_id:010d}"
            w.writerow([i, member_id, provider, provider_id])
    print(f"  social_member.csv : {config.SOCIAL_MEMBER_COUNT}행")


def _generate_refresh_token(output_dir: str) -> None:
    """
    모든 member(1 ~ 5,000)가 1번씩 로그인한 상황.
    token_hash : SHA-256(member_id + seed)
    issued_at  : 2025-01-01 ~ 2025-12-31 사이 랜덤 날짜
    expired_at : issued_at + 14일
    device_fid : 'device-{member_id:08d}' (guest의 device_fid와 충돌 없음)
    """
    path = f"{output_dir}/refresh_token.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "member_id", "device_fid", "token_hash", "issued_at", "expired_at"])
        for i in range(1, config.REFRESH_TOKEN_COUNT + 1):
            member_id = i
            device_fid = f"device-m{member_id:08d}"
            raw = f"token-{member_id}-{config.SEED}".encode()
            token_hash = hashlib.sha256(raw).hexdigest()
            offset_days = random.randint(0, 364)
            issued_at = _BASE_DATE + timedelta(days=offset_days)
            expired_at = issued_at + timedelta(days=14)
            w.writerow([
                i, member_id, device_fid, token_hash,
                issued_at.strftime("%Y-%m-%d %H:%M:%S"),
                expired_at.strftime("%Y-%m-%d %H:%M:%S"),
            ])
    print(f"  refresh_token.csv : {config.REFRESH_TOKEN_COUNT}행")
