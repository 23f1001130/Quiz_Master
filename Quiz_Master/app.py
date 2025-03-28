from flask import Flask
import os
from extensions import db
from models.models import User, Subject, Question, Chapter, Quiz, Option

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.urandom(24)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz_master.db"


    db.init_app(app)


    from controllers.routes import register_routes
    register_routes(app)

    return app

if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("Creating admin user...")
            admin = User(user_mail='admin', fullname='admin', is_admin=True)
            admin.password = "12345"
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")

    app.run(debug=True)