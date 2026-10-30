"""Task 9 recording plan: which sessions to record and what to write in each.

From docs/后续任务规划.md: digits 0-9 x10, the nine first characters x5,
horizontal/vertical line, circle and cross, five simple drawings, and one
session where the paper is moved part-way. Four extra sessions repeat
digits and characters with the exposure capped at one anti-flicker step
(~12.7 ms instead of ~38 ms) to give Task 10 motion-blur data. 30 sessions.
"""

from __future__ import annotations

from dataclasses import dataclass, field

DIGITS = [str(d) for d in range(10)]
CHARACTERS = ["十", "口", "日", "大", "人", "山", "中", "田", "木"]
STROKES = ["横线", "竖线", "圆", "十字"]
DRAWINGS = ["房子", "太阳", "鱼", "树", "小猫"]
ONE_STEP_LINES = 300  # EXPOSURE auto 300 -> one band step (295 lines)


@dataclass(frozen=True)
class Prompt:
    label: str  # what is written (dataset label)
    kind: str  # digit | character | stroke | drawing | action
    text: str  # what the operator is shown


@dataclass(frozen=True)
class SessionSpec:
    name: str
    kind: str
    prompts: tuple[Prompt, ...]
    exposure_max_lines: int | None = None
    cell: int = 0  # writing-cell index on the page (3x3 grid)
    notes: str = ""
    tags: tuple[str, ...] = field(default=())


def _prompts(labels, kind, template="写：{}") -> tuple[Prompt, ...]:
    return tuple(Prompt(label, kind, template.format(label)) for label in labels)


def build_plan() -> list[SessionSpec]:
    plan: list[SessionSpec] = []

    def add(name, kind, prompts, **kwargs):
        plan.append(
            SessionSpec(name, kind, tuple(prompts), cell=len(plan) % 9, **kwargs)
        )

    for i in range(10):
        add(f"digits-{i + 1:02d}", "digits", _prompts(DIGITS, "digit"))
    for i in range(5):
        add(f"chars-{i + 1:02d}", "characters", _prompts(CHARACTERS, "character"))
    for i in range(5):
        add(f"strokes-{i + 1:02d}", "strokes", _prompts(STROKES, "stroke", "画：{}"))
    for i, drawing in enumerate(DRAWINGS):
        add(
            f"draw-{i + 1:02d}", "drawing", _prompts([drawing], "drawing", "简笔画：{}")
        )
    add(
        "move-01",
        "paper-move",
        [
            *_prompts(CHARACTERS[:3], "character"),
            Prompt("move-paper", "action", "移动纸张（摄像头不动），放好后按 m"),
            *_prompts(CHARACTERS[3:6], "character"),
        ],
        notes="Paper moved part-way; the tool marks it and takes page snapshots.",
        tags=("paper-moved",),
    )
    for i in range(2):
        add(
            f"digits-cap1-{i + 1:02d}",
            "digits",
            _prompts(DIGITS, "digit"),
            exposure_max_lines=ONE_STEP_LINES,
            tags=("exposure-1-step",),
        )
    for i in range(2):
        add(
            f"chars-cap1-{i + 1:02d}",
            "characters",
            _prompts(CHARACTERS, "character"),
            exposure_max_lines=ONE_STEP_LINES,
            tags=("exposure-1-step",),
        )
    return plan


def plan_by_name() -> dict[str, SessionSpec]:
    return {spec.name: spec for spec in build_plan()}
