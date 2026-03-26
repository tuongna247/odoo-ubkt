# KẾ HOẠCH PHÁT TRIỂN — UBKT DONOR PORTAL
> Ngày lập: 2026-03-26

---

## Mục tiêu
Xây dựng cổng thông tin cá nhân hóa dành cho ân nhân (Donor Portal) trên nền tảng Odoo hiện có, giúp ân nhân:
- Thấy được tác động thực tế của việc dâng hiến
- Theo dõi tiến độ các dự án đã góp
- Dâng hiến trực tiếp qua cổng
- Đặt mục tiêu dâng hiến hàng năm

---

## Nền tảng hiện tại
- **Hệ thống:** Odoo (Python / QWeb)
- **Module có sẵn:** `donor_portal`, `project_custom`, `account_custom`, `employee_custom`
- **Đã có:** Lịch sử dâng hiến, lọc theo ngày, thông tin dự án cơ bản, thanh tiến độ ngân sách

---

## Các tính năng cần xây dựng

### 1. Dashboard cá nhân — `/my/dashboard`
- Thẻ số liệu tác động: số dự án, tín hữu được giúp, lớp KT, rao tin lành, người tin nhận
- Tổng tiền đã dâng (link sang trang tài chính)
- Bản đồ Việt Nam SVG phân tỉnh, hiển thị ghim vị trí nhà thờ đã được giúp
- Khu vực clip nổi bật (nhúng YouTube)

### 2. Dự án của tôi — `/my/projects` + `/my/projects/<id>`
- Lưới thẻ: tên HT, tỉnh, ảnh đại diện, mục sư
- Chi tiết dự án:
  - Ảnh trước/sau có timestamp
  - Clip video
  - Mô tả dự án
  - Bảng ngân sách: tổng kinh phí / đã có / còn thiếu
  - Thanh tiến độ xây dựng
  - Tài liệu đính kèm
  - Báo cáo sau dâng hiến

### 3. Khám phá dự án mới — `/my/explore`
- Danh sách dự án đang cần hỗ trợ
- Mỗi dự án: ảnh, mô tả, thanh tiến độ ngân sách, nút **"Dâng hiến ngay"**

### 4. Luồng dâng hiến — `/my/donate/<id>`
- Form: nhập số tiền, chọn phương thức (chuyển khoản / QR / ví), ghi chú
- Trang xác nhận: mã QR VietQR (dùng VietQR public API)
- Trang cảm ơn: câu Kinh Thánh + ảnh công trình
- Tự động tạo bản ghi `account.payment` trạng thái nháp

### 5. Tài chính của tôi — `/my/donations` (nâng cấp)
- Thêm nút tải biên nhận đính kèm cho từng khoản dâng
- Giao diện kiểu sao kê ngân hàng (bộ lọc ngày đã có sẵn)

### 6. Mục tiêu cá nhân — `/my/goals`
- Đặt mục tiêu năm: số dự án, số tiền, lời cầu nguyện
- Thanh tiến độ so sánh thực tế vs mục tiêu

---

## Phạm vi kỹ thuật

| Hạng mục | Chi tiết |
|---|---|
| Model Odoo mới | 1 (`donor.goal`) |
| Fields mới trên model hiện có | ~15 fields trên `project.task` và `account.payment` |
| Controller Python | 7 route mới trong `portal.py` |
| Template QWeb | 8 template mới/sửa |
| Static files | 1 SVG bản đồ VN, 1 JS, 1 CSS |
| Tích hợp bên ngoài | VietQR public API |
| Bảo mật | CSRF, record-level security, TOTP 2FA |

---

## Danh sách file cần tạo / sửa

| File | Hành động |
|---|---|
| `donor_portal/__init__.py` | Sửa — import package `models` mới |
| `donor_portal/__manifest__.py` | Sửa — thêm assets, models |
| `donor_portal/models/__init__.py` | **Tạo mới** |
| `donor_portal/models/donor_goal.py` | **Tạo mới** — model `donor.goal` |
| `donor_portal/controllers/portal.py` | Sửa — thêm 7 route mới |
| `donor_portal/views/donor_portal_templates.xml` | Sửa — thêm 8 template |
| `donor_portal/security/ir.model.access.csv` | Sửa — phân quyền `donor.goal` |
| `donor_portal/static/src/img/vietnam_provinces.svg` | **Tạo mới** |
| `donor_portal/static/src/js/donor_map.js` | **Tạo mới** |
| `donor_portal/static/src/css/donor_portal.css` | **Tạo mới** |
| `project_custom/models/finance_promotion.py` | Sửa — thêm fields tác động + bản đồ |
| `account_custom/models/account_payment.py` | Sửa — thêm field biên nhận |

> Tất cả đường dẫn nằm trong: `addons_ubkt_prod/opt/odoo/ubkt_addons/`

---

## Bảo mật

1. **Record-level security:** Mọi query trong portal đều lọc theo `benefactor_id = employee.id`
2. **CSRF:** Tích hợp sẵn của Odoo, bắt buộc trên tất cả POST form
3. **TOTP 2FA:** Bật module `auth_totp` của Odoo cho portal users (Google Authenticator)
4. **Email OTP khi dâng hiến:** Gửi mã 6 số về email trước khi xác nhận chuyển tiền
5. **Signed URL:** Dùng pattern `access_token` (đã có sẵn trong `account.payment`)
6. **Audit trail:** `account.payment` đã có `mail.thread` — mọi sự kiện dâng hiến được ghi nhật ký

---

## Yêu cầu khi tuyển đơn vị phát triển
- Kinh nghiệm **Odoo 14 hoặc 16** (Python, QWeb, ORM)
- Hiểu **Odoo Portal / CustomerPortal** pattern
- Biết tích hợp SVG tương tác với JavaScript cơ bản
- Không cần backend thanh toán phức tạp — chỉ dùng VietQR public API

---

## Kiểm tra sau khi hoàn thành

- [ ] Đăng nhập portal → `/my/dashboard` hiển thị đúng số liệu tác động
- [ ] Bản đồ VN hiển thị ghim đúng tỉnh thành
- [ ] `/my/projects` liệt kê đúng dự án của ân nhân
- [ ] Chi tiết dự án: ảnh trước/sau, tiến độ, báo cáo
- [ ] `/my/explore` hiển thị dự án mở, nút dâng hiến hoạt động
- [ ] Luồng dâng hiến → QR → cảm ơn hoạt động end-to-end
- [ ] `/my/donations` hiển thị nút tải biên nhận
- [ ] `/my/goals` lưu và hiển thị tiến độ đúng
- [ ] Ân nhân A không thể xem dữ liệu của ân nhân B (kiểm tra bảo mật)
