from flask import redirect, request, render_template, jsonify, Blueprint, session, g
from models import User, Post
from db_connect import db
from flask_bcrypt import Bcrypt

board = Blueprint('board', __name__)
bcrypt = Bcrypt()


@board.before_app_request
def load_logged_in_user():
    user_id = session.get('login')
    if login is None:
        g.user = None
    else:
        g.user = db.session.query(User).filter(User.id == user_id).first()


@board.route("/board")
def board_home():
    if session.get('login') is None:
        return redirect("/login")
    else:
        return redirect("/post")


@board.route("/post", methods=["GET", "POST"])
def post():
    if session.get("login") is not None:
        if request.method == 'GET':
            data = Post.query.order_by(Post.created_at.desc()).all()
            return render_template("index.html", post_list=data)
        else:
            content = request.form['content']
            author = request.form['author']

            post = Post(author, content)
            db.session.add(post)
            db.session.commit()
            return jsonify({"result": "success"})
    else:
        return redirect("/board")


@board.route("/join", methods=["GET", "POST"])
def join():
    if session.get("login") is None:
        if request.method == 'GET':
            return render_template('join.html')
        else:
            user_id = request.form['user_id']
            user_pw = request.form['user_pw']
            pw_hash = bcrypt.generate_password_hash(user_pw).decode()

            user = User(user_id, pw_hash)
            db.session.add(user)
            db.session.commit()
            return jsonify({"result": "success"})
    else:
        return redirect("/board")


@board.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('login') is None:
        if request.method == 'GET':
            return render_template('login.html')
        else:
            user_id = request.form['user_id']
            user_pw = request.form['user_pw']
            user = User.query.filter(User.user_id == user_id).first()
            if user is not None:
                if bcrypt.check_password_hash(user.user_pw, user_pw):
                    session['login'] = user.id
                    return jsonify({"result": "success"})
                else:
                    return jsonify({"result": "fail"})
            else:
                return jsonify({"result": "fail"})
    else:
        return redirect("/board")


@board.route("/logout")
def logout():
    session['login'] = None
    return redirect('/board')


@board.route("/post", methods=["DELETE"])
def delete_post():
    id = request.form['id']
    author = request.form['author']
    data = Post.query.filter(Post.id == id, Post.author == author).first()
    if data is not None:
        db.session.delete(data)
        db.session.commit()
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail'})


@board.route("/post", methods=["PATCH"])
def update_post():
    id = request.form['id']
    content = request.form['content']
    author = User.query.filter(User.id == session['login']).first()

    data = Post.query.filter(
        Post.id == id, Post.author == author.user_id
    ).first()

    data.content = content
    db.session.commit()

    return jsonify({'result': 'success'})
