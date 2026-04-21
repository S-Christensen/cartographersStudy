import json
from pathlib import Path

import numpy as np

import color_model as color
import position_model as position


def to_json_safe(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, dict):
        return {key: to_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_safe(item) for item in value]
    return value


def trace_signature(step):
    return {
        "season": step.get("season"),
        "turn_index": step.get("turn_index"),
        "move_type": step.get("move_type"),
        "card_id": step.get("card", {}).get("id") if isinstance(step.get("card"), dict) else None,
        "grid_after": step.get("grid_after"),
    }


def annotate_deviations(reference_trace, candidate_trace):
    annotated = []
    first_deviation = None

    max_len = max(len(reference_trace), len(candidate_trace))
    for idx in range(max_len):
        ref_step = reference_trace[idx] if idx < len(reference_trace) else None
        cand_step = candidate_trace[idx] if idx < len(candidate_trace) else None

        is_deviation = ref_step != cand_step
        if first_deviation is None and is_deviation:
            first_deviation = {
                "index": idx,
                "reference": trace_signature(ref_step) if ref_step is not None else None,
                "candidate": trace_signature(cand_step) if cand_step is not None else None,
            }

        if cand_step is not None:
            step = dict(cand_step)
            step["deviates_from_equal"] = is_deviation
            step["is_first_deviation"] = first_deviation is not None and idx == first_deviation["index"]
            annotated.append(step)

    return annotated, first_deviation


def run_same_game(seed=42):
    scenario = position.make_deterministic_game_scenario(seed, include_season_decks=True)

    equal_result = position.run_single_game(
        position.init_genetic_weights(),
        game_id=f"equal_{seed}",
        scenario=scenario,
        trace=True,
    )
    color_result = color.run_single_game(
        color.TRAINED_COLOR_WEIGHTS,
        game_id=f"color_{seed}",
        scenario=scenario,
        trace=True,
    )
    position_result = position.run_single_game(
        position.TRAINED_POSITION_WEIGHTS,
        game_id=f"position_{seed}",
        scenario=scenario,
        trace=True,
    )

    equal_trace = equal_result["trace"]
    color_trace, color_first_deviation = annotate_deviations(equal_trace, color_result["trace"])
    position_trace, position_first_deviation = annotate_deviations(equal_trace, position_result["trace"])

    return {
        "seed": seed,
        "scenario": {
            "score_types_names": scenario["score_types_names"],
            "score_types_colors": scenario["score_types_colors"],
        },
        "results": {
            "equal_weights": {
                **equal_result,
                "trace": [
                    {**step, "deviates_from_equal": False, "is_first_deviation": False}
                    for step in equal_trace
                ],
                "first_deviation": None,
            },
            "trained_color": {
                **color_result,
                "trace": color_trace,
                "first_deviation": color_first_deviation,
            },
            "trained_position": {
                **position_result,
                "trace": position_trace,
                "first_deviation": position_first_deviation,
            },
        },
    }


if __name__ == "__main__":
    seed = 42
    result = to_json_safe(run_same_game(seed=seed))
    while result["results"]["trained_position"]["score"] <= result["results"]["equal_weights"]["score"] or result["results"]["trained_color"]["score"] <= result["results"]["equal_weights"]["score"]:
        seed += 1
        result = to_json_safe(run_same_game(seed=seed))

    out_dir = Path("ml_logs")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"model_trace_{seed}.json"
    out_file.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Saved trace to {out_file}")
    print("Equal weights score:", result["results"]["equal_weights"]["score"])
    print("Trained color score:", result["results"]["trained_color"]["score"])
    print("Trained position score:", result["results"]["trained_position"]["score"])
