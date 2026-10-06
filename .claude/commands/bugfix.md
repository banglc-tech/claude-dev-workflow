---
description: Sửa một issue lỗi theo quy trình của team (tái hiện → nguyên nhân gốc → sửa → review)
argument-hint: <số issue>
---

Sửa lỗi #$ARGUMENTS theo đúng thứ tự dưới đây. Bạn là agent chính: điều phối các sub agent và là nơi duy nhất thao tác git.

1. Đọc lỗi có **Mã = $ARGUMENTS** trong bảng Bugs của Base `BLUEMARQ-ONE` qua MCP `lark-ihouzz` (xem `DAU-VAO-LARK-BASE.md`). Kiểm tra đủ: Bước tái hiện, Kết quả mong đợi, Kết quả thực tế, Tiêu chí bị vi phạm, Mức độ. Đọc đặc tả của Task liên kết bằng `docx-get-raw-content`. Thiếu gì thì gọi `decider` (sự cố: thiếu đầu vào) trước khi dừng. Đủ thì đổi Trạng thái sang Đang sửa.
2. Mức độ Nghiêm trọng: báo dev, chỉ làm khi dev đang theo dõi trực tiếp.
3. Tạo nhánh `fix/$ARGUMENTS-<tên ngắn>` từ `dev` mới nhất. Môi trường = Production thì DỪNG và nhắc dev làm theo mục hotfix trong tài liệu Quy trình quản lý source Git & deploy.
4. Gọi sub agent `bug-investigator`. Trình nguyên nhân gốc và cách sửa cho dev rồi DỪNG, chờ dev duyệt.
5. Gọi `implementer`: sửa nhỏ nhất, test tái hiện pass, toàn bộ test cũ vẫn pass. Commit theo quy ước và push nhánh fix lên GitLab. Chưa xong mà hết lượt thì commit `wip(#$ARGUMENTS): …` và push.
6. Gọi `reviewer`. Còn vấn đề mức Chặn thì giao lại `implementer` (tối đa 2 vòng, sau đó gọi `decider` với sự cố: reviewer chặn).
7. Tóm tắt cho dev: nguyên nhân, cách sửa, kết quả test, chỗ khác có cùng nguyên nhân.
8. CHỈ khi dev bảo "mở MR": push nhánh và mở MR có nhãn `bug`, dòng `Base: <link bản ghi lỗi>`; điền link MR vào Nhánh / MR. Trạng thái lỗi đổi sang Chờ test sau khi người review merge. Không bao giờ merge.

## Khi quy trình bị vướng: luôn qua decider trước
Bất kỳ lúc nào một bước không đi tiếp được (sub agent nêu câu hỏi mở, thiếu đầu vào trên Base, test fail 3 lần, reviewer CHẶN sau 2 vòng, `check-mr.sh` chặn, pipeline đỏ, conflict với `dev`, kế hoạch vượt 1 ngày…), KHÔNG dừng ngay và KHÔNG hỏi dev ngay. Gọi sub agent `decider` với loại sự cố và báo cáo liên quan:
- Dòng **ĐÃ QUYẾT**: thực thi đúng quyết định, ghi nối vào `.bangiao/$ARGUMENTS/00-quyet-dinh.md`, tạo bản ghi trong bảng *Quyết định Claude* trên Base (Task, Sự cố, Quyết định, Căn cứ, Hoàn tác bằng, Trạng thái = Chưa xem) để Bằng xem lại, rồi đi tiếp.
- Dòng **HỎI BẰNG**: làm ba việc theo `DAU-VAO-LARK-BASE.md` mục 4 (comment lên đặc tả nếu là câu hỏi về đặc tả; tạo ticket Decisions với Người quyết như decider ghi, mặc định là Bằng; ghi `Chờ Decisions <mã>` vào Ghi chú Claude và đổi Trạng thái task sang Chờ quyết định), rồi DỪNG. Việc không bị chặn thì vẫn làm tiếp.
- Cùng một sự cố tái diễn sau khi decider đã quyết thì không gọi decider lần hai; tạo ticket cho Bằng ngay.
decider không thay thế hai điểm dev duyệt (kế hoạch, nguyên nhân gốc). Khi tóm tắt cho dev, liệt kê mọi quyết định decider đã đưa ra trong lần chạy này.
## Sổ bàn giao
Mỗi issue có một thư mục `.bangiao/$ARGUMENTS/` (đã có trong .gitignore), gồm `00-quyet-dinh.md` (decider, ghi nối) và các file dưới đây. Sau mỗi sub agent, lưu nguyên văn báo cáo vào đúng file, và giao cho sub agent sau đọc file của bước trước:
- `01-dieu-tra.md` (bug-investigator, kèm dòng "Dev duyệt: <tên>, <ngày>")
- `02-thay-doi.md` (implementer)
- `03-danh-gia.md` (reviewer, kết luận CHỐT / CẦN SỬA / CHẶN)
Bắt đầu issue mới thì không dùng lại sổ của issue khác.
