import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime

conn = sqlite3.connect("goalflow.db")

# Example: aggregate weekly balance changes
query = """
SELECT 
    strftime('%Y-%W', datetime) AS week,
    SUM(CASE WHEN origin_account IS NOT NULL THEN -amount ELSE amount END) AS net_flow
FROM Transactions
GROUP BY week
ORDER BY week;
"""
df = pd.read_sql_query(query, conn)
conn.close()

# Add lag features (previous week flow)
df["prev_flow"] = df["net_flow"].shift(1)
df.dropna(inplace=True)

# Train a simple regression
X = df[["prev_flow"]]
y = df["net_flow"]

model = LinearRegression().fit(X, y)

# Forecast next week's flow
predicted = model.predict([[df["net_flow"].iloc[-1]]])[0]
print(f"Predicted next week's net flow: {predicted:.2f}")
