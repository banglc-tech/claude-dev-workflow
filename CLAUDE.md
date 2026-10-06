# CLAUDE.md — Sales Zone · Bluemarq

> Chủ sở hữu file: Bằng (Tech Lead). Mọi thay đổi đi qua MR do Bằng duyệt.
> Phần trong <> là chỗ cần điền theo repo thật.

## Dự án
- Sản phẩm: Sales Zone cho Bluemarq.
- Stack: <ngôn ngữ, framework, DB>
- Cấu trúc thư mục chính: <src/..., tests/...>
- Lệnh:
  - Cài đặt: `<lệnh>`
  - Chạy Dev: `<lệnh>` (Docker Compose)
  - Test: `<lệnh>`
  - Lint / type check: `<lệnh>`

## Đầu vào
- Task, lỗi, câu hỏi và trạng thái nằm trên Lark Base `BLUEMARQ` (bảng Tasks, Bugs, Decisions); đặc tả là Lark Docs link từ task. Đọc qua MCP `lark-ihouzz`, theo `DAU-VAO-LARK-BASE.md`. Không nhận yêu cầu qua chat.
- Có câu hỏi nghiệp vụ hoặc rủi ro cao: comment lên đặc tả + tạo ticket Decisions + ghi Ghi chú Claude, rồi dừng. Không đoán.
- Trên Lark chỉ được: tạo bản ghi Decisions, cập nhật Trạng thái / Nhánh / MR / Ghi chú Claude, tạo comment. Không xóa, không sửa tài liệu, không gửi tin nhắn.

## Quy trình bắt buộc
- Tính năng: `/feature <Mã task>`. Lỗi: `/bugfix <Mã lỗi>`. Mã lấy từ trường Mã trên Base.
- Quy trình bị vướng ở đâu (câu hỏi mở, thiếu đầu vào, test fail 3 lần, reviewer chặn, check-mr chặn, pipeline đỏ, conflict): gọi `decider` (model fable) trước, không dừng ngay. decider quyết khi có căn cứ và hoàn tác được, ghi vào bảng Quyết định Claude để Bằng xem; không quyết được mới tạo ticket Decisions hỏi Bằng (nghiệp vụ: BA).
- Lập kế hoạch trước, code sau. Dừng lại chờ dev duyệt kế hoạch hoặc nguyên nhân gốc.
- Nhánh: `feature/<số issue>-<tên ngắn>` hoặc `fix/<số issue>-<tên ngắn>`, tạo từ `dev`.
- Commit: `<loại>(#<Mã>): <mô tả>`, ví dụ `feat(#123): giữ chỗ căn hộ`; commit dở dùng `wip(#<Mã>): …`.
- Push nhánh feature/fix lên GitLab sau mỗi bước có commit và trước khi kết thúc lượt chạy; mỗi nhánh phải có push ít nhất một lần mỗi ngày trước 17:00.
- MR: tiêu đề `[<tính năng>] <việc> (#<số issue>)`, nhãn `feature::<tính năng>` hoặc `bug`, dùng MR template.
- Review MR: `/mr-review <số MR>`. Chỉ kết luận QUA khi mọi vấn đề ở mức Gợi ý; không approve, không merge.
- Chỉ con người được merge, theo `QUY-TRINH-MERGE.md`: squash merge, người duyệt bấm merge, MR mức Rủi ro cao cần Tech Lead. Claude không push lên `dev`, không merge.

## Vùng cấm
- Không sửa: Jenkinsfile, Dockerfile, docker-compose*, cấu hình Kubernetes, repo `bluemarq-deploy`, `.env*`.
- Không đọc hay in secret. Không trỏ vào Staging hoặc Production.
- Không thêm thư viện nếu kế hoạch đã duyệt chưa ghi.
- Migration: chỉ khi kế hoạch có ghi, phải chạy ngược lại được, chỉ chạy trên Dev.

## Quy ước code
- <đặt tên, cấu trúc module, xử lý lỗi, log, i18n...>
- Giao diện dùng component của iHouzz Design System, không tự tạo component khi đã có.

## Test
- Mỗi tiêu chí đạt có ít nhất một test, tên test ghi mã tiêu chí (`TC2: ...`).
- Mock dịch vụ ngoài bằng <công cụ>. Không gọi dịch vụ thật trong test.
- Không xóa, skip hay nới lỏng test có sẵn để cho pass.

## Bài học (thêm khi phải sửa Claude cùng một lỗi lần thứ hai)
- <ngày> — <quy tắc>
