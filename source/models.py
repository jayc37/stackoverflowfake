from datetime import datetime
from source import db, login_manager,app
from flask_login import UserMixin
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_username = db.Column(db.String(100), unique=True, nullable=False)
    user_email = db.Column(db.String(100), unique=True, nullable=True)
    user_image = db.Column(db.String(100), nullable=True, default='default.jpg')
    user_password = db.Column(db.String(100), nullable=False)
    user_status     = db.Column(db.Boolean, nullable=False,default= False)
    questions = db.relationship('Question', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='article_author',lazy = True)

    def vote_question(self, question):
        if not self.has_voted_question(question):
            vote = Vote(v_u_id=self.id, v_q_id=question.id)
            db.session.add(vote)
            db.session.commit()

    def unvote_question(self, question):
        if self.has_voted_question(question):
            Vote.query.filter_by(
                v_u_id=self.id,
                v_q_id=question.id).delete()
            db.session.commit()
        

    def has_voted_question(self, question):
        return Vote.query.filter(
            Vote.v_u_id == self.id,
            Vote.v_q_id == question.id).count() > 0
            
    def __repr__(self):
        return f"User('{self.user_username}', '{self.user_email}', '{str(self.user_image)}')"

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    q_title = db.Column(db.Text, nullable=False)
    q_datecreate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    q_tag_name = db.Column(db.Text, nullable=True)
    q_vote    =  db.Column(db.Integer, nullable=False,default=0)
    q_status  =  db.Column(db.Boolean, nullable=False)
    q_body =    db.Column(db.Text, nullable=False)
    q_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='article',cascade="all, delete-orphan", lazy='dynamic',passive_deletes=True)
    votes = db.relationship('Vote', backref='question', lazy='dynamic')

    def __repr__(self):
        return f"question('{self.q_title}', '{self.q_datecreate}', '{self.q_status}')"
    

        
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cm_body = db.Column(db.Text, nullable=False)
    cm_q_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), nullable=False)
    cm_status = db.Column(db.Boolean, default=True, nullable=False)
    cm_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)    
    cm_datecreate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cm_vote         = db.Column(db.Integer, nullable=True,default=0)
   
    def __repr__(self):
        return f"Comments('{self.cm_body}', '{self.cm_datecreate}')"


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    v_q_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    v_u_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"Vote('{self.v_count}')"

