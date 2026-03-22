# Hướng Dẫn Deploy Odoo 15 UBKT Lên Server Production

---

## 1. Cấu Hình Server Khuyến Nghị

### Tối thiểu (dưới 20 người dùng đồng thời)
| Thành phần | Cấu hình |
|---|---|
| CPU | 4 vCPU |
| RAM | 8 GB |
| Ổ cứng | 100 GB SSD |
| Băng thông | 100 Mbps |

### Khuyến nghị (20–50 người dùng đồng thời)
| Thành phần | Cấu hình |
|---|---|
| CPU | 8 vCPU |
| RAM | 16 GB |
| Ổ cứng | 200 GB SSD |
| Băng thông | 200 Mbps |

### Hệ điều hành
- **Ubuntu 22.04 LTS** (khuyến nghị) hoặc Debian 11

### Nhà cung cấp VPS gợi ý (Việt Nam)
- **Viettel IDC** — vps.viettelidc.com.vn
- **VNPT Cloud** — cloud.vnpt.vn
- **Bizfly Cloud** — bizflycloud.vn
- **DigitalOcean** (Singapore region) — digitalocean.com

---

## 2. Kiến Trúc Deploy

```
Internet
    │
    ▼
[Nginx - Port 80/443]  ← SSL/HTTPS (Let's Encrypt)
    │
    ├── / → Odoo:8069
    └── /longpolling → Odoo:8072

[Docker: odoo:15 - Port 8069, 8072]
    │
    ▼
[PostgreSQL 13 - Port 5432]  ← Chạy trực tiếp trên server (không qua Docker)

[Filestore] → /opt/ubkt/data/filestore/
[Addons]    → /opt/ubkt/addons/
[Backups]   → /opt/ubkt/backups/
```

---

## 3. Cài Đặt Server

### Bước 1 — Cập nhật hệ thống
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git vim ufw fail2ban
```

### Bước 2 — Cài Docker
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker

# Cài docker-compose
sudo apt install -y docker-compose-plugin
docker compose version
```

### Bước 3 — Cài PostgreSQL 13
```bash
sudo apt install -y postgresql-13 postgresql-client-13
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Tạo user odoo15
sudo -u postgres psql <<EOF
CREATE ROLE odoo15 WITH LOGIN PASSWORD 'B@0Ng0c' CREATEDB;
CREATE DATABASE db_ubkt_prod_00 OWNER odoo15;
GRANT ALL PRIVILEGES ON DATABASE db_ubkt_prod_00 TO odoo15;
EOF
```

### Bước 4 — Cấu hình PostgreSQL cho Docker
```bash
sudo nano /etc/postgresql/13/main/pg_hba.conf
```
Thêm dòng (cho phép Docker network kết nối):
```
host    all             odoo15          172.16.0.0/12           scram-sha-256
host    all             odoo15          127.0.0.1/32            scram-sha-256
```

```bash
sudo nano /etc/postgresql/13/main/postgresql.conf
```
Sửa dòng:
```
listen_addresses = 'localhost,172.17.0.1'
```

```bash
sudo systemctl restart postgresql
```

### Bước 5 — Tạo cấu trúc thư mục
```bash
sudo mkdir -p /opt/ubkt/{data,addons,backups,config}
sudo chown -R $USER:$USER /opt/ubkt
```

### Bước 6 — Upload file lên server
Từ máy Windows, dùng SCP hoặc FileZilla:
```powershell
# Upload addons
scp -r "D:\Projects\UBKT\addons_ubkt_prod\opt\odoo\ubkt_addons" user@server:/opt/ubkt/addons/

# Upload filestore
scp -r "D:\Projects\UBKT\odoo-docker\data\filestore" user@server:/opt/ubkt/data/

# Upload config
scp "D:\Projects\UBKT\odoo-docker\odoo.conf" user@server:/opt/ubkt/config/
```

### Bước 7 — Restore database
```bash
# Upload file dump trước, sau đó:
psql -U postgres -d db_ubkt_prod_00 -f /opt/ubkt/backups/db_ubkt_prod_00.sql
```

---

## 4. Cấu Hình Docker Compose (Production)

Tạo file `/opt/ubkt/docker-compose.yml`:

```yaml
version: '3.8'

services:
  odoo:
    image: odoo:15
    container_name: ubkt_odoo15
    restart: always
    ports:
      - "127.0.0.1:8069:8069"
      - "127.0.0.1:8072:8072"
    volumes:
      - /opt/ubkt/data:/var/lib/odoo
      - /opt/ubkt/config/odoo.conf:/etc/odoo/odoo.conf:ro
      - /opt/ubkt/addons/ubkt_addons:/mnt/extra-addons:ro
    environment:
      - HOST=172.17.0.1
      - PORT=5432
      - USER=odoo15
      - PASSWORD=B@0Ng0c
    extra_hosts:
      - "host.docker.internal:host-gateway"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
```

> ⚠️ Port `127.0.0.1:8069` — chỉ bind localhost, KHÔNG expose ra ngoài. Nginx sẽ là cổng duy nhất ra internet.

---

## 5. Cấu Hình odoo.conf (Production)

Tạo file `/opt/ubkt/config/odoo.conf`:

```ini
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
db_host = host.docker.internal
db_port = 5432
db_user = odoo15
db_password = B@0Ng0c
db_name = db_ubkt_prod_00
data_dir = /var/lib/odoo

; Bảo mật — đổi mật khẩu này!
admin_passwd = Ubkt@2024#Secure!

; Hiệu suất
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 120
limit_time_real = 300

; Proxy
proxy_mode = True

; Log
logfile = /var/lib/odoo/odoo.log
log_level = warn
```

