from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))


class Category(db.Model):

    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


class Post(db.Model):

    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))
    content = db.Column(db.Text)

    image = db.Column(db.String(200))

    status = db.Column(db.String(20))

    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))

    category = db.relationship("Category", backref="posts")


class Comment(db.Model):

    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.String(500))

    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

    post = db.relationship("Post", backref="comments")


class Like(db.Model):

    __tablename__ = "like"

    id = db.Column(db.Integer, primary_key=True)

    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

    post = db.relationship("Post", backref="likes")