# Module Ân Nhân (donor_portal) — Hướng Dẫn Cài Đặt & Sử Dụng

---

## Cài Đặt Module

### Bước 1 — Dừng Odoo
```cmd
docker stop ubkt_odoo15
```

### Bước 2 — Cài module donor_portal
```cmd
docker run --rm -v D:/Projects/UBKT/odoo-docker/data:/var/lib/odoo -v D:/Projects/UBKT/odoo-docker/odoo.conf:/etc/odoo/odoo.conf:ro -v D:/Projects/UBKT/addons_ubkt_prod/opt/odoo/ubkt_addons:/mnt/extra-addons:ro --add-host host.docker.internal:host-gateway odoo:15 odoo -d db_ubkt_prod_00 -i donor_portal --stop-after-init --no-http
```

### Bước 3 — Khởi động lại
```cmd
docker start ubkt_odoo15
```

---

## Thiết Lập Cho Ân Nhân

### Bước 1 — Liên kết nhân viên với portal
**Vào: Nhân viên → [chọn ân nhân] → Tab "Thông tin riêng tư"**
- Điền `address_home_id` → chọn hoặc tạo địa chỉ liên kết portal

### Bước 2 — Tạo tài khoản portal
**Vào: Cài đặt → Người dùng → Mời người dùng portal**
- Nhập email của ân nhân
- Chọn loại: **Portal**
- Gửi lời mời

### Bước 3 — Ân nhân đăng nhập
- Truy cập: `http://localhost:8069`
- Đăng nhập bằng email đã được mời
- Vào mục **"Lịch sử dâng hiến"**

---

## Tính Năng

| URL | Nội dung |
|---|---|
| `/my/donations` | Danh sách tất cả lần dâng + tóm tắt theo dự án |
| `/my/donations/<id>` | Chi tiết 1 lần dâng + tiến độ tài chính dự án |

### Trang danh sách `/my/donations`
1. **Thẻ thông tin** — Tên, tổng số lần dâng, tổng tiền VNĐ/USD
2. **Tóm tắt theo dự án** — Số lần + tổng tiền từng dự án
3. **Bộ lọc** — Theo ngày bắt đầu/kết thúc, sắp xếp
4. **Timeline** — Từng lần dâng: ngày, mã phiếu, dự án, số tiền

### Trang chi tiết `/my/donations/<id>`
- Ngày dâng hiến
- Dự án / hạng mục
- Số tiền VNĐ + ngoại tệ (nếu có)
- Tiến độ tài chính dự án (thanh progress bar)
- Người xác nhận + thời điểm ký

---

## Bảo Mật

- Ân nhân chỉ thấy dữ liệu của **chính họ** (lọc theo `benefactor_id`)
- Chỉ hiện phiếu `state = 'posted'` (đã xác nhận)
- Mục **"Payment Approvals"** bị ẩn với ân nhân
- Quyền: **chỉ đọc** — không thể sửa hay xóa

---

## Cấu Trúc Module

```
donor_portal/
├── __manifest__.py                     ← khai báo module
├── __init__.py
├── controllers/
│   └── portal.py                       ← xử lý logic & route
├── views/
│   └── donor_portal_templates.xml      ← giao diện portal
└── security/
    └── ir.model.access.csv             ← phân quyền read-only
```
