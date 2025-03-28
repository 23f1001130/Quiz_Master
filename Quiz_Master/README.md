# Quiz Master

**Quiz Master** is a multi-user web application designed for exam preparation across multiple courses. It provides two roles—an administrator (Quiz Master) and a regular user—with distinct features for managing quizzes and tracking performance.

## Features

### For Admin:
- **User Management:** Manage registered users.
- **Content Management:** Create, update, and delete subjects, chapters, quizzes, and questions.
- **Search Capability:** Search through quizzes, subjects, and users.
- **Analytics & Graphs:** View visual reports displaying top scorers and user attempts for each quiz.

### For Users:
- **User Authentication:** Register, log in, and manage profiles.
- **Quiz Attempts:** Browse available quizzes for each chapter, attempt quizzes with multiple-choice questions, and track quiz attempts.
- **Score Records:** Access historical records of previous quiz scores.

## Technologies
- **Flask:** Application backend framework.
- **Flask-SQLAlchemy:** ORM for interacting with the SQLite database.
- **Jinja2, HTML, CSS, Bootstrap:** Frontend templating and responsive UI design.
- **JavaScript & Chart.js (optional):** For interactive graphs and analytics on the admin dashboard.

## Project Structure
Quiz_Master/ ├── controllers/ # Application routes/controllers ├── models/ # SQLAlchemy models ├── static/ # Static files (CSS, JS, images) ├── templates/ # Jinja2 HTML templates ├── extensions.py # Flask extension initialization ├── app.py # Main application entry point ├── requirements.txt # Project dependencies └── .gitignore # Specifies files/folders to ignore (e.g., env/, pycache)
