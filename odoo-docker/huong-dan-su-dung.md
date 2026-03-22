# Hướng Dẫn Sử Dụng Hệ Thống UBKT Odoo 15

---

## 1. Thiết Lập Ban Đầu (Bắt Buộc)

Trước khi sử dụng các quy trình, cần thiết lập đúng vai trò cho từng người dùng.

### Cách thiết lập vai trò người dùng
**Vào: Cài đặt → Người dùng → [chọn người dùng]**

| Vai trò | Giá trị `user_role` | `is_approval` | Trách nhiệm |
|---|---|---|---|
| Mục sư / Giám đốc | `pastor` | ✓ Bật | Duyệt cuối cùng cho dự án & phiếu chi/thu |
| Kế toán | `accountant` | ✓ Bật | Duyệt bước 1 cho phiếu chi/thu, gửi duyệt lần cuối |
| Thủ quỹ | `treasurer` | ✓ Bật | Duyệt bước 2 cho phiếu chi/thu |
| Người giao tiền | `delivered_person` | Tùy chọn | Ký trên phiếu chi |
| Người nhận tiền | `received_person` | Tùy chọn | Ký trên phiếu thu |
| Người duyệt nhập liệu | (bất kỳ) | — | Bật `data_entry_approval = True` |

### Cách tải chữ ký & con dấu
**Vào: Cài đặt → Người dùng → [chọn người dùng]**

Tải lên các hình ảnh sau:
- `sign_signature` — Hình chữ ký tay (scan hoặc chụp ảnh)
- `sign_stamp` — Hình con dấu chính thức
- `sign_stamp_send` — Hình con dấu dùng trên văn bản gửi đi

> ⚠️ **Lưu ý:** Chữ ký trên phiếu chi/thu sẽ lấy tự động từ hồ sơ người dùng. Nếu chưa tải lên thì chữ ký sẽ trống trên PDF.

---

## 2. Quy Trình Dự Án / Công Trình

### Sơ đồ tổng quát
```
Tạo dự án → Nhập liệu → Duyệt nhập liệu
→ Điền ý kiến → Gửi email → Mục sư duyệt trên portal
→ Đã duyệt ✓ / Từ chối ✗
```

---

### Bước 1 — Tạo Dự Án
**Ai:** Nhân viên
**Vào:** Dự án → Nhiệm vụ → Mới

Điền các thông tin:
- Tên dự án
- Bật cờ phù hợp:
  - `finance_promotion = True` → Dự án tài chính / xây dựng
  - `construction_info = True` → Thông tin công trình
  - `icm_flag = True` → Biểu mẫu ICM

Hệ thống tự động gán:
- `approval_id` = Mục sư / Người có thẩm quyền
- `approval_state` = `open` (chờ duyệt)
- `approved_data_entry` = `False` (chưa duyệt nhập liệu)

---

### Bước 2 — Nhập Liệu
**Ai:** Nhân viên nhập liệu
**Điền đầy đủ các thông tin:**

**Thông tin đất đai:**
- `land_length` / `land_width` → Kích thước đất
- `land_origin` → Nguồn gốc đất
- `land_owner` → Chủ đất (liên kết `res.partner`)

**Thông tin tài chính:**
- `total_estimate_church` → Tổng kinh phí dự kiến
- `total_amount_spent` → Số tiền đã chi
- `child_god_donate` → Con Chúa dâng hiến
- `benefactor_donate` → Ân nhân tài trợ
- `currency_id` / `exchange_rate` → Tiền tệ và tỷ giá

**Thông tin ICM (nếu có):**
- `icm_spintend_name` / `icm_spintend_phone` → Thông tin người phụ trách
- `icm_official_believers` → Số tín hữu chính thức
- `icm_attend_num` → Số người tham dự nhóm
- `icm_total_build_cost_vnd` / `icm_total_build_cost_usd` → Chi phí xây dựng

> ⚠️ **Không thể chuyển sang giai đoạn tiếp theo** cho đến khi hoàn thành Bước 3.

---

### Bước 3 — Duyệt Nhập Liệu
**Ai:** Người có `data_entry_approval = True`
**Vào:** Form nhiệm vụ → Nhấn nút **"Approve Data Entry"**

