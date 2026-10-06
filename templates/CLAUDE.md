# CLAUDE.md — <tên dự án>

> Chủ sở hữu file: Tech Lead. Mọi thay đổi đi qua MR do Tech Lead duyệt.
> File này chỉ chứa phần RIÊNG của repo. Quy trình chung (đầu vào Lark Base, /feature, /bugfix,
> decider, merge, vùng cấm) được nạp từ dòng @ ở cuối file, không chép lại vào đây.

## Dự án
- Sản phẩm: <tên sản phẩm / khách hàng>
- Stack: <ngôn ngữ, framework, DB>
- Cấu trúc thư mục chính: <src/..., tests/...>
- Lệnh:
  - Cài đặt: `<lệnh>`
  - Chạy Dev: `<lệnh>`
  - Test: `<lệnh>`
  - Lint / type check: `<lệnh>`

## Quy ước code
- <đặt tên, cấu trúc module, xử lý lỗi, log, i18n...; repo lớn thì viết docs/CONVENTION-AI.md và trỏ tới đây>
- Giao diện dùng component của iHouzz Design System, không tự tạo component khi đã có.
- Mock dịch vụ ngoài trong test bằng <công cụ>.

## Vùng cấm riêng của repo
- <thư mục / file không được sửa, nếu có>

## Bài học (thêm khi phải sửa Claude cùng một lỗi lần thứ hai)
- <ngày> — <quy tắc>

## Quy trình làm việc với Claude (do bộ claude-dev-workflow quản lý, không sửa tại đây)
@docs/claude-workflow/CLAUDE-QUY-TRINH.md
