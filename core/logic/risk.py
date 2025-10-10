from dataclasses import dataclass

@dataclass
class RiskProfile:
    score: int
    label: str
    answers: dict

def score_to_label(score: int) -> str:
    if score < 35: return "Conservative"
    if score < 70: return "Balanced"
    return "Growth"

def compute_risk(answers: dict) -> RiskProfile:
    """
    answers keys expected:
      horizon (0-10), drawdown (0-10), experience (0-10), income_stability (0-10), goal_focus (0-10)
    """
    raw = sum([
        answers.get("horizon", 0),
        answers.get("drawdown", 0),
        answers.get("experience", 0),
        answers.get("income_stability", 0),
        answers.get("goal_focus", 0),
    ])
    # max 50 → scale to 0..100
    score = round(raw * 2)
    return RiskProfile(score=score, label=score_to_label(score), answers=answers)
