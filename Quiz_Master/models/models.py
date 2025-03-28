from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from datetime import datetime


# -------------------------------- User --------------------------------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_mail = db.Column(db.String(60), unique=True, nullable=False)
    passhash = db.Column(db.String(80), nullable=False)
    fullname = db.Column(db.String(115), nullable=False)
    qualification = db.Column(db.String(100))
    dob = db.Column(db.String(10), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)

# -------------------------------- Subject --------------------------------
class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.String(180), nullable=True)


    subj_to_chap = db.relationship(
        'Chapter',
        backref='subject',
        lazy=True,
        cascade="all, delete-orphan"
    )


# -------------------------------- Chapter --------------------------------
class Chapter(db.Model):
    __tablename__ = "chapters"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True, nullable=False)
    title = db.Column(db.String(50), nullable=True)
    statement = db.Column(db.String(150))
    description = db.Column(db.String(200))
    num_questions = db.Column(db.Integer, default=0)

    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    chap_to_quiz = db.relationship(
        'Quiz',
        backref='chapter',
        lazy=True,
        cascade="all, delete-orphan"
    )
# -------------------------------- Quiz --------------------------------
class Quiz(db.Model):
    __tablename__ = "quizzes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)


    quiz_to_question = db.relationship(
        'Question',
        backref='quiz',
        lazy=True,
        cascade="all, delete-orphan"
    )


# -------------------------------- Question --------------------------------
class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    ques_text = db.Column(db.String(1000), unique=True, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=True)
    points = db.Column(db.Integer, nullable=False, default=1)


    ques_to_option = db.relationship(
        'Option',
        backref='question',
        lazy=True,
        cascade="all, delete-orphan"
    )


# -------------------------------- Option --------------------------------
class Option(db.Model):
    __tablename__ = "options"
    id = db.Column(db.Integer, primary_key=True)
    ques_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    option_text = db.Column(db.String(1000), nullable=False)
    correct = db.Column(db.Boolean, nullable=False, default=False)



# -------------------------------- Score --------------------------------
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    score = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)

