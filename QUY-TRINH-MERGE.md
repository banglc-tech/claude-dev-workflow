# Quy trình duyệt và merge vào nhánh `dev`

> Áp dụng cho mọi MR vào `dev` của dự án Sales Zone · Bluemarq. Chủ sở hữu: Bằng (Tech Lead).
> Nguyên tắc: **`dev` luôn chạy được.** Một MR vào `dev` là một issue đã xong, đã có test, đã được người khác xem.

## 1. Ba mức MR

Người mở MR tự xếp mức ngay khi mở, ghi vào mục "Mức" của MR template. Người review có quyền nâng mức, không được hạ.

| Mức | Khi nào | Ai duyệt | Số người duyệt |
| --- | --- | --- | --- |
| **Thường** | Tính năng hoặc lỗi trong phạm vi một module, không đổi schema, không thêm thư viện, không đụng phân quyền hay thanh toán | Một dev khác trong team (theo lịch xoay vòng) | 1 |
| **Rủi ro cao** | Có migration hoặc đổi schema; thêm hoặc nâng thư viện; đụng phân quyền, đăng nhập, thanh toán, dữ liệu khách hàng; sửa API dùng chung; thay đổi cấu trúc thư mục | Tech Lead, **cộng thêm** một dev khác | 2 |
| **Hạ tầng** | Jenkinsfile, Dockerfile, docker-compose, cấu hình Kubernetes, `.claude/settings.json`, `CLAUDE.md` | Bằng | 1 (Bằng) |

MR mức Hạ tầng không được do Claude tạo; dev tự làm bằng tay.

## 2. Điều kiện để merge (tất cả phải đạt)

GitLab chặn bằng cài đặt ở mục 6. Reviewer kiểm tra bằng mắt những điều còn lại.

**Máy kiểm tra**
- [ ] Pipeline Jenkins xanh trên commit cuối cùng của MR
- [ ] Đủ số người duyệt theo mức, người duyệt không phải người mở MR
- [ ] Mọi thread comment đã được resolve
- [ ] Nhánh đã cập nhật với `dev` mới nhất (không có conflict, không "behind")

**Người kiểm tra**
- [ ] MR liên kết đúng issue, có link đặc tả và thiết kế (với tính năng) hoặc bước tái hiện (với lỗi)
- [ ] Mỗi tiêu chí đạt trong issue có ít nhất một test, tên test ghi mã TC
- [ ] Không có test nào bị xóa, skip hay nới lỏng so với `dev`
- [ ] Diff chỉ gồm file trong kế hoạch đã duyệt; file ngoài kế hoạch có ghi lý do
- [ ] Không có thư viện mới ngoài kế hoạch; không lộ secret, không có cấu hình môi trường thật
- [ ] Báo cáo `reviewer` trong sổ bàn giao kết luận **CHỐT**; người review đã đọc báo cáo đó
- [ ] Người mở MR đã tự chạy thử trên Dev theo từng tiêu chí và ghi kết quả vào MR
- [ ] MR dưới 400 dòng thay đổi (không tính test và file sinh tự động). Lớn hơn thì tách MR, trừ khi Bằng đồng ý

## 3. Review làm gì, trong bao lâu

- **Thời hạn:** MR mở trước 14:00 thì review xong trong ngày; sau 14:00 thì trước 10:00 hôm sau. Quá hạn thì người mở MR nhắc trong buổi 9:30.
- **Người review** đọc theo thứ tự: issue và tiêu chí đạt → báo cáo `reviewer` trong sổ bàn giao → test → code. Đọc test trước code để biết MR có kiểm chứng đúng điều cần kiểm chứng không.
- **Comment** ghi rõ mức: **Chặn** (phải sửa mới merge), **Nên sửa** (sửa trong MR này hoặc mở issue mới, người review quyết), **Gợi ý** (tùy người mở MR). Comment mức Chặn phải nêu tiêu chí đạt hoặc rule nào bị vi phạm.
- **Người mở MR** sửa và trả lời từng comment; sửa xong thì nhấn resolve và ghi "đã sửa ở <commit>". Không resolve comment của người khác khi chưa sửa.
- Tối đa **2 vòng sửa**. Sang vòng 3 thì hai bên gọi nhau 15 phút thay vì comment tiếp; vẫn không chốt được thì Bằng quyết. Với vòng review nội bộ của Claude (sub agent reviewer), sau 2 vòng là `decider` phân xử và báo Bằng.
- Code do Claude viết review như code người viết: không nhẹ tay vì "AI viết", không nặng tay vì "AI viết". Kiểm kỹ thêm hai chỗ AI hay mắc: test chỉ để pass, và sửa lan ra ngoài phạm vi.

## 4. Cách merge

