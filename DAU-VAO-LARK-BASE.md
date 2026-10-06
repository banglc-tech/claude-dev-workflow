# Đầu vào của Dev: đặc tả, task, lỗi và câu hỏi nằm trên Lark Base

> Ngoài source code trên GitLab, mọi đầu vào của Dev nằm ở **một Base duy nhất**: `BLUEMARQ` (Lark Drive › BLUEMARQ). Claude đọc Base và tài liệu qua **MCP Lark của iHouzz**, không đọc qua link dán tay hay nội dung copy vào chat.
> Chủ sở hữu quy định: Bằng. Chủ sở hữu dữ liệu trên Base: PM và BA.

## 1. Nguồn dữ liệu

| Loại đầu vào | Nằm ở đâu | Claude đọc bằng |
| --- | --- | --- |
| Task / tính năng | Base `BLUEMARQ` › bảng **Tasks** | `base-v3-get-record`, `base-v3-list-records` |
| Lỗi | Base `BLUEMARQ` › bảng **Bugs** | như trên |
| Câu hỏi chung, quyết định | Base `BLUEMARQ` › bảng **Decisions** | như trên, và `base-v3-create-record` khi có câu hỏi mới |
| Test case | Base `BLUEMARQ` › bảng **Test Cases** | `base-v3-list-records` (Test ghi, Dev chỉ đọc) |
| Đặc tả (PRD, Technical Spec, Feature Spec) | Lark Docs, link nằm trong trường **Spec liên kết** của task | `docx-get-raw-content` |
| Thiết kế | Claude Design, link nằm trong trường **Link thiết kế** | Mở link (chỉ đọc) |
| Code, nhánh, MR | GitLab | `git`, `glab` |

Base là nơi duy nhất ghi trạng thái task và lỗi. GitLab chỉ giữ nhánh và MR; MR trỏ về bản ghi trên Base bằng link.

## 2. Trường bắt buộc trên Base

Bằng và PM bổ sung các trường này một lần. Thiếu trường là Claude dừng ở bước kiểm tra đầu vào.

**Tasks** (đã có: Hạng mục, MD ước tính, Spec liên kết, Hạn, Nhóm, Wave, Trạng thái, Người phụ trách)

| Trường cần thêm | Kiểu | Dùng để |
| --- | --- | --- |
| Mã | Số tự tăng | Đặt tên nhánh `feature/<Mã>-<tên ngắn>` và tiêu đề MR `(#<Mã>)` |
| Tiêu chí đạt | Văn bản dài | Danh sách TC1, TC2… áp dụng cho task; BA ghi, copy từ đặc tả |
| Link thiết kế | Link | Màn hình Claude Design đã duyệt |
| Trạng thái đặc tả | Chọn một: Nháp / Đã duyệt | Chỉ task có đặc tả Đã duyệt mới được giao Claude |
| Nhánh / MR | Link | Claude điền khi mở MR |
| Ghi chú Claude | Văn bản dài | Claude ghi tóm tắt khi chạy qua đêm hoặc khi dừng |
| Repo | Chọn nhiều: tên các repo | Repo cần sửa; bắt buộc khi dev mở Claude Code ở thư mục chung nhiều repo |

**Bugs** (bảng đang trống, tạo đủ các trường sau)

| Trường | Kiểu |
| --- | --- |
| Mã | Số tự tăng |
| Tiêu đề | Văn bản |
| Task liên kết | Liên kết sang Tasks |
| Bước tái hiện | Văn bản dài |
| Kết quả mong đợi · Kết quả thực tế | Văn bản dài |
| Tiêu chí bị vi phạm | Văn bản (TC…) |
| Mức độ | Chọn một: Nghiêm trọng / Cao / Trung bình / Thấp |
| Ảnh | Tệp đính kèm |
| Môi trường | Chọn một: Dev / Staging / Production |
| Trạng thái | Chọn một: Mới / Đang sửa / Chờ test / Đã đóng / Mở lại |
| Người báo · Người phụ trách | Người |
| Repo | Chọn nhiều: tên các repo |
| Nhánh / MR | Link |
| Ghi chú Claude | Văn bản dài |

