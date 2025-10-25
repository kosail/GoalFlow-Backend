from flask import Flask
from routes.accounts import accounts_bp
from routes.transactions import transactions_bp
from routes.goals import goals_bp
from routes.missions import missions_bp
from routes.docs import docs_bp

app = Flask(__name__)
app.config['DATABASE'] = 'db/goalflow.db'

# Register Blueprints
app.register_blueprint(accounts_bp, url_prefix='/accounts')
app.register_blueprint(transactions_bp, url_prefix='/transactions')
app.register_blueprint(goals_bp, url_prefix='/goals')
app.register_blueprint(missions_bp, url_prefix='/missions')
app.register_blueprint(docs_bp)

if __name__ == "__main__":
    app.run(debug=True)
