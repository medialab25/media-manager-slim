from flask import Flask
import json
import os

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    with open(config_path) as f:
        config = json.load(f)
        print(f"Loaded configuration: {json.dumps(config, indent=2)}")
        app.config.update(config)
    
    # Register blueprints
    from app.routes import main, media
    app.register_blueprint(main.bp)
    app.register_blueprint(media.bp)
    
    return app

# Create app instance for Gunicorn
application = create_app() 