**Decisions** (đã có: Vấn đề, Ngày chốt, Nguồn, Chặn cái gì, Trạng thái, Người quyết)

| Trường cần thêm | Kiểu | Dùng để |
| --- | --- | --- |
| Loại | Chọn một: Nghiệp vụ / Kỹ thuật / Rủi ro cao | Khớp ba loại của decider |
| Task liên kết | Liên kết sang Tasks hoặc Bugs | Biết câu hỏi chặn việc nào |
| Người hỏi | Người | Dev giao Claude |
| Link comment | Link | Comment Claude đã đặt trên đặc tả |
| Đề xuất | Văn bản dài | Phương án Claude đề xuất (với loại Rủi ro cao: 2 phương án) |

**Quyết định Claude** (bảng mới, nơi Bằng xem mọi việc decider đã tự quyết)

| Trường | Kiểu |
| --- | --- |
| Task liên kết | Liên kết sang Tasks hoặc Bugs |
| Sự cố | Chọn một: Câu hỏi kỹ thuật / Thiếu đầu vào / Kế hoạch vượt 1 ngày / Test fail / Reviewer chặn / Check-mr chặn / Pipeline đỏ / Conflict / Mức MR / Khác |
| Nội dung · Quyết định · Căn cứ · Hoàn tác bằng | Văn bản dài |
| Ngày | Ngày tạo |
| Trạng thái | Chọn một: Chưa xem / Đã xem / Bác bỏ |
| Ghi chú của Bằng | Văn bản dài |

Bằng xem các dòng Chưa xem trong buổi 9:30. Đổi sang **Bác bỏ** kèm ghi chú thì Claude hoàn tác theo cột "Hoàn tác bằng" ở lần chạy kế tiếp của task đó, và ghi bài học vào CLAUDE.md nếu cùng loại sự cố bị bác bỏ lần thứ hai.

Giá trị của **Trạng thái** trong Decisions giữ nguyên: Chưa chốt / Đã chốt. Khi Đã chốt, BA cập nhật đặc tả trước rồi mới đổi trạng thái, theo quy định "Thay đổi yêu cầu đi qua BA".

## 3. Claude đọc đầu vào thế nào

Lệnh `/feature <Mã>` và `/bugfix <Mã>` bắt đầu bằng việc đọc Base, không hỏi dev dán link:

1. Tìm bản ghi có **Mã** = số được giao trong bảng Tasks (hoặc Bugs). Không thấy thì dừng.
2. Kiểm tra đủ trường: task cần Spec liên kết, Trạng thái đặc tả = Đã duyệt, Link thiết kế, Tiêu chí đạt, MD ước tính ≤ 1; lỗi cần Bước tái hiện, Kết quả mong đợi, Tiêu chí bị vi phạm, Mức độ. Thiếu thì ghi vào **Ghi chú Claude** "Thiếu: …" và dừng.
3. Đọc đặc tả bằng `docx-get-raw-content` từ link trong Spec liên kết. Đặc tả là căn cứ duy nhất; chat hay tin nhắn không phải căn cứ.
4. Đọc bảng **Decisions** lọc theo Task liên kết: câu hỏi nào còn **Chưa chốt** thì task chưa được làm phần bị chặn. Câu hỏi **Đã chốt** thì đọc để biết quyết định.
5. Đổi Trạng thái task sang **Đang làm** (Bugs: Đang sửa), rồi mới tạo nhánh.

Khi mở MR: điền link MR vào **Nhánh / MR**, đổi Trạng thái sang **Chờ duyệt** (Bugs: Chờ test sau khi merge). MR template ghi `Base: <link bản ghi>` thay cho `Closes #`.

## 4. Khi quy trình bị vướng: decider quyết trước, không quyết được mới hỏi Bằng

Mọi sự cố trong dây chuyền (câu hỏi mở, thiếu đầu vào, test fail, reviewer chặn, check-mr chặn, pipeline đỏ, conflict…) đi qua `decider` trước. Decider quyết khi có căn cứ và hoàn tác được; agent chính thực thi và ghi vào bảng **Quyết định Claude** để Bằng xem lại, quy trình không dừng. Phần dưới đây áp dụng cho các dòng decider kết luận **HỎI BẰNG**: Người quyết mặc định là Bằng; câu hỏi nghiệp vụ thì Người quyết là BA (PM nếu là phạm vi hoặc hạn), rủi ro cao là Tech Lead. Bằng luôn nằm trong danh sách theo dõi của ticket. Agent chính làm ba việc, theo đúng thứ tự, rồi mới dừng:

