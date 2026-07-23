from flask import Flask, jsonify
from .database import engine
from . import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)

from .api import calls, tasks, children, emergency
app.register_blueprint(calls.bp, url_prefix='/calls')
app.register_blueprint(tasks.bp, url_prefix='/tasks')
app.register_blueprint(children.bp, url_prefix='/children')
app.register_blueprint(emergency.bp, url_prefix='/emergency')

@app.route("/")
def read_root():
    return jsonify({"message": "Parental Task Delegation API is running"})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
