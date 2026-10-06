#!/usr/bin/env python3
"""Hook PreToolUse (Bash) của claude-dev-workflow: chặn thao tác git sai quy trình trước khi chạy.

Chặn (exit 2, lý do gửi lại cho Claude):
  - commit khi đang ở nhánh dev / main / master
  - commit có -m mà không đúng mẫu <loại>(#<Mã>): <mô tả>
  - push lên dev / main / master, push --force
  - push nhánh không đúng mẫu feature/<Mã>-<tên> hoặc fix/<Mã>-<tên>
  - push khi lệnh kiểm tra của repo (.claude/kiem-tra-truoc-push) báo lỗi
Không phân tích được lệnh thì cho qua: luật chặn quyền và GitLab protected branch vẫn còn đó.
"""
import json
import os
import re
import shlex
import subprocess
import sys

PROTECTED = {"dev", "main", "master"}
BRANCH_RE = re.compile(r"^(feature|fix)/[0-9]+-[a-z0-9]+(-[a-z0-9]+)*$")
COMMIT_RE = re.compile(r"^(feat|fix|wip|test|refactor|perf|docs|chore|style)\(#[0-9]+\): \S")
CHECK_FILE = ".claude/kiem-tra-truoc-push"


def block(msg):
    print("CHẶN bởi hook claude-dev-workflow: " + msg, file=sys.stderr)
    sys.exit(2)


def git(args, cwd):
    try:
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=20)
        return r.returncode, r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


def segments(command):
    """Tách chuỗi lệnh theo &&, ||, ;, | (bỏ qua phần trong nháy)."""
    out, cur, quote, i = [], "", None, 0
    while i < len(command):
        c = command[i]
        if quote:
            cur += c
            if c == quote:
                quote = None
        elif c in "'\"":
            quote, cur = c, cur + c
        elif command.startswith("&&", i) or command.startswith("||", i):
            out.append(cur); cur = ""; i += 1
        elif c in ";|\n":
            out.append(cur); cur = ""
        else:
            cur += c
        i += 1
    out.append(cur)
    return [s.strip() for s in out if s.strip()]


def check_commit(words, cwd):
    code, branch = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if code == 0 and branch in PROTECTED:
        block(f"đang ở nhánh {branch}. Không commit trên {branch}; tạo nhánh feature/<Mã>-<tên> hoặc fix/<Mã>-<tên> từ dev.")
    msg = None
    for i, w in enumerate(words):
        if w in ("-m", "--message") and i + 1 < len(words):
            msg = words[i + 1]
            break
        if w.startswith("--message="):
            msg = w.split("=", 1)[1]
            break
    if msg is not None and "$(" not in msg:
        first = msg.strip().splitlines()[0] if msg.strip() else ""
        if not COMMIT_RE.match(first):
            block(f"tiêu đề commit '{first[:80]}' sai mẫu. Đúng: <loại>(#<Mã>): <mô tả>, ví dụ feat(#123): giữ chỗ căn hộ; commit dở dùng wip(#<Mã>): …")


def check_push(words, cwd):
    args = [w for w in words if not w.startswith("-")]
    flags = [w for w in words if w.startswith("-")]
    if any(f in ("-f", "--force", "--force-with-lease") or f.startswith("--force") for f in flags):
        block("không force push.")
    if "--delete" in flags or "-d" in flags or any(a.startswith(":") for a in args):
        block("không xóa nhánh trên remote bằng git push.")
    refspecs = args[1:]  # args[0] là remote
    for ref in refspecs:
        dest = ref.split(":")[-1].replace("refs/heads/", "").lstrip("+")
        if dest in PROTECTED:
            block(f"không push lên {dest}. Push nhánh feature/fix rồi mở MR.")
    code, branch = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    targets = [r.split(":")[-1].replace("refs/heads/", "").lstrip("+") for r in refspecs]
    targets = [branch if t == "HEAD" else t for t in targets] or ([branch] if code == 0 else [])
    for t in targets:
        if t in PROTECTED:
            block(f"đang đẩy lên {t}. Push nhánh feature/fix rồi mở MR.")
        if t and not BRANCH_RE.match(t):
            block(f"nhánh '{t}' sai mẫu. Đúng: feature/<Mã>-<tên ngắn> hoặc fix/<Mã>-<tên ngắn>, chữ thường và dấu gạch ngang. Đổi tên: git branch -m <tên mới>.")
    code, top = git(["rev-parse", "--show-toplevel"], cwd)
    if code == 0:
        f = os.path.join(top, CHECK_FILE)
        if os.path.isfile(f):
            cmd = open(f, encoding="utf-8").read().strip()
            if cmd:
                try:
                    r = subprocess.run(cmd, shell=True, cwd=top, capture_output=True, text=True, timeout=840)
                except subprocess.TimeoutExpired:
                    block(f"lệnh kiểm tra trước push ({cmd}) chạy quá 14 phút.")
                if r.returncode != 0:
                    tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-25:])
                    block(f"lệnh kiểm tra trước push ({cmd}) báo lỗi, sửa rồi push lại:\n{tail}")


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        sys.exit(0)
    if data.get("tool_name") != "Bash":
        sys.exit(0)
    command = (data.get("tool_input") or {}).get("command", "")
    cwd = data.get("cwd") or os.getcwd()
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if proj and os.path.isfile(os.path.join(proj, "scripts/cai-dat.py")) and os.path.isfile(os.path.join(proj, "CLAUDE-QUY-TRINH.md")):
        sys.exit(0)  # đang sửa chính repo bộ quy trình: không áp luật nhánh feature/fix
    for seg in segments(command):
        try:
            words = shlex.split(seg)
        except ValueError:
            continue
        while words and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]):
            words = words[1:]  # bỏ biến môi trường đặt trước lệnh
        if not words:
            continue
        if words[0] == "cd" and len(words) > 1:
            cwd = os.path.normpath(os.path.join(cwd, os.path.expanduser(words[1])))
            continue
        if words[0] != "git":
            continue
        rest = words[1:]
        while rest and rest[0].startswith("-"):  # git -c x=y, git --no-pager ...
            if rest[0] in ("-c", "-C") and len(rest) > 1:
                if rest[0] == "-C":
                    block("không dùng git -C; chạy dạng cd <repo> && git ...")
                rest = rest[2:]
            else:
                rest = rest[1:]
        if not rest:
            continue
        sub, opts = rest[0], rest[1:]
        if sub == "commit":
            check_commit(opts, cwd)
        elif sub == "push":
            check_push(opts, cwd)
    sys.exit(0)


if __name__ == "__main__":
    main()
