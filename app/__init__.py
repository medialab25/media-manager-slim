from flask import Flask
import json
import os

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    with open(config_path) as f:
        app.config.update(json.load(f))
    
    # Register blueprints
    from app.routes import main, media
    app.register_blueprint(main.bp)
    app.register_blueprint(media.bp)
    
    return app

# Create app instance for Gunicorn
application = create_app() 