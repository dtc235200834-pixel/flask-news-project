# =========================================
# WEBSITE QUẢN LÝ TIN TỨC BÓNG ĐÁ
# Công nghệ: Flask + SQLite + Bootstrap
# Chức năng: CRUD bài viết, upload ảnh, duyệt bài, tìm kiếm, thống kê
# =========================================

from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.utils import secure_filename
import os

# import các model database
from models import db, Post, User, Category, Comment, Like

app = Flask(__name__)
app.secret_key = "secret123"

# cấu hình database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# thư mục lưu ảnh upload
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# =========================================
# KIỂM TRA ĐỊNH DẠNG FILE ẢNH
# chỉ cho phép upload các định dạng sau
# =========================================
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

db.init_app(app)

# =========================================
# TẠO DATABASE BAN ĐẦU (DATA MẪU)
# =========================================
with app.app_context():

    db.create_all()

    # tạo tài khoản admin mặc định
    if User.query.count() == 0:
        admin = User(username="admin", password="123", role="admin")
        db.session.add(admin)
        db.session.commit()

    # tạo danh mục mẫu
    if Category.query.count() == 0:
        c1 = Category(name="Bóng đá")
        c2 = Category(name="Esport")
        c3 = Category(name="Chuyển nhượng")

        db.session.add_all([c1, c2, c3])
        db.session.commit()

    # tạo bài viết mẫu
    if Post.query.count() == 0:
        p1 = Post(
            title="Messi tỏa sáng",
            content="Ghi bàn vào lưới Real",
            status="pending",
            category_id=1
        )

        p2 = Post(
            title="Ronaldo lập hattrick",
            content="Al Nassr thắng lớn",
            status="approved",
            category_id=1
        )

        db.session.add_all([p1, p2])
        db.session.commit()


# =========================================
# ĐĂNG NHẬP HỆ THỐNG
# =========================================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session["user"] = user.username
            session["role"] = user.role

            flash("Đăng nhập thành công", "success")
            return redirect("/")

        flash("Sai tài khoản", "danger")

    return render_template("login.html")


# =========================================
# ĐĂNG XUẤT
# =========================================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================================
# TRANG DASHBOARD QUẢN LÝ BÀI VIẾT
# có chức năng tìm kiếm và lọc trạng thái
# =========================================
@app.route("/")
def index():

    s = request.args.get("search", "")
    status = request.args.get("status", "")

    query = Post.query

    # tìm kiếm theo tiêu đề
    if s:
        query = query.filter(Post.title.contains(s))

    # lọc theo trạng thái
    if status:
        query = query.filter(Post.status == status)

    posts = query.all()

    categories = Category.query.all()

    # thống kê số lượng bài viết
    pending_count = Post.query.filter_by(status="pending").count()
    approved_count = Post.query.filter_by(status="approved").count()
    total = Post.query.count()

    return render_template(
        "index.html",
        posts=posts,
        categories=categories,
        total=total,
        pending_count=pending_count,
        approved_count=approved_count
    )


# =========================================
# TRANG THỐNG KÊ (BIỂU ĐỒ)
# =========================================
@app.route("/stats")
def stats():

    pending = Post.query.filter_by(status="pending").count()
    approved = Post.query.filter_by(status="approved").count()

    return render_template(
        "stats.html",
        pending=pending,
        approved=approved
    )


# =========================================
# THÊM BÀI VIẾT MỚI
# =========================================
@app.route("/add", methods=["POST"])
def add():

    if "user" not in session:
        return redirect("/login")

    title = request.form["title"]
    content = request.form["content"]
    category_id = request.form["category_id"]

    file = request.files.get("image")
    filename = None

    # kiểm tra file ảnh hợp lệ
    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)

        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        file.save(path)

    post = Post(
        title=title,
        content=content,
        image=filename,
        category_id=category_id,
        status="pending"
    )

    db.session.add(post)
    db.session.commit()

    flash("Đăng tin thành công", "success")

    return redirect("/")


# =========================================
# DUYỆT BÀI VIẾT (ADMIN)
# =========================================
@app.route("/approve/<int:id>")
def approve(id):

    if session.get("role") != "admin":
        return redirect("/")

    post = Post.query.get_or_404(id)

    post.status = "approved"
    db.session.commit()

    flash("Bài viết đã được duyệt", "success")

    return redirect("/")


# =========================================
# TỪ CHỐI BÀI VIẾT
# =========================================
@app.route("/reject/<int:id>")
def reject(id):

    if session.get("role") != "admin":
        return redirect("/")

    post = Post.query.get_or_404(id)

    post.status = "rejected"
    db.session.commit()

    flash("Bài viết đã bị từ chối", "warning")

    return redirect("/")


# =========================================
# XOÁ BÀI VIẾT
# =========================================
@app.route("/delete/<int:id>")
def delete(id):

    if session.get("role") != "admin":
        return redirect("/")

    post = Post.query.get_or_404(id)

    db.session.delete(post)
    db.session.commit()

    flash("Đã xoá bài viết", "danger")

    return redirect("/")


# =========================================
# SỬA BÀI VIẾT
# =========================================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    post = Post.query.get_or_404(id)

    if request.method == "POST":

        post.title = request.form["title"]
        post.content = request.form["content"]

        db.session.commit()

        flash("Đã cập nhật bài viết", "success")

        return redirect("/")

    return render_template("edit.html", post=post)


# =========================================
# ROUTE TEST (KIỂM TRA SERVER)
# =========================================
@app.route("/test")
def test():
    return "OK"


# =========================================
# CHẠY SERVER FLASK
# =========================================
if __name__ == "__main__":
    app.run(debug=True)