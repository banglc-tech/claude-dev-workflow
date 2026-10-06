---
description: Làm một issue tính năng theo quy trình của team (kế hoạch → test → code → review)
argument-hint: <số issue>
---

Làm issue tính năng #$ARGUMENTS theo đúng thứ tự dưới đây. Bạn là agent chính: điều phối các sub agent và là nơi duy nhất thao tác git.

1. Đọc task có **Mã = $ARGUMENTS** trong bảng Tasks của Base `BLUEMARQ` qua MCP `lark-ihouzz` (xem `DAU-VAO-LARK-BASE.md`). Kiểm tra đủ: Spec liên kết, Trạng thái đặc tả = Đã duyệt, Link thiết kế, Tiêu chí đạt, MD ước tính ≤ 1. Đọc đặc tả bằng `docx-get-raw-content`. Đọc bảng Decisions lọc theo task: còn ticket Chưa chốt thì DỪNG, báo đang chờ ai. Thiếu gì thì gọi `decider` (sự cố: thiếu đầu vào) trước khi dừng. Đủ thì đổi Trạng thái task sang Đang làm.
2. Tạo nhánh `feature/$ARGUMENTS-<tên ngắn>` từ `dev` mới nhất.
3. Gọi sub agent `planner`. Trình kế hoạch cho dev rồi DỪNG, chờ dev trả lời "Duyệt, làm tiếp", "Sửa kế hoạch: ..." hoặc "Dừng".
4. Sau khi kế hoạch được duyệt: gọi `test-writer`. Kiểm tra test fail đúng chỗ.
5. Gọi `implementer` với kế hoạch đã duyệt. Khi test pass, commit theo quy ước trong CLAUDE.md và push nhánh feature lên GitLab (`git push -u origin <nhánh>`). Chưa xong mà hết lượt thì vẫn commit `wip(#$ARGUMENTS): …` và push.
6. Gọi `reviewer`. Còn vấn đề mức Chặn thì giao lại `implementer` sửa, rồi review lại (tối đa 2 vòng, sau đó gọi `decider` với sự cố: reviewer chặn).
7. Tóm tắt cho dev: đã làm gì, kết quả test, báo cáo reviewer, câu hỏi còn mở.
8. CHỈ khi dev bảo "mở MR": push nhánh và mở MR theo template (dòng `Base: <link task>`), gắn nhãn; điền link MR vào trường Nhánh / MR và đổi Trạng thái task sang Chờ duyệt. Không bao giờ merge.

Nếu đang chạy qua đêm (không có dev trả lời): chỉ làm khi kế hoạch đã được duyệt sẵn trong issue, đi từ bước 4 đến bước 7, rồi push nhánh feature (kể cả commit wip) và ghi tóm tắt kèm link commit cuối vào trường Ghi chú Claude của task. Không mở MR.

## Khi quy trình bị vướng: luôn qua decider trước
Bất kỳ lúc nào một bước không đi tiếp được (sub agent nêu câu hỏi mở, thiếu đầu vào trên Base, test fail 3 lần, reviewer CHẶN sau 2 vòng, `check-mr.sh` chặn, pipeline đỏ, conflict với `dev`, kế hoạch vượt 1 ngày…), KHÔNG dừng ngay và KHÔNG hỏi dev ngay. Gọi sub agent `decider` với loại sự cố và báo cáo liên quan:
- Dòng **ĐÃ QUYẾT**: thực thi đúng quyết định, ghi nối vào `.bangiao/$ARGUMENTS/00-quyet-dinh.md`, tạo bản ghi trong bảng *Quyết định Claude* trên Base (Task, Sự cố, Quyết định, Căn cứ, Hoàn tác bằng, Trạng thái = Chưa xem) để Bằng xem lại, rồi đi tiếp.
- Dòng **HỎI BẰNG**: làm ba việc theo `DAU-VAO-LARK-BASE.md` mục 4 (comment lên đặc tả nếu là câu hỏi về đặc tả; tạo ticket Decisions với Người quyết như decider ghi, mặc định là Bằng; ghi `Chờ Decisions <mã>` vào Ghi chú Claude và đổi Trạng thái task sang Chờ quyết định), rồi DỪNG. Việc không bị chặn thì vẫn làm tiếp.
- Cùng một sự cố tái diễn sau khi decider đã quyết thì không gọi decider lần hai; tạo ticket cho Bằng ngay.
decider không thay thế hai điểm dev duyệt (kế hoạch, nguyên nhân gốc). Khi tóm tắt cho dev, liệt kê mọi quyết định decider đã đưa ra trong lần chạy này.
## Sổ bàn giao
Mỗi issue có một thư mục `.bangiao/$ARGUMENTS/` (đã có trong .gitignore), gồm `00-quyet-dinh.md` (decider, ghi nối) và các file dưới đây. Sau mỗi sub agent, lưu nguyên văn báo cáo vào đúng file, và giao cho sub agent sau đọc file của bước trước:
- `01-ke-hoach.md` (planner, kèm dòng "Dev duyệt: <tên>, <ngày>")
- `02-test.md` (test-writer)
- `03-thay-doi.md` (implementer)
- `04-danh-gia.md` (reviewer, kết luận CHỐT / CẦN SỬA / CHẶN)
Bắt đầu issue mới thì không dùng lại sổ của issue khác.
