# Cài bộ quy trình Claude vào repo dự án

Bộ quy trình (6 sub agent, `/feature`, `/bugfix`, `/mr-review`, luật chặn, MR template, tài liệu) nằm ở repo
[`banglc-tech/claude-dev-workflow`](https://github.com/banglc-tech/claude-dev-workflow). Mỗi repo dự án nhận một bản sao
qua script `scripts/cai-dat.py`, rồi commit bản sao đó vào repo dự án. Nhờ vậy ai clone repo dự án cũng có đủ quy trình,
không cần làm gì thêm ngoài bước chuẩn bị máy.

Có ba tình huống. Tìm đúng tình huống của bạn rồi làm theo.

| Tình huống | Ai làm | Làm mấy lần |
| --- | --- | --- |
| A. Repo dự án chưa có quy trình | Tech Lead hoặc dev được giao | Một lần cho mỗi repo |
| B. Repo dự án đã có quy trình, bạn mới clone về | Mọi dev | Một lần cho mỗi máy |
| C. Bộ quy trình có bản mới | Tech Lead hoặc dev được giao | Mỗi lần bộ quy trình đổi |

## Chuẩn bị máy (mọi dev, một lần)

1. Cài Claude Code, `git`, `glab` (`brew install glab`) và Python 3 (macOS có sẵn khi cài Xcode Command Line Tools).
2. Đăng nhập GitLab: `glab auth login`.
3. Xin Tech Lead token MCP Lark, thêm vào `~/.zshrc` rồi mở lại terminal:
   ```bash
   export LARK_MCP_TOKEN="<token>"
   ```
   Không dán token vào chat, vào file trong repo hay vào Claude.
4. Lấy bộ quy trình về máy, để cố định ở thư mục home:
   ```bash
   git clone git@github.com:banglc-tech/claude-dev-workflow.git ~/claude-dev-workflow
   ```

## A. Cài vào repo dự án lần đầu

```bash
cd ~/Source/<repo dự án>
git checkout dev && git pull
git checkout -b chore/claude-workflow
python3 ~/claude-dev-workflow/scripts/cai-dat.py
```

Script kéo bản mới nhất của bộ quy trình rồi ghi vào repo dự án:

| Ghi vào repo dự án | Cách ghi |
| --- | --- |
| `.claude/agents/` (6 agent), `.claude/commands/` (3 lệnh) | Chép đè bằng bản của bộ quy trình |
| `.claude/settings.json` | Giữ cấu hình sẵn có, thêm các luật chặn còn thiếu |
| `.mcp.json` | Giữ server sẵn có, thêm `lark-ihouzz` nếu chưa có |
| `.gitlab/merge_request_templates/Default.md`, `scripts/check-mr.sh` | Chép đè |
| `docs/claude-workflow/` | Quy trình chung, hướng dẫn dev, quy trình merge, đầu vào Lark Base, file này, 3 lưu đồ |
| `CLAUDE.md` | Chưa có: tạo từ mẫu. Đã có: giữ nguyên, chỉ thêm dòng `@docs/claude-workflow/CLAUDE-QUY-TRINH.md` ở cuối |
| `.gitignore` | Thêm `.bangiao/` và `.claude/settings.local.json` nếu thiếu |
| `.claude/claude-dev-workflow.version` | Ghi phiên bản đã cài, để biết lúc nào cần cập nhật |

Script không commit, không push. Sau khi chạy:

1. Xem lại: `git status` và `git diff`.
2. Điền các chỗ `<...>` trong `CLAUDE.md`: stack, lệnh cài, chạy, test, lint, quy ước code, công cụ mock. Repo lớn thì viết thêm `docs/CONVENTION-AI.md` và trỏ tới từ `CLAUDE.md`. Chỉ ghi phần riêng của repo, không chép lại quy trình chung.
3. Thử trong Claude Code tại thư mục gốc repo:
   - `/agents` thấy đủ planner, test-writer, implementer, bug-investigator, reviewer, decider.
   - `/mcp` thấy `lark-ihouzz` ở trạng thái connected.
   - Gõ `/` thấy `/feature`, `/bugfix`, `/mr-review`.
4. Commit và mở MR mức Hạ tầng cho Tech Lead duyệt:
   ```bash
   git add -A && git commit -m "chore: cài quy trình claude-dev-workflow"
   git push -u origin chore/claude-workflow
   ```
5. Tech Lead bật trên GitLab: protected branch `dev`, CODEOWNERS cho `.claude/`, `CLAUDE.md`, `docs/claude-workflow/` (xem `QUY-TRINH-MERGE.md`), stage "Kiểm tra MR" trong Jenkins chạy `scripts/check-mr.sh`.

## B. Dev mới, repo đã có quy trình

Không cần chạy script cài đặt. Làm xong phần Chuẩn bị máy, clone repo dự án như thường, rồi kiểm tra:

```bash
cd ~/Source/<repo dự án>
python3 ~/claude-dev-workflow/scripts/cai-dat.py --kiem-tra
```

Kết quả "Đạt" là dùng được. Còn dòng THIẾU thì làm theo gợi ý trên dòng đó (thường là thiếu token hoặc chưa `glab auth login`).
Sau đó đọc `docs/claude-workflow/HUONG-DAN.md` rồi nhận task đầu tiên bằng `/feature <Mã task>`.

Cài đặt riêng của bạn (ví dụ cho phép thêm lệnh) để trong `.claude/settings.local.json`, file này không lên git.
Không sửa `.claude/settings.json`.

## C. Cập nhật khi bộ quy trình có bản mới

Tech Lead báo khi bộ quy trình đổi. Người phụ trách repo làm:

```bash
cd ~/Source/<repo dự án>
git checkout dev && git pull && git checkout -b chore/claude-workflow-<ngày>
python3 ~/claude-dev-workflow/scripts/cai-dat.py
git diff
```

Script chỉ đè các file do bộ quy trình quản lý. Phần riêng trong `CLAUDE.md`, server MCP khác và luật riêng trong
`settings.json` được giữ nguyên. Commit, mở MR mức Hạ tầng như lần đầu.

Muốn biết repo đang chậm bản nào: `--kiem-tra` in "repo đang dùng X, bộ cài mới nhất Y".

## Sửa quy trình ở đâu

| Muốn đổi | Sửa ở |
| --- | --- |
| Quy trình chung, agent, lệnh, luật chặn, MR template | Repo `claude-dev-workflow`, rồi cập nhật từng repo dự án theo mục C |
| Stack, lệnh, quy ước code, vùng cấm riêng, bài học của một repo | `CLAUDE.md` của repo dự án đó |
| Quyền riêng của một dev | `.claude/settings.local.json` trên máy dev đó |

Sửa thẳng file trong `docs/claude-workflow/` hoặc `.claude/agents/` của repo dự án sẽ bị đè ở lần cập nhật sau.

## Gặp lỗi

| Hiện tượng | Cách xử lý |
| --- | --- |
| `/mcp` báo `lark-ihouzz` failed | Kiểm tra `echo $LARK_MCP_TOKEN` có giá trị; mở lại terminal rồi mở lại Claude Code. URL trong `.mcp.json` còn `<...>` thì hỏi Tech Lead |
| `/agents` không thấy agent | Phải mở Claude Code ở thư mục gốc repo (nơi có `.claude/`) |
| Agent decider báo không nhận model fable | Đổi `model: fable` thành `model: opus` trong bộ quy trình, báo Tech Lead |
| Script báo "không phải repo git" | `cd` vào repo dự án trước, hoặc truyền đường dẫn: `cai-dat.py ~/Source/<repo>` |
| Script báo không kéo được bản mới | Kiểm tra quyền truy cập GitHub; tạm chạy với `--khong-pull` để dùng bản đang có |
