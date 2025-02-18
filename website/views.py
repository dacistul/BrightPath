from flask import Blueprint, render_template, request, flash, jsonify, redirect,g
from flask_login import login_user, login_required, logout_user, current_user
from .models import Course, User, Chat, Message, Enrollment

from . import db
from datetime import datetime
import json

from datetime import timedelta
from flask import jsonify
from flask_babel import gettext as _
views = Blueprint('views', __name__)

# Load common data for all routes
@views.before_request
def load_global_data():
    if current_user.is_authenticated:
        g.students = User.query.filter_by(account_type="student").all()
        g.professors = User.query.filter_by(account_type="professor").all()
       

@views.route('/')
def home():
    #chat profs 
    #students = User.query.filter_by(account_type="student").all()
    #professors = User.query.filter_by(account_type="professor").all()
    courses = Course.query.all()
    return render_template("home.html", user=current_user, courses=courses)
    

@views.route('/home')
def homes():
    courses = Course.query.all()
    return render_template("home.html", user=current_user, courses=courses)

@views.route('/enroll-course', methods=['POST'])
@login_required
def enroll_course():
    data = request.json
    course_id = data['courseId']
    course = Course.query.get(course_id)
    if course:
        enrollment = Enrollment(course_id=course.id, student_id=current_user.id)
        db.session.add(enrollment)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@views.route('/course/<int:course_id>')
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course.html', user=current_user, course=course)

@views.route('/achievements')
def achievements():
    return render_template("achievements.html", user=current_user)
    
@views.route('/test')
@login_required
def test():
    courses = Course.query.all()
    return render_template("test.html", user=current_user, courses=courses)

@views.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
          name = request.form.get('name')
          description = request.form.get('description')
          language = request.form.get('language')
          category = request.form.get('category')
          paragraphs = request.form.get('paragraphs')
           # Replace newlines with <br> for proper rendering
          processed_paragraphs = paragraphs.replace("\n", "<br>")
          new_course = Course(name=name, description=description, language=language, category=category, paragraphs=processed_paragraphs, professor_id=current_user.id)
          db.session.add(new_course)
          db.session.commit()
          flash(_('Course uploaded!'), category='success')
    return render_template("upload.html", user=current_user)

@views.route('/cancel-course', methods=['POST'])
def cancel_course():
    data = request.json
    course_id = data['courseId']
    enrollment = Enrollment.query.filter_by(course_id=course_id, student_id=current_user.id).first()
    if enrollment:
        db.session.delete(enrollment)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@views.route('/account')
@login_required
def account():
    return render_template("account.html", user=current_user)

@views.route('/professors', methods=['GET'])
@login_required
def list_professors():
    professors = User.query.filter_by(account_type="professor").all()
    return render_template('professors.html', user=current_user, professors=professors)


@views.route('/start_chat/<int:user_id>', methods=['POST'])
@login_required
def start_chat(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    
    if current_user.account_type == "student" and user.account_type == "professor":
        # Logic for student starting a chat with a professor
        chat = Chat.query.filter_by(student_id=current_user.id, professor_id=user.id).first()
        if not chat:
            chat = Chat(student_id=current_user.id, professor_id=user.id)
            db.session.add(chat)
            db.session.commit()

        return jsonify({"success": True, "chatId": chat.id, "professorName": user.username}), 200
    
    elif current_user.account_type == "professor" and user.account_type == "student":
        # Logic for professor starting a chat with a student
        chat = Chat.query.filter_by(student_id=user.id, professor_id=current_user.id).first()
        if not chat:
            chat = Chat(student_id=user.id, professor_id=current_user.id)
            db.session.add(chat)
            db.session.commit()

        return jsonify({"success": True, "chatId": chat.id, "studentName": user.username}), 200

    return jsonify({"error": "Invalid chat participants."}), 400

@views.route('/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.json
    chat_id = data.get('chatId')
    message = data.get('message')

    if not chat_id or not message:
        return jsonify({"success": False, "error": "Invalid data!"}), 400

    # Fetch the chat to ensure it exists
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({"success": False, "error": "Chat not found!"}), 404

    # Ensure the current user is part of the chat
    if current_user.id not in [chat.student_id, chat.professor_id]:
        return jsonify({"success": False, "error": "You are not a participant in this chat."}), 403

    # Save the message to the database
    new_message = Message(chat_id=chat_id, sender_id=current_user.id, content=message)
    db.session.add(new_message)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": {
            "content": new_message.content,
            "senderId": new_message.sender_id,
            "timestamp": new_message.timestamp.isoformat(),
             "senderUsername": new_message.sender.username  # Add this line
        }
    }), 200

@views.route('/get_messages/<int:chat_id>', methods=['GET'])
@login_required
def get_messages(chat_id):
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({"success": False, "error": "Chat not found!"}), 404

    if current_user.id not in [chat.student_id, chat.professor_id]:
        return jsonify({"success": False, "error": "Unauthorized access!"}), 403

    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    message_data = [
        {
            "content": msg.content,
            "senderId": msg.sender_id,
            "timestamp": msg.timestamp.isoformat(),
            "senderUsername": msg.sender.username  # Include the sender's username
        }
        for msg in messages
    ]
    return jsonify({"success": True, "messages": message_data}), 200



