#!/usr/bin/env bash
set -euo pipefail

# PostgreSQL 16 trên Windows, chạy bằng Git Bash.
PG_BIN="${PG_BIN:-/c/Program Files/PostgreSQL/16/bin}"

if [[ -d "$PG_BIN" ]]; then
    export PATH="$PG_BIN:$PATH"
fi

DB_HOST="127.0.0.1"
DB_PORT="5432"
DB_USER="postgres"
DB_NAME="${1:-arimms_python}"

for tool in pg_isready psql; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "Không tìm thấy $tool. Kiểm tra đường dẫn PG_BIN."
        exit 1
    fi
done

is_postgres_running() {
    pg_isready \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d postgres \
        -t 1 \
        -q
}

if is_postgres_running; then
    echo "PostgreSQL đang chạy."
else
    echo "Đang khởi động PostgreSQL Windows Service..."

    powershell.exe -NoProfile -Command \
        "Start-Service -Name 'postgresql-x64-16' -ErrorAction Stop"

    for ((attempt = 1; attempt <= 15; attempt++)); do
        if is_postgres_running; then
            break
        fi
        sleep 1
    done

    if ! is_postgres_running; then
        echo "PostgreSQL chưa sẵn sàng nhận kết nối."
        exit 1
    fi
fi

echo "Kiểm tra database: $DB_NAME"
echo "Nhập mật khẩu PostgreSQL nếu được yêu cầu."

psql \
    -X \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d postgres \
    -v ON_ERROR_STOP=1 \
    -v db_name="$DB_NAME" <<'SQL'
SELECT format('CREATE DATABASE %I', :'db_name')
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_database
    WHERE datname = :'db_name'
)
\gexec
SQL

echo "Database $DB_NAME đã sẵn sàng."
echo "Tiếp theo chạy Alembic migration và seed theo README."