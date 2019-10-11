from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "jIxfJ7UoLjcGYyCO8mooT&!r"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref ='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup', 'users', 'userpost']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        else:
            if not user:
                flash('Username does not exist', 'error')
                return render_template('login.html')
            elif password != user.password:
                flash('Password is incorrect.', 'error')
                return redirect('login')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''
        existing_user_error = ''

        existing_user = User.query.filter_by(username=username).first()
        #validate username
        if int(len(username)) <= 0:
            username_error = 'Thats not a valid username'
            username = ''
        else:
            if int(len(username)) < 3 or int(len(username)) > 20:
                username_error = 'Thats not a valid username'
                username = ''
        #validate password
        if int(len(password)) <= 0:
            password_error = 'Thats not a valid password'
            password = ''
        else:
            if int(len(password)) < 3 or int(len(password)) > 20:
                password_error = 'Thats not a valid password'
                password = ''
        #validate password verification
        if int(len(verify)) <= 0:
            verify_error = 'Password do not match'
            verify = ''
        else:
            if password != verify:
                verify_error = 'Password do not match'
                verify = ''
        #all errors passed
        if username_error or password_error or verify_error:
            return render_template('signup.html', username_error=username_error,password_error=password_error, verify_error=verify_error,username=username, password=password, verify=verify)
        #validate user
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('newpost')
        else:
            flash('A user with that username already exists', 'error')
            return redirect('signup')

    return render_template('signup.html')

#logout returns you to homepage
@app.route('/logout')
def logout():
    del session['username']
    return redirect('blog')

@app.route('/blog', methods=['POST', 'GET'])
def display_blog():
    if request.args:
        blog_id = request.args.get('id')
        blogs = Blog.query.filter_by(id=blog_id).all()
        return render_template('single_post.html', blogs=blogs)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build a Blog", blogs=blogs)


@app.route('/newpost')
def display():
    return render_template('new_post.html')


@app.route('/newpost', methods=['post', 'get'])
def create_new_post():
    if request.method == 'GET':
        return render_template('new_post.html', title="New Blog Post")

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_owner = request.form['owner']
        blog_body = request.form['body']

        new_blog = Blog(blog_title, blog_owner, blog_body)

        title_error = ''

        body_error = ''

        if len(blog_title) == 0:
            title_error = "Your post must have a title. Make it snazzy. No click-bait!"
        if len(blog_body) == 0:
            body_error = "Please fill in your post! We want to hear your ideas!"

        if not title_error and not body_error:
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_blog.id))
        else:
            blogs = Blog.query.all()
            return render_template('new_post.html', title="Build a Blog", blogs=blogs, blog_title=blog_title, title_error=title_error, blog_body=blog_body, body_error=body_error, blog_owner=blog_owner)


@app.route('/', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    return render_template('blog.html', title="Build a Blog", blogs=blogs)

if __name__ == "__main__":
    app.run()
