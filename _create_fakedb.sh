#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# _create_fakedb.sh
# Tạo database demo từ production và anonymize toàn bộ dữ liệu thật.
# Production DB không bị ảnh hưởng.
#
# Usage:
#   bash _create_fakedb.sh
#
# Requires: Docker Desktop running
# ─────────────────────────────────────────────────────────────────────────────

SOURCE_DB="db_ubkt_prod_00"
DEMO_DB="db_ubkt_demo"
PG_HOST="host.docker.internal"
PG_USER="postgres"
PG_PASS="B@0Ng0c"
COMPOSE_FILE="D:/Projects/UBKT/odoo-docker/docker-compose.yml"
ODOO_CONTAINER="ubkt_odoo15"

PSQL="docker run --rm --network host -e PGPASSWORD=${PG_PASS} postgres:13 psql -h ${PG_HOST} -U ${PG_USER}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " UBKT — Tạo Demo Database từ Production"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Step 1: Stop Odoo ────────────────────────────────────────
echo ""
echo "[1/5] Dừng Odoo container..."
docker compose -f "${COMPOSE_FILE}" stop odoo
echo "      ✓ Odoo đã dừng."

# ── Step 2: Drop old demo DB if exists ──────────────────────
echo ""
echo "[2/5] Xóa demo DB cũ (nếu có)..."
${PSQL} -c "DROP DATABASE IF EXISTS ${DEMO_DB};" 2>&1
echo "      ✓ Xong."

# ── Step 3: Clone production → demo ─────────────────────────
echo ""
echo "[3/5] Clone '${SOURCE_DB}' → '${DEMO_DB}'..."
${PSQL} -c "CREATE DATABASE ${DEMO_DB} WITH TEMPLATE ${SOURCE_DB} OWNER odoo15;"
if [ $? -ne 0 ]; then
  echo "      ✗ Lỗi khi clone DB. Thử restart Odoo trước rồi chạy lại."
  docker compose -f "${COMPOSE_FILE}" start odoo
  exit 1
fi
echo "      ✓ Clone thành công."

# ── Step 4: Anonymize data ───────────────────────────────────
echo ""
echo "[4/5] Anonymize dữ liệu trong '${DEMO_DB}'..."

${PSQL} -d "${DEMO_DB}" <<'SQL'

-- Ân nhân / nhân viên
UPDATE hr_employee SET
  name        = 'Ân Nhân ' || id,
  work_email  = 'annhan' || id || '@demo.com',
  work_phone  = '090000' || LPAD(id::text, 4, '0'),
  work_mobile = NULL,
  barcode     = NULL,
  pin         = NULL;

-- Partners (hội thánh, đối tác, người dùng)
UPDATE res_partner SET
  name    = CASE
              WHEN name ILIKE '%hội thánh%' OR name ILIKE '%ht %'
                THEN 'Hội Thánh Demo ' || id
              WHEN name ILIKE '%nhà thờ%'
                THEN 'Nhà Thờ Demo ' || id
              WHEN name ILIKE '%ban%' OR name ILIKE '%ủy%'
                THEN 'Tổ Chức Demo ' || id
              ELSE 'Đối Tác ' || id
            END,
  email   = CASE WHEN email  IS NOT NULL THEN 'demo' || id || '@demo.com'  END,
  phone   = CASE WHEN phone  IS NOT NULL THEN '09' || LPAD((id % 99999999)::text, 8, '0') END,
  mobile  = NULL,
  street  = 'Địa chỉ demo ' || id,
  street2 = NULL,
  website = NULL,
  vat     = NULL,
  comment = NULL;

-- User logins (giữ nguyên admin id=1 và id=2)
UPDATE res_users SET
  login = 'user' || id || '@demo.com'
WHERE id > 2;

-- Payments / khoản dâng hiến
UPDATE account_payment SET
  amount         = ROUND((RANDOM() * 490 + 10) * 1000000),
  foreign_amount = CASE
                     WHEN foreign_amount > 0
                     THEN ROUND((RANDOM() * 4900 + 100)::numeric, 2)
                     ELSE 0
                   END,
  description    = 'Dâng hiến demo #' || id,
  paper_payment_code = 'DEMO-' || LPAD(id::text, 5, '0');

-- Sync amount back through exchange rate
UPDATE account_payment SET
  amount = ROUND(foreign_amount * exchange_rate)
WHERE foreign_amount > 0 AND exchange_rate > 1;

-- Project tasks (dự án)
UPDATE project_task SET
  name        = 'Dự Án Demo ' || id,
  description = 'Mô tả demo cho dự án số ' || id
WHERE id IN (
  SELECT DISTINCT project_task_id FROM account_payment WHERE project_task_id IS NOT NULL
);

-- Attachments — xóa nội dung nhạy cảm, giữ cấu trúc
UPDATE ir_attachment SET
  name     = 'file_demo_' || id,
  datas    = NULL,
  store_fname = NULL,
  url      = NULL
WHERE res_model IN ('account.payment', 'project.task', 'hr.employee', 'hr.applicant');

-- Mail messages — xóa nội dung
UPDATE mail_message SET
  body        = '<p>Nội dung demo</p>',
  subject     = 'Demo',
  email_from  = 'demo@demo.com',
  reply_to    = NULL
WHERE message_type IN ('email', 'comment');

SQL

if [ $? -ne 0 ]; then
  echo "      ✗ Lỗi khi anonymize."
  docker compose -f "${COMPOSE_FILE}" start odoo
  exit 1
fi
echo "      ✓ Anonymize hoàn tất."

# ── Step 5: Start Odoo ───────────────────────────────────────
echo ""
echo "[5/5] Khởi động lại Odoo..."
docker compose -f "${COMPOSE_FILE}" start odoo
echo "      ✓ Odoo đang chạy."

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ✓ XONG!"
echo ""
echo "  Demo DB : ${DEMO_DB}"
echo "  URL     : http://localhost:8069/web/database/selector"
echo "            → Chọn '${DEMO_DB}' để dùng bản demo"
echo ""
echo "  Production DB '${SOURCE_DB}' KHÔNG bị thay đổi."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
