"""
k6 부하테스트용 JWT 토큰 CSV 생성기

생성 파일: tokens.csv
  헤더 : token
  행 수 : ACCOUNT_COUNT

환경변수)
  JWT_SECRET        - 시크릿 키 (기본: 부하테스트 서버용 키)
  JWT_SECRET_BASE64 - Base64 인코딩된 시크릿인 경우 'true' (기본: false)
  JWT_ALGORITHM     - 알고리즘 (기본: HS256)
  JWT_EXPIRE_DAYS   - 토큰 유효기간 일수 (기본: 30)
  ACCOUNT_COUNT     - 생성할 토큰 수 (기본: 10000)

사용 예)
  python3 generate_tokens.py
  ACCOUNT_COUNT=5000 python3 generate_tokens.py
"""

import csv
import os
import base64
from datetime import datetime, timezone, timedelta

import jwt  # PyJWT

_DEFAULT_SECRET  = "YHO6Su3gPrDNThlRRO8ahrEuFeOVpNNVAI4v/lFMx+w="
_JWT_SECRET      = os.environ.get("JWT_SECRET", _DEFAULT_SECRET)
_JWT_ALGORITHM   = os.environ.get("JWT_ALGORITHM", "HS256")
_JWT_SECRET_B64  = os.environ.get("JWT_SECRET_BASE64", "false").lower() == "true"
_JWT_EXPIRE_DAYS = int(os.environ.get("JWT_EXPIRE_DAYS", 30))
_ACCOUNT_COUNT   = int(os.environ.get("ACCOUNT_COUNT", 10_000))


def _signing_key() -> bytes:
    return base64.b64decode(_JWT_SECRET) if _JWT_SECRET_B64 else _JWT_SECRET.encode("utf-8")


def _make_token(account_id: int, signing_key: bytes) -> str:
    now = datetime.now(tz=timezone.utc)
    payload = {
        "accountId": account_id,
        "role":      "USER",
        "iat":       now,
        "exp":       now + timedelta(days=_JWT_EXPIRE_DAYS),
    }
    return jwt.encode(payload, signing_key, algorithm=_JWT_ALGORITHM,
                      headers={"typ": "JWT"})


def main():
    signing_key = _signing_key()
    log_step    = max(_ACCOUNT_COUNT // 10, 1)

    print(f"JWT 토큰 생성 중... ({_ACCOUNT_COUNT:,}개 / {_JWT_ALGORITHM} / {_JWT_EXPIRE_DAYS}일 유효)")

    with open("tokens.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["token"])
        for account_id in range(1, _ACCOUNT_COUNT + 1):
            w.writerow([_make_token(account_id, signing_key)])
            if account_id % log_step == 0:
                print(f"  {account_id / _ACCOUNT_COUNT * 100:.0f}%")

    print(f"완료 → tokens.csv ({_ACCOUNT_COUNT:,}행)")


if __name__ == "__main__":
    main()
