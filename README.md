# turip-dummy-data-creator

Turip 서비스의 개발용 더미데이터를 생성하는 Python 스크립트 모음입니다.
CSV 파일 생성 후 MySQL `LOAD DATA INFILE` 로 일괄 적재합니다.

---

## 생성 데이터 규모

| 도메인          | 테이블                  |           행 수 |
| --------------- | ----------------------- | --------------: |
| Region          | country                 |              50 |
|                 | province                |              17 |
|                 | city                    |             250 |
| Account/Auth    | account                 |          10,000 |
|                 | guest                   |           5,000 |
|                 | member                  |           5,000 |
|                 | turip_member            |           2,500 |
|                 | social_member           |           2,500 |
|                 | refresh_token           |           5,000 |
| Place           | category                |             200 |
|                 | place                   |       1,700,000 |
|                 | place_category          |          50,000 |
| Creator/Content | creator                 |           7,500 |
|                 | content                 |         100,000 |
|                 | content_place           |       2,000,000 |
| Favorite        | favorite_folder         |          50,000 |
|                 | favorite_folder_account |         110,000 |
|                 | favorite_content        |         200,000 |
|                 | favorite_place          |         750,000 |
| **합계**        |                         | **≈ 4,997,517** |

---

## 사전 준비

macOS는 `python` 대신 `python3`을 사용하며, 가상환경을 권장합니다.

```bash
# 가상환경 생성 (최초 1회)
python3 -m venv .venv

# 가상환경 활성화 (터미널 열 때마다)
source .venv/bin/activate

# 의존성 설치 (최초 1회)
pip install -r requirements.txt
```

---

## 사용 방법

> **전제 조건**: 스프링 프로젝트의 Flyway 마이그레이션이 먼저 실행되어 테이블이 생성된 상태여야 합니다.

### 1. CSV 생성

```bash
python main.py
```

`output/` 디렉토리에 테이블별 CSV 파일이 생성됩니다.
대용량 테이블(place, content_place)은 10% 단위 진행률을 출력합니다.

### 2. CSV → Docker 컨테이너 복사

```bash
docker exec turip-mysql-dev mkdir -p /var/lib/mysql-files/turip
docker cp output/. turip-mysql-dev:/var/lib/mysql-files/turip/
docker cp load/load_all.sql turip-mysql-dev:/var/lib/mysql-files/turip/
```

### 3. MySQL 접속 후 적재

```bash
docker exec -it turip-mysql-dev mysql -u root -p turip_dummy_1
```

```sql
SOURCE /var/lib/mysql-files/turip/load_all.sql;
```

---

## 파일 구조

```
turip-dummy-data-creator/
├── main.py               # 진입점 — 도메인 순서대로 생성기 호출
├── config.py             # 행 수, 시드값 등 전역 상수
├── generate_tokens.py    # k6 부하테스트용 JWT 토큰 CSV 생성 (독립 실행)
├── requirements.txt
├── .gitignore
├── generators/
│   ├── region.py         # country / province / city
│   ├── account.py        # account / guest / member / turip_member / social_member / refresh_token
│   ├── place.py          # category / place / place_category
│   ├── content.py        # creator / content / content_place
│   └── favorite.py       # favorite_folder / favorite_folder_account / favorite_content / favorite_place
└── load/
    └── load_all.sql      # LOAD DATA INFILE 스크립트
```

---

## k6 부하테스트용 JWT 토큰 생성

`generate_tokens.py`는 더미데이터와 **독립적으로** 동작하는 스크립트입니다.
k6 스크립트와 같은 디렉토리에서 실행하거나, 생성된 `tokens.csv`를 k6 실행 위치로 복사하세요.

### 환경변수

| 변수                | 설명                                      | 기본값               |
| ------------------- | ----------------------------------------- | -------------------- |
| `JWT_SECRET`        | 시크릿 키                                 | 부하테스트 서버용 키 |
| `JWT_SECRET_BASE64` | `true` 시 시크릿을 Base64 디코딩하여 사용 | `false`              |
| `JWT_ALGORITHM`     | 서명 알고리즘                             | `HS256`              |
| `JWT_EXPIRE_DAYS`   | 토큰 유효기간 (일)                        | `30`                 |
| `ACCOUNT_COUNT`     | 생성할 토큰 수 (account_id 1 ~ N)         | `10000`              |

### 실행

```bash
# 기본값으로 실행
python3 generate_tokens.py

# 토큰 수 지정
ACCOUNT_COUNT=500 python3 generate_tokens.py

# 다른 서버 시크릿 사용
JWT_SECRET=other-secret JWT_SECRET_BASE64=false python3 generate_tokens.py
```

`tokens.csv`가 생성되며 k6에서 아래와 같이 사용합니다.

```js
const tokens = new SharedArray("tokens", function () {
  return open("./tokens.csv")
    .split("\n")
    .slice(1)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
});
```

---

## ID 구간 설계

### Account

| 테이블 | account_id 범위 | 비고                   |
| ------ | --------------- | ---------------------- |
| member | 1 ~ 5,000       | member.id = account_id |
| guest  | 5,001 ~ 10,000  | guest.id = 1 ~ 5,000   |

| 테이블        | member_id 범위 | account_id 범위 |
| ------------- | -------------- | --------------- |
| turip_member  | 1 ~ 2,500      | 1 ~ 2,500       |
| social_member | 2,501 ~ 5,000  | 2,501 ~ 5,000   |

### Favorite Folder

| folder_id 범위  | 종류          | is_default | is_shared |
| --------------- | ------------- | ---------- | --------- |
| 1 ~ 10,000      | 기본 폴더     | 1          | 0         |
| 10,001 ~ 20,000 | 공유 커스텀 1 | 0          | 1         |
| 20,001 ~ 30,000 | 공유 커스텀 2 | 0          | 1         |
| 30,001 ~ 40,000 | 개인 커스텀 1 | 0          | 0         |
| 40,001 ~ 50,000 | 개인 커스텀 2 | 0          | 0         |

---

## 재현성

모든 생성기는 `config.SEED = 42` 로 고정되어 있어 동일한 CSV를 반복 생성할 수 있습니다.
