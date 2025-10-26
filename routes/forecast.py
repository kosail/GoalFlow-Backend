from flask import Blueprint, jsonify
import sqlite3
import pandas as pd
from prophet import Prophet

PERIODS = 24 # 12 - 3 months | 24 - 6 months
CD_RATE = 0.035

forecast_bp = Blueprint("analyse", __name__)

DB_PATH = "db/goalflow.db"

def get_weekly_balance(account_id):
    with sqlite3.connect(DB_PATH) as conn:
        query = """
        SELECT 
            strftime('%Y-%W', datetime) AS week,
            SUM(
                CASE 
                    WHEN origin_account = ? THEN -amount
                    WHEN destination_account = ? THEN amount
                    ELSE 0
                END
            ) AS net_flow
        FROM Transactions
        WHERE origin_account = ? OR destination_account = ?
        GROUP BY week
        ORDER BY week;
        """
        df = pd.read_sql_query(query, conn, params=(account_id, account_id, account_id, account_id))
    return df


@forecast_bp.route("/forecast/<int:account_id>", methods=["GET"])
def predict_balance(account_id):
    df = get_weekly_balance(account_id)
    if df.empty:
        return jsonify({"error": "Not enough transaction data"}), 400

    # Prophet requires 'ds' and 'y'
    df = df.rename(columns={"week": "ds", "net_flow": "y"})
    df["ds"] = pd.to_datetime(df["ds"] + "-1", format="%Y-%W-%w")

    try:
        model = Prophet()
        model.fit(df)

        # Forecast 12 weeks ahead
        future = model.make_future_dataframe(periods=PERIODS, freq="W")
        forecast = model.predict(future)
        forecast["week"] = forecast["ds"].dt.strftime("%Y-%W")

        baseline = forecast["yhat"].tolist()

        # --- Scenario 1: CapitalOne 360 CD Rate (3.5% APY)
  
        capitalone_cd = [
            round(value * ((1 + CD_RATE / 52) ** i), 2)
            for i, value in enumerate(baseline)
        ]

        # --- Scenario 2: AI-Optimized Spending (-10% avg expenses)
        ai_spending_factor = 1.05  # small overall improvement
        ai_optimized = [
            round(value * ai_spending_factor, 2) for value in baseline
        ]

        # --- Scenario 3: Combined Strategy
        combined = [
            round(value * ((1 + CD_RATE / 52) ** i) * ai_spending_factor, 2)
            for i, value in enumerate(baseline)
        ]

        # Build unified response
        result = {
            "account_id": account_id,
            "scenarios": {
                "Baseline Trend": [
                    {
                        "balances": [round(b, 2) for b in baseline],
                        "weeks": forecast["week"].tolist()
                    }
                ],
                "CapitalOne 360 CD": [
                    {
                        "balances": capitalone_cd,
                        "weeks": forecast["week"].tolist()
                    }
                ],
                "AI-Optimized Spending": [
                    {
                        "balances": ai_optimized,
                        "weeks": forecast["week"].tolist()
                    }
                ],
                "Combined Strategy": [
                    {
                        "balances": combined,
                        "weeks": forecast["week"].tolist()
                    }
                ]
            }
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
