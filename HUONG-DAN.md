# Hướng dẫn dùng Claude Code cho team Dev

> Dành cho dev Sales Zone · Bluemarq. Câu hỏi về quy trình hỏi Bằng (Tech Lead).
> Nguyên tắc chung: Claude làm, dev duyệt, con người merge.

## 1. Chuẩn bị một lần

1. Cài Claude Code và `glab`, đăng nhập GitLab: `glab auth login`.
2. Lấy bộ quy trình về máy (`git clone git@github.com:banglc-tech/claude-dev-workflow.git ~/claude-dev-workflow`), kiểm tra `/mcp` đã có MCP Lark (chưa có thì xem `CAI-DAT.md`), rồi trong repo dự án chạy `python3 ~/claude-dev-workflow/scripts/cai-dat.py --kiem-tra`. Repo dự án chưa có quy trình thì làm theo `CAI-DAT.md` mục A. Chi tiết: `CAI-DAT.md`.
3. Không sửa `.claude/settings.json`. File này chặn Claude merge, force push, chạy `kubectl`, đọc `.env`. Cần nới gì thì nói với Bằng.
4. Cài đặt riêng của bạn (nếu cần) để trong `.claude/settings.local.json`, file này đã nằm trong `.gitignore`.

## 2. Hai lệnh duy nhất

| Việc | Lệnh | Nhánh tạo ra |
| --- | --- | --- |
| Tính năng mới | `/feature <số issue>` | `feature/<số issue>-<tên ngắn>` từ `dev` |
| Sửa lỗi | `/bugfix <số issue>` | `fix/<số issue>-<tên ngắn>` từ `dev` |

Mở Claude Code tại thư mục gốc repo, đang ở nhánh `dev` đã pull mới nhất, rồi gõ lệnh. Không tự tạo nhánh trước, Claude sẽ tạo.

## 3. Trước khi giao: bản ghi trên Base phải đủ

Task và lỗi nằm trên Lark Base `BLUEMARQ`, Claude tự đọc qua MCP. Bạn chỉ cần đưa **Mã** (trường Mã trên Base). Chi tiết các trường và luồng câu hỏi: `DAU-VAO-LARK-BASE.md`.

Claude kiểm tra ở bước đầu và DỪNG nếu thiếu. Tự kiểm tra trước để khỏi mất một vòng.

**Issue tính năng**
- Link đặc tả đã duyệt
- Link thiết kế đã duyệt
- Tiêu chí đạt, đánh số TC1, TC2...
- Ước lượng không quá 1 ngày. Lớn hơn thì tách issue trước.

**Issue lỗi**
- Bước tái hiện
- Kết quả mong đợi
- Tiêu chí bị vi phạm
- Mức độ. Mức Nghiêm trọng chỉ làm khi bạn ngồi theo dõi trực tiếp.

## 4. Làm tính năng: các điểm dừng

```
/feature 123
  │
  ├─ 1. Đọc issue, kiểm tra đủ thông tin
  ├─ 2. Tạo nhánh từ dev
  ├─ 3. planner lập kế hoạch ──────────── ⏸ DỪNG: bạn duyệt kế hoạch
  ├─ 4. test-writer viết test (phải fail)
  ├─ 5. implementer code đến khi test pass, commit
  ├─ 6. reviewer soát diff (tối đa 2 vòng sửa)
  ├─ 7. Tóm tắt cho bạn ──────────────── ⏸ DỪNG: bạn xem kết quả
  └─ 8. Chỉ khi bạn nói "mở MR": push nhánh, mở MR
```

**Điểm dừng 1: duyệt kế hoạch.** Đọc kỹ, đây là chỗ quan trọng nhất. Kiểm tra:
- Danh sách file sửa có hợp lý không, có file nào đáng ngờ không.
- Bảng tiêu chí đạt → test có đủ từng TC không.
- Có dùng lại component iHouzz Design System và code có sẵn không.
- Có đề xuất thêm thư viện hay migration không. Nếu có mà chưa bàn với Bằng thì chưa duyệt.
- Mục "Câu hỏi cho BA" còn gì chưa trả lời không.

Trả lời bằng đúng một trong ba câu:
- `Duyệt, làm tiếp`
- `Sửa kế hoạch: <nói rõ sửa gì>`
- `Dừng`

**Điểm dừng 2: xem kết quả.** Claude báo đã làm gì, kết quả test, báo cáo reviewer, các quyết định decider đã đưa ra. Tự chạy thử trên Dev theo từng tiêu chí trước khi cho mở MR.

