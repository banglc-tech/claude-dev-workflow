---
description: Sửa một issue lỗi theo quy trình của team (tái hiện → nguyên nhân gốc → sửa → review)
argument-hint: <số issue>
---

Sửa lỗi #$ARGUMENTS theo đúng thứ tự dưới đây. Bạn là agent chính: điều phối các sub agent và là nơi duy nhất thao tác git.

1. Đọc issue #$ARGUMENTS. Kiểm tra đủ: bước tái hiện, kết quả mong đợi, tiêu chí bị vi phạm, mức độ. Thiếu thì DỪNG và liệt kê những gì cần hỏi Test.
2. Mức độ Nghiêm trọng: báo dev, chỉ làm khi dev đang theo dõi trực tiếp.
3. Tạo nhánh `fix/$ARGUMENTS-<tên ngắn>` từ `dev` mới nhất. Lỗi trên Production thì DỪNG và nhắc dev làm theo mục hotfix trong tài liệu Quy trình quản lý source Git & deploy.
4. Gọi sub agent `bug-investigator`. Trình nguyên nhân gốc và cách sửa cho dev rồi DỪNG, chờ dev duyệt.
5. Gọi `implementer`: sửa nhỏ nhất, test tái hiện pass, toàn bộ test cũ vẫn pass. Commit theo quy ước.
6. Gọi `reviewer`. Còn vấn đề mức Chặn thì giao lại `implementer` (tối đa 2 vòng).
7. Tóm tắt cho dev: nguyên nhân, cách sửa, kết quả test, chỗ khác có cùng nguyên nhân.
8. CHỈ khi dev bảo "mở MR": push nhánh và mở MR có nhãn `bug`, ghi `Closes #$ARGUMENTS`. Không bao giờ merge.

## Khi có câu hỏi còn mở
Báo cáo của bất kỳ sub agent nào có câu hỏi còn mở thì gọi sub agent `decider` trước khi dừng:
- decider kết luận "Tiếp tục được": áp dụng quyết định, ghi vào `00-quyet-dinh.md`, rồi đi tiếp.
- decider kết luận "Phải dừng": DỪNG, chuyển câu hỏi cho đúng người (BA, PM, Bằng hoặc anh Huy) như decider đã ghi.
decider không thay thế bước dev duyệt kế hoạch hay nguyên nhân gốc. Khi tóm tắt cho dev, luôn liệt kê các quyết định decider đã đưa ra để dev xem lại.

## Sổ bàn giao
Mỗi issue có một thư mục `.bangiao/$ARGUMENTS/` (đã có trong .gitignore), gồm `00-quyet-dinh.md` (decider, ghi nối) và các file dưới đây. Sau mỗi sub agent, lưu nguyên văn báo cáo vào đúng file, và giao cho sub agent sau đọc file của bước trước:
- `01-dieu-tra.md` (bug-investigator, kèm dòng "Dev duyệt: <tên>, <ngày>")
- `02-thay-doi.md` (implementer)
- `03-danh-gia.md` (reviewer, kết luận CHỐT / CẦN SỬA / CHẶN)
Bắt đầu issue mới thì không dùng lại sổ của issue khác.