Kết quả:
- `approved_data_entry = True`
- Có thể chuyển giai đoạn tiếp theo

---

### Bước 4 — Điền Ý Kiến
**Ai:** Ban chấp sự / Cố vấn / Ủy ban
**Vào:** Tab **"Ý kiến"** trên form nhiệm vụ

Điền:
- `opinion_deacon_board` → Ý kiến ban chấp sự
- `opinion_advisor` → Ý kiến cố vấn
- `opinion_pastor` → Ý kiến mục sư (điền sau khi duyệt)

Chuyển giai đoạn:
- Giai đoạn **Mục sư** (stage = 68) → Gửi để mục sư duyệt
- Giai đoạn **Tư vấn** (stage = 69) → Gửi cho hội thánh tham khảo

---

### Bước 5 — Gửi Email
**Ai:** Nhân viên
**Vào:** Form nhiệm vụ → Nhấn nút **"Send by Email"**

Hệ thống tự chọn mẫu email theo giai đoạn:

| Giai đoạn | Mẫu email | Gửi đến |
|---|---|---|
| Mục sư (stage = 68) | "Gửi để duyệt" | `approval_id` (mục sư) — kèm PDF |
| Tư vấn (stage = 69) | "Gửi tham khảo" | `partner_id` (hội thánh) — kèm 3 ý kiến |
| Giai đoạn khác | Mẫu chung | Người dùng chọn |

---

### Bước 6 — Mục Sư Duyệt Trên Portal
**Ai:** Người dùng `approval_id` (mục sư)
**Vào:** Link trong email → Trang portal

Hành động:
- Đọc tài liệu đính kèm
- Nhập ý kiến vào ô văn bản
- Nhấn **"Chấp nhận"** hoặc **"Từ chối"**

✅ **Chấp nhận:**
- `approval_state` = `approved`
- `opinion_pastor` = ý kiến đã nhập
- Tin nhắn ghi vào chatter

❌ **Từ chối:**
- `approval_state` = `rejected`
- `opinion_pastor` = lý do từ chối
- Quay lại Bước 4 để chỉnh sửa

---

## 3. Quy Trình Phiếu Chi / Thu

### Sơ đồ tổng quát
```
Tạo phiếu (Draft)
→ [Kế toán duyệt]
→ [Thủ quỹ duyệt]
→ [Kế toán gửi email lên mục sư]
→ Mục sư ký trên portal → Đã đăng ✓
→ PDF có 3 chữ ký
```

---

### Bước 1 — Tạo Phiếu Chi/Thu
**Ai:** Nhân viên kế toán
**Vào:** Kế toán → Thanh toán → Mới

Điền các thông tin:

| Field | Ý nghĩa | Bắt buộc |
|---|---|---|
| `partner_id` | Đối tác / Người nhận | ✓ |
| `amount` | Số tiền (VNĐ) | ✓ |
| `pay_currency_id` | Loại tiền tệ nước ngoài | Nếu có |
| `foreign_amount` | Số tiền ngoại tệ | Nếu có |
| `exchange_rate` | Tỷ giá quy đổi | Nếu có |
| `payment_type` | `outbound` = Chi / `inbound` = Thu | ✓ |
| `project_task_id` | Liên kết dự án | ✓ (chi thường) |
| `description` | Nội dung thanh toán | — |
| `benefactor_id` | Người thụ hưởng (`hr.employee`) | Nếu tạm ứng |
| `is_advance` | Có phải tạm ứng không | — |

Hệ thống tự động gán:
- `approval_id` = Mục sư
- `accountant_id` = Kế toán
- `treasurer_id` = Thủ quỹ
- `delivered_person` = Người giao tiền
- `received_person` = Người nhận tiền
- Số phiếu: `BN/PC-DD-MM-YYYY-XXX` (chi) hoặc `BN/PT-...` (thu)

---

### Bước 2 — Kế Toán Duyệt
**Ai:** Người dùng có `user_role = 'accountant'`
**Vào:** Form phiếu → Nhấn **"Approved by Accountant"**

Kiểm tra tự động:
- Nếu phiếu chi (`outbound`) + không phải tạm ứng + không phải chuyển khoản nội bộ → `project_task_id` **bắt buộc phải điền**

