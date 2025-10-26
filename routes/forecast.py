from flask import Blueprint, jsonify, request
from datetime import date, timedelta

forecast_bp = Blueprint("forecast", __name__)

def generate_sample_forecast(
    start_date: date,
    days: int,
    initial_balance: float,
    baseline_daily_delta: float = 10.0,  # average daily net change
    cd_apy: float = 0.035,               # 3.5% APY
    ai_delta: float = 0.10,              # +10% improved spending/savings
):
    """
    Generates simulated forecast data for baseline, CD, AI, and combined scenarios.
    """
    if days <= 0:
        raise ValueError("days must be positive")

    # Precompute date strings
    dates = [(start_date + timedelta(days=i+1)).strftime("%Y-%m-%d") for i in range(days)]

    daily_rate = cd_apy / 365.0
    baseline, cd, ai, combined = [], [], [], []

    b_prev = c_prev = a_prev = combo_prev = initial_balance

    for _ in range(days):
        # Baseline: linear change
        b_next = b_prev + baseline_daily_delta

        # CD: compound interest + same delta
        c_next = c_prev * (1.0 + daily_rate) + baseline_daily_delta

        # AI: improved daily delta (e.g. +10%)
        ai_next = a_prev + baseline_daily_delta * (1.0 + ai_delta)

        # Combined: interest + improved delta
        combo_next = combo_prev * (1.0 + daily_rate) + baseline_daily_delta * (1.0 + ai_delta)

        baseline.append(round(b_next, 2))
        cd.append(round(c_next, 2))
        ai.append(round(ai_next, 2))
        combined.append(round(combo_next, 2))

        b_prev, c_prev, a_prev, combo_prev = b_next, c_next, ai_next, combo_next

    return {
        "dates": dates,
        "scenarios": {
            "baseline": baseline,
            "cd_3_5": cd,
            "ai_goals": ai,
            "combined": combined
        }
    }


@forecast_bp.route("/<int:account_id>", methods=["GET"])
def forecast(account_id: int):
    """
    Returns sample forecast data for a user's account.
    Optional query params:
      - days (int): number of forecast days (default=30)
      - initial_balance (float): starting balance (default=5000)
      - cd_apy (float): CD annual interest rate (default=0.035)
      - ai_delta (float): AI daily improvement multiplier (default=0.10)
    """
    try:
        days = int(request.args.get("days", 30))
        initial_balance = float(request.args.get("initial_balance", 5000))
        cd_apy = float(request.args.get("cd_apy", 0.035))
        ai_delta = float(request.args.get("ai_delta", 0.10))

        result = generate_sample_forecast(
            start_date=date.today(),
            days=days,
            initial_balance=initial_balance,
            cd_apy=cd_apy,
            ai_delta=ai_delta
        )
        result["account_id"] = account_id
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 400
