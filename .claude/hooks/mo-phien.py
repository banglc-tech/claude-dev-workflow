#!/usr/bin/env python3
"""Hook SessionStart của claude-dev-workflow: in vài dòng bối cảnh đầu phiên để Claude đọc.

Gồm: chế độ (repo / thư mục chung), nhánh hiện tại, việc dở trong .bangiao/, nhắc quy tắc cốt lõi,
và báo khi bộ quy trình trên máy có bản mới hơn bản đang cài.
"""
import json
import os
import subprocess
import sys


def git(args, cwd):
    try:
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=10)
        return r.returncode, r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        data = {}
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    lines = ["[claude-dev-workflow] Bối cảnh đầu phiên:"]

    inside, _ = git(["rev-parse", "--is-inside-work-tree"], root)
    code, branch = git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    if inside == 0:
        branch = branch if code == 0 else "(chưa có commit)"
        lines.append(f"- Chế độ repo, nhánh hiện tại: {branch}.")
        if branch in ("dev", "main", "master"):
            lines.append(f"- Đang ở {branch}: chỉ được pull và tạo nhánh mới, không commit, không push lên {branch}.")
    else:
        lines.append("- Chế độ thư mục chung nhiều repo: xác định repo theo trường Repo của task, chạy lệnh dạng cd <repo> && <lệnh>.")

    bg = os.path.join(root, ".bangiao")
    if os.path.isdir(bg):
        items = []
        for name in sorted(os.listdir(bg)):
            d = os.path.join(bg, name)
            if not os.path.isdir(d):
                continue
            files = sorted(f for f in os.listdir(d) if f.endswith(".md"))
            if files:
                items.append((os.path.getmtime(os.path.join(d, files[-1])), name, files[-1]))
        items.sort(reverse=True)
        if items:
            lines.append("- Việc có sổ bàn giao (mới nhất trước): " +
                         "; ".join(f"Mã {n} (bước cuối {f})" for _, n, f in items[:5]) +
                         ". Dev gõ lại /feature hoặc /bugfix với Mã đó để làm tiếp từ bước dở.")

    lines.append("- Quy tắc cốt lõi: chỉ nhận việc qua /feature <Mã> hoặc /bugfix <Mã>; lập kế hoạch và chờ dev duyệt trước khi code; "
                 "vướng thì gọi decider trước; không merge, không push lên dev/main; push nhánh đang làm ít nhất mỗi ngày trước 17:00.")

    vf = os.path.join(root, ".claude/claude-dev-workflow.version")
    kit = os.path.expanduser("~/claude-dev-workflow")
    if os.path.isfile(vf) and os.path.isdir(os.path.join(kit, ".git")):
        installed = open(vf, encoding="utf-8").read().split()[0]
        code, latest = git(["rev-parse", "--short", "HEAD"], kit)
        if code == 0 and latest and installed != latest:
            c2, _ = git(["merge-base", "--is-ancestor", installed, latest], kit)
            if c2 == 0:
                lines.append(f"- Bộ quy trình trên máy có bản mới ({latest}, đang cài {installed}): nhắc dev chạy "
                             "python3 ~/claude-dev-workflow/scripts/cai-dat.py.")

    print("\n".join(lines))
    sys.exit(0)


if __name__ == "__main__":
    main()
