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
| D. Thư mục chung chứa nhiều repo (không phải git) | Mỗi dev, trên máy mình | Một lần, chạy lại khi bộ quy trình đổi |

## Chuẩn bị máy (mọi dev, một lần)

1. Cài Claude Code, `git`, `glab` (`brew install glab`) và Python 3 (macOS có sẵn khi cài Xcode Command Line Tools).
2. Đăng nhập GitLab: `glab auth login`.
3. MCP Lark của iHouzz: máy đã kết nối sẵn (gõ `/mcp` trong Claude Code thấy server Lark connected, tên gì cũng được) thì không cần làm gì thêm. Chưa có thì thêm một lần, dùng cho mọi repo:
   ```bash
   claude mcp add --transport http --scope user lark-ihouzz <URL> --header "Authorization: Bearer <token>"
   ```
   URL và token xin Tech Lead. Không dán token vào chat, vào file trong repo hay vào Claude.
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
| `.claude/settings.json` | Giữ cấu hình sẵn có, thêm các luật chặn và hook còn thiếu |
| `.claude/hooks/` | Hai hook chạy tự động: `kiem-soat-git.py` chặn commit/push sai quy trình, `mo-phien.py` nạp bối cảnh đầu phiên. Chép đè |
| `.claude/settings.local.json` (không lên git) | Tìm server MCP Lark đã kết nối trên máy, chặn tool Lark bị cấm và cho phép tool được dùng theo đúng tên server đó. Không ghi `.mcp.json` |
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
   - `/mcp` thấy server MCP Lark ở trạng thái connected.
   - Gõ `/` thấy `/feature`, `/bugfix`, `/mr-review`.
4. Commit và mở MR mức Hạ tầng cho Tech Lead duyệt:
   ```bash
   git add -A && git commit -m "chore: cài quy trình claude-dev-workflow"
   git push -u origin chore/claude-workflow
   ```
5. Tech Lead bật trên GitLab: protected branch `dev`, CODEOWNERS cho `.claude/`, `CLAUDE.md`, `docs/claude-workflow/` (xem `QUY-TRINH-MERGE.md`), stage "Kiểm tra MR" trong Jenkins chạy `scripts/check-mr.sh`.

### Hook tự động

Hai hook chạy mà không cần dev hay Claude nhớ gọi:

| Hook | Khi nào | Làm gì |
| --- | --- | --- |
| `kiem-soat-git.py` | Trước mỗi lệnh Bash Claude chạy | Chặn: commit trên `dev`/`main`; tiêu đề commit sai mẫu `<loại>(#<Mã>): <mô tả>`; push lên `dev`/`main`, force push, xóa nhánh remote; push nhánh không đúng mẫu `feature/<Mã>-<tên>` hoặc `fix/<Mã>-<tên>`; `git -C`. Nếu repo có file `.claude/kiem-tra-truoc-push` thì chạy lệnh trong đó trước mỗi lần push, lỗi là chặn |
| `mo-phien.py` | Đầu mỗi phiên Claude Code | Cho Claude biết chế độ (repo hay thư mục chung), nhánh hiện tại, việc đang dở trong `.bangiao/`, quy tắc cốt lõi, và nhắc khi bộ quy trình trên máy có bản mới |

Lệnh kiểm tra trước push đặt riêng cho từng repo, một dòng, ví dụ `pnpm lint && pnpm test --changed`
(chậm quá 14 phút là bị chặn). File này commit cùng repo để cả team dùng chung.
Hook chỉ chặn lệnh Claude chạy; lệnh dev tự gõ trong terminal không bị ảnh hưởng.

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

## D. Thư mục chung chứa nhiều repo

Dùng khi một dự án gồm nhiều repo đặt chung một thư mục, ví dụ `~/Source/prophub/` chứa `dxs-o2o-backend/`,
`dxs-o2o-web/`... và bạn muốn mở Claude Code một lần ở thư mục cha để làm task đụng nhiều repo.

```bash
python3 ~/claude-dev-workflow/scripts/cai-dat.py ~/Source/prophub
python3 ~/claude-dev-workflow/scripts/cai-dat.py ~/Source/prophub --ca-repo-con   # thêm MR template, check-mr.sh vào từng repo con
```

Script nhận ra thư mục không phải git và chuyển sang chế độ thư mục chung:

| Ghi vào | Nội dung |
| --- | --- |
| Thư mục chung | `.claude/` (agent, lệnh, luật chặn, `settings.local.json` theo MCP Lark của máy), `docs/claude-workflow/`, `CLAUDE.md` |
| `CLAUDE.md` của thư mục chung | Tạo từ mẫu thư mục chung, có sẵn bảng các repo con tìm được (sâu tối đa 2 cấp); bạn điền vai trò và lệnh test từng repo |
| Từng repo con (chỉ khi có `--ca-repo-con`) | MR template, `scripts/check-mr.sh`, dòng `.bangiao/` trong `.gitignore` |

Cách làm việc:

1. Luôn mở Claude Code tại thư mục chung. Agent, lệnh và luật chặn chỉ có hiệu lực khi mở ở đây; mở trong repo con thì Claude chỉ thấy CLAUDE.md, không thấy `/feature`, `/bugfix` và luật chặn (trừ khi repo con cũng đã cài theo mục A).
2. Trên Base nên có trường Repo cho mỗi task. Claude dựa vào đó để biết sửa repo nào; trống thì suy từ đặc tả và bảng repo, không chắc thì hỏi decider.
3. Claude chạy git trong từng repo con. Task sửa hai repo thì có hai nhánh cùng tên và hai MR trỏ chéo nhau.
4. Thư mục chung không có git nên các file cài ở đó không được quản lý phiên bản: mỗi dev tự chạy script trên máy mình, và chạy lại khi bộ quy trình có bản mới. Phần MR template, `check-mr.sh` trong repo con thì commit vào repo con qua MR như mục A.
5. Kiểm tra: `python3 ~/claude-dev-workflow/scripts/cai-dat.py ~/Source/prophub --kiem-tra`. Lệnh này báo cả repo con nào chưa có MR template hoặc chưa có trong bảng repo của CLAUDE.md.

Repo con nào được làm riêng thường xuyên (mở Claude Code ngay trong repo đó) thì cài thêm cho repo đó theo mục A. Hai cách dùng song song được.

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
| `/mcp` báo server Lark failed | Token hết hạn hoặc sai: xin lại Tech Lead, chạy lại `claude mcp add` (xóa bản cũ bằng `claude mcp remove <tên>`) |
| Script báo chưa thấy MCP Lark dù `/mcp` có | Tên và URL server không chứa chữ lark hay ihouzz: báo Tech Lead tên server để thêm vào script |
| Đổi tên server MCP Lark | Chạy lại script để cập nhật luật chặn theo tên mới; luật theo tên cũ không còn tác dụng |
| `/agents` không thấy agent | Phải mở Claude Code ở thư mục gốc repo (nơi có `.claude/`) |
| Agent decider báo không nhận model fable | Đổi `model: fable` thành `model: opus` trong bộ quy trình, báo Tech Lead |
| Script chạy chế độ thư mục chung trong khi bạn muốn cài cho một repo | Bạn đang đứng ngoài repo: `cd` vào repo hoặc truyền đúng đường dẫn repo |
| Thư mục chung: `/feature` không có khi mở Claude Code | Đang mở trong repo con; mở lại tại thư mục chung |
| Script báo không kéo được bản mới | Kiểm tra quyền truy cập GitHub; tạm chạy với `--khong-pull` để dùng bản đang có |
