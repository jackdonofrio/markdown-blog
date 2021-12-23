from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from markdown_blog import app, db, bcrypt
from markdown_blog.forms import MdeForm, RegistrationForm, LoginForm, UpdateAccountForm, CommentForm
from markdown_blog.models import Article, User, Comment
from markdown_blog.utils import format_time, time_ago, markdown_into_sanitized_html


@app.route('/')
@app.route('/home')
def home():
    # fill in with stuff idk
    
    return render_template('home.html')

@app.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = MdeForm()
    if form.validate_on_submit():
        raw = request.form['editor']
        html = markdown_into_sanitized_html(raw)
        article = Article(title=form.title.data, html_content=html,
                          raw=raw, user_id=current_user.id)
        db.session.add(article)
        db.session.commit()
        flash('Your article has been created', 'success')
        return redirect(url_for('article_page', article_id=article.id))
    return render_template('new.html', form=form)


@app.route('/article/<int:article_id>', methods=['GET', 'POST'])
def article_page(article_id):
    article = Article.query.get_or_404(article_id)
    new_form = CommentForm()
    edit_form = CommentForm()

    editing = request.args.get('editing') # comment id
    if editing:
        if not current_user.is_authenticated:
            flash('You must be logged in to edit.', 'warning')
            return redirect(url_for('article_page', article_id=article_id))
        comment = Comment.query.get_or_404(editing)
        if current_user.username != comment.author.username:
            flash('You do not have permission to edit this comment.', 'warning')
            return redirect(url_for('article_page', article_id=article_id))
        if edit_form.validate_on_submit():
            comment.message = edit_form.message.data
            db.session.commit()
            flash('Your comment has been edited.', 'success')
            return redirect(url_for('article_page', article_id=article_id))
        elif request.method == 'GET':
            edit_form.message.data = comment.message

    elif new_form.validate_on_submit():
        comment = Comment(message=new_form.message.data, user_id=current_user.id, article_id=article.id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted.', 'success')
        return redirect(url_for('article_page', article_id=article_id))
    comments = Comment.query.filter_by(article_id=article.id).all()
    return render_template('article.html', article=article, new_form=new_form, edit_form=edit_form, edit_id=editing,
                            comments=comments, format_time=format_time, time_ago=time_ago, is_comment_to_edit=is_comment_to_edit)

def is_comment_to_edit(edit_id, comment_id):
    return int(edit_id) == int(comment_id)

@app.route('/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit(article_id):
    article = Article.query.get_or_404(article_id)
    if current_user.username != article.author.username: # later add admin privileges
        flash('You do not have permission to edit this article', 'warning')
        return redirect(url_for('article_page', article_id=article_id))
    form = MdeForm()
    if form.validate_on_submit():
        article.title = form.title.data
        raw = request.form['editor']
        article.raw = raw
        article.html_content = markdown_into_sanitized_html(raw)
        db.session.commit()
        flash('Your article has been edited.', 'success')
        return redirect(url_for('article_page', article_id=article_id))
    elif request.method == 'GET':
        form.title.data = article.title
        form.editor.data = article.raw
    return render_template('edit.html',form=form)

@app.route('/delete_post/<int:article_id>')
@login_required
def delete_post(article_id):
    article = Article.query.get_or_404(article_id)
    if current_user.username != article.author.username:
        flash('You do not have permission to delete this article', 'warning')
        return redirect(url_for('article_page', article_id=article_id))
    db.session.delete(article)
    db.session.commit()
    flash('Article deleted.', 'info')
    return redirect(url_for('home'))

@app.route('/delete_comment/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user.username != comment.author.username:
        flash('You do not have permission to delete this comment.', 'warning')
        return redirect(url_for('article_page', article_id=comment.article_id))        
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'info')
    return redirect(url_for('article_page', article_id=comment.article_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('You have successfully logged in.', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('home'))
        flash('Login unsuccessful. Please check email & password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('home'))

# remember to keep as much logic outside jinja templates as possible

@app.route('/user/<string:username>', methods=['GET', 'POST'])
def user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash(f'Unable to find user {username}', 'danger')
        return redirect(url_for('home'))
    articles = Article.query.filter_by(author=user).order_by(Article.date_posted.desc()).all()
    if current_user.is_authenticated and user and username == current_user.username:
        form = UpdateAccountForm()
        if form.validate_on_submit():
            current_user.email = form.email.data
            current_user.bio = form.bio.data
            db.session.commit()
            flash('Your account has been updated.', 'success')
            return redirect(url_for('user', username=username))
        elif request.method == 'GET':
            form.email.data = current_user.email
            form.bio.data = current_user.bio
        return render_template('user.html', user=user, form=form,
                                format_time=format_time, is_owner=True, articles=articles)
    return render_template('user.html', user=user, format_time=format_time,
                            is_owner=False, articles=articles)


@app.route('/all')
def all():
    page = request.args.get('page', 1, type=int)
    articles = Article.query.order_by(Article.date_posted.desc()).paginate(page=page, per_page=8)
    return render_template('all.html', articles=articles,format_time=format_time, time_ago=time_ago)

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    """ from flask docs """
    return render_template('404.html'), 404
