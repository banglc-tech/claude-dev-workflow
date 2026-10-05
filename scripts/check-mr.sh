#!/usr/bin/env bash
# Kiểm tra hình thức MR trước khi review nội dung. Chạy trong Jenkins (stage "Kiểm tra MR")
# hoặc tại máy: scripts/check-mr.sh <nhánh nguồn> <tiêu đề MR> <file chứa mô tả MR> [nhãn, cách nhau bằng dấu phẩy]
# Exit 0 = đạt; exit 1 = Chặn (in lý do). Mỗi lỗi một dòng, bắt đầu bằng CHẶN:.
set -u
BRANCH="${1:-}"; TITLE="${2:-}"; DESC_FILE="${3:-}"; LABELS="${4:-}"
fail=0
chan() { echo "CHẶN: $1"; fail=1; }

# 1. Tên nhánh: feature/<số issue>-<tên ngắn> hoặc fix/<số issue>-<tên ngắn>; chữ thường, số, dấu gạch
if ! [[ "$BRANCH" =~ ^(feature|fix)/[0-9]+-[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  chan "tên nhánh '$BRANCH' sai mẫu. Đúng: feature/<số issue>-<tên ngắn> hoặc fix/<số issue>-<tên ngắn>, chữ thường và dấu gạch ngang."
fi
ISSUE_IN_BRANCH="$(echo "$BRANCH" | sed -E 's#^(feature|fix)/([0-9]+)-.*#\2#')"

# 2. Tiêu đề MR: [<tính năng>] <việc> (#<số issue>)
TITLE_RE='^\[[^]]+\] .+ \(#([0-9]+)\)$'
if ! [[ "$TITLE" =~ $TITLE_RE ]]; then
  chan "tiêu đề MR sai mẫu. Đúng: [<tính năng>] <việc> (#<số issue>)."
else
  ISSUE_IN_TITLE="${BASH_REMATCH[1]}"
  [[ "$ISSUE_IN_TITLE" == "$ISSUE_IN_BRANCH" ]] || chan "số issue trong tiêu đề (#$ISSUE_IN_TITLE) khác số issue trong tên nhánh (#$ISSUE_IN_BRANCH)."
fi
[[ ${#TITLE} -le 100 ]] || chan "tiêu đề MR dài hơn 100 ký tự."

# 3. Mô tả MR theo template
if [[ -z "$DESC_FILE" || ! -f "$DESC_FILE" ]]; then
  chan "không đọc được mô tả MR."
else
  DESC="$(cat "$DESC_FILE")"
  grep -qE "^Base: https://ihouzz-com\.sg\.larksuite\.com/base/" <<<"$DESC" || chan "mô tả thiếu dòng 'Base: <link bản ghi trên BLUEMARQ-ONE>'."
  grep -qE "^## Mức" <<<"$DESC" || chan "mô tả thiếu mục '## Mức'."
  grep -qE "^- \[x\] (Thường|Rủi ro cao|Hạ tầng)" <<<"$DESC" || chan "chưa chọn mức MR (tick một ô trong mục Mức)."
  grep -qE "^## Tiêu chí đạt" <<<"$DESC" || chan "mô tả thiếu bảng 'Tiêu chí đạt → test'."
  grep -qE "^\| TC[0-9]+ \|" <<<"$DESC" || chan "bảng tiêu chí đạt chưa có dòng TC nào."
  grep -qE "^## Kết quả chạy thử trên Dev" <<<"$DESC" || chan "mô tả thiếu mục 'Kết quả chạy thử trên Dev'."
  grep -qE "<[^>]+>" <<<"$DESC" && grep -qE "<(số issue|Mã|link bản ghi trên BLUEMARQ-ONE|link Claude Docs|link Claude Design|tên test|2–5 dòng|rủi ro, chỗ cần xem kỹ|từng tiêu chí: đạt / không đạt)>" <<<"$DESC" \
    && chan "mô tả còn chỗ giữ chỗ '<...>' chưa điền."
  if grep -qE "^- \[x\] Thường" <<<"$DESC"; then
    grep -qE "Đặc tả: https?://" <<<"$DESC" || grep -qE "^- \[x\].*bug" <<<"$DESC" || true
  fi
  # Checklist: mọi ô trong mục Checklist phải được tick
  UNCHECKED="$(awk '/^## Checklist/{f=1;next} /^## /{f=0} f && /^- \[ \]/' <<<"$DESC" | wc -l | tr -d ' ')"
  [[ "$UNCHECKED" == "0" ]] || chan "checklist còn $UNCHECKED ô chưa tick."
fi

# 4. Nhãn
if [[ "$BRANCH" == fix/* ]]; then
  grep -qE "(^|,)bug(,|$)" <<<"$LABELS" || chan "nhánh fix/ phải có nhãn 'bug'."
else
  grep -qE "(^|,)feature::[^,]+" <<<"$LABELS" || chan "nhánh feature/ phải có nhãn 'feature::<tính năng>'."
fi

# 5. Kích thước diff (không tính test và file sinh tự động), cần có origin/dev
if git rev-parse --verify -q origin/dev >/dev/null 2>&1; then
  LINES="$(git diff --numstat origin/dev...HEAD -- . ':(exclude)*test*' ':(exclude)*spec*' ':(exclude)*.lock' ':(exclude)*.snap' ':(exclude)*.min.*' \
    | awk '{a+=$1+$2} END{print a+0}')"
  if (( LINES > 400 )); then
    echo "CẢNH BÁO: diff $LINES dòng (>400). Cần Bằng đồng ý hoặc tách MR."
  fi
  # 6. File cấm
  git diff --name-only origin/dev...HEAD | grep -E '^(Jenkinsfile|Dockerfile|docker-compose.*|\.env.*|k8s/.*|\.claude/.*|CLAUDE\.md)$' \
    | while read -r f; do echo "CẢNH BÁO: MR sửa file hạ tầng '$f' → mức Hạ tầng, chỉ Bằng duyệt."; done
  # 7. Test bị xóa hoặc skip
  if git diff origin/dev...HEAD -- '*test*' '*spec*' | grep -E '^\-.*\b(it|test|describe)\(' >/dev/null; then
    echo "CẢNH BÁO: có test bị xóa hoặc đổi so với dev. Reviewer phải xem."
  fi
  if git diff origin/dev...HEAD | grep -E '^\+.*\b(it|test|describe)\.(skip|only)\(|^\+.*@pytest\.mark\.skip|^\+.*xit\(' >/dev/null; then
    chan "có test bị skip/only thêm vào. Không được nới lỏng test."
  fi
fi

if (( fail )); then echo "KẾT QUẢ: CHẶN — sửa các dòng CHẶN rồi đẩy lại."; exit 1; fi
echo "KẾT QUẢ: ĐẠT hình thức. Chuyển sang review nội dung."
