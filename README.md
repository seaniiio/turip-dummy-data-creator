# turip-dummy-data-creator

Turip 서비스의 개발용 더미데이터를 생성하는 Python 스크립트 모음입니다.
CSV 파일 생성 후 MySQL `LOAD DATA INFILE` 로 일괄 적재합니다.

---

## 생성 데이터 규모

| 도메인 | 테이블 | 행 수 |
|--------|--------|------:|
| Region | country | 50 |
| | province | 17 |
| | city | 250 |
| Account/Auth | account | 10,000 |
| | guest | 5,000 |
| | member | 5,000 |
| | turip_member | 2,500 |
| | social_member | 2,500 |
| | refresh_token | 5,000 |
| Place | category | 200 |
| | place | 1,700,000 |
| | place_category | 50,000 |
| Creator/Content | creator | 7,500 |
| | content | 100,000 |
| | content_place | 2,000,000 |
| Favorite | favorite_folder | 50,000 |
| | favorite_folder_account | 110,000 |
| | favorite_content | 200,000 |
| | favorite_place | 750,000 |
| **합계** | | **≈ 4,997,517** |

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

## ID 구간 설계

### Account

| 테이블 | account_id 범위 | 비고 |
|--------|----------------|------|
| guest | 1 ~ 5,000 | guest.id = account_id |
| member | 5,001 ~ 10,000 | member.id = 1 ~ 5,000 |

| 테이블 | member_id 범위 |
|--------|---------------|
| turip_member | 1 ~ 2,500 |
| social_member | 2,501 ~ 5,000 |

### Favorite Folder

| folder_id 범위 | 종류 | is_default | is_shared |
|---------------|------|-----------|---------|
| 1 ~ 10,000 | 기본 폴더 | 1 | 0 |
| 10,001 ~ 20,000 | 공유 커스텀 1 | 0 | 1 |
| 20,001 ~ 30,000 | 공유 커스텀 2 | 0 | 1 |
| 30,001 ~ 40,000 | 개인 커스텀 1 | 0 | 0 |
| 40,001 ~ 50,000 | 개인 커스텀 2 | 0 | 0 |

---

## 재현성

모든 생성기는 `config.SEED = 42` 로 고정되어 있어 동일한 CSV를 반복 생성할 수 있습니다.
