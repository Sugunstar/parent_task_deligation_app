import os
import logging
from dotenv import load_dotenv

# Load .env BEFORE any other imports that read env vars
load_dotenv()

from flask import Flask, jsonify, render_template
from database import engine
import models

# ─── Logging ─────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── Create database tables ─────────────────────────────────────

models.Base.metadata.create_all(bind=engine)

# ─── Flask App ───────────────────────────────────────────────────

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static'),
)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

# ─── Register API blueprints ────────────────────────────────────

from api import calls, tasks, children, emergency

app.register_blueprint(calls.bp, url_prefix='/api/calls')
app.register_blueprint(tasks.bp, url_prefix='/api/tasks')
app.register_blueprint(children.bp, url_prefix='/api/children')
app.register_blueprint(emergency.bp, url_prefix='/api/emergency')

# ─── Page routes (PWA frontend) ─────────────────────────────────

@app.route('/')
def index():
    """Main page — redirects to the home/dashboard."""
    return render_template('index.html')


@app.route('/record')
def record_page():
    """Audio recording + processing page."""
    return render_template('record.html')


@app.route('/history')
def history_page():
    """Task history page."""
    return render_template('history.html')


@app.route('/task/<int:task_id>')
def task_detail_page(task_id):
    """Individual task / approval card page."""
    return render_template('task.html', task_id=task_id)


@app.route('/emergency/<int:event_id>')
def emergency_page(event_id):
    """Emergency alert page."""
    return render_template('emergency.html', event_id=event_id)


# ─── Health check ───────────────────────────────────────────────

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Parental Task Delegation API is running",
        "sarvam_configured": bool(os.environ.get('SARVAM_API_KEY', '').strip()
                                  and os.environ.get('SARVAM_API_KEY') != 'your_sarvam_api_key_here'),
        "gemini_configured": bool(os.environ.get('GEMINI_API_KEY', '').strip()),
    })


# ─── Run ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)
