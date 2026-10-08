---
description: Review tự động một MR theo rule của team; chỉ tự cho qua khi mọi vấn đề đều ở mức Gợi ý
argument-hint: <số MR>
---

Review MR !$ARGUMENTS theo `QUY-TRINH-MERGE.md` mục 8. Bạn chỉ đọc, chạy test và viết nhận xét; không sửa code, không approve, không merge.

## Bước 1: Kiểm tra hình thức
1. Lấy thông tin MR: `glab mr view $ARGUMENTS -F json` → nhánh nguồn, tiêu đề, mô tả, nhãn, số dòng thay đổi.
2. Ghi mô tả ra file tạm rồi chạy `scripts/check-mr.sh <nhánh> "<tiêu đề>" <file mô tả> "<nhãn>"`.
3. Script trả CHẶN → gọi `decider` (sự cố: check-mr chặn). Dòng ĐÃ QUYẾT thì sửa theo (đổi tên nhánh, sửa tiêu đề hoặc mô tả MR, gắn nhãn) và chạy lại script; vẫn chặn hoặc HỎI NGƯỜI thì đăng các dòng CHẶN thành comment trên MR, kết luận **CHẶN – hình thức** và dừng. Không review nội dung khi hình thức chưa đạt.

## Bước 2: Review nội dung
Checkout nhánh nguồn, gọi sub agent `reviewer` với diff `origin/dev...HEAD` và task liên kết. Ngoài checklist của reviewer, kiểm thêm:
- Tiêu chí đạt nào trong task chưa có test tương ứng.
- Mức MR người mở đã chọn có đúng không: diff đụng migration, thư viện mới, `src/auth`, `src/payment`, API dùng chung → phải là Rủi ro cao; đụng file hạ tầng → Hạ tầng. Chọn thấp hơn thực tế là **Chặn**.
- Mô tả "Đã làm" có khớp với diff không; diff làm nhiều hơn mô tả là **Nên sửa**.

## Bước 3: Phân loại và kết luận
Mỗi vấn đề ghi đúng một mức theo bảng trong `QUY-TRINH-MERGE.md` mục 8. Khi phân vân giữa hai mức, chọn mức cao hơn.

| Kết quả | Khi nào | Làm gì |
| --- | --- | --- |
| **QUA** | Không có vấn đề nào, hoặc chỉ có mức **Gợi ý** | Comment "Review tự động: QUA" kèm danh sách gợi ý (nếu có), gắn nhãn `review::qua`. Người review chỉ cần xác nhận và merge. |
| **CẦN NGƯỜI XEM** | Có ít nhất một vấn đề mức **Nên sửa** | Comment từng vấn đề (file:dòng, lý do, cách sửa), gắn nhãn `review::can-xem`. Người review quyết sửa trong MR này hay tạo task mới trên Base. |
| **CHẶN** | Có ít nhất một vấn đề mức **Chặn**, hoặc test/lint fail | Comment từng vấn đề, nêu rõ tiêu chí đạt hoặc rule bị vi phạm, gắn nhãn `review::chan`. Người mở MR phải sửa và đẩy lại. |

## Rule
- Không bao giờ kết luận QUA khi có vấn đề mức Nên sửa trở lên, dù chỉ một.
- Không approve MR, không merge, không sửa code sản phẩm. Trên GitLab chỉ được: comment, đổi nhãn, và sửa tiêu đề / mô tả / tên nhánh khi decider đã quyết để qua kiểm tra hình thức.
- Mỗi vấn đề một comment, đặt đúng dòng trong diff. Comment tổng kết đặt cuối, theo mẫu: kết luận · số vấn đề theo mức · lệnh test đã chạy và kết quả · thời gian review.
- Chạy lại khi có commit mới: xóa nhãn `review::*` cũ trước khi gắn nhãn mới.
- Không bình luận về phong cách nếu lint đã pass; đó không phải vấn đề.
