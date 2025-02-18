from . import db
from flask_login import UserMixin
import enum

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    courses = db.relationship('Course', secondary='enrollment', backref='students', foreign_keys=[Enrollment.student_id, Enrollment.course_id])
    #chat modifs
    ''' student_chats = db.relationship('Chat', foreign_keys='Chat.student_id', backref='student', lazy=True)
    teacher_chats = db.relationship('Chat', foreign_keys='Chat.teacher_id', backref='teacher', lazy=True)
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    '''
    #stud/prof
    account_type = db.Column(db.String(50))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    language = db.Column(db.String(100))
    category = db.Column(db.String(100))
    paragraphs = db.Column(db.String(5000))
    professor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#chat classes

from datetime import datetime

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Student's user ID
    professor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Professor's user ID
    messages = db.relationship('Message', backref='chat', lazy=True)  # Relationship with messages
    created_at = db.Column(db.DateTime, default=db.func.now())  # Chat creation timestamp

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)  # Link to a chat
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ID of the sender
    content = db.Column(db.Text, nullable=False)  # The message content
    timestamp = db.Column(db.DateTime, default=db.func.now())  # When the message was sent

    sender = db.relationship('User', backref='sent_messages')  # Relationship with the sender
