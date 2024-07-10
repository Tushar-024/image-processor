from flask import Flask
from .celery import make_celery


def create_app():
    app = Flask(__name__)
    
    
    app.config.from_object("config.Config")
    app.config['UPLOAD_FOLDER'] = 'temp_uploads'
    # Initialize MongoDB

    # Initialize Celery
    celery = make_celery(app)
    app.celery = celery

    from controller.fileController import fileController_bp

    app.register_blueprint(fileController_bp)

    return app