---

## 6. Cài Đặt Nginx + SSL

### Cài Nginx
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
sudo systemctl enable nginx
```

### Tạo cấu hình Nginx
```bash
sudo nano /etc/nginx/sites-available/ubkt-odoo
```

```nginx
upstream odoo {
    server 127.0.0.1:8069;
}
upstream odoo-longpolling {
    server 127.0.0.1:8072;
}

# Redirect HTTP → HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL (Let's Encrypt sẽ tự điền sau)
    ssl_certificate     /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # Gzip
    gzip on;
    gzip_types text/css text/less text/plain text/xml application/xml application/json application/javascript;

    # Upload size tối đa
    client_max_body_size 200m;

    # Timeout
    proxy_read_timeout  720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout  720s;

    # Header bảo mật
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Static files (cache dài)
    location ~* /web/static/ {
        proxy_cache_valid 200 90d;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
        proxy_set_header Host $host;
    }

    # Longpolling (live chat, notifications)
    location /longpolling {
        proxy_pass http://odoo-longpolling;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Odoo chính
    location / {
        proxy_pass http://odoo;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ubkt-odoo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Cài SSL miễn phí (Let's Encrypt)
```bash
# Thay your-domain.com bằng tên miền thực
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Tự động gia hạn
sudo crontab -e
# Thêm dòng:
0 3 * * * certbot renew --quiet
```

---

## 7. Tường Lửa (UFW)

```bash
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
# KHÔNG mở 8069, 5432 ra internet
sudo ufw enable
sudo ufw status
```

---

## 8. Backup Tự Động

Tạo script `/opt/ubkt/backup.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d_%H-%M)
BACKUP_DIR="/opt/ubkt/backups"
DB_NAME="db_ubkt_prod_00"
KEEP_DAYS=30

# Backup database
pg_dump -U odoo15 -h 127.0.0.1 $DB_NAME | gzip > "$BACKUP_DIR/db_${DB_NAME}_${DATE}.sql.gz"

# Backup filestore
tar -czf "$BACKUP_DIR/filestore_${DATE}.tar.gz" /opt/ubkt/data/filestore/

# Xóa backup cũ hơn 30 ngày
find $BACKUP_DIR -name "*.gz" -mtime +$KEEP_DAYS -delete

echo "Backup done: $DATE"
```

```bash
chmod +x /opt/ubkt/backup.sh

# Chạy tự động mỗi ngày lúc 2 giờ sáng
crontab -e
# Thêm dòng:
0 2 * * * /opt/ubkt/backup.sh >> /opt/ubkt/backups/backup.log 2>&1
```

---

## 9. Khởi Động Odoo

```bash
cd /opt/ubkt
docker compose up -d

# Kiểm tra logs
docker logs ubkt_odoo15 -f

# Cập nhật modules sau khi deploy
docker stop ubkt_odoo15
docker run --rm \
  -v /opt/ubkt/data:/var/lib/odoo \
  -v /opt/ubkt/config/odoo.conf:/etc/odoo/odoo.conf:ro \
  -v /opt/ubkt/addons/ubkt_addons:/mnt/extra-addons:ro \
  --add-host host.docker.internal:host-gateway \
  odoo:15 odoo -d db_ubkt_prod_00 -u all --stop-after-init --no-http
docker start ubkt_odoo15
```

---

## 10. Checklist Trước Khi Go-Live

- [ ] Đổi `admin_passwd` trong `odoo.conf` (không dùng `admin`)
- [ ] Đổi mật khẩu user `admin` trong Odoo UI
- [ ] SSL đã cài và hoạt động (HTTPS)
- [ ] Port 8069, 5432 không mở ra ngoài (kiểm tra `sudo ufw status`)
- [ ] Backup tự động đã chạy thử (`/opt/ubkt/backup.sh`)
- [ ] `proxy_mode = True` trong `odoo.conf`
- [ ] `workers = 4` (hoặc = số CPU × 2)
- [ ] Tên miền trỏ đúng về IP server
- [ ] Fail2ban đang chạy (`sudo systemctl status fail2ban`)
- [ ] Đã test đăng nhập qua HTTPS
- [ ] Đã test portal người dâng hiến qua HTTPS
- [ ] Đã test gửi email (SMTP settings trong Odoo)

---

## 11. Lệnh Thường Dùng Trên Server

```bash
# Xem logs Odoo
docker logs ubkt_odoo15 --tail 100 -f

# Restart Odoo
docker restart ubkt_odoo15

# Vào shell Odoo
docker exec -it ubkt_odoo15 odoo shell -d db_ubkt_prod_00 --no-http

# Kiểm tra PostgreSQL
sudo -u postgres psql -c "\l"

# Kiểm tra dung lượng
df -h /opt/ubkt

# Kiểm tra RAM/CPU
htop
```

---

## 12. Sơ Đồ Tổng Kết

```
[Người dùng - Browser]
        │ HTTPS:443
        ▼
[Nginx - Ubuntu Server]
  ├── SSL termination
  ├── Static file cache
  └── Reverse proxy
        │ HTTP:8069 / 8072
        ▼
[Docker: odoo:15]
  ├── /opt/ubkt/data      → /var/lib/odoo
  ├── /opt/ubkt/config    → /etc/odoo/odoo.conf
  └── /opt/ubkt/addons    → /mnt/extra-addons
        │
        ▼
[PostgreSQL 13 - localhost:5432]
  └── db_ubkt_prod_00

[Cron: 2h sáng] → Backup DB + Filestore → /opt/ubkt/backups/
```
