# CLAUDE.md — repo claude-dev-workflow (bộ cài, không phải repo dự án)

Repo này chứa bộ quy trình Claude Code dùng chung cho các repo dự án của team Dev. Không chạy `/feature`, `/bugfix` ở đây.

- Quy trình chung nạp vào mọi repo dự án: `CLAUDE-QUY-TRINH.md`.
- Mẫu CLAUDE.md cho repo dự án mới: `templates/CLAUDE.md` (chỉ phần riêng của repo, cuối file có dòng @ nạp quy trình chung).
- Script cài / cập nhật / kiểm tra: `scripts/cai-dat.py`, hướng dẫn trong `CAI-DAT.md`.
- Khi đổi quy trình: sửa file ở đây, cập nhật tài liệu Lark "02 Quy trình giao việc cho Claude", commit, báo các repo dự án chạy lại `scripts/cai-dat.py`.
- Tên tài liệu (`HUONG-DAN.md`, `QUY-TRINH-MERGE.md`, `DAU-VAO-LARK-BASE.md`, `CLAUDE-QUY-TRINH.md`, `CAI-DAT.md`) được script tự đổi thành `docs/claude-workflow/<tên>` khi chép sang repo dự án; khi nhắc tới chúng chỉ ghi tên file trần.