- **Squash merge**, một commit cho một MR. Tiêu đề commit lấy từ tiêu đề MR: `[<tính năng>] <việc> (#<số issue>)`. Nội dung commit gồm dòng `Closes #<số issue>`.
- **Người duyệt cuối cùng là người bấm merge**, không phải người mở MR. Với mức Rủi ro cao, Tech Lead bấm.
- Merge xong: xóa nhánh nguồn (GitLab tự làm), chuyển issue sang **Ready for test**, dán link MR vào dòng việc trên Lark Base và đổi trạng thái sang "Chờ test".
- Không merge sau **17:00 thứ Sáu** trừ lỗi mức Nghiêm trọng, để không ai phải sửa `dev` cuối tuần.
- Không bao giờ push thẳng lên `dev`, không force push, không "merge tạm để test". Muốn test chung thì Test kéo nhánh feature về chạy.

## 4a. Push code hằng ngày

Code chỉ nằm trên máy một người là code chưa tồn tại với team. Mỗi nhánh `feature/` và `fix/` đang làm phải được **push lên GitLab ít nhất một lần mỗi ngày, trước 17:00**, kể cả khi chưa xong.

- **Commit dở được phép trên nhánh feature/fix**, tiền tố `wip(#<Mã>): <đang làm gì>`. Khi merge sẽ squash nên lịch sử `dev` không bị bẩn. Commit dở không được chứa test bị skip hay code comment-out để "cho pass".
- **Ai push:** dev push trong ngày khi làm việc trực tiếp; Claude push lúc kết thúc lượt chạy qua đêm (trước khi ghi Ghi chú Claude), và push sau mỗi bước có commit trong `/feature`, `/bugfix`. `settings.json` chỉ chặn push lên `dev` và `main`, push nhánh feature/fix được phép.
- **17:00 báo cáo cuối ngày** ghi link commit cuối cùng của từng nhánh đang làm. Nhánh có commit mới trên máy mà chưa push là chưa báo cáo xong.
- **Nhánh không có push trong 2 ngày làm việc** thì PM hỏi trong buổi 9:30: còn làm không, hay đóng task. Nhánh quá 5 ngày không push thì Bằng xóa nhánh trên GitLab sau khi báo người phụ trách.
- **Không push bằng force** lên nhánh đã có người khác kéo về; cần sửa lịch sử thì tạo nhánh mới.
- Mỗi sáng trước khi làm tiếp, kéo `dev` mới nhất về nhánh của mình (`git merge dev` hoặc rebase nếu nhánh chưa ai kéo). Conflict thì xử lý ngay, không để dồn tới lúc mở MR.

## 5. Khi `dev` hỏng sau merge

- Pipeline `dev` đỏ hoặc Test báo luồng chính không chạy được: **revert trong vòng 1 giờ**, không sửa đè. Người merge chịu trách nhiệm revert; ai thấy trước thì báo trong nhóm Lark dự án.
- Revert xong, mở lại issue, gắn nhãn `bug`, ghi rõ nguyên nhân vào comment. Sửa trên nhánh mới và đi lại quy trình MR từ đầu.
- Hai lần revert cùng một nguyên nhân thì ghi bài học vào `CLAUDE.md` và, nếu là lỗ hổng review, thêm vào checklist mục 2.

## 6. Cài đặt GitLab để quy trình được công cụ chặn

Bằng cài một lần trong Settings → Repository → Protected branches và Merge requests. Không ai được tự nới.

| Cài đặt | Giá trị |
| --- | --- |
| Protected branch `dev` | Allowed to push: **No one**. Allowed to merge: **Maintainers** |
| Protected branch `main` | Allowed to push: No one. Allowed to merge: Bằng |
| Force push | Tắt trên `dev` và `main` |
| Merge request approvals | Tối thiểu **1**; rule riêng cho mức Rủi ro cao: **2**, trong đó bắt buộc có Tech Lead (dùng Code Owners cho các thư mục nhạy cảm) |
| Prevent approval by author | Bật |
| Remove all approvals when commits are added | Bật |
| Pipelines must succeed | Bật |
| All threads must be resolved | Bật |
| Merge method | Squash commits, bắt buộc |
| Delete source branch | Mặc định bật |
| Token GitLab cấp cho Claude | Vai trò **Developer**, không có quyền merge vào nhánh protected |

File `CODEOWNERS` (đặt tại gốc repo) để GitLab tự yêu cầu Tech Lead duyệt khi MR đụng thư mục nhạy cảm:

```
# Thư mục nhạy cảm: bắt buộc Tech Lead duyệt (nhóm GitLab @tech-lead)
/migrations/        @tech-lead
/src/auth/          @tech-lead
/src/payment/       @tech-lead
Jenkinsfile         @banglc
Dockerfile          @banglc
docker-compose*     @banglc
/k8s/               @banglc
/.claude/           @banglc
CLAUDE.md           @banglc
```

Điền lại đường dẫn và tên tài khoản GitLab cho đúng repo thật.

## 8. Review tự động: kiểm tra theo rule, chỉ tự cho qua lỗi nhỏ

