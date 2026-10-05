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

## Quy trình bắt buộc
- Tính năng: `/feature <số issue>`. Lỗi: `/bugfix <số issue>`.
- Câu hỏi còn mở: gọi `decider` (model fable). Chỉ câu hỏi kỹ thuật trong phạm vi được tự quyết; nghiệp vụ hỏi BA, rủi ro cao hỏi Tech Lead.
- Lập kế hoạch trước, code sau. Dừng lại chờ dev duyệt kế hoạch hoặc nguyên nhân gốc.
- Nhánh: `feature/<số issue>-<tên ngắn>` hoặc `fix/<số issue>-<tên ngắn>`, tạo từ `dev`.
- Commit: `<loại>(#<số issue>): <mô tả>`, ví dụ `feat(#123): giữ chỗ căn hộ`.
- MR: tiêu đề `[<tính năng>] <việc> (#<số issue>)`, nhãn `feature::<tính năng>` hoặc `bug`, dùng MR template.
- Chỉ con người được merge. Claude không push lên `dev`, không merge.

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
