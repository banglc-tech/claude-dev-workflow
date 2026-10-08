# CLAUDE.md — thư mục chung <tên dự án>

> Thư mục này không phải repo git; nó chứa nhiều repo con. Mở Claude Code tại đây, không mở trong repo con.
> File này chỉ chứa phần RIÊNG của dự án. Quy trình chung được nạp từ dòng @ ở cuối file.
> Repo con có CLAUDE.md riêng thì Claude đọc thêm khi làm việc trong repo đó.

## Các repo trong thư mục

<<BANG_REPO>>

- Mỗi task trên Base thuộc một repo, ghi ở trường Repo. Trường trống thì suy từ đặc tả và bảng trên; vẫn không chắc thì gọi `decider`.
- Repo không có trong bảng: không sửa.

## Dự án
- Sản phẩm: <tên sản phẩm / khách hàng>
- Base dự án trên Lark: `<tên Base>` (Tasks, Bugs, Decisions); repo deploy: `<tên repo>`
- Cách các repo nói chuyện với nhau: <API, hàng đợi, thư viện dùng chung...>

## Quy ước code chung
- <quy ước áp dụng cho mọi repo; quy ước riêng của repo nào ghi trong CLAUDE.md của repo đó>
- Giao diện dùng component của iHouzz Design System, không tự tạo component khi đã có.

## Bài học (thêm khi phải sửa Claude cùng một lỗi lần thứ hai)
- <ngày> — <quy tắc>

## Quy trình làm việc với Claude (do bộ claude-dev-workflow quản lý, không sửa tại đây)
@docs/claude-workflow/CLAUDE-QUY-TRINH.md
