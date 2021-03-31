import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from source import app, db, bcrypt
from source.forms import RegistrationForm, LoginForm, UpdateAccountForm, QuestionForm,CommentForm
from source.models import User, Question,Comment
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    questions = Question.query.all()
    return render_template('home.html', questions=questions)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(user_username=form.username.data, user_email=form.email.data, user_password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.user_password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/vote/<int:question_id>/<action>')
@login_required
def vote_action(question_id, action):
    question = Question.query.filter_by(id=question_id).first_or_404()
    if action == 'vote':
        current_user.vote_question(question)
        db.session.commit()
    if action == 'unvote':
        current_user.unvote_question(question)
        db.session.commit()
    return redirect(request.referrer)
    
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.user_username = form.username.data
        current_user.user_email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.user_username
        form.email.data = current_user.user_email
    image_file = url_for('static', filename='profile_pics/default.jpg')
    # image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/question/new", methods=['GET', 'POST'])
@login_required
def new_question():
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(q_title=form.title.data, q_body=form.content.data, author=current_user)
        db.session.add(question)
        db.session.commit()
        flash('Your question has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_question.html', title='New question',
                           form=form, legend='New question')



@app.route("/question/<int:question_id>",methods=['GET', 'POST'])
@login_required
def question(question_id):
    question = Question.query.get_or_404(question_id)
    form = CommentForm()
   
    comment =  question.comments.order_by(Comment.cm_datecreate.asc())
    
    if form.validate_on_submit():
        comment = Comment(cm_body=form.body.data,
                        article = question,
                          article_author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been post.')
        return redirect(url_for('question', question_id=(question.id)))
    
    return render_template('question.html', title=question.q_title, question=question,form=form,legend='Comment',comments = comment)

@app.route("/question/<int:question_id>/update", methods=['GET', 'POST'])
@login_required
def update_question(question_id):
    question = Question.query.get_or_404(question_id)
    if question.author != current_user:
        abort(403)
    form = QuestionForm()
    if form.validate_on_submit():
        question.q_title = form.title.data
        question.q_body = form.content.data
        db.session.commit()
        flash('Your question has been updated!', 'success')
        return redirect(url_for('question', question_id=(question.id)))
    elif request.method == 'GET':
        form.title.data = question.q_title
        form.content.data = question.q_body
    return render_template('create_Question.html', title='Update Question',
                           form=form, legend='Update Question')

@app.route("/question/<int:question_id>/delete", methods=['POST'])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    if question.author != current_user:
        abort(403)
    db.session.delete(question)
    db.session.commit()
    flash('Your question has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.user_status:
        return redirect(url_for('home'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('home'))


@app.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('home'))