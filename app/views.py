################ Importing Libraries #######################################################
from app import googler
from flask import render_template, flash, redirect, url_for, session, request, g
import flask
import httplib2
from oauth2client import client
from flask_login import login_user, logout_user, current_user
from .models import User, Post, Category
from .forms import PostForm
from app import app, db, lm
from datetime import datetime
import re

###########################################################################################
# required for login_user function to work
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

# this will be executed every time a view function request is received
@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        # this way we can update last_seen column in the users table
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
############################################################################################
@app.route('/')
@app.route('/index')
def index():
    # get all the posts posted by Victor ! :D
    u = User.query.get(1)
    posts = u.posts.all()
    # render index and pass the posts object
    categories = Category.query.all()
    return render_template('index.html', posts=posts, cats=categories)

############################################################################################
# our login function
@app.route('/login')
def login():
    # if the current_user (g.user) is already authenticated
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    # otherwise, go ahead and send them to google's view
    return redirect(url_for('oauth2callback'))

############################################################################################
# google view for authenticating, same as the callback
@app.route('/oauth2callback')
def oauth2callback():
    # if we don't have valid authorization code (valid one contains 'code' in the string)
    if 'code' not in flask.request.args:
        return googler.step1()
    # if we do have a valid one, proceed with step2
    else:
        googler.step2()
        userinfor = googler.userinfo()
        name = userinfor['name']
        email = userinfor['email']
        nickname = userinfor['email'].split('@')[0]  # the nickname is the email before the @ symbol
        avatar = userinfor['picture']  # the url of the profile picture
        user = User.query.filter_by(email=email).first() # check to see if the email is already in the database
        if user is None:
            user = User(nickname=nickname, email=email, name=name, avatar=avatar)
            db.session.add(user)
            db.session.commit()
        login_user(user, True) # log the user in
        flash('Welcome %s' % name)
        return redirect(request.args.get('next') or url_for('index'))  # redirect to desired view or index

############################################################################################

@app.route('/user/<nickname>')
def user(nickname):
    usern = User.query.filter_by(nickname=nickname).first()
    if usern == None:
        flash('User not found', 'danger')
        return redirect(url_for('index'))
    if current_user != usern:
        return flash('You are not authorized', 'danger')
    categories = Category.query.all()
    return render_template('user.html', user=usern, cats=categories)

############################################################################################

# so I can publish new posts
@app.route('/poster', methods=['GET', 'POST'])
def poster():
    # check to see if its a random person of if its me ! :D
    if g.user.is_anonymous:
        return redirect(url_for('index'))
    if g.user.email != 'vraulsan@gmail.com':
        return redirect(url_for('index'))
    # if its me, then load the poster.html and collect info from the form
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, timestamp=datetime.utcnow(), author=g.user)
        cat = Category.query.get(form.category.data)
        cat.posts.append(post)
        db.session.add(post)
        db.session.commit()
        flash('Post is now live !', 'success')
        return redirect(url_for('index'))
    return render_template('poster.html', form=form)

@app.route('/postedit/<int:id>', methods=['GET', 'POST'])
def postedit(id):
    post = Post.query.get_or_404(id)
    form = PostForm(obj=post)
    if current_user != post.author:
        return "Dont try that..."
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.commit()
        flash('You have updated this post !', 'success')
        return redirect(url_for('index'))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('postedit.html', post=post, form=form)

############################################################################################
# log people out and also revoking the credentials string from google
@app.route('/logout')
def logout():
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    credentials.revoke(httplib2.Http())
    logout_user()
    flash('You have been logged out')
    return flask.redirect(flask.url_for('index'))

############################################################################################
# "title" is the raw post title  returned from index.html after users click
# on the post name, we use this view just so we can URLify the post title
# and we also use the raw title to retrieve the database object
@app.route('/posttitle/<title>')
def posttitle(title):
    # convert raw title to urlified title
    urltitle = re.sub(r'\W+', '-', title).lower()
    # since we still have the raw title, we use it to search the database
    postobject = Post.query.filter_by(title=title).first()
    # store the post id number in a varaible called "i"
    i = postobject.id
    # store the post id number in a global variable called "post"
    session['post'] = i
    return redirect(url_for('post', urltitle=urltitle))

# the actual view function for the post the user is trying to read
@app.route('/post/<urltitle>')
def post(urltitle):
    # bring the post id number back in a variable called "i"
    i = session['post']
    # create the post object from the post id stored in "i" so we can pass it to the html file
    post = Post.query.get(i)
    categories = Category.query.all()
    return render_template('post.html', post=post, cats=categories)

############################################################################################

@app.route('/category/<name>')
def category(name):
    category = Category.query.filter_by(name=name).first()
    categories = Category.query.all()
    posts = category.posts.all()
    return render_template('index.html', posts=posts, cats=categories)
############################################################################################
# for testing purposes, so I can delete the posts for now
@app.route('/delete/<int:id>')
def postdelete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    import uuid
    db.create_all()
    app.secret_key = str(uuid.uuid4())
    app.run(debug=True)
