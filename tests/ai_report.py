import argparse
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone


def _read_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _first_line(text: str) -> str:
    if not text:
        return ""
    return text.strip().splitlines()[0].strip()


def _label_map(labels):
    result = defaultdict(list)
    for item in labels or []:
        name = item.get("name")
        value = item.get("value")
        if name and value:
            result[name].append(value)
    return result


def _classify_failure(message: str, trace: str) -> str:
    blob = f"{message}\n{trace}".lower()
    rules = [
        ("AUTH_401_403", r"\b(401|403)\b|unauthorized|forbidden|invalid credentials|token"),
        ("NOT_FOUND_404", r"\b404\b|not found"),
        ("SERVER_500", r"\b500\b|internal server error"),
        ("DB_CONSTRAINT", r"foreign key|unique constraint|not null constraint|integrityerror|psycopg"),
        ("ASSERTION", r"assertionerror|assert .*==|expected .* got"),
        ("KEY_ERROR", r"keyerror"),
        ("JSON_DECODE", r"jsondecodeerror|expecting value"),
        ("TIMEOUT", r"timeout|timed out"),
        ("CONNECTION", r"connectionerror|connection refused|name or service not known|failed to establish"),
        ("TYPE_ERROR", r"typeerror"),
        ("VALUE_ERROR", r"valueerror"),
    ]
    for label, pattern in rules:
        if re.search(pattern, blob):
            return label
    return "UNKNOWN"


def _load_allure_results(results_dir: str):
    items = []
    for root, _, files in os.walk(results_dir):
        for name in files:
            if not name.endswith("-result.json"):
                continue
            path = os.path.join(root, name)
            data = _read_json(path)
            if not isinstance(data, dict):
                continue
            items.append(data)
    return items


def _summarize(items):
    total = len(items)
    status_counter = Counter()
    failures = []
    for item in items:
        status = (item.get("status") or "unknown").lower()
        status_counter[status] += 1
        if status in {"failed", "broken"}:
            sd = item.get("statusDetails") or {}
            message = sd.get("message") or ""
            trace = sd.get("trace") or ""
            labels = _label_map(item.get("labels"))
            failures.append(
                {
                    "name": item.get("name") or item.get("fullName") or "unknown",
                    "fullName": item.get("fullName") or "",
                    "status": status,
                    "feature": (labels.get("feature") or [""])[0],
                    "story": (labels.get("story") or [""])[0],
                    "severity": (labels.get("severity") or [""])[0],
                    "message": _first_line(message),
                    "category": _classify_failure(message, trace),
                }
            )

    category_counter = Counter([f["category"] for f in failures])
    top_failures = failures[:10]
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "status": dict(status_counter),
        "failedOrBroken": len(failures),
        "failureCategories": dict(category_counter),
        "topFailures": top_failures,
    }


def _to_markdown(summary: dict) -> str:
    lines = []
    lines.append(f"# AI Test Summary")
    lines.append("")
    lines.append(f"- GeneratedAt (UTC): {summary.get('generatedAt', '')}")
    lines.append(f"- Total: {summary.get('total', 0)}")
    status = summary.get("status") or {}
    lines.append(f"- Passed: {status.get('passed', 0)} | Failed: {status.get('failed', 0)} | Broken: {status.get('broken', 0)} | Skipped: {status.get('skipped', 0)}")
    lines.append("")
    lines.append("## Failure Categories")
    fc = summary.get("failureCategories") or {}
    if not fc:
        lines.append("- None")
    else:
        for k, v in sorted(fc.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Top Failures")
    tf = summary.get("topFailures") or []
    if not tf:
        lines.append("- None")
    else:
        for f in tf:
            title = f.get("name") or ""
            status = f.get("status") or ""
            category = f.get("category") or ""
            feature = f.get("feature") or ""
            story = f.get("story") or ""
            msg = f.get("message") or ""
            meta = " | ".join([x for x in [feature, story] if x])
            if meta:
                lines.append(f"- [{status.upper()}] {title} ({category}) — {meta} — {msg}")
            else:
                lines.append(f"- [{status.upper()}] {title} ({category}) — {msg}")
    lines.append("")
    lines.append("## Suggestions")
    if not fc:
        lines.append("- All tests passed. Consider enabling smarter regression selection and data fuzzing for higher defect discovery.")
    else:
        if fc.get("NOT_FOUND_404", 0) > 0:
            lines.append("- 404: 优先检查路由前缀、Jenkins/Docker 环境 base_url、以及版本前缀 /api/v1 是否一致。")
        if fc.get("AUTH_401_403", 0) > 0:
            lines.append("- 401/403: 检查 Token 获取流程、Authorization Header 注入、tokenUrl 配置与过期时间。")
        if fc.get("SERVER_500", 0) > 0 or fc.get("DB_CONSTRAINT", 0) > 0:
            lines.append("- 500/DB: 优先查看后端日志与数据库约束（外键/唯一键），必要时补齐测试前置数据。")
        if fc.get("ASSERTION", 0) > 0:
            lines.append("- Assertion: 核对接口期望状态码/返回字段，避免写死不稳定字段（时间戳/自增ID等）。")
        if fc.get("CONNECTION", 0) > 0 or fc.get("TIMEOUT", 0) > 0:
            lines.append("- Connection/Timeout: 检查服务是否启动、端口映射、容器网络与等待策略。")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results_dir")
    parser.add_argument("--out-json", default=None)
    parser.add_argument("--out-md", default=None)
    args = parser.parse_args()

    items = _load_allure_results(args.results_dir)
    summary = _summarize(items)

    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    if args.out_md:
        with open(args.out_md, "w", encoding="utf-8") as f:
            f.write(_to_markdown(summary))

    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()

