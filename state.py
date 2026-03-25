"""
state.py — GameState 스키마 + 저장/불러오기

절대 규칙:
  - LLM 호출 금지
  - GameState 스키마 변경 금지 (필드 추가/삭제/타입 변경 모두 금지)
  - import: dataclasses, json, copy, typing만 허용
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# 유틸리티
# ---------------------------------------------------------------------------

def clip(value: float, lo: float = 0, hi: float = 100) -> float:
    """0~100 범위 클리핑 (기본값). lo/hi 커스터마이즈 가능."""
    return max(lo, min(hi, value))


# ---------------------------------------------------------------------------
# GameState 스키마  ← 절대 변경 금지
# ---------------------------------------------------------------------------

def _default_team_stats() -> dict:
    return {
        "condition": 70,               # 0~100
        "morale": 50,                  # 0~100
        "tactical_understanding": 50,  # 0~100
        "cohesion": 60,                # 0~100
        "fan_sentiment": 50,           # 0~100
        "owner_trust": 60,             # 0~100 — 0이 되면 sacked 엔딩
        "press_level": 5,              # 1~10
    }


def _default_captain_stats() -> dict:
    return {
        "condition": 80,
        "morale": 60,
        "manager_relation": 70,
        "press_sentiment": 75,
        "leadership": 85,
        "professionalism": 90,
        "loyalty": 80,
    }


def _default_vice_captain_stats() -> dict:
    return {
        "condition": 75,
        "morale": 58,
        "manager_relation": 65,
        "press_sentiment": 70,
        "leadership": 78,
        "professionalism": 85,
        "loyalty": 75,
    }


def _default_rival_teams() -> dict:
    return {
        "Nottingham Forest": {"points": 32, "remaining_matches": 7, "goal_difference": -12},
        "West Ham":          {"points": 29, "remaining_matches": 7, "goal_difference": -21},
        "Leeds United":      {"points": 33, "remaining_matches": 7, "goal_difference": -11},
        "Burnley":           {"points": 19, "remaining_matches": 7, "goal_difference": -28},
        "Wolves":            {"points": 17, "remaining_matches": 7, "goal_difference": -30},
    }


def _default_schedule() -> list:
    return [
        {"round": 32, "opponent": "Sunderland",  "is_home": False, "opponent_strength": 6,  "date": "2026-04-11"},
        {"round": 33, "opponent": "Brighton",    "is_home": True,  "opponent_strength": 7,  "date": "2026-04-18"},
        {"round": 34, "opponent": "Wolves",      "is_home": False, "opponent_strength": 5,  "date": "2026-04-25"},
        {"round": 35, "opponent": "Aston Villa", "is_home": False, "opponent_strength": 8,  "date": "2026-05-02"},
        {"round": 36, "opponent": "Leeds",       "is_home": True,  "opponent_strength": 6,  "date": "2026-05-09"},
        {"round": 37, "opponent": "Chelsea",     "is_home": False, "opponent_strength": 9,  "date": "2026-05-17"},
        {"round": 38, "opponent": "Everton",     "is_home": True,  "opponent_strength": 7,  "date": "2026-05-24"},
    ]


@dataclass
class GameState:
    # ── 팀 / 선수 수치 ─────────────────────────────────────────────────────
    team_stats: dict         = field(default_factory=_default_team_stats)
    captain_stats: dict      = field(default_factory=_default_captain_stats)
    vice_captain_stats: dict = field(default_factory=_default_vice_captain_stats)

    # ── 경기 진행 ──────────────────────────────────────────────────────────
    remain_round: int  = 7    # 잔여 경기 수 ← current_round 혼용 절대 금지
    points: int        = 37   # 현재 승점
    position: int      = 16   # 현재 순위
    match_history: list = field(default_factory=list)

    # ── 훈련 버프 ─────────────────────────────────────────────────────────
    training_buff: float          = 0.0
    training_buff_expires: int    = 0   # 몇 경기 후 만료

    # ── 엔딩 / 모드 ───────────────────────────────────────────────────────
    game_over: bool    = False
    ending_type: str   = ""   # "survival" | "relegation" | "sacked"
    mode: str          = "normal"

    # ── 연패 / 감독 정보 ──────────────────────────────────────────────────
    consecutive_losses: int = 0
    manager_name: str       = "감독"

    # ── 경쟁팀 / 스케줄 ───────────────────────────────────────────────────
    rival_teams: dict  = field(default_factory=_default_rival_teams)
    schedule: list     = field(default_factory=_default_schedule)


# ---------------------------------------------------------------------------
# 저장 / 불러오기
# ---------------------------------------------------------------------------

def save_state(gs: GameState, path: str = "save.json") -> None:
    """GameState를 JSON 파일로 저장."""
    import dataclasses
    data = dataclasses.asdict(gs)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_state(path: str = "save.json") -> GameState:
    """JSON 파일에서 GameState 복원."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return GameState(**data)


# ---------------------------------------------------------------------------
# 새 게임
# ---------------------------------------------------------------------------

def new_game(manager_name: str = "감독") -> GameState:
    """기본값 GameState 생성 후 manager_name만 교체."""
    gs = GameState()
    gs.manager_name = manager_name
    return gs