Kết quả:
- `approved_accountant = True`
- Trạng thái vẫn là `draft`

---

### Bước 3 — Thủ Quỹ Duyệt
**Ai:** Người dùng có `user_role = 'treasurer'`
**Vào:** Form phiếu → Nhấn **"Approved by Treasurer"**

Kiểm tra tự động: Tương tự Bước 2

Kết quả:
- `approved_treasurer = True`
- Trạng thái vẫn là `draft`

---

### Bước 4 — Gửi Lên Mục Sư Để Duyệt
**Ai:** Kế toán (`user_role = 'accountant'`)
**Vào:** Form phiếu → Nhấn **"Send to Approval"**

> ⚠️ Nút chỉ hiện khi:
> - `approved_accountant = True`
> - `approved_treasurer = True`
> - `state = 'draft'`
> - Người dùng hiện tại có `user_role = 'accountant'`

Hành động:
- Mở cửa sổ soạn email
- Gửi email đến `approval_id` (mục sư) kèm PDF phiếu
- Tiêu đề: `{Tên công ty} Payment Receipt (Ref {name_seq})`

---

### Bước 5 — Mục Sư Ký Duyệt Trên Portal
**Ai:** Người dùng `approval_id` (mục sư)
**Vào:** Link trong email → Trang portal `/my/account_payments/{id}`

Trang portal hiển thị:
- Thông tin phiếu chi/thu
- Số tiền
- Mã dự án liên quan
- Chữ ký kế toán & thủ quỹ

✅ **Chấp nhận & Ký:**
- Hệ thống ghi:
  - `signed_by` = tên mục sư
  - `signed_on` = thời điểm hiện tại
  - `signature` = ảnh `sign_signature` từ hồ sơ mục sư
- `action_post()` → `state = 'posted'` ✓
- Email xác nhận gửi về mục sư
- PDF cuối có **3 chữ ký**

❌ **Từ chối:**
- `action_cancel()` → `state = 'cancel'`
- Tin nhắn: "Phiếu bị từ chối bởi {tên}: {lý do}"
- Quay lại Bước 1 để tạo lại

---

### Bước 6 — Phiếu Đã Hoàn Tất (Posted)
Kết quả:
- Bút toán kế toán được ghi nhận
- Phiếu có thể tải PDF từ portal
- PDF hiển thị 3 chữ ký:

```
┌────────────────┬────────────────┬────────────────────┐
│    MỤC SƯ      │   KẾ TOÁN      │  THỦ QUỸ /         │
│  (approval_id) │ (accountant_id)│  NGƯỜI NHẬN TIỀN   │
│   chữ ký ảnh  │  chữ ký ảnh   │    chữ ký ảnh      │
└────────────────┴────────────────┴────────────────────┘
```

---

## 4. Quy Trình Thanh Toán Định Kỳ (Recurring Payments)

**Vào:** Kế toán → Thanh toán định kỳ

Các bước:

1. **Tạo mẫu định kỳ** (`account.recurring.template`)
   - `journal_id` → Sổ nhật ký
   - `recurring_period` → Chu kỳ (ngày/tuần/tháng/năm)
   - `recurring_interval` → Tần suất (ví dụ: mỗi 1 tháng)

2. **Tạo thanh toán định kỳ** (`recurring.payment`)
   - `partner_id` → Đối tác
   - `template_id` → Mẫu định kỳ đã tạo
   - `date_begin` / `date_end` → Thời gian áp dụng
   - `amount` → Số tiền mỗi kỳ

3. **Hệ thống tự tạo** `recurring.payment.line` cho từng kỳ
   - Mỗi dòng liên kết `payment_id` → `account.payment` thực tế

---

## 5. Theo Dõi Công Nợ Khách Hàng (Customer Follow-up)

**Vào:** Kế toán → Theo dõi công nợ

| Field | Ý nghĩa |
|---|---|
| `latest_followup_level_id` | Mức độ nhắc nợ hiện tại |
| `payment_amount_due` | Tổng số tiền còn nợ |
| `payment_amount_overdue` | Số tiền quá hạn |
| `payment_next_action_date` | Ngày hành động tiếp theo |
| `payment_responsible_id` | Người phụ trách thu hồi nợ |

