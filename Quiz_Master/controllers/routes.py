from flask import render_template, request, flash, redirect, url_for, session
from models.models import User, Subject, Question, Chapter, Quiz, Option,Score
from extensions import db
from functools import wraps
from datetime import datetime

def required_auth(func):
   @wraps(func)
   def inner(*args, **kwargs):
      if 'user_id' not in session:
       return redirect(url_for('Login'))
      return func(*args, **kwargs)
   return inner

def register_routes(app):
    @app.route('/')
    @required_auth
    def Homepage():
       user = User.query.get(session['user_id'])
       if user.is_admin:
          return redirect(url_for('Admin'))
       else:

          quizzes = Quiz.query.all()


          for quiz in quizzes:
              quiz.questions = Question.query.filter_by(quiz_id=quiz.id).all()

          return render_template('Homepage.html', user=user, quizzes=quizzes)

    @app.route('/admin')
    @required_auth
    def Admin():
      user = User.query.get(session['user_id'])
      if not user.is_admin:
        flash('You are not Authorized as Administrator')
        return redirect(url_for('Homepage'))

      subjects = Subject.query.all()

      for subject in subjects:
        for chapter in subject.subj_to_chap:
            question_count = Question.query.filter_by(chapter_id=chapter.id).count()
            chapter.num_questions = question_count

      db.session.commit()

      return render_template('admin.html', user=user, subjects=subjects)

    @app.route('/login')
    def Login():
        return render_template('User.html')

    @app.route('/login', methods=['POST'])
    def Login_post():
      username = request.form.get('username')
      password = request.form.get('password')

      if username == '' or password == '':
         flash('Username or Password cannot be Empty')
         return redirect(url_for('Register'))

      user = User.query.filter_by(user_mail=username).first()
      if not user:
         flash('Please register first')
         return redirect(url_for('Login'))

      if not user.check_password(password):
         flash('Incorrect Password')
         return redirect(url_for('Login'))

      session['user_id'] = user.id
      flash('Login Successful')
      return redirect(url_for('Homepage'))

    @app.route('/register')
    def Register():
        return render_template('register.html')

    @app.route('/register', methods=['POST'])
    def Register_post():
      full_name = request.form.get('name')
      username = request.form.get('username')
      dob = request.form.get('date')
      qualification = request.form.get('qualification')
      password = request.form.get('password')

      if username == '' or password == '':
         flash('Username or Password cannot be Empty')
         return redirect(url_for('Register'))

      if User.query.filter_by(user_mail=username).first():
         flash('Username Already Exists, please Login')
         return redirect(url_for('Login'))

      user = User(user_mail=username, password=password, fullname=full_name, qualification=qualification, dob=dob)
      db.session.add(user)
      db.session.commit()
      flash('User Successfully Registered!')
      return redirect(url_for('Login'))

    @app.route('/logout')
    @required_auth
    def Logout():
        session.pop('user_id', None)
        flash("Logged out successfully.")
        return redirect(url_for('Login'))

    @app.route('/subject/add')
    @required_auth
    def Add():
       return render_template('Subject/add_subj.html', user=User.query.get(session['user_id']))

    @app.route('/subject/add', methods=['POST'])
    @required_auth
    def Add_post():
        subject = request.form.get('subject')
        description = request.form.get('description')

        existing_subject = Subject.query.filter_by(subject=subject).first()
        if existing_subject:
            flash('Subject already exists!', 'warning')
            return redirect(url_for('Admin'))

        new_subject = Subject(subject=subject, description=description)
        db.session.add(new_subject)
        db.session.commit()

        flash('Subject Added Successfully!', 'success')
        return redirect(url_for('Admin'))

    @app.route('/subject/edit/<int:subject_id>')
    @required_auth
    def Edit(subject_id):
       subject = Subject.query.get_or_404(subject_id)
       return render_template('Subject/edit_subj.html', subject=subject, user=User.query.get(session['user_id']))

    @app.route('/subject/edit/<int:subject_id>', methods=['POST'])
    @required_auth
    def Edit_post(subject_id):
        subject = Subject.query.get_or_404(subject_id)
        subject.subject = request.form.get('subject')
        subject.description = request.form.get('description')
        db.session.commit()
        flash('Subject Updated Successfully!', 'success')
        return redirect(url_for('Admin'))

    @app.route('/subject/delete/<int:subject_id>')
    @required_auth
    def Delete(subject_id):
        subject = Subject.query.get_or_404(subject_id)
        db.session.delete(subject)
        db.session.commit()
        flash('Subject Deleted Successfully!', 'success')
        return redirect(url_for('Admin'))

    @app.route('/subject/<int:subject_id>/chapter/add')
    @required_auth
    def Add_chapter(subject_id):
     subject = Subject.query.get_or_404(subject_id)
     return render_template('Subject/add_chap.html', subject_id=subject.id)

    @app.route('/subject/<int:subject_id>/chapter/add', methods=['POST'])
    @required_auth
    def Add_chapter_post(subject_id):
        chapter_name = request.form.get('chapter')
        description = request.form.get('description')

        existing_chapter = Chapter.query.filter_by(subject_id=subject_id, name=chapter_name).first()
        if existing_chapter:
            flash('Chapter already exists in this subject!', 'warning')
            return redirect(url_for('Admin'))

        new_chapter = Chapter(
            name=chapter_name,
            description=description,
            subject_id=subject_id
        )
        db.session.add(new_chapter)
        db.session.commit()

        flash('Chapter Added Successfully!', 'success')
        return redirect(url_for('Admin'))

    @app.route('/subject/<int:subject_id>/chapter/<int:chapter_id>/edit')
    @required_auth
    def Edit_chapter(subject_id, chapter_id):
     chapter = Chapter.query.get_or_404(chapter_id)
     subject = Subject.query.get_or_404(subject_id)
     return render_template('Subject/edit_chap.html', chapter=chapter, subject=subject, user=User.query.get(session['user_id']))

    @app.route('/subject/<int:subject_id>/chapter/<int:chapter_id>/edit', methods=['POST'])
    @required_auth
    def Edit_chapter_post(subject_id, chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id)
        chapter.name = request.form.get('chapter')
        chapter.description = request.form.get('description')

        db.session.commit()
        flash('Chapter Updated Successfully!', 'success')
        return redirect(url_for('Admin'))

    @app.route('/chapter/delete/<int:chapter_id>')
    @required_auth
    def Delete_chapter(chapter_id):
     chapter = Chapter.query.get_or_404(chapter_id)
     db.session.delete(chapter)
     db.session.commit()
     flash('Chapter Deleted Successfully!', 'success')
     return redirect(url_for('Admin'))

    @app.route('/admin/quiz')
    @required_auth
    def adm_Quiz():
        user = User.query.get(session['user_id'])
        if not user.is_admin:
            flash('You are not Authorized as Administrator')
            return redirect(url_for('Homepage'))

        chapters = Chapter.query.all()
        subjects = Subject.query.all()
        return render_template('adm_quiz.html', chapters=chapters, user=user, subjects=subjects)



    @app.route('/chapter/<int:chapter_id>/quiz/add')
    @required_auth
    def Add_quiz(chapter_id):
     chapter = Chapter.query.get_or_404(chapter_id)
     subjects = Subject.query.all()
     chapters = Chapter.query.filter_by(subject_id=chapter.subject_id).all()
     return render_template('Quiz/add_quiz.html', chapter=chapter, chapters=chapters, user=User.query.get(session['user_id']))

    @app.route('/chapter/<int:chapter_id>/quiz/add', methods=['POST'])
    @required_auth
    def Add_quiz_post(chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id)

        title = request.form.get('title')
        date_str = request.form.get('date')
        duration_str = request.form.get('duration')

        new_quiz = Quiz(
            title=title,
            date=date_str,
            duration=duration_str,
            chapter_id=chapter.id
        )
        db.session.add(new_quiz)
        db.session.commit()

        flash('Quiz Added Successfully!', 'success')
        return redirect(url_for('adm_Quiz'))

    @app.route('/chapter/<int:chapter_id>/quiz/<int:quiz_id>/edit')
    @required_auth
    def Edit_quiz(chapter_id, quiz_id):
        chapter = Chapter.query.get_or_404(chapter_id)
        quiz = Quiz.query.get_or_404(quiz_id)
        chapters = Chapter.query.filter_by(subject_id=chapter.subject_id).all()
        return render_template('Quiz/edit_quiz.html', chapter=chapter, quiz=quiz, chapters=chapters, user=User.query.get(session['user_id']))

    @app.route('/chapter/<int:chapter_id>/quiz/<int:quiz_id>/edit', methods=['POST'])
    @required_auth
    def Edit_quiz_post(chapter_id, quiz_id):
     quiz = Quiz.query.get_or_404(quiz_id)

     quiz.title = request.form.get('title')
     date_str = request.form.get('date')
     duration_str = request.form.get('duration')

     new_chapter_id = request.form.get('chapter_id')
     if new_chapter_id:
         quiz.chapter_id = int(new_chapter_id)

     db.session.commit()
     flash('Quiz Updated Successfully!', 'success')
     return redirect(url_for('adm_Quiz'))

    @app.route('/chapter/<int:chapter_id>/quiz/<int:quiz_id>/delete')
    @required_auth
    def Delete_quiz(chapter_id, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        db.session.delete(quiz)
        db.session.commit()

        flash('Quiz Deleted Successfully!', 'success')
        return redirect(url_for('adm_Quiz'))

    @app.route('/quiz/<int:quiz_id>/question/add')
    @required_auth
    def Add_question(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        return render_template('Quiz/add_question.html', quiz=quiz, user=User.query.get(session['user_id']))

    @app.route('/quiz/<int:quiz_id>/question/add', methods=['POST'])
    @required_auth
    def Add_question_post(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)

        ques_text = request.form.get('ques_text')
        points = int(request.form.get('points'))

        new_question = Question(
            ques_text=ques_text,
            chapter_id=quiz.chapter_id,
            quiz_id=quiz.id,
            points=points
        )
        db.session.add(new_question)
        db.session.commit()


        option_texts = request.form.getlist('option_text')
        option_texts = [text.strip() for text in option_texts if text.strip()]


        try:
            correct_option = int(request.form.get('correct_option', 0))
        except ValueError:
            correct_option = 0


        for i, option_text in enumerate(option_texts[:4]):  # Max 4 options
            option = Option(
                ques_id=new_question.id,
                option_text=option_text,
                correct=(i == correct_option)
            )
            db.session.add(option)

        db.session.commit()
        flash('Question Added Successfully!', 'success')
        return redirect(url_for('Quiz_questions', quiz_id=quiz_id))
    @app.route('/quiz/<int:quiz_id>/questions')
    @required_auth
    def Quiz_questions(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        return render_template('Quiz/questions.html', quiz=quiz, questions=questions, user=User.query.get(session['user_id']))

    @app.route('/question/<int:question_id>/edit')
    @required_auth
    def Edit_question(question_id):
     question = Question.query.get_or_404(question_id)
     options = Option.query.filter_by(ques_id=question_id).all()
     quiz = Quiz.query.get_or_404(question.quiz_id)
     return render_template('Quiz/edit_question.html', question=question, options=options, quiz=quiz, user=User.query.get(session['user_id']))

    @app.route('/question/<int:question_id>/edit', methods=['POST'])
    @required_auth
    def Edit_question_post(question_id):
     question = Question.query.get_or_404(question_id)

     question.ques_text = request.form.get('ques_text')
     question.points = int(request.form.get('points'))

     Option.query.filter_by(ques_id=question_id).delete()

     option_texts = []
     for i in range(1, 5):
         option_text = request.form.get(f'option{i}')
         option_texts.append(option_text)

     correct_option = int(request.form.get('correct_option', 0))

     for i, option_text in enumerate(option_texts):
         if option_text.strip():
             option = Option(
                 ques_id=question.id,
                 option_text=option_text,
                 correct=(i == correct_option)
             )
             db.session.add(option)

     db.session.commit()
     flash('Question Updated Successfully!', 'success')
     return redirect(url_for('Quiz_questions', quiz_id=question.quiz_id))

    @app.route('/question/<int:question_id>/delete')
    @required_auth
    def Delete_question(question_id):
        question = Question.query.get_or_404(question_id)
        quiz_id = question.quiz_id

        db.session.delete(question)
        db.session.commit()

        flash('Question Deleted Successfully!', 'success')
        return redirect(url_for('Quiz_questions', quiz_id=quiz_id))

    @app.route('/admin/search', methods=['GET', 'POST'])
    @required_auth
    def Search():
     if request.method == 'POST':
         search_term = request.form.get('search_term', '')
         search_type = request.form.get('search_type', 'all')
         filter_by = request.form.get('filter_by', 'all')

         results = {}

         if search_type in ['all', 'users']:
             users = User.query.filter(User.fullname.contains(search_term) |
                                      User.user_mail.contains(search_term)).all()
             results['users'] = users

         if search_type in ['all', 'subjects']:
             subjects = Subject.query.filter(Subject.subject.contains(search_term) |
                                           Subject.description.contains(search_term)).all()
             results['subjects'] = subjects

         if search_type in ['all', 'quizzes']:
             quizzes = Quiz.query.filter(Quiz.title.contains(search_term)).all()
             results['quizzes'] = quizzes

         return render_template('admin_results.html',
                               results=results,
                               search_term=search_term,
                               search_type=search_type,
                               filter_by=filter_by,
                               user=User.query.get(session['user_id']))

     return render_template('admin_search.html', user=User.query.get(session['user_id']))


    @app.route('/admin/summary')
    @required_auth
    def admin_summary():
        subjects = Subject.query.all()

        subject_attempts = []
        subject_names = []
        subject_scores = []

        for subject in subjects:
            subject_names.append(subject.subject)


            attempt_count = (
                db.session.query(db.func.count(Score.id))
                .join(Quiz, Score.quiz_id == Quiz.id)
                .join(Chapter, Chapter.id == Quiz.chapter_id)
                .filter(Chapter.subject_id == subject.id)
                .scalar() or 0
            )
            subject_attempts.append(attempt_count)


            top_score = (
                db.session.query(db.func.max(Score.score))
                .join(Quiz, Score.quiz_id == Quiz.id)
                .join(Chapter, Chapter.id == Quiz.chapter_id)
                .filter(Chapter.subject_id == subject.id)
                .scalar() or 0  # Default to 0 if no scores exist
            )
            subject_scores.append(top_score)

        return render_template(
            'admin_summary.html',
            subjects=subject_names,
            attempts=subject_attempts,
            scores=subject_scores,
            user=User.query.get(session.get('user_id'))
        )



    @app.route('/scores')
    @required_auth
    def Scores():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('Login'))

        scores = Score.query.filter_by(user_id=user_id).all()
        return render_template('user_scores.html', scores=scores,user=User.query.get(session['user_id']))



    @app.route('/quizzes')
    @required_auth
    def user_quizzes():
        quizzes = Quiz.query.all()
        for quiz in quizzes:
            quiz.question_count = Question.query.filter_by(quiz_id=quiz.id).count()
        return render_template(
            'quiz_list.html',
            quizzes=quizzes,
            user=User.query.get(session['user_id'])
        )

    @app.route('/quiz/<int:quiz_id>/view')
    @required_auth
    def view_quiz(quiz_id):

        quiz = Quiz.query.get_or_404(quiz_id)


        questions = Question.query.filter_by(quiz_id=quiz_id).all()

        return render_template(
            'user_view.html',
            quiz=quiz,
            questions=questions,
            user=User.query.get(session['user_id'])
        )

    #---------------------------------------------------
    @app.route('/quiz/<int:quiz_id>/start', methods=['GET'])
    @required_auth
    def start_quiz(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.options(db.joinedload(Question.ques_to_option)).filter_by(quiz_id=quiz_id).all()
        total_questions = len(questions)
        question_index = int(request.args.get('question_index', 0))


        session.setdefault('quiz_answers', {})


        if question_index >= total_questions:
            return redirect(url_for('submit_quiz', quiz_id=quiz_id))

        return render_template(
            'user_quiz.html',
            quiz=quiz,
            question=questions[question_index],
            question_index=question_index,
            total_questions=total_questions,
            user=User.query.get(session['user_id'])
        )

    @app.route('/quiz/<int:quiz_id>/question/<int:question_index>', methods=['POST'])
    @required_auth
    def handle_question(quiz_id, question_index):

        session.setdefault('quiz_answers', {})
        current_question_id = request.form.get('current_question_id')
        selected_option = request.form.get('selected_option')

        if current_question_id and selected_option:
            session['quiz_answers'][str(current_question_id)] = selected_option
            session.modified = True


        total_questions = Question.query.filter_by(quiz_id=quiz_id).count()


        if question_index < total_questions - 1:
            return redirect(url_for('start_quiz', quiz_id=quiz_id, question_index=question_index + 1))
        return redirect(url_for('submit_quiz', quiz_id=quiz_id))

    @app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
    @required_auth
    def submit_quiz(quiz_id):

        session.setdefault('quiz_answers', {})
        current_question_id = request.form.get('current_question_id')
        selected_option = request.form.get('selected_option')

        if current_question_id and selected_option:
            session['quiz_answers'][str(current_question_id)] = selected_option
            session.modified = True


        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        total_score = 0
        total_points = 0

        for question in questions:
            total_points += question.points  # Sum up total points available
            if option_id := session['quiz_answers'].get(str(question.id)):
                if (option := Option.query.get(int(option_id))) and option.correct:
                    total_score += question.points


        new_score = Score(
            user_id=session['user_id'],
            quiz_id=quiz.id,
            score=total_score,
            total_questions=total_points,
            date=datetime.utcnow()
        )
        db.session.add(new_score)
        db.session.commit()

        session.pop('quiz_answers', None)
        flash(f'Final Score: {total_score}/{total_points}', 'success')
        return redirect(url_for('Scores'))

    @app.route('/summary/user')
    @required_auth
    def user_summary():
        user = User.query.get(session['user_id'])


        from sqlalchemy import func


        subjects_data = db.session.query(
            Subject.subject,
            func.count(Quiz.id)
        ).join(Chapter, Chapter.subject_id == Subject.id)\
         .join(Quiz, Quiz.chapter_id == Chapter.id)\
         .group_by(Subject.subject)\
         .all()


        months_data = db.session.query(
            func.strftime('%Y-%m', Score.date),
            func.count(Score.id)
        ).filter(Score.user_id == user.id)\
         .group_by(func.strftime('%Y-%m', Score.date))\
         .all()

      
        subject_names = [sub[0] for sub in subjects_data]
        quiz_counts = [sub[1] for sub in subjects_data]
        month_labels = [m[0] for m in months_data]
        monthly_attempts = [m[1] for m in months_data]

        return render_template("user_summary.html",
                               user=user,
                               subjects=subject_names,
                               quiz_counts=quiz_counts,
                               months=month_labels,
                               monthly_attempts=monthly_attempts)