Trả lời `mở MR` khi hài lòng. Chưa hài lòng thì nói rõ cần sửa gì, Claude sẽ giao lại implementer.

## 5. Sửa lỗi: các điểm dừng

```
/bugfix 456
  │
  ├─ 1. Đọc issue, kiểm tra đủ thông tin
  ├─ 2. Mức Nghiêm trọng: chỉ làm khi bạn theo dõi trực tiếp
  ├─ 3. Tạo nhánh từ dev. Lỗi trên Production: DỪNG, đi theo quy trình hotfix
  ├─ 4. bug-investigator tái hiện, viết test fail, tìm nguyên nhân gốc ── ⏸ DỪNG: bạn duyệt
  ├─ 5. implementer sửa nhỏ nhất, test tái hiện pass, test cũ vẫn pass
  ├─ 6. reviewer soát (tối đa 2 vòng)
  ├─ 7. Tóm tắt cho bạn ──────────────────────────────────────────────── ⏸ DỪNG
  └─ 8. Chỉ khi bạn nói "mở MR": push, mở MR nhãn bug, Closes #456
```

**Duyệt nguyên nhân gốc.** Kiểm tra:
- Có test tái hiện đang fail thật không, hay chỉ "nghi ngờ". Báo cáo phải phân biệt rõ hai mức này.
- Nguyên nhân gốc chỉ ra file và dòng cụ thể, giải thích vì sao sai.
- Cách sửa đề xuất là nhỏ nhất, không kèm refactor.
- Mục "chỗ khác có cùng nguyên nhân" đã được liệt kê.

Không tái hiện được thì Claude dừng và liệt kê cần hỏi Test gì. Chuyển câu hỏi đó cho Test, đừng ép Claude đoán.

**Lỗi trên Production** không đi qua `/bugfix`. Làm theo mục hotfix trong tài liệu Quy trình quản lý source Git & deploy.

## 6. Khi Claude gặp vướng

Claude không dừng ngay khi gặp vướng (câu hỏi, thiếu thông tin, test fail, reviewer chặn, pipeline đỏ…). Nó gọi `decider` trước: quyết được thì làm tiếp và ghi vào bảng *Quyết định Claude* trên Base để Bằng xem; không quyết được mới tạo ticket Decisions hỏi Bằng (hoặc BA với câu hỏi nghiệp vụ) rồi dừng. Bạn chỉ cần đọc phần "Quyết định decider" trong tóm tắt cuối mỗi lần chạy.

### Khi Claude dừng vì câu hỏi còn mở

Sub agent nào có câu hỏi thì Claude gọi `decider` trước khi dừng. decider xếp mỗi câu vào một trong ba loại:

| Loại | Ví dụ | Ai quyết |
| --- | --- | --- |
| Kỹ thuật, trong phạm vi | đặt tên, chọn component có sẵn, cấu trúc file, cách viết test | decider tự quyết, ghi vào `00-quyet-dinh.md`, làm tiếp |
| Nghiệp vụ, phạm vi | luồng nghiệp vụ, quy tắc tính, quyền người dùng, nội dung hiển thị | BA (phạm vi, hạn thì PM) |
| Rủi ro cao | kiến trúc, schema DB, migration, thư viện mới, bảo mật, thanh toán | Tech Lead |

Khi Claude báo "Phải dừng": chuyển câu hỏi cho đúng người, có câu trả lời thì dán lại cho Claude và nói làm tiếp.

Mọi quyết định decider đã đưa ra đều được liệt kê trong tóm tắt cuối. Lướt qua một lượt, không đồng ý cái nào thì bảo Claude đổi lại, mỗi quyết định đều đổi được trong một commit.

## 7. Sổ bàn giao `.bangiao/<số issue>/`

Mỗi issue có một thư mục, không commit (đã trong `.gitignore`). Đây là chỗ đọc lại khi cần biết Claude đã làm gì.

| File | Ai viết | Dùng khi |
| --- | --- | --- |
| `00-quyet-dinh.md` | decider | xem lại các quyết định kỹ thuật |
| `01-ke-hoach.md` / `01-dieu-tra.md` | planner / bug-investigator | kế hoạch hoặc nguyên nhân gốc đã duyệt, có dòng "Dev duyệt: <tên>, <ngày>" |
| `02-test.md` | test-writer | test nào cho TC nào, fail vì sao |
| `02-thay-doi.md` / `03-thay-doi.md` | implementer | file đã sửa, kết quả test, lý do sửa file ngoài kế hoạch |
| `03-danh-gia.md` / `04-danh-gia.md` | reviewer | kết luận CHỐT / CẦN SỬA / CHẶN |

