# claude-dev-workflow

Quy trình giao việc cho Claude Code của team Dev iHouzz: tính năng mới và sửa lỗi, với 6 sub agent.

> Repo này là bản gốc duy nhất. Trang Lark "02 Quy trình giao việc cho Claude" chỉ giữ phần quy định cho người đọc và link về đây; repo đổi quy định thì Tech Lead cập nhật trang Lark trong 2 ngày làm việc.

- `HUONG-DAN.md`: hướng dẫn dùng hằng ngày cho dev (điểm dừng, cách trả lời, sổ bàn giao)
- `CAI-DAT.md`: **cài bộ quy trình vào repo dự án** (lần đầu, dev mới, cập nhật)
- `scripts/cai-dat.py`: script cài / cập nhật / kiểm tra (`--kiem-tra`)
- `CLAUDE-QUY-TRINH.md`: quy trình chung, được nạp vào CLAUDE.md của mọi repo dự án
- `templates/CLAUDE.md`: mẫu CLAUDE.md cho repo dự án (chỉ phần riêng của repo)
- `templates/CLAUDE-THU-MUC-CHUNG.md`: mẫu CLAUDE.md cho thư mục chung chứa nhiều repo
- `.claude/agents/`: planner, test-writer, implementer, bug-investigator, reviewer, decider (model fable)
- `.claude/commands/`: `/feature <Mã>`, `/bugfix <Mã>`, `/mr-review <số MR>`
- `scripts/check-mr.sh`: kiểm tra hình thức MR (tên nhánh, tiêu đề, mô tả, nhãn) cho Jenkins
- `.claude/settings.json`: chặn merge, force push, kubectl, đọc `.env`; khai báo hook
- `.claude/hooks/`: `kiem-soat-git.py` (chặn commit/push sai quy trình, chạy lệnh kiểm tra trước push), `mo-phien.py` (bối cảnh đầu phiên)
- `.gitlab/merge_request_templates/Default.md`: MR template
- `DAU-VAO-LARK-BASE.md`: đầu vào từ Lark Base (Tasks, Bugs, Decisions) qua MCP; luồng câu hỏi → comment đặc tả + ticket Decisions
- `templates/mcp-mau.json`: mẫu khai báo MCP Lark theo project (ưu tiên dùng MCP đã kết nối ở máy dev, xem `CAI-DAT.md`)
- `QUY-TRINH-MERGE.md`: quy trình duyệt và merge vào `dev` (3 mức MR, điều kiện merge, cài đặt GitLab)

## Cài vào repo dự án

```bash
git clone git@github.com:banglc-tech/claude-dev-workflow.git ~/claude-dev-workflow   # một lần mỗi máy
cd ~/Source/<repo dự án> && git checkout -b chore/claude-workflow
python3 ~/claude-dev-workflow/scripts/cai-dat.py          # cài hoặc cập nhật
python3 ~/claude-dev-workflow/scripts/cai-dat.py --kiem-tra   # dev mới: kiểm tra máy và repo
python3 ~/claude-dev-workflow/scripts/cai-dat.py ~/Source/prophub --ca-repo-con   # thư mục chung nhiều repo (không phải git)
```

Chi tiết từng tình huống trong `CAI-DAT.md`. Sau khi cài, điền các chỗ `<...>` trong `CLAUDE.md` của repo dự án và mở MR mức Hạ tầng. Dev mới đọc `HUONG-DAN.md` trước.
