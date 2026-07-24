-- ============================================================
-- Turip 더미데이터 LOAD DATA INFILE 스크립트
-- 대상 DB : turip_dummy_1
-- 실행 전  : CSV 파일을 MySQL 컨테이너 내부로 복사
--
-- [사용 방법]
-- 1. CSV 생성
--    python main.py
--
-- 2. CSV 파일을 컨테이너 내부로 복사
--    docker cp output/. turip-mysql-dev:/var/lib/mysql-files/turip/
--
-- 3. MySQL 접속 후 스크립트 실행
--    docker exec -it turip-mysql-dev mysql -u root -p turip_dummy_1
--    mysql> SOURCE /var/lib/mysql-files/turip/load_all.sql;
--
-- [주의]
-- - MySQL 설정에서 secure_file_priv 경로 확인 필요
--   SHOW VARIABLES LIKE 'secure_file_priv';
-- - city.province_id : 빈값 → NULL 변환 처리 포함
-- ============================================================

SET @csv_dir = '/var/lib/mysql-files/turip';

SET FOREIGN_KEY_CHECKS = 0;
SET UNIQUE_CHECKS      = 0;
SET SQL_LOG_BIN        = 0;
SET autocommit         = 0;

-- ──────────────────────────────────────────────────────────────
-- 0. 기존 데이터 초기화 (재실행 가능하도록, 역 FK 순서)
-- ──────────────────────────────────────────────────────────────

TRUNCATE TABLE favorite_place;
TRUNCATE TABLE favorite_content;
TRUNCATE TABLE favorite_folder_account;
TRUNCATE TABLE favorite_folder;
TRUNCATE TABLE content_place;
TRUNCATE TABLE content;
TRUNCATE TABLE creator;
TRUNCATE TABLE place_category;
TRUNCATE TABLE place;
TRUNCATE TABLE category;
TRUNCATE TABLE fcm_token;
TRUNCATE TABLE refresh_token;
TRUNCATE TABLE social_member;
TRUNCATE TABLE turip_member;
TRUNCATE TABLE member;
TRUNCATE TABLE guest;
TRUNCATE TABLE account;
TRUNCATE TABLE city;
TRUNCATE TABLE province;
TRUNCATE TABLE country;

COMMIT;
SELECT '===== 테이블 초기화 완료 =====' AS status;

-- ──────────────────────────────────────────────────────────────
-- 1. Region 도메인
-- ──────────────────────────────────────────────────────────────

LOAD DATA INFILE '/var/lib/mysql-files/turip/country.csv'
INTO TABLE country
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, name, image_url);

LOAD DATA INFILE '/var/lib/mysql-files/turip/province.csv'
INTO TABLE province
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, name);

-- province_id 빈값 → NULL 변환
LOAD DATA INFILE '/var/lib/mysql-files/turip/city.csv'
INTO TABLE city
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, country_id, @province_id, name, image_url)
SET province_id = NULLIF(@province_id, '');

COMMIT;
SELECT 'Region 도메인 완료' AS status;

-- ──────────────────────────────────────────────────────────────
-- 2. Account / Auth 도메인
-- ──────────────────────────────────────────────────────────────

LOAD DATA INFILE '/var/lib/mysql-files/turip/account.csv'
INTO TABLE account
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, role, nickname);

LOAD DATA INFILE '/var/lib/mysql-files/turip/guest.csv'
INTO TABLE guest
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, account_id, device_fid);

LOAD DATA INFILE '/var/lib/mysql-files/turip/member.csv'
INTO TABLE member
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, account_id, email, is_first_login, is_migration_decided);

LOAD DATA INFILE '/var/lib/mysql-files/turip/turip_member.csv'
INTO TABLE turip_member
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, member_id, login_id, login_password);

LOAD DATA INFILE '/var/lib/mysql-files/turip/social_member.csv'
INTO TABLE social_member
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, member_id, provider, provider_id);

LOAD DATA INFILE '/var/lib/mysql-files/turip/refresh_token.csv'
INTO TABLE refresh_token
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, member_id, device_fid, token_hash, issued_at, expired_at);

LOAD DATA INFILE '/var/lib/mysql-files/turip/fcm_token.csv'
INTO TABLE fcm_token
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, account_id, device_fid, token, notification_enabled, created_at, updated_at);

COMMIT;
SELECT 'Account/Auth 도메인 완료' AS status;

-- ──────────────────────────────────────────────────────────────
-- 3. Place 도메인
-- ──────────────────────────────────────────────────────────────

LOAD DATA INFILE '/var/lib/mysql-files/turip/category.csv'
INTO TABLE category
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, name);

-- place는 대용량(170만) — 배치 단위 커밋 권장
LOAD DATA INFILE '/var/lib/mysql-files/turip/place.csv'
INTO TABLE place
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, name, url, address, latitude, longitude);

LOAD DATA INFILE '/var/lib/mysql-files/turip/place_category.csv'
INTO TABLE place_category
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, place_id, category_id);

COMMIT;
SELECT 'Place 도메인 완료' AS status;

-- ──────────────────────────────────────────────────────────────
-- 4. Creator / Content 도메인
-- ──────────────────────────────────────────────────────────────

LOAD DATA INFILE '/var/lib/mysql-files/turip/creator.csv'
INTO TABLE creator
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, channel_name, profile_image);

LOAD DATA INFILE '/var/lib/mysql-files/turip/content.csv'
INTO TABLE content
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, creator_id, city_id, title, url, uploaded_date);

-- content_place는 대용량(200만) — 가장 오래 걸리는 구간
LOAD DATA INFILE '/var/lib/mysql-files/turip/content_place.csv'
INTO TABLE content_place
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, content_id, place_id, visit_day, visit_order, time_line);

COMMIT;
SELECT 'Creator/Content 도메인 완료' AS status;

-- ──────────────────────────────────────────────────────────────
-- 5. Favorite 도메인
-- ──────────────────────────────────────────────────────────────

LOAD DATA INFILE '/var/lib/mysql-files/turip/favorite_folder.csv'
INTO TABLE favorite_folder
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, name, is_default, is_shared);

LOAD DATA INFILE '/var/lib/mysql-files/turip/favorite_folder_account.csv'
INTO TABLE favorite_folder_account
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, favorite_folder_id, account_id, account_role);

LOAD DATA INFILE '/var/lib/mysql-files/turip/favorite_content.csv'
INTO TABLE favorite_content
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, account_id, content_id, created_at);

LOAD DATA INFILE '/var/lib/mysql-files/turip/favorite_place.csv'
INTO TABLE favorite_place
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, favorite_folder_id, place_id, favorite_order);

COMMIT;
SELECT 'Favorite 도메인 완료' AS status;

-- ──────────────────────────────────────────────────────────────
-- 마무리
-- ──────────────────────────────────────────────────────────────

SET FOREIGN_KEY_CHECKS = 1;
SET UNIQUE_CHECKS      = 1;
SET SQL_LOG_BIN        = 1;
SET autocommit         = 1;

SELECT '===== 전체 더미데이터 로드 완료 =====' AS status;