Làm issue mới thì Claude tạo thư mục mới, không dùng lại sổ cũ. Có thể xóa thư mục sau khi MR đã merge.

## 8. Mở MR và review

- MR theo template có sẵn: tiêu đề `[<tính năng>] <việc> (#<số issue>)`, nhãn `feature::<tính năng>` hoặc `bug`, bảng tiêu chí → test, checklist.
- Chỉ mở MR khi reviewer kết luận **CHỐT**. Kết luận **CHẶN** thì không mở, dù bạn thấy ổn.
- Người review MR không phải người giao Claude làm. Người review đọc cả báo cáo reviewer trong sổ bàn giao.
- Chỉ con người merge. Claude không push lên `dev`, không merge, và settings đã chặn việc này.
- Sau khi mở MR, Jenkins chạy `scripts/check-mr.sh` kiểm tra tên nhánh, tiêu đề, mô tả, nhãn. Đỏ thì sửa theo dòng CHẶN. Xanh rồi gõ `/mr-review <số MR>` để Claude review nội dung và gắn nhãn `review::qua`, `review::can-xem` hoặc `review::chan`. Chỉ `review::qua` là người review có thể xác nhận nhanh.
- Mức MR, điều kiện merge, thời hạn review và cách xử lý khi `dev` hỏng: xem `QUY-TRINH-MERGE.md`.

## 8a. Push code hằng ngày

Nhánh đang làm phải lên GitLab ít nhất một lần mỗi ngày trước 17:00, dù chưa xong: `git add . && git commit -m "wip(#<Mã>): đang làm gì" && git push`. Claude tự push sau mỗi bước có commit; bạn chỉ cần kiểm tra trước khi báo cáo 17:00 là commit cuối đã có trên GitLab. Chi tiết: `QUY-TRINH-MERGE.md` mục 4a.

## 9. Chạy qua đêm

Chỉ với issue tính năng đã có kế hoạch được duyệt sẵn ghi trong issue. Claude đi từ bước test đến bước tóm tắt, push nhánh feature (kể cả commit wip) rồi ghi kết quả vào Ghi chú Claude trên Base, không mở MR. Sáng hôm sau đọc comment và sổ bàn giao, rồi quyết định mở MR hay sửa.

Không chạy `/bugfix` qua đêm.

## 10. Việc không làm

**Claude không được** (đã ghi trong CLAUDE.md và settings):
- Sửa Jenkinsfile, Dockerfile, docker-compose, Kubernetes, repo `bluemarq-deploy`, `.env*`.
- Đọc hay in secret. Trỏ vào Staging hoặc Production.
- Thêm thư viện, chạy migration khi kế hoạch chưa ghi.
- Xóa, skip hay nới lỏng test có sẵn.
- Merge, force push, push lên `dev`.

**Dev không nên**:
- Bỏ qua điểm dừng bằng cách gõ "Duyệt" mà chưa đọc kế hoạch.
- Bảo Claude "cứ làm cho pass" khi test fail. Test fail là tín hiệu, không phải vật cản.
- Tự sửa code bằng tay giữa chừng rồi để Claude làm tiếp mà không nói. Nói rõ đã sửa gì để sổ bàn giao khớp.
- Dùng Claude làm thẳng trên `dev` hoặc nhánh của người khác.
- Dán secret, dữ liệu khách hàng thật vào chat.

## 11. Khi gặp vấn đề

- **Claude lặp lại cùng một lỗi**: mỗi sub agent được thử tối đa 3 lần rồi phải dừng và báo. Đọc phần "đã thử" trong báo cáo trước khi bảo thử tiếp.
- **Claude sửa file ngoài kế hoạch**: báo cáo implementer phải ghi lý do. Không có lý do thì bảo hoàn lại.
- **Claude làm sai cùng một lỗi lần thứ hai**: ghi vào mục "Bài học" cuối `CLAUDE.md`, dạng `<ngày> — <quy tắc>`, gửi MR cho Bằng duyệt.
- **Cần nới quyền trong settings.json**: hỏi Bằng, không tự sửa.

## 12. Tóm tắt lệnh

```
glab auth login                 # một lần
git checkout dev && git pull    # trước mỗi issue
/feature 123                    # tính năng
/bugfix 456                     # lỗi

Duyệt, làm tiếp                 # duyệt kế hoạch / nguyên nhân gốc
Sửa kế hoạch: ...               # yêu cầu sửa kế hoạch
Dừng                            # dừng hẳn
mở MR                           # cho phép push và mở MR
```
