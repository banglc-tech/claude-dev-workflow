# claude-dev-workflow

Quy trình giao việc cho Claude Code của team Dev: tính năng mới và sửa lỗi, với 6 sub agent.

- `HUONG-DAN.md`: hướng dẫn dùng hằng ngày cho dev (điểm dừng, cách trả lời, sổ bàn giao)
- `CLAUDE.md`: quy ước repo, vùng cấm
- `.claude/agents/`: planner, test-writer, implementer, bug-investigator, reviewer, decider (model fable)
- `.claude/commands/`: `/feature <số issue>`, `/bugfix <số issue>`, `/mr-review <số MR>`
- `scripts/check-mr.sh`: kiểm tra hình thức MR (tên nhánh, tiêu đề, mô tả, nhãn) cho Jenkins
- `.claude/settings.json`: chặn merge, force push, kubectl, đọc `.env`
- `.gitlab/merge_request_templates/Default.md`: MR template
- `DAU-VAO-LARK-BASE.md`: đầu vào từ Lark Base (Tasks, Bugs, Decisions) qua MCP; luồng câu hỏi → comment đặc tả + ticket Decisions
- `.mcp.json`: khai báo MCP Lark của iHouzz
- `QUY-TRINH-MERGE.md`: quy trình duyệt và merge vào `dev` (3 mức MR, điều kiện merge, cài đặt GitLab)
- `HUONG-DAN.md`: hướng dẫn dùng hằng ngày cho dev

Cách dùng: chép toàn bộ vào repo dự án, điền các chỗ `<...>` trong CLAUDE.md. Dev mới đọc `HUONG-DAN.md` trước.
