import json
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path("ml_logs")
DATA_DIR.mkdir(exist_ok=True)

def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

def log_move(
    room_code: str,
    player_id: str,
    season: int,
    turn_index: int,
    card_dict: Dict[str, Any],
    grid_before: List[List[str]],
    grid_after: List[List[str]],
    placement_diff: List[List[str]],
    coins_before: int,
    coins_after: int,
) -> None:
    record = {
        "room_code": room_code,
        "player_id": player_id,
        "season": season,
        "turn_index": turn_index,
        "card": card_dict,
        "grid_before": grid_before,
        "grid_after": grid_after,
        "placement_diff": placement_diff,
        "coins_before": coins_before,
        "coins_after": coins_after,
    }
    _append_jsonl(DATA_DIR / "moves.jsonl", record)

def log_season_result(
    room_code: str,
    player_id: str,
    season: int,
    score1: int,
    score2: int,
    coins: int,
    monsters: int,
    season_total: int,
    cumulative_score: int,
) -> None:
    record = {
        "room_code": room_code,
        "player_id": player_id,
        "season": season,
        "score1": score1,
        "score2": score2,
        "coins": coins,
        "monsters": monsters,
        "season_total": season_total,
        "cumulative_score": cumulative_score,
    }
    _append_jsonl(DATA_DIR / "seasons.jsonl", record)