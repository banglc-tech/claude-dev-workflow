---
description: Sửa một issue lỗi theo quy trình của team (tái hiện → nguyên nhân gốc → sửa → review)
argument-hint: <số issue>
---

Sửa lỗi #$ARGUMENTS theo đúng thứ tự dưới đây. Bạn là agent chính: điều phối các sub agent và là nơi duy nhất thao tác git.

1. Đọc lỗi có **Mã = $ARGUMENTS** trong bảng Bugs của Base `BLUEMARQ-ONE` qua MCP `lark-ihouzz` (xem `DAU-VAO-LARK-BASE.md`). Kiểm tra đủ: Bước tái hiện, Kết quả mong đợi, Kết quả thực tế, Tiêu chí bị vi phạm, Mức độ. Đọc đặc tả của Task liên kết bằng `docx-get-raw-content`. Thiếu gì thì ghi "Thiếu: …" vào Ghi chú Claude, đổi Trạng thái về Mới và DỪNG để Test bổ sung. Đủ thì đổi Trạng thái sang Đang sửa.
2. Mức độ Nghiêm trọng: báo dev, chỉ làm khi dev đang theo dõi trực tiếp.
3. Tạo nhánh `fix/$ARGUMENTS-<tên ngắn>` từ `dev` mới nhất. Môi trường = Production thì DỪNG và nhắc dev làm theo mục hotfix trong tài liệu Quy trình quản lý source Git & deploy.
4. Gọi sub agent `bug-investigator`. Trình nguyên nhân gốc và cách sửa cho dev rồi DỪNG, chờ dev duyệt.
5. Gọi `implementer`: sửa nhỏ nhất, test tái hiện pass, toàn bộ test cũ vẫn pass. Commit theo quy ước.
6. Gọi `reviewer`. Còn vấn đề mức Chặn thì giao lại `implementer` (tối đa 2 vòng).
7. Tóm tắt cho dev: nguyên nhân, cách sửa, kết quả test, chỗ khác có cùng nguyên nhân.
8. CHỈ khi dev bảo "mở MR": push nhánh và mở MR có nhãn `bug`, dòng `Base: <link bản ghi lỗi>`; điền link MR vào Nhánh / MR. Trạng thái lỗi đổi sang Chờ test sau khi người review merge. Không bao giờ merge.

## Khi có câu hỏi còn mở
Báo cáo của bất kỳ sub agent nào có câu hỏi còn mở thì gọi sub agent `decider` trước khi dừng:
- decider kết luận "Tiếp tục được": áp dụng quyết định, ghi vào `00-quyet-dinh.md`, rồi đi tiếp.
- decider kết luận "Phải dừng": với mỗi câu hỏi loại Nghiệp vụ hoặc Rủi ro cao, làm đủ ba việc theo `DAU-VAO-LARK-BASE.md` mục 4 rồi mới DỪNG: (1) comment lên đặc tả bằng `drive-create-comment`; (2) tạo bản ghi Decisions (kiểm tra trùng trước); (3) ghi `Chờ Decisions <mã>` vào Ghi chú Claude của lỗi. Câu hỏi về dữ liệu tái hiện thì không tạo ticket, chỉ ghi Ghi chú Claude và đổi Trạng thái về Mới cho Test.
decider không thay thế bước dev duyệt kế hoạch hay nguyên nhân gốc. Khi tóm tắt cho dev, luôn liệt kê các quyết định decider đã đưa ra để dev xem lại.

## Sổ bàn giao
Mỗi issue có một thư mục `.bangiao/$ARGUMENTS/` (đã có trong .gitignore), gồm `00-quyet-dinh.md` (decider, ghi nối) và các file dưới đây. Sau mỗi sub agent, lưu nguyên văn báo cáo vào đúng file, và giao cho sub agent sau đọc file của bước trước:
- `01-dieu-tra.md` (bug-investigator, kèm dòng "Dev duyệt: <tên>, <ngày>")
- `02-thay-doi.md` (implementer)
- `03-danh-gia.md` (reviewer, kết luận CHỐT / CẦN SỬA / CHẶN)
Bắt đầu issue mới thì không dùng lại sổ của issue khác.