Các mức nhắc nợ (`followup.line`) được cấu hình tại:
**Kế toán → Cấu hình → Mức nhắc nợ**

---

## 6. Giới Hạn Tín Dụng Khách Hàng

**Vào:** Cài đặt → Kế toán → Bật "Giới hạn tín dụng"

Sau đó vào từng khách hàng (`res.partner`):
- `amount_credit_limit` → Hạn mức tín dụng

Khi tạo hóa đơn / đơn hàng:
- Nếu `show_partner_credit_warning = True` → Hệ thống cảnh báo vượt hạn mức

---

## 7. Thông Báo Hoạt Động (Activity Notifications)

**Vào:** Cài đặt → Công ty → Tab thông báo hoạt động

Cấu hình:
- `activity_due_notification` → Bật thông báo khi đến hạn
- `ondue_date_notify` → Thông báo đúng ngày đến hạn
- `before_first_notify` → Thông báo trước N ngày (lần 1)
- `before_second_notify` → Thông báo trước N ngày (lần 2)
- `after_first_notify` → Thông báo sau N ngày quá hạn (lần 1)
- `after_second_notify` → Thông báo sau N ngày quá hạn (lần 2)

---

## 8. Năm Tài Chính & Khóa Sổ

**Vào:** Kế toán → Cấu hình → Năm tài chính

Tạo năm tài chính (`account.fiscal.year`):
- `date_from` / `date_to` → Ngày bắt đầu / kết thúc
- `company_id` → Công ty

Khóa sổ kế toán:
- `period_lock_date` → Khóa đến ngày (không được nhập bút toán trước ngày này)
- `fiscalyear_lock_date` → Khóa toàn bộ năm tài chính

---

## 9. Nhập Sao Kê Ngân Hàng

**Vào:** Kế toán → Sao kê ngân hàng → Nhập

Hỗ trợ file: CSV, Excel, OFX

Lưu ý:
- `unique_import_id` tự động sinh để tránh nhập trùng
- Cấu hình mẫu file nhập tại: Cài đặt → Kế toán → Mẫu nhập

---

## 10. Quản Lý Tài Sản Cố Định

**Vào:** Kế toán → Tài sản cố định

Tạo danh mục tài sản (`account.asset.category`):
- `account_asset_id` → TK nguyên giá
- `account_depreciation_id` → TK hao mòn lũy kế
- `account_depreciation_expense_id` → TK chi phí khấu hao
- `journal_id` → Sổ nhật ký
- `method` → Phương pháp khấu hao (đường thẳng / số dư giảm dần)
- `method_number` → Số kỳ khấu hao
- `method_period` → Số tháng mỗi kỳ

Khi mua tài sản:
- Trên dòng hóa đơn → chọn `asset_category_id`
- Hệ thống tự tạo tài sản và lịch khấu hao

---

## 11. Thông Tin Hội Thánh (contacts_custom)

**Vào:** Liên hệ → [chọn hội thánh] → Tab "HT Information"

| Field | Ý nghĩa |
|---|---|
| `is_foreign` | Hội thánh nước ngoài |
| `total_this_year` | Tổng số tín hữu năm nay |
| `total_last_year` | Tổng số tín hữu năm ngoái |
| `total_last_two_year` | Tổng số tín hữu 2 năm trước |
| `meet_this_year` | Số người nhóm đều năm nay |
| `meet_last_year` | Số người nhóm đều năm ngoái |
| `meet_last_two_year` | Số người nhóm đều 2 năm trước |

---

## Tóm Tắt Nhanh

| Tình huống | Quy trình |
|---|---|
| Xây dựng / sửa chữa nhà thờ | Workflow 2 — Dự án |
| Chi tiền cho công trình | Workflow 3 — Phiếu chi |
| Thu dâng hiến / hỗ trợ | Workflow 3 — Phiếu thu |
| Thanh toán hàng tháng cố định | Mục 4 — Recurring Payments |
| Theo dõi nợ chưa thanh toán | Mục 5 — Follow-up |
| Kiểm soát hạn mức mua chịu | Mục 6 — Credit Limit |
| Nhắc nhở công việc đến hạn | Mục 7 — Activity Notifications |
| Đóng sổ cuối năm | Mục 8 — Fiscal Year |
