from flask import Flask
from flask_cors import CORS
from routes.accounts import accounts_bp
from routes.transactions import transactions_bp
from routes.goals import goals_bp
from routes.missions import missions_bp
from routes.forecast import forecast_bp

app = Flask(__name__)
app.config['DATABASE'] = 'db/goalflow.db'

# Enable CORS for frontend (replace URL later if needed)
CORS(app, resources={r"/*": {"origins": "*"}})

# Register Blueprints
app.register_blueprint(accounts_bp, url_prefix='/accounts')
app.register_blueprint(transactions_bp, url_prefix='/transactions')
app.register_blueprint(goals_bp, url_prefix='/goals')
app.register_blueprint(missions_bp, url_prefix='/missions')
app.register_blueprint(forecast_bp, url_prefix="/forecast")

if __name__ == "__main__":
    # Use 0.0.0.0 so AWS or Docker can access it
    app.run(host='0.0.0.0', port=5000, debug=True)
