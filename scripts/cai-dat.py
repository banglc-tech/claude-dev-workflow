#!/usr/bin/env python3
"""Cài hoặc cập nhật bộ quy trình claude-dev-workflow vào một repo dự án.

Cách dùng (chạy từ bất kỳ đâu):
  python3 ~/claude-dev-workflow/scripts/cai-dat.py [đường dẫn repo dự án]      # cài / cập nhật
  python3 ~/claude-dev-workflow/scripts/cai-dat.py --kiem-tra [đường dẫn repo]  # chỉ kiểm tra, không ghi gì
  thêm --khong-pull nếu không muốn kéo bản mới của bộ cài trước khi chạy.

Mặc định repo dự án là thư mục hiện tại. Script không commit, không push: xem `git status`
rồi mở MR như mọi thay đổi khác (mức Hạ tầng, Tech Lead duyệt).
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = "docs/claude-workflow"
DOCS = ["CLAUDE-QUY-TRINH.md", "HUONG-DAN.md", "QUY-TRINH-MERGE.md", "DAU-VAO-LARK-BASE.md", "CAI-DAT.md"]
IMAGES = ["luu-do-tong-quan.png", "luu-do-chi-tiet.png", "luu-do-sub-agent.png"]
IMPORT_LINE = "@docs/claude-workflow/CLAUDE-QUY-TRINH.md"
GITIGNORE_LINES = [".bangiao/", ".claude/settings.local.json"]
VERSION_FILE = ".claude/claude-dev-workflow.version"
DOC_REF = re.compile(r"(?<![\w/.-])(" + "|".join(d[:-3] for d in DOCS) + r")\.md")

log_lines = []


def say(kind, msg):
    line = f"  [{kind}] {msg}"
    log_lines.append(line)
    print(line)


def git(args, cwd):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, text):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def rewrite_refs(text):
    """Trong repo dự án, tài liệu quy trình nằm ở docs/claude-workflow/: sửa đường dẫn cho khớp."""
    return DOC_REF.sub(lambda m: f"{DOCS_DIR}/{m.group(1)}.md", text)


def copy_text(src_rel, dst_rel, repo, rewrite=True, check=False):
    src = os.path.join(KIT, src_rel)
    dst = os.path.join(repo, dst_rel)
    new = read(src)
    if rewrite:
        new = rewrite_refs(new)
    old = read(dst) if os.path.exists(dst) else None
    if old == new:
        say("giữ", dst_rel)
        return
    if check:
        say("THIẾU" if old is None else "KHÁC", f"{dst_rel} (chạy cài đặt để cập nhật)")
        return
    write(dst, new)
    say("mới" if old is None else "cập nhật", dst_rel)


def copy_binary(src_rel, dst_rel, repo, check=False):
    src = os.path.join(KIT, src_rel)
    dst = os.path.join(repo, dst_rel)
    same = os.path.exists(dst) and open(src, "rb").read() == open(dst, "rb").read()
    if same:
        say("giữ", dst_rel)
    elif check:
        say("THIẾU" if not os.path.exists(dst) else "KHÁC", dst_rel)
    else:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        say("mới", dst_rel)


def merge_settings(repo, check=False):
    """settings.json: giữ cấu hình riêng của repo, thêm mọi luật deny của bộ cài."""
    kit = json.loads(read(os.path.join(KIT, ".claude/settings.json")))
    dst = os.path.join(repo, ".claude/settings.json")
    cur = json.loads(read(dst)) if os.path.exists(dst) else {}
    perms = cur.setdefault("permissions", {})
    deny = perms.setdefault("deny", [])
    missing = [r for r in kit["permissions"]["deny"] if r not in deny]
    if not missing:
        say("giữ", ".claude/settings.json (đủ luật chặn)")
        return
    if check:
        say("THIẾU", f".claude/settings.json thiếu {len(missing)} luật chặn")
        return
    deny.extend(missing)
    write(dst, json.dumps(cur, ensure_ascii=False, indent=2) + "\n")
    say("cập nhật", f".claude/settings.json (+{len(missing)} luật chặn)")


def merge_mcp(repo, check=False):
    kit = json.loads(read(os.path.join(KIT, ".mcp.json")))
    dst = os.path.join(repo, ".mcp.json")
    cur = json.loads(read(dst)) if os.path.exists(dst) else {}
    servers = cur.setdefault("mcpServers", {})
    if "lark-ihouzz" in servers:
        url = servers["lark-ihouzz"].get("url", "")
        if url.startswith("<"):
            say("CẦN ĐIỀN", ".mcp.json: URL MCP Lark còn là chỗ trống, hỏi Tech Lead")
        else:
            say("giữ", ".mcp.json (đã có lark-ihouzz)")
        return
    if check:
        say("THIẾU", ".mcp.json chưa khai báo lark-ihouzz")
        return
    servers["lark-ihouzz"] = kit["mcpServers"]["lark-ihouzz"]
    write(dst, json.dumps(cur, ensure_ascii=False, indent=2) + "\n")
    say("cập nhật", ".mcp.json (+ lark-ihouzz)")


def ensure_claude_md(repo, check=False):
    dst = os.path.join(repo, "CLAUDE.md")
    if not os.path.exists(dst):
        if check:
            say("THIẾU", "CLAUDE.md")
            return
        write(dst, read(os.path.join(KIT, "templates/CLAUDE.md")))
        say("mới", "CLAUDE.md (từ mẫu; điền các chỗ <...>)")
        return
    text = read(dst)
    if IMPORT_LINE not in text:
        if check:
            say("THIẾU", f"CLAUDE.md chưa có dòng {IMPORT_LINE}")
            return
        block = ("\n## Quy trình làm việc với Claude (do bộ claude-dev-workflow quản lý, không sửa tại đây)\n"
                 f"{IMPORT_LINE}\n")
        write(dst, text.rstrip("\n") + "\n" + block)
        say("cập nhật", "CLAUDE.md (+ dòng nạp quy trình chung, phần riêng của repo giữ nguyên)")
    else:
        say("giữ", "CLAUDE.md (đã nạp quy trình chung)")
    holes = sorted(set(re.findall(r"<[^<>\n]{2,60}>", text)) - {"<Mã>", "<Mã task>", "<Mã lỗi>"})
    if holes:
        say("CẦN ĐIỀN", f"CLAUDE.md còn {len(holes)} chỗ trống, ví dụ {holes[0]}")


def ensure_gitignore(repo, check=False):
    dst = os.path.join(repo, ".gitignore")
    text = read(dst) if os.path.exists(dst) else ""
    have = {l.strip() for l in text.splitlines()}
    missing = [l for l in GITIGNORE_LINES if l not in have]
    if not missing:
        say("giữ", ".gitignore")
    elif check:
        say("THIẾU", f".gitignore thiếu {', '.join(missing)}")
    else:
        add = "\n# claude-dev-workflow\n" + "\n".join(missing) + "\n"
        write(dst, (text.rstrip("\n") + "\n" if text else "") + add)
        say("cập nhật", f".gitignore (+ {', '.join(missing)})")


def check_machine():
    print("\nMáy của bạn:")
    for tool, hint in [("claude", "cài Claude Code"), ("glab", "brew install glab, rồi glab auth login"),
                       ("git", "cài git")]:
        if shutil.which(tool):
            say("có", tool)
        else:
            say("THIẾU", f"{tool}: {hint}")
    if shutil.which("glab"):
        r = subprocess.run(["glab", "auth", "status"], capture_output=True, text=True)
        say("có" if r.returncode == 0 else "THIẾU", "glab đã đăng nhập GitLab" if r.returncode == 0
            else "glab chưa đăng nhập: glab auth login")
    if os.environ.get("LARK_MCP_TOKEN"):
        say("có", "biến LARK_MCP_TOKEN")
    else:
        say("THIẾU", "biến LARK_MCP_TOKEN: thêm export LARK_MCP_TOKEN=... vào ~/.zshrc (token xin Tech Lead)")


def main():
    args = [a for a in sys.argv[1:]]
    check = "--kiem-tra" in args
    no_pull = "--khong-pull" in args
    rest = [a for a in args if not a.startswith("--")]
    repo = os.path.abspath(rest[0] if rest else os.getcwd())

    if os.path.abspath(repo) == KIT:
        sys.exit("Đang đứng trong chính repo bộ cài. Hãy cd vào repo dự án hoặc truyền đường dẫn repo dự án.")
    code, top, _ = git(["rev-parse", "--show-toplevel"], repo)
    if code != 0:
        sys.exit(f"{repo} không phải repo git.")
    repo = top

    if not check and not no_pull:
        c, _, err = git(["pull", "--ff-only", "-q"], KIT)
        if c != 0:
            print(f"(Không kéo được bản mới của bộ cài, dùng bản đang có: {err.splitlines()[-1] if err else ''})")
    _, kit_rev, _ = git(["rev-parse", "--short", "HEAD"], KIT)

    if not check:
        _, dirty, _ = git(["status", "--porcelain"], repo)
        if dirty:
            print("Lưu ý: repo dự án đang có thay đổi chưa commit; thay đổi của bộ cài sẽ lẫn vào. "
                  "Nên chạy trên nhánh sạch, ví dụ chore/claude-workflow.")

    print(f"{'Kiểm tra' if check else 'Cài'} claude-dev-workflow {kit_rev} vào {repo}\n")
    for d in ("agents", "commands"):
        for f in sorted(os.listdir(os.path.join(KIT, ".claude", d))):
            if f.endswith(".md"):
                copy_text(f".claude/{d}/{f}", f".claude/{d}/{f}", repo, check=check)
    merge_settings(repo, check)
    merge_mcp(repo, check)
    copy_text(".gitlab/merge_request_templates/Default.md", ".gitlab/merge_request_templates/Default.md", repo, check=check)
    copy_text("scripts/check-mr.sh", "scripts/check-mr.sh", repo, rewrite=False, check=check)
    if not check:
        os.chmod(os.path.join(repo, "scripts/check-mr.sh"), 0o755)
    for d in DOCS:
        copy_text(d, f"{DOCS_DIR}/{d}", repo, check=check)
    for img in IMAGES:
        copy_binary(f"docs/{img}", f"{DOCS_DIR}/{img}", repo, check=check)
    ensure_claude_md(repo, check)
    ensure_gitignore(repo, check)

    vf = os.path.join(repo, VERSION_FILE)
    installed = read(vf).split()[0] if os.path.exists(vf) else None
    if check:
        say("phiên bản", f"repo đang dùng {installed or 'chưa cài'}, bộ cài mới nhất {kit_rev}")
    else:
        write(vf, f"{kit_rev} {datetime.date.today().isoformat()}\n")

    check_machine()

    problems = [l for l in log_lines if "[THIẾU]" in l or "[KHÁC]" in l or "[CẦN ĐIỀN]" in l]
    print()
    if check:
        print("Đạt." if not problems else f"Còn {len(problems)} việc, xem các dòng THIẾU / KHÁC / CẦN ĐIỀN ở trên.")
    else:
        print("Xong. Việc tiếp theo:\n"
              "  1. git status && git diff  — xem lại thay đổi\n"
              "  2. Điền các chỗ <...> trong CLAUDE.md (stack, lệnh test, quy ước code)\n"
              "  3. Mở Claude Code trong repo, gõ /agents (thấy 6 agent) và /mcp (lark-ihouzz connected)\n"
              "  4. Commit trên nhánh riêng, mở MR mức Hạ tầng cho Tech Lead duyệt")
    sys.exit(1 if (check and problems) else 0)


if __name__ == "__main__":
    main()
