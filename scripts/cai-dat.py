#!/usr/bin/env python3
"""Cài hoặc cập nhật bộ quy trình claude-dev-workflow vào một repo dự án hoặc một thư mục chung chứa nhiều repo.

Cách dùng (chạy từ bất kỳ đâu):
  python3 ~/claude-dev-workflow/scripts/cai-dat.py [đường dẫn]              # cài / cập nhật
  python3 ~/claude-dev-workflow/scripts/cai-dat.py --kiem-tra [đường dẫn]   # chỉ kiểm tra, không ghi gì
Tùy chọn:
  --khong-pull     không kéo bản mới của bộ cài trước khi chạy
  --ca-repo-con    (thư mục chung) cài thêm MR template, check-mr.sh, .gitignore vào từng repo con

MCP Lark: dùng server đã kết nối sẵn trên máy (tên tùy máy); script áp luật chặn/cho phép theo đúng
tên đó vào .claude/settings.local.json. Không ghi .mcp.json.

Đường dẫn mặc định là thư mục hiện tại.
  - Là repo git (hoặc nằm trong repo git): cài vào gốc repo đó (chế độ repo).
  - Không phải git: cài vào chính thư mục đó, dùng chung cho mọi repo con bên trong (chế độ thư mục chung).
Script không commit, không push.
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
SKIP_DIRS = {"node_modules", ".git", ".claude", "dist", "build", ".venv", "vendor"}
DOC_REF = re.compile(r"(?<![\w/.-])(" + "|".join(d[:-3] for d in DOCS) + r")\.md")
KNOWN_TOKENS = {"<Mã>", "<Mã task>", "<Mã lỗi>", "<số issue>", "<tên ngắn>"}

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
    """Ở nơi cài, tài liệu quy trình nằm trong docs/claude-workflow/: sửa đường dẫn cho khớp."""
    return DOC_REF.sub(lambda m: f"{DOCS_DIR}/{m.group(1)}.md", text)


def rel(path, base):
    return os.path.relpath(path, base)


def copy_text(src_rel, dst_rel, root, rewrite=True, check=False, label_base=None):
    src = os.path.join(KIT, src_rel)
    dst = os.path.join(root, dst_rel)
    shown = rel(dst, label_base or root)
    new = read(src)
    if rewrite:
        new = rewrite_refs(new)
    old = read(dst) if os.path.exists(dst) else None
    if old == new:
        say("giữ", shown)
        return
    if check:
        say("THIẾU" if old is None else "KHÁC", f"{shown} (chạy cài đặt để cập nhật)")
        return
    write(dst, new)
    say("mới" if old is None else "cập nhật", shown)


def copy_binary(src_rel, dst_rel, root, check=False):
    src = os.path.join(KIT, src_rel)
    dst = os.path.join(root, dst_rel)
    same = os.path.exists(dst) and open(src, "rb").read() == open(dst, "rb").read()
    if same:
        say("giữ", dst_rel)
    elif check:
        say("THIẾU" if not os.path.exists(dst) else "KHÁC", dst_rel)
    else:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        say("mới", dst_rel)


def merge_settings(root, check=False):
    """settings.json: giữ cấu hình sẵn có, thêm mọi luật deny của bộ cài."""
    kit = json.loads(read(os.path.join(KIT, ".claude/settings.json")))
    dst = os.path.join(root, ".claude/settings.json")
    cur = json.loads(read(dst)) if os.path.exists(dst) else {}
    deny = cur.setdefault("permissions", {}).setdefault("deny", [])
    missing = [r for r in kit["permissions"]["deny"] if r not in deny]
    # hook: thêm các hook của bộ cài còn thiếu (so theo lệnh), giữ hook riêng của repo
    hooks = cur.setdefault("hooks", {})
    have = {h.get("command") for ev in hooks.values() for g in ev for h in g.get("hooks", [])}
    new_groups = []
    for ev, groups in kit.get("hooks", {}).items():
        for g in groups:
            if any(h.get("command") not in have for h in g.get("hooks", [])):
                new_groups.append((ev, g))
    if not missing and not new_groups:
        say("giữ", ".claude/settings.json (đủ luật chặn và hook)")
    elif check:
        say("THIẾU", f".claude/settings.json thiếu {len(missing)} luật chặn, {len(new_groups)} hook")
    else:
        deny.extend(missing)
        for ev, g in new_groups:
            hooks.setdefault(ev, []).append(g)
        if not hooks:
            cur.pop("hooks")
        write(dst, json.dumps(cur, ensure_ascii=False, indent=2) + "\n")
        say("cập nhật", f".claude/settings.json (+{len(missing)} luật chặn, +{len(new_groups)} hook)")



def repo_table(root, repos):
    lines = ["| Repo | Đường dẫn | Vai trò | Lệnh test |", "| --- | --- | --- | --- |"]
    for r in repos:
        lines.append(f"| {os.path.basename(r)} | `{rel(r, root)}/` | <vai trò> | `<lệnh>` |")
    return "\n".join(lines)


def ensure_claude_md(root, workspace, repos, check=False):
    dst = os.path.join(root, "CLAUDE.md")
    if not os.path.exists(dst):
        if check:
            say("THIẾU", "CLAUDE.md")
            return
        if workspace:
            text = read(os.path.join(KIT, "templates/CLAUDE-THU-MUC-CHUNG.md"))
            text = text.replace("<<BANG_REPO>>", repo_table(root, repos) if repos else
                                "| <repo> | `<đường dẫn>/` | <vai trò> | `<lệnh>` |")
        else:
            text = read(os.path.join(KIT, "templates/CLAUDE.md"))
        write(dst, text)
        say("mới", "CLAUDE.md (từ mẫu " + ("thư mục chung" if workspace else "repo") + "; điền các chỗ <...>)")
        return
    text = read(dst)
    if IMPORT_LINE not in text:
        if check:
            say("THIẾU", f"CLAUDE.md chưa có dòng {IMPORT_LINE}")
            return
        block = ("\n## Quy trình làm việc với Claude (do bộ claude-dev-workflow quản lý, không sửa tại đây)\n"
                 f"{IMPORT_LINE}\n")
        write(dst, text.rstrip("\n") + "\n" + block)
        say("cập nhật", "CLAUDE.md (+ dòng nạp quy trình chung, phần riêng giữ nguyên)")
        text = read(dst)
    else:
        say("giữ", "CLAUDE.md (đã nạp quy trình chung)")
    holes = sorted(set(re.findall(r"<[^<>\n`]{2,60}>", text)) - KNOWN_TOKENS)
    if holes:
        say("CẦN ĐIỀN", f"CLAUDE.md còn {len(holes)} chỗ trống, ví dụ {holes[0]}")
    if workspace:
        missing = [r for r in repos if f"`{rel(r, root)}/`" not in text]
        if missing:
            say("CẦN ĐIỀN", "CLAUDE.md chưa có trong bảng repo: " + ", ".join(rel(r, root) for r in missing))


def ensure_gitignore(root, check=False, label_base=None):
    dst = os.path.join(root, ".gitignore")
    shown = rel(dst, label_base or root)
    text = read(dst) if os.path.exists(dst) else ""
    have = {l.strip() for l in text.splitlines()}
    missing = [l for l in GITIGNORE_LINES if l not in have]
    if not missing:
        say("giữ", shown)
    elif check:
        say("THIẾU", f"{shown} thiếu {', '.join(missing)}")
    else:
        add = "\n# claude-dev-workflow\n" + "\n".join(missing) + "\n"
        write(dst, (text.rstrip("\n") + "\n" if text else "") + add)
        say("cập nhật", f"{shown} (+ {', '.join(missing)})")


def find_repos(root, depth=2):
    """Các repo git con trong thư mục chung, sâu tối đa 2 cấp."""
    found = []

    def walk(d, level):
        try:
            entries = sorted(os.scandir(d), key=lambda e: e.name)
        except OSError:
            return
        for e in entries:
            if not e.is_dir(follow_symlinks=False) or e.name in SKIP_DIRS or e.name.startswith("."):
                continue
            if os.path.exists(os.path.join(e.path, ".git")):
                found.append(e.path)
            elif level < depth:
                walk(e.path, level + 1)

    walk(root, 1)
    return found


def repo_level_files(repo, root, check):
    """Các thứ phải nằm trong từng repo vì GitLab/Jenkins đọc theo repo."""
    copy_text(".gitlab/merge_request_templates/Default.md", ".gitlab/merge_request_templates/Default.md",
              repo, check=check, label_base=root)
    copy_text("scripts/check-mr.sh", "scripts/check-mr.sh", repo, rewrite=False, check=check, label_base=root)
    if not check:
        os.chmod(os.path.join(repo, "scripts/check-mr.sh"), 0o755)
    ensure_gitignore(repo, check, label_base=root)


LARK_HINTS = ("lark", "ihouzz")
# Tool Lark được dùng không cần hỏi (đọc + 3 việc ghi được phép theo DAU-VAO-LARK-BASE.md mục 6)
LARK_ALLOW = [
    "base-v3-list-tables", "base-v3-list-records", "base-v3-get-record",
    "docx-get-raw-content", "docx-get-document", "docx-list-blocks",
    "drive-get-file-meta", "drive-list-comments", "drive-list-files",
    "sheets-get-spreadsheet", "sheets-list-sheets", "sheets-read-range", "contact-search-user",
    "base-v3-create-record", "base-v3-update-record", "drive-create-comment", "drive-reply-comment",
]


def tool_prefix(server_name):
    """Tên server MCP -> tiền tố tool trong Claude Code (ký tự lạ thành _)."""
    return "mcp__" + re.sub(r"[^A-Za-z0-9_-]", "_", server_name) + "__lark-api-ihouzz-"


def find_lark_servers(root):
    """Tìm server MCP Lark đã kết nối sẵn trên máy dev (tên server mỗi máy có thể khác)."""
    names = set()
    cfg = os.path.expanduser("~/.claude.json")
    if os.path.exists(cfg):
        try:
            data = json.loads(read(cfg))
            pools = [data.get("mcpServers", {})]
            for path, proj in (data.get("projects") or {}).items():
                if os.path.abspath(path) in (root, os.path.dirname(root)) or root.startswith(os.path.abspath(path) + os.sep):
                    pools.append(proj.get("mcpServers", {}))
            for pool in pools:
                for name, spec in pool.items():
                    blob = (name + " " + json.dumps(spec)).lower()
                    if any(h in blob for h in LARK_HINTS):
                        names.add(name)
        except (ValueError, OSError):
            pass
    if shutil.which("claude"):
        try:
            r = subprocess.run(["claude", "mcp", "list"], cwd=root, capture_output=True, text=True, timeout=90)
            for line in r.stdout.splitlines():
                m = re.match(r"^(.+?): (\S+).* - (.+)$", line.strip())
                if m and any(h in (m.group(1) + m.group(2)).lower() for h in LARK_HINTS):
                    names.add(m.group(1).strip())
        except (subprocess.TimeoutExpired, OSError):
            pass
    return sorted(names)


def setup_lark_mcp(root, check=False):
    """Dùng MCP Lark đã có trên máy; áp luật chặn/cho phép theo đúng tên server của máy này
    vào .claude/settings.local.json (không lên git, mỗi máy một bản)."""
    kit_deny = json.loads(read(os.path.join(KIT, ".claude/settings.json")))["permissions"]["deny"]
    blocked = sorted({r.split("__lark-api-ihouzz-", 1)[1] for r in kit_deny if "__lark-api-ihouzz-" in r})
    servers = find_lark_servers(root)
    if not servers:
        say("THIẾU", "MCP Lark trên máy: chưa thấy server nào. Thêm một lần cho mọi repo: "
            "claude mcp add --transport http --scope user lark-ihouzz <URL> "
            "--header \"Authorization: Bearer <token>\" (URL và token xin Tech Lead)")
        return
    say("có", "MCP Lark trên máy: " + ", ".join(servers))
    dst = os.path.join(root, ".claude/settings.local.json")
    cur = json.loads(read(dst)) if os.path.exists(dst) else {}
    perms = cur.setdefault("permissions", {})
    deny, allow = perms.setdefault("deny", []), perms.setdefault("allow", [])
    want_deny = [tool_prefix(s) + t for s in servers for t in blocked]
    want_allow = [tool_prefix(s) + t for s in servers for t in LARK_ALLOW]
    add_d = [r for r in want_deny if r not in deny]
    add_a = [r for r in want_allow if r not in allow]
    # Repo còn khai báo lark-ihouzz trong .mcp.json (bản cài cũ): tắt để khỏi trùng với server trên máy
    disable = []
    mcpf = os.path.join(root, ".mcp.json")
    if os.path.exists(mcpf) and "lark-ihouzz" in json.loads(read(mcpf)).get("mcpServers", {}) \
            and "lark-ihouzz" not in servers:
        if "lark-ihouzz" not in cur.get("disabledMcpjsonServers", []):
            disable = ["lark-ihouzz"]
    if not (add_d or add_a or disable):
        say("giữ", ".claude/settings.local.json (luật Lark theo tên server máy này)")
    elif check:
        say("THIẾU", f".claude/settings.local.json thiếu {len(add_d)} luật chặn, {len(add_a)} luật cho phép Lark")
    else:
        deny.extend(add_d)
        allow.extend(add_a)
        if disable:
            cur.setdefault("disabledMcpjsonServers", []).extend(disable)
        write(dst, json.dumps(cur, ensure_ascii=False, indent=2) + "\n")
        say("cập nhật", f".claude/settings.local.json (+{len(add_d)} chặn, +{len(add_a)} cho phép Lark"
            + (", tắt lark-ihouzz trong .mcp.json" if disable else "") + ")")


def check_machine():
    print("\nMáy của bạn:")
    for tool, hint in [("claude", "cài Claude Code"), ("glab", "brew install glab, rồi glab auth login"),
                       ("git", "cài git")]:
        say("có" if shutil.which(tool) else "THIẾU", tool if shutil.which(tool) else f"{tool}: {hint}")
    if shutil.which("glab"):
        r = subprocess.run(["glab", "auth", "status"], capture_output=True, text=True)
        say("có" if r.returncode == 0 else "THIẾU",
            "glab đã đăng nhập GitLab" if r.returncode == 0 else "glab chưa đăng nhập: glab auth login")


def main():
    args = sys.argv[1:]
    check = "--kiem-tra" in args
    no_pull = "--khong-pull" in args
    sub_repos = "--ca-repo-con" in args
    rest = [a for a in args if not a.startswith("--")]
    target = os.path.abspath(os.path.expanduser(rest[0] if rest else os.getcwd()))

    if not os.path.isdir(target):
        sys.exit(f"{target} không phải thư mục.")
    if target == KIT:
        sys.exit("Đang đứng trong chính repo bộ cài. Hãy cd vào repo dự án / thư mục chung, hoặc truyền đường dẫn.")
    if target in (os.path.expanduser("~"), "/"):
        sys.exit("Không cài vào thư mục home hoặc thư mục gốc. Chọn thư mục chứa các repo, ví dụ ~/Source/prophub.")

    code, top, _ = git(["rev-parse", "--show-toplevel"], target)
    workspace = code != 0
    root = target if workspace else top
    repos = find_repos(root) if workspace else []

    if not check and not no_pull:
        c, _, err = git(["pull", "--ff-only", "-q"], KIT)
        if c != 0:
            print(f"(Không kéo được bản mới của bộ cài, dùng bản đang có: {err.splitlines()[-1] if err else ''})")
    _, kit_rev, _ = git(["rev-parse", "--short", "HEAD"], KIT)

    mode = "thư mục chung" if workspace else "repo"
    print(f"{'Kiểm tra' if check else 'Cài'} claude-dev-workflow {kit_rev} vào {root} (chế độ {mode})\n")
    if workspace:
        print(f"Repo con tìm thấy ({len(repos)}): " + (", ".join(rel(r, root) for r in repos) or "không có") + "\n")
    elif not check:
        _, dirty, _ = git(["status", "--porcelain"], root)
        if dirty:
            print("Lưu ý: repo đang có thay đổi chưa commit; nên chạy trên nhánh sạch, ví dụ chore/claude-workflow.\n")

    for d in ("agents", "commands"):
        for f in sorted(os.listdir(os.path.join(KIT, ".claude", d))):
            if f.endswith(".md"):
                copy_text(f".claude/{d}/{f}", f".claude/{d}/{f}", root, check=check)
    for f in sorted(os.listdir(os.path.join(KIT, ".claude", "hooks"))):
        if f.endswith(".py"):
            copy_text(f".claude/hooks/{f}", f".claude/hooks/{f}", root, rewrite=False, check=check)
            if not check:
                os.chmod(os.path.join(root, ".claude/hooks", f), 0o755)
    merge_settings(root, check)
    setup_lark_mcp(root, check)
    for d in DOCS:
        copy_text(d, f"{DOCS_DIR}/{d}", root, check=check)
    for img in IMAGES:
        copy_binary(f"docs/{img}", f"{DOCS_DIR}/{img}", root, check=check)
    ensure_claude_md(root, workspace, repos, check)

    if not workspace:
        repo_level_files(root, root, check)
    elif sub_repos or check:
        print("\nTừng repo con (MR template, check-mr.sh, .gitignore):")
        for r in repos:
            repo_level_files(r, root, check)

    vf = os.path.join(root, VERSION_FILE)
    installed = read(vf).split()[0] if os.path.exists(vf) else None
    if check:
        print()
        say("phiên bản", f"đang dùng {installed or 'chưa cài'}, bộ cài mới nhất {kit_rev}")
    else:
        write(vf, f"{kit_rev} {datetime.date.today().isoformat()}\n")

    check_machine()

    problems = [l for l in log_lines if "[THIẾU]" in l or "[KHÁC]" in l or "[CẦN ĐIỀN]" in l]
    print()
    if check:
        print("Đạt." if not problems else f"Còn {len(problems)} việc, xem các dòng THIẾU / KHÁC / CẦN ĐIỀN ở trên.")
    elif workspace:
        print("Xong. Việc tiếp theo:\n"
              "  1. Điền CLAUDE.md của thư mục chung: vai trò và lệnh test của từng repo trong bảng\n"
              "  2. Luôn mở Claude Code tại thư mục chung này (không mở trong repo con), gõ /agents và /mcp để kiểm tra\n"
              + ("" if sub_repos else
                 "  3. MR template và check-mr.sh phải nằm trong từng repo: chạy lại với --ca-repo-con, rồi commit\n"
                 "     trong từng repo con qua MR mức Hạ tầng\n")
              + "  Thư mục chung không có git: muốn đồng bộ cho cả team thì mỗi người tự chạy script trên máy mình.")
    else:
        print("Xong. Việc tiếp theo:\n"
              "  1. git status && git diff  — xem lại thay đổi\n"
              "  2. Điền các chỗ <...> trong CLAUDE.md (stack, lệnh test, quy ước code)\n"
              "  3. Mở Claude Code trong repo, gõ /agents (thấy 6 agent) và /mcp (MCP Lark connected)\n"
              "  4. Commit trên nhánh riêng, mở MR mức Hạ tầng cho Tech Lead duyệt")
    sys.exit(1 if (check and problems) else 0)


if __name__ == "__main__":
    main()
