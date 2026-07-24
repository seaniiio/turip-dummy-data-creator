#!/usr/bin/env bash
set -euo pipefail

# ─── 설정 (환경변수로 재정의 가능) ──────────────────────────────────────────
CONTAINER="${MYSQL_CONTAINER:-turip-mysql-loadtest}"
DB="${MYSQL_DB:-turip_loadtest}"
MYSQL_USER="${MYSQL_USER:-}"  # 디폴트값 없음 - 환경변수 또는 입력 필수
CONTAINER_CSV_DIR="/var/lib/mysql-files/turip"

# ─── 출력 헬퍼 ──────────────────────────────────────────────────────────────
info()    { echo ""; echo "[INFO]  $*"; }
success() { echo "[OK]    $*"; }
error()   { echo ""; echo "[ERROR] $*" >&2; exit 1; }

echo "=================================================="
echo "  Turip Dummy Data Deploy"
echo "=================================================="

# ─── 사전 확인 ───────────────────────────────────────────────────────────────
command -v docker &>/dev/null          || error "docker가 설치되어 있지 않습니다."
command -v python3 &>/dev/null         || error "python3가 설치되어 있지 않습니다."
docker inspect "$CONTAINER" &>/dev/null || error "Docker 컨테이너 '$CONTAINER'가 실행 중이지 않습니다."

# ─── ACCOUNT_COUNT 입력 ──────────────────────────────────────────────────────
if [ -z "${ACCOUNT_COUNT:-}" ]; then
  read -rp "ACCOUNT_COUNT (기본값 10000): " ACCOUNT_COUNT
  ACCOUNT_COUNT="${ACCOUNT_COUNT:-10000}"
fi
export ACCOUNT_COUNT

# ─── MySQL 사용자 ────────────────────────────────────────────────────────────
if [ -z "${MYSQL_USER:-}" ]; then
  read -rp "MySQL 사용자 (예: turip_loader): " MYSQL_USER
  [ -z "$MYSQL_USER" ] && error "MySQL 사용자는 필수입니다."
fi

# ─── MySQL 비밀번호 ──────────────────────────────────────────────────────────
if [ -z "${MYSQL_PASSWORD:-}" ]; then
  read -rsp "MySQL 비밀번호 (user: $MYSQL_USER): " MYSQL_PASSWORD
  echo
fi

# ─── 1. CSV 생성 ─────────────────────────────────────────────────────────────
info "1/3  CSV 생성 중... (ACCOUNT_COUNT=$ACCOUNT_COUNT)"
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi
python3 main.py
success "CSV 생성 완료 → output/"

# ─── 2. 파일 복사 ────────────────────────────────────────────────────────────
info "2/3  Docker 컨테이너로 파일 복사 중..."
docker exec "$CONTAINER" mkdir -p "$CONTAINER_CSV_DIR"
docker cp output/. "$CONTAINER:$CONTAINER_CSV_DIR/"
success "파일 복사 완료 → $CONTAINER:$CONTAINER_CSV_DIR/"

# ─── 3. 데이터 적재 ──────────────────────────────────────────────────────────
info "3/3  MySQL 데이터 적재 중... (수 분 소요될 수 있습니다)"
docker exec -i -e MYSQL_PWD="$MYSQL_PASSWORD" "$CONTAINER" \
  mysql -u"$MYSQL_USER" "$DB" < load/load_all.sql
success "데이터 적재 완료!"

echo ""
echo "=================================================="
echo "  배포 완료!"
echo "  컨테이너    : $CONTAINER"
echo "  데이터베이스 : $DB"
echo "  ACCOUNT_COUNT: $ACCOUNT_COUNT"
echo "=================================================="
