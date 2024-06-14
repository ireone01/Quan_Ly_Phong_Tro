from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask import jsonify 

app = Flask(__name__, static_folder='assets')
app.config.from_pyfile('config.py')
app.secret_key = 'your_secret_key' 
db = SQLAlchemy(app)

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = 'assets/image'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    
class KhachHang(db.Model):
    __tablename__ = 'KhachHang'
    
    ID_KhachHang = db.Column(db.Integer, primary_key=True)
    TenKhachHang = db.Column(db.String(100), nullable=False)
    GioiTinh = db.Column(db.String(10), nullable=False)  
    NgaySinh = db.Column(db.Date, nullable=False)
    DiaChi = db.Column(db.String(255), nullable=False)
    SoDienThoai = db.Column(db.String(15), nullable=False)
    DaThuePhong = db.Column(db.Boolean, nullable=False) # 1: Đã thuê, 0: Chưa thuê
    TenDangNhap = db.Column(db.String(50), nullable=False, unique=True)
    MatKhau = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(100), nullable=False, unique=True)
    NgayTao = db.Column(db.Date, nullable=False, default=db.func.current_date())
    VaiTro = db.Column(db.Boolean, nullable=False) # 1: Admin, 0: Khách hàng
    ID_Phong = db.Column(db.Integer, db.ForeignKey('PhongTro.ID_Phong'), nullable=True)

    phong = db.relationship('PhongTro', backref='khachhang')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = KhachHang.query.filter_by(TenDangNhap=username).first()
        if user and user.MatKhau == password:
            session['username'] = user.TenDangNhap
            session['user_id'] = user.ID_KhachHang
            session['role'] = user.VaiTro
            session['name']=user.TenKhachHang
            if user.VaiTro:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('role', None)
    session.pop('name', None)
    return redirect(url_for('home'))

class HopDong(db.Model):
    __tablename__ = 'HopDongThue'
    
    ID_HopDong = db.Column(db.Integer, primary_key=True)
    NgayBatDau = db.Column(db.Date, nullable=False)
    NgayKetThuc  = db.Column(db.Date, nullable=False)
    TienDatCoc = db.Column(db.Numeric(10, 2), nullable=False)
    TrangThai = db.Column(db.String(50), nullable=False) # 0: chưa xác nhận, 1: đã Xác Nhận, 3: chưa Xac nhận Hủy, 4:Đã Hủy
    ID_Phong = db.Column(db.Integer, db.ForeignKey('PhongTro.ID_Phong'), nullable=True)
    ID_KhachHang = db.Column(db.Integer, db.ForeignKey('KhachHang.ID_KhachHang'), nullable=True)

    phong = db.relationship('PhongTro', backref='hopdong')
    kh = db.relationship('KhachHang', backref='hopdong')

@app.route('/cus_contract')
def cus_contract():
    if 'user_id' in session:
        user_id = session['user_id']
        hop_dong = HopDong.query.filter_by(ID_KhachHang=user_id).all()
        return render_template('CUS_contract.html', hop_dong=hop_dong)
    else:
        return render_template('CUS_contract.html', hop_dong=None)

@app.route('/cus_customer')
def cus_customer():
    return render_template('CUS_customer.html')

@app.route('/cus_edit_customer')
def cus_edit_customer():
    if 'user_id' in session:
        user_id = session['user_id']
        user_info = KhachHang.query.filter_by(ID_KhachHang=user_id).first()
        if user_info:
            return render_template('CUS_edit-customer.html', user_info=user_info)
        
    return redirect(url_for('cus_customer'))
if __name__ == '__main__':
    app.run(debug=True)
