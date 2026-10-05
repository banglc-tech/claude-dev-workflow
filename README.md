# claude-dev-workflow

Quy trình giao việc cho Claude Code của team Dev: tính năng mới và sửa lỗi, với 6 sub agent.

- `HUONG-DAN.md`: hướng dẫn dùng hằng ngày cho dev (điểm dừng, cách trả lời, sổ bàn giao)
- `CLAUDE.md`: quy ước repo, vùng cấm
- `.claude/agents/`: planner, test-writer, implementer, bug-investigator, reviewer, decider (model fable)
- `.claude/commands/`: `/feature <số issue>`, `/bugfix <số issue>`
- `.claude/settings.json`: chặn merge, force push, kubectl, đọc `.env`
- `.gitlab/merge_request_templates/Default.md`: MR template

Cách dùng: chép toàn bộ vào repo dự án, điền các chỗ `<...>` trong CLAUDE.md. Dev mới đọc `HUONG-DAN.md` trước.