1. **Comment lên đúng chỗ trong đặc tả** bằng `drive-create-comment` trên tài liệu Spec liên kết. Nội dung comment theo mẫu:
   ```
   [Claude · Task #<Mã>] Câu hỏi: <một câu>
   Ngữ cảnh: <mục / đoạn trong đặc tả>
   Đề xuất: <phương án, nếu có>
   Ticket: <link bản ghi Decisions, điền sau bước 2>
   ```
   Không comment vào chat Lark, không gửi tin nhắn riêng. Câu hỏi về thiết kế thì comment trên màn hình Claude Design (dev làm tay, Claude ghi sẵn nội dung).
2. **Tạo một bản ghi trong bảng Decisions** bằng `base-v3-create-record`: Vấn đề = câu hỏi; Loại; Nguồn = tên đặc tả và mục; Chặn cái gì = việc cụ thể trong task; Task liên kết; Người hỏi = dev; Người quyết = BA (Nghiệp vụ), PM nếu là phạm vi hoặc hạn, Tech Lead (Rủi ro cao); Trạng thái = Chưa chốt; Đề xuất; Link comment = link comment ở bước 1. Sau đó cập nhật dòng "Ticket" trong comment.
3. **Ghi vào task**: thêm vào Ghi chú Claude dòng `Chờ Decisions <Mã ticket>: <câu hỏi>`, đổi Trạng thái task sang **Chờ quyết định**. Ghi cùng nội dung vào `.bangiao/<Mã>/00-quyet-dinh.md`.

Một câu hỏi, một ticket. Nhiều câu hỏi cùng lúc thì nhiều ticket, nhưng gom vào một comment nếu cùng một mục đặc tả. Không tạo ticket trùng: trước khi tạo, đọc Decisions lọc theo Task liên kết; đã có câu hỏi cùng ý thì chỉ ghi vào Ghi chú Claude và trỏ về ticket cũ.

**Tiếp tục sau khi chốt.** Dev gõ lại `/feature <Mã>`. Claude đọc Decisions: ticket Đã chốt → đọc lại đặc tả (BA đã sửa) và `01-ke-hoach.md`; kế hoạch bị ảnh hưởng thì planner cập nhật và dev duyệt lại, không thì đi tiếp từ bước đang dở. Ticket còn Chưa chốt → dừng, báo dev đang chờ ai.

**Người trả lời** làm việc trên Base và đặc tả, không trả lời trong chat: sửa đặc tả, ghi Ngày chốt và đổi Trạng thái ticket sang Đã chốt, trả lời comment trên tài liệu bằng "đã chốt, xem mục …". PM xem các ticket Chưa chốt quá 1 ngày trong buổi 9:30.

## 5. Quyền của Claude trên Lark

Token MCP cấp cho Claude là tài khoản bot riêng, quyền tối thiểu:

| Được | Không được |
| --- | --- |
| Đọc Base, đọc tài liệu Docs, đọc file Drive | Xóa bản ghi, xóa file, xóa bảng |
| Tạo bản ghi trong **Decisions** và **Quyết định Claude**; cập nhật trường Trạng thái, Nhánh / MR, Ghi chú Claude trong Tasks và Bugs | Sửa trường khác (Hạng mục, Tiêu chí đạt, Hạn, Người phụ trách), tạo bản ghi trong Tasks hay Bugs |
| Tạo comment trên tài liệu đặc tả | Sửa nội dung tài liệu, tạo tài liệu, gửi tin nhắn Lark, tạo sự kiện lịch |

`.claude/settings.json` chặn các tool MCP ghi ngoài danh sách trên khi server tên `lark-ihouzz`. Máy dev đã kết nối MCP Lark với tên khác thì `scripts/cai-dat.py` ghi luật chặn và cho phép theo đúng tên đó vào `.claude/settings.local.json`; chạy lại script mỗi khi đổi tên server.
