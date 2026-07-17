#!/usr/bin/env python3
"""Generate a deterministic spaced-review schedule for one learning topic."""

from __future__ import annotations

import argparse
import json
from datetime import date, timedelta


DEFAULT_INTERVALS = (1, 3, 7, 14, 30)


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc


def parse_intervals(value: str) -> tuple[int, ...]:
    try:
        intervals = tuple(int(item.strip()) for item in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("intervals must be comma-separated integers") from exc
    if not intervals or any(item <= 0 for item in intervals):
        raise argparse.ArgumentTypeError("intervals must contain positive integers")
    if tuple(sorted(set(intervals))) != intervals:
        raise argparse.ArgumentTypeError("intervals must be unique and increasing")
    return intervals


def build_schedule(
    topic: str,
    learned_date: date,
    target_date: date | None,
    intervals: tuple[int, ...],
) -> list[dict[str, object]]:
    schedule = []
    for day_offset in intervals:
        review_date = learned_date + timedelta(days=day_offset)
        if target_date is not None and review_date > target_date:
            continue
        schedule.append(
            {
                "topic": topic,
                "interval_day": day_offset,
                "review_date": review_date.isoformat(),
                "pass_rule": "闭卷复述要点，并独立完成一个同阶段小任务；正确且能解释关键步骤",
            }
        )
    return schedule


def render_markdown(schedule: list[dict[str, object]]) -> str:
    lines = [
        "| 知识点 | 间隔 | 复习日期 | 通过条件 |",
        "|---|---:|---|---|",
    ]
    for item in schedule:
        lines.append(
            f"| {item['topic']} | 第 {item['interval_day']} 天 | "
            f"{item['review_date']} | {item['pass_rule']} |"
        )
    if not schedule:
        lines.append("| — | — | — | 截止日期前无可安排的默认复习节点 |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True, help="knowledge point or error type")
    parser.add_argument("--learned-date", required=True, type=parse_date)
    parser.add_argument("--target-date", type=parse_date)
    parser.add_argument(
        "--intervals",
        type=parse_intervals,
        default=DEFAULT_INTERVALS,
        help="unique increasing day offsets, default: 1,3,7,14,30",
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()

    if args.target_date is not None and args.target_date < args.learned_date:
        parser.error("target date cannot be earlier than learned date")

    schedule = build_schedule(args.topic, args.learned_date, args.target_date, args.intervals)
    if args.format == "json":
        print(json.dumps(schedule, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(schedule))


if __name__ == "__main__":
    main()
