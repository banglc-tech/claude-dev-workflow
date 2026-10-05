---
description: Làm một issue tính năng theo quy trình của team (kế hoạch → test → code → review)
argument-hint: <số issue>
---

Làm issue tính năng #$ARGUMENTS theo đúng thứ tự dưới đây. Bạn là agent chính: điều phối các sub agent và là nơi duy nhất thao tác git.

1. Đọc issue #$ARGUMENTS trên GitLab (dùng `glab issue view $ARGUMENTS` nếu có). Kiểm tra đủ: link đặc tả đã duyệt, link thiết kế đã duyệt, tiêu chí đạt, ước lượng không quá 1 ngày. Thiếu thì DỪNG và liệt kê những gì còn thiếu.
2. Tạo nhánh `feature/$ARGUMENTS-<tên ngắn>` từ `dev` mới nhất.
3. Gọi sub agent `planner`. Trình kế hoạch cho dev rồi DỪNG, chờ dev trả lời "Duyệt, làm tiếp", "Sửa kế hoạch: ..." hoặc "Dừng".
4. Sau khi kế hoạch được duyệt: gọi `test-writer`. Kiểm tra test fail đúng chỗ.
5. Gọi `implementer` với kế hoạch đã duyệt. Khi test pass, commit theo quy ước trong CLAUDE.md.
6. Gọi `reviewer`. Còn vấn đề mức Chặn thì giao lại `implementer` sửa, rồi review lại (tối đa 2 vòng, sau đó dừng và báo dev).
7. Tóm tắt cho dev: đã làm gì, kết quả test, báo cáo reviewer, câu hỏi còn mở.
8. CHỈ khi dev bảo "mở MR": push nhánh và mở MR theo template, gắn nhãn, liên kết issue. Không bao giờ merge.

Nếu đang chạy qua đêm (không có dev trả lời): chỉ làm khi kế hoạch đã được duyệt sẵn trong issue, đi từ bước 4 đến bước 7, rồi ghi tóm tắt vào comment của issue. Không push, không mở MR.

## Khi có câu hỏi còn mở
Báo cáo của bất kỳ sub agent nào có câu hỏi còn mở thì gọi sub agent `decider` trước khi dừng:
- decider kết luận "Tiếp tục được": áp dụng quyết định, ghi vào `00-quyet-dinh.md`, rồi đi tiếp.
- decider kết luận "Phải dừng": DỪNG, chuyển câu hỏi cho đúng người (BA, PM, Bằng hoặc anh Huy) như decider đã ghi.
decider không thay thế bước dev duyệt kế hoạch hay nguyên nhân gốc. Khi tóm tắt cho dev, luôn liệt kê các quyết định decider đã đưa ra để dev xem lại.

## Sổ bàn giao
Mỗi issue có một thư mục `.bangiao/$ARGUMENTS/` (đã có trong .gitignore), gồm `00-quyet-dinh.md` (decider, ghi nối) và các file dưới đây. Sau mỗi sub agent, lưu nguyên văn báo cáo vào đúng file, và giao cho sub agent sau đọc file của bước trước:
- `01-ke-hoach.md` (planner, kèm dòng "Dev duyệt: <tên>, <ngày>")
- `02-test.md` (test-writer)
- `03-thay-doi.md` (implementer)
- `04-danh-gia.md` (reviewer, kết luận CHỐT / CẦN SỬA / CHẶN)
Bắt đầu issue mới thì không dùng lại sổ của issue khác.