Mỗi MR được review tự động hai lớp trước khi đến tay người review. Lớp 1 là script, lớp 2 là Claude. Review tự động **không thay người duyệt**, nó chỉ lọc bớt việc: MR sạch thì người review xác nhận nhanh; MR có vấn đề thì người mở MR sửa trước khi ai phải đọc.

**Lớp 1: hình thức, chạy bằng `scripts/check-mr.sh`** (stage "Kiểm tra MR" trong Jenkins, chạy trên mỗi push vào MR). Sai một điểm là pipeline đỏ và MR không merge được:

| Rule | Mẫu đúng |
| --- | --- |
| Tên nhánh | `feature/<số issue>-<tên ngắn>` hoặc `fix/<số issue>-<tên ngắn>`, chữ thường, dấu gạch ngang |
| Tiêu đề MR | `[<tính năng>] <việc> (#<số issue>)`, dưới 100 ký tự, số issue trùng với tên nhánh |
| Mô tả MR | Đủ các mục của template, đã chọn mức, có `Closes #`, bảng TC có ít nhất một dòng, không còn chỗ `<...>`, checklist tick hết |
| Nhãn | `feature::<tính năng>` cho nhánh feature, `bug` cho nhánh fix |
| Test | Không có `skip`, `only`, `xit` thêm vào so với `dev` |

Khi script chặn, `/mr-review` gọi `decider`: lỗi hình thức sửa được (tên nhánh, tiêu đề, mô tả, nhãn) thì Claude tự sửa và chạy lại, không làm phiền người. Script còn in **cảnh báo** (không chặn) khi diff trên 400 dòng, khi MR đụng file hạ tầng, hoặc khi có test bị xóa. Người review phải đọc các cảnh báo này.

**Lớp 2: nội dung, chạy bằng `/mr-review <số MR>`** (dev hoặc Jenkins gọi sau khi lớp 1 đạt). Claude dùng sub agent `reviewer`, kiểm thêm mức MR có khai đúng không và mô tả có khớp diff không, rồi xếp mỗi vấn đề vào một trong ba mức:

| Mức | Là gì | Ví dụ | Tự cho qua? |
| --- | --- | --- | --- |
| **Gợi ý** (lỗi nhỏ) | Không đổi hành vi, không ảnh hưởng người dùng, sửa hay không đều được | Tên biến chưa rõ; comment thừa; có thể gộp hai hàm; thứ tự import; log debug còn sót nhưng không in dữ liệu nhạy cảm | **Có** |
| **Nên sửa** | Đúng nhưng chưa tốt, hoặc có rủi ro về sau | Thiếu xử lý trạng thái rỗng ở luồng phụ; lặp code đã có sẵn; truy vấn N+1 ở màn hình ít dùng; test có nhưng chỉ kiểm trường hợp chạy đúng; mô tả MR ít hơn diff | Không, cần người xem |
| **Chặn** | Sai tiêu chí đạt, sai rule, hoặc nguy hiểm | Thiếu test cho một TC; test bị nới lỏng; file ngoài kế hoạch không ghi lý do; thư viện mới; lộ secret; thiếu phân quyền; khai mức MR thấp hơn thực tế; test hoặc lint fail | Không, phải sửa |

Kết luận của Claude và việc tiếp theo:

| Kết luận | Điều kiện | Nhãn | Người review làm gì |
| --- | --- | --- | --- |
| **QUA** | Chỉ có Gợi ý, hoặc không có gì | `review::qua` | Đọc tóm tắt, xác nhận, merge. Gợi ý sửa hay không tùy người mở MR |
| **CẦN NGƯỜI XEM** | Có Nên sửa, không có Chặn | `review::can-xem` | Quyết sửa trong MR này hay mở issue mới |
| **CHẶN** | Có Chặn | `review::chan` | Không đọc tiếp. Người mở MR sửa và đẩy lại |

Ba ranh giới không được vượt:
- **Chỉ Gợi ý mới được tự cho qua.** Một vấn đề Nên sửa là đủ để chuyển sang Cần người xem. Khi Claude phân vân giữa hai mức, phải chọn mức cao hơn.
- **QUA của Claude không phải approval.** Nhãn `review::qua` chỉ rút ngắn thời gian đọc; người duyệt theo mức ở mục 1 vẫn phải approve và bấm merge. GitLab không được cấu hình cho bot approve.
- **Claude không sửa, không approve, không merge trên MR.** Chỉ comment và đổi nhãn `review::*`.

Theo dõi hằng tuần: Bằng xem tỷ lệ MR Claude kết luận QUA mà người review vẫn tìm ra vấn đề Nên sửa trở lên. Trên 1 trong 10 MR thì rule phân mức đang quá lỏng, siết lại bảng trên và ghi ví dụ vào CLAUDE.md.

## 9. Tóm tắt một dòng cho dev

Mở MR đúng mức → script và `/mr-review` lọc trước → người khác review trong ngày → đủ điều kiện mục 2 → người duyệt squash merge → issue sang Ready for test. `dev` hỏng thì revert trong 1 giờ.
