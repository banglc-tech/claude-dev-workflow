# Quy trình làm việc với Claude (dùng chung mọi repo)

> File này do bộ claude-dev-workflow quản lý và được nạp từ CLAUDE.md của repo dự án.
> Không sửa trực tiếp trong repo dự án: sửa ở repo claude-dev-workflow rồi chạy lại `scripts/cai-dat.py`.
> Áp dụng cho mọi dev iHouzz giao việc cho Claude Code. Phần riêng của từng dự án (tên Base, repo deploy, stack, lệnh, quy ước code) nằm trong CLAUDE.md của dự án đó.

## Đầu vào
- Task, lỗi, câu hỏi và trạng thái nằm trên Lark Base của dự án (tên ghi trong CLAUDE.md; bảng Tasks, Bugs, Decisions); Base là nơi duy nhất giữ trạng thái, không dùng issue GitLab; đặc tả là Lark Docs link từ task. Đọc qua MCP Lark đã kết nối trên máy (các tool `lark-api-ihouzz-*`, tên server tùy máy), theo `DAU-VAO-LARK-BASE.md`. Không nhận yêu cầu qua chat.
- Có câu hỏi nghiệp vụ hoặc rủi ro cao: comment lên đặc tả + tạo ticket Decisions + ghi Ghi chú Claude, rồi dừng. Không đoán.
- Trên Lark chỉ được: tạo bản ghi Decisions, cập nhật Trạng thái / Nhánh / MR / Ghi chú Claude, tạo comment. Không xóa, không sửa tài liệu, không gửi tin nhắn.

## Quy trình bắt buộc
- Tính năng: `/feature <Mã task>`. Lỗi: `/bugfix <Mã lỗi>`. Mã lấy từ trường Mã trên Base.
- Quy trình bị vướng ở đâu (câu hỏi mở, thiếu đầu vào, test fail 3 lần, reviewer chặn, check-mr chặn, pipeline đỏ, conflict): gọi `decider` (model fable) trước, không dừng ngay. decider quyết khi có căn cứ và hoàn tác được, ghi vào bảng Quyết định Claude để Tech Lead xem; không quyết được mới tạo ticket Decisions hỏi Tech Lead (nghiệp vụ: BA).
- Lập kế hoạch trước, code sau. Dừng lại chờ dev duyệt kế hoạch hoặc nguyên nhân gốc.
- Nhánh: `feature/<Mã>-<tên ngắn>` hoặc `fix/<Mã>-<tên ngắn>`, tạo từ `dev`.
- Commit: `<loại>(#<Mã>): <mô tả>`, ví dụ `feat(#123): giữ chỗ căn hộ`; commit dở dùng `wip(#<Mã>): …`.
- Push nhánh feature/fix lên GitLab sau mỗi bước có commit và trước khi kết thúc lượt chạy; mỗi nhánh phải có push ít nhất một lần mỗi ngày trước 17:00.
- MR: tiêu đề `[<tính năng>] <việc> (#<Mã>)`, nhãn `feature::<tính năng>` hoặc `bug`, dùng MR template.
- Review MR: `/mr-review <số MR>`. Chỉ kết luận QUA khi mọi vấn đề ở mức Gợi ý; không approve, không merge.
- Chỉ con người được merge, theo `QUY-TRINH-MERGE.md`: squash merge, người duyệt bấm merge, MR mức Rủi ro cao cần Tech Lead. Claude không push lên `dev`, không merge.

## Khi mở Claude Code ở thư mục chung nhiều repo
Áp dụng khi thư mục đang mở không phải repo git (chạy `git rev-parse` báo lỗi) mà chứa nhiều repo con.
- Trước khi tạo nhánh, xác định task thuộc repo nào: trường Repo trên Base, không có thì theo bảng repo trong CLAUDE.md. Không chắc thì gọi `decider`; không đoán.
- Mọi lệnh git, glab, test, lint chạy bên trong repo đó theo dạng `cd <repo> && <lệnh>`. Không dùng `git -C` (bị chặn, vì làm luật chặn push không nhận ra). Không chạy git ở thư mục chung.
- Nhánh, commit, push, MR đều tính theo từng repo. Task phải sửa hai repo: tạo nhánh cùng tên ở cả hai, mở hai MR, mỗi MR ghi link MR kia trong mô tả. Thứ tự merge: repo cung cấp (API, contract, thư viện dùng chung) merge trước, repo dùng merge sau; ghi thứ tự này trong mô tả cả hai MR.
- Kế hoạch và sổ bàn giao ghi rõ repo cho từng file sửa. Sổ bàn giao `.bangiao/<Mã>/` để ở thư mục chung.
- Không sửa repo không có trong bảng repo của CLAUDE.md.

## Hook
- Hook `kiem-soat-git.py` chặn commit/push sai quy trình. Bị chặn thì đọc lý do và sửa theo (đổi tên nhánh, sửa tiêu đề commit, sửa lỗi lint/test), không tìm cách lách. Không sửa file trong `.claude/hooks/`.

## Vùng cấm
- Không sửa (ở mọi thư mục con, không chỉ thư mục gốc): Jenkinsfile, Dockerfile, docker-compose*, cấu hình Kubernetes, repo deploy, `.env*`, `.claude/settings.json`, các file trong `docs/claude-workflow/`.
- Không đọc hay in secret. Không trỏ vào Staging hoặc Production.
- Không thêm thư viện nếu kế hoạch đã duyệt chưa ghi.
- Migration: chỉ khi kế hoạch có ghi, phải chạy ngược lại được, chỉ chạy trên Dev.

## Test
- Mỗi tiêu chí đạt có ít nhất một test, tên test ghi mã tiêu chí (`TC2: ...`).
- Không gọi dịch vụ thật trong test; mock theo công cụ ghi trong CLAUDE.md của repo.
- Không xóa, skip hay nới lỏng test có sẵn để cho pass.
