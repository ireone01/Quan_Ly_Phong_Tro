from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import jsonify 
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='assets')
app.config.from_pyfile('config.py')
app.secret_key = 'your_secret_key' 
db = SQLAlchemy(app)

class PhongTro(db.Model):
    __tablename__ = 'PhongTro'
    
    ID_Phong = db.Column(db.Integer, primary_key=True)
    TenPhong = db.Column(db.String(100), nullable=False)
    GiaThue = db.Column(db.Numeric(10, 2), nullable=False)
    DienTich = db.Column(db.Float, nullable=False)
    TinhTrang = db.Column(db.Boolean, nullable=False)  # 1: Đã thuê, 0: Chưa thuê
    SoNguoiToiDa = db.Column(db.Integer, nullable=False)
    DacDiem = db.Column(db.String(255))
    Images = db.Column(db.String)

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
    
@app.route('/')
def home():
    phong_tro = PhongTro.query.all()
    return render_template('CUS_room.html',phong_tro=phong_tro)

@app.route('/admin')
def admin():
    return render_template('AD_dashbroard.html')

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        
        if password != confirm_password:
            flash('Mật khẩu và mật khẩu xác nhận không khớp.', 'danger')
            return redirect(url_for('register'))
        
        existing_user = KhachHang.query.filter_by(TenDangNhap=username).first()
        if existing_user:
            flash('Tên đăng nhập đã tồn tại.', 'danger')
            return redirect(url_for('register'))
        
        existing_email = KhachHang.query.filter_by(Email=email).first()
        if existing_email:
            flash('Email đã tồn tại.', 'danger')
            return redirect(url_for('register'))
        
        session['username'] = username
        session['password'] = password
        session['email'] = email
        
        return redirect(url_for('register_info'))
        
    return render_template('register.html')


@app.route('/register_info', methods=['GET', 'POST'])
def register_info():
    if request.method == 'POST':
        
        TenKhachHang = request.form['TenKhachHang']
        GioiTinh = request.form['GioiTinh']
        NgaySinh_text = request.form['NgaySinh']
        DiaChi = request.form['DiaChi']
        SoDienThoai = request.form['SoDienThoai']
        
        NgaySinh = datetime.strptime(NgaySinh_text, '%d/%m/%Y').strftime('%Y-%m-%d')
        
        username = session['username']
        password = session['password']
        email = session['email']
        
        new_customer = KhachHang(TenKhachHang=TenKhachHang, GioiTinh=GioiTinh, NgaySinh=NgaySinh, DiaChi=DiaChi, 
                         SoDienThoai=SoDienThoai, DaThuePhong=False, TenDangNhap=username, 
                         MatKhau=password, Email=email, VaiTro=False)
        db.session.add(new_customer)
        db.session.commit()
        
        flash('Đăng kí thành công!', 'success')
        session.pop('username')
        session.pop('password')
        session.pop('email')
        
        return redirect(url_for('login'))
        
    return render_template('register-info.html')

@app.route('/room')
def room():
    phong_tro = PhongTro.query.all()
    return render_template('AD_all-room.html',phong_tro=phong_tro)

@app.route('/get_room_details', methods=['GET'])
def get_room_details():
    room_id = request.args.get('id', type=int)
    room = PhongTro.query.get(room_id)
    return jsonify({
        'ID_Phong': room.ID_Phong,
        'TenPhong': room.TenPhong,
        'SoNguoiToiDa': room.SoNguoiToiDa,
        'DienTich': room.DienTich,
        'GiaThue': room.GiaThue,
        'DacDiem': room.DacDiem,
        'TinhTrang': room.TinhTrang,
        'Images': room.Images
    })
    
@app.route('/delete_room', methods=['POST'])
def delete_room():
    room_id = request.form.get('id', type=int)
    room = PhongTro.query.get(room_id)
    if room:
        db.session.delete(room)
        db.session.commit()
        return jsonify({}), 200
    else:
        return jsonify({}), 404
    
    
    
UPLOAD_FOLDER = 'assets/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        TenPhong = request.form['TenPhong']
        GiaThue = request.form['GiaThue']
        DienTich = request.form['DienTich']
        SoNguoiToiDa = request.form['SoNguoiToiDa']
        DacDiem = request.form['DacDiem']
        TinhTrang = False 
        images = []

        
        if 'filename' in request.files:
            files = request.files.getlist('filename')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    images.append(filename)

        new_room = PhongTro(
            TenPhong=TenPhong,
            GiaThue=GiaThue,
            DienTich=DienTich,
            TinhTrang=TinhTrang,
            SoNguoiToiDa=SoNguoiToiDa,
            DacDiem=DacDiem,
            Images=' '.join(images)
        )

        db.session.add(new_room)
        db.session.commit()
        
        flash('Phòng trọ đã được thêm thành công!', 'success')
        return redirect(url_for('room'))

    return render_template('AD_add-room.html')


@app.route('/edit_room/<int:id>', methods=['GET', 'POST'])
def edit_room(id):
    room = PhongTro.query.get_or_404(id)
    if request.method == 'POST':
        room.TenPhong = request.form['TenPhong']
        room.GiaThue = request.form['GiaThue']
        room.DienTich = request.form['DienTich']
        room.SoNguoiToiDa = request.form['SoNguoiToiDa']
        room.DacDiem = request.form['DacDiem']
        
        # Handle file uploads
        if 'filename' in request.files:
            files = request.files.getlist('filename')
            existing_files = room.Images.split() if room.Images else []

            # Add new files to the list
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    existing_files.append(filename)

            # Handle file deletion
            files_to_delete = request.form.getlist('delete_files')
            for file in files_to_delete:
                if file in existing_files:
                    existing_files.remove(file)
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))

            room.Images = ' '.join(existing_files)

        db.session.commit()
        flash('Room updated successfully!', 'success')
        return redirect(url_for('room', id=room.ID_Phong))

    existing_files = room.Images.split() if room.Images else []
    return render_template('AD_edit-room.html', room=room, existing_files=existing_files)

@app.route('/customer')
def customer():
    khach_hang = KhachHang.query.all()
    return render_template('AD_all-customer.html',khach_hang=khach_hang)

@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    customer_id = request.form.get('id', type=int)
    customer = KhachHang.query.get(customer_id)
    if customer:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({}), 200
    else:
        return jsonify({}), 404
    
    
@app.route('/get_customer_details', methods=['GET'])
def get_customer_details():
    customer_id = request.args.get('id', type=int)
    customer = KhachHang.query.get(customer_id)
    return jsonify({
        'ID_KhachHang': customer.ID_KhachHang,
        'TenKhachHang': customer.TenKhachHang,
        'GioiTinh': customer.GioiTinh,
        'NgaySinh': customer.NgaySinh,
        'DiaChi': customer.DiaChi,
        'SoDienThoai': customer.SoDienThoai,
        'DaThuePhong': customer.DaThuePhong,
        'TenDangNhap': customer.TenDangNhap,
        'MatKhau': customer.MatKhau,
        'Email': customer.Email,
        'NgayTao': customer.NgayTao,
        'VaiTro': customer.VaiTro,
        'ID_Phong': customer.ID_Phong
    })
    
    
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

@app.route('/contract')
def contract():
    hop_dong = HopDong.query.all()
    return render_template('AD_all-contract.html',hop_dong=hop_dong)

@app.route('/delete_contract', methods=['POST'])
def delete_contract():
    contract_id = request.form.get('id', type=int)
    contract = HopDong.query.get(contract_id)
    if contract:
        db.session.delete(contract)
        db.session.commit()
        return jsonify({}), 200
    else:
        return jsonify({}), 404
    
    
@app.route('/cancel_contract', methods=['POST'])
def cancel_contract():
    contract_id = request.form.get('id')
    contract = HopDong.query.get(contract_id)
    if contract:
        contract.TrangThai = '0'
        db.session.commit()
        
    return redirect(url_for('contract'))


class ChiTietDichVu(db.Model):
    __tablename__ = 'ChiTietDichVu'
    
    ID_ChiTietDichVu = db.Column(db.Integer, primary_key=True)
    ID_Phong = db.Column(db.Integer, db.ForeignKey('PhongTro.ID_Phong'), nullable=True)
    ThangNam = db.Column(db.String(7), nullable=False)    
    SoDien= db.Column(db.Numeric(10, 2), nullable=False)
    SoNuoc= db.Column(db.Numeric(10, 2), nullable=False)
    Internet = db.Column(db.Boolean, nullable=False) # 1: Đã thuê, 0: Chưa thuê
    VeSinh = db.Column(db.Boolean, nullable=False) # 1: Đã thuê, 0: Chưa thuê
    BaoVe = db.Column(db.Boolean, nullable=False) # 1: Đã thuê, 0: Chưa thuê
    TongTienDichVu = db.Column(db.Numeric(10, 2), nullable=False)

    phong = db.relationship('PhongTro', backref='chitietdichvu')
    
@app.route('/servicedetail')
def servicedetail():
    chi_tiet_dich_vu = ChiTietDichVu.query.all()
    return render_template('AD_servicedetail.html',chi_tiet_dich_vu=chi_tiet_dich_vu)

@app.route('/delete_servicedetail', methods=['POST'])
def delete_servicedetail():
    servicedetail_id = request.form.get('id', type=int)
    servicedetail = ChiTietDichVu.query.get(servicedetail_id)
    if servicedetail:
        db.session.delete(servicedetail)
        db.session.commit()
        return jsonify({}), 200
    else:
        return jsonify({}), 404
    

@app.route('/add_contract', methods=['GET', 'POST'])
def add_contract():
    if request.method == 'POST':
        NgayBatDau_text = request.form['NgayBatDau']
        NgayKetThuc_text = request.form['NgayKetThuc']
        TienDatCoc = request.form['TienDatCoc']
        ID_KhachHang = request.form['ID_KhachHang']
        ID_Phong = request.form['ID_Phong']
        
        NgayBatDau = datetime.strptime(NgayBatDau_text, '%d/%m/%Y').strftime('%Y-%m-%d')
        NgayKetThuc = datetime.strptime(NgayKetThuc_text, '%d/%m/%Y').strftime('%Y-%m-%d')
        
        new_contract = HopDong(
            NgayBatDau=NgayBatDau,
            NgayKetThuc=NgayKetThuc,
            TienDatCoc=TienDatCoc,
            TrangThai='0',
            ID_KhachHang=ID_KhachHang,
            ID_Phong=ID_Phong
        )
        
        db.session.add(new_contract)
        db.session.commit()

        return redirect(url_for('contract'))
    
    khach_hangs = KhachHang.query.all()
    phongs = PhongTro.query.all()
    return render_template('AD_add-contract.html', khach_hangs=khach_hangs, phongs=phongs)


class DichVu(db.Model):
    __tablename__ = 'DichVu'
    
    ID_DichVu = db.Column(db.Integer, primary_key=True)
    TenDichVu  = db.Column(db.String(100), nullable=False)    
    GiaDichVu = db.Column(db.Numeric(10, 2), nullable=False)
    
@app.route('/service')
def service():
    dich_vu = DichVu.query.all()
    return render_template('AD_service.html',dich_vu=dich_vu)

@app.route('/delete_service', methods=['POST'])
def delete_service():
    service_id = request.form.get('id', type=int)
    service = DichVu.query.get(service_id)
    if servicedetail:
        db.session.delete(service)
        db.session.commit()
        return jsonify({}), 200
    else:
        return jsonify({}), 404
    
@app.route('/edit_service/<int:id>', methods=['GET', 'POST'])
def edit_service(id):
    service = DichVu.query.get_or_404(id)
    if request.method == 'POST':
        service.TenDichVu = request.form['TenDichVu']
        service.GiaDichVu = request.form['GiaDichVu']

        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('service'))

    return render_template('AD_edit-service.html', service=service)

@app.route('/add_service', methods=['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        TenDichVu = request.form['TenDichVu']
        GiaDichVu = request.form['GiaDichVu']
        
        new_service = DichVu(
            TenDichVu=TenDichVu,
            GiaDichVu=GiaDichVu,
        )
        
        db.session.add(new_service)
        db.session.commit()

        return redirect(url_for('service'))
    
    return render_template('AD_add-service.html')

class HoaDon(db.Model):
    __tablename__ = 'HoaDon'
    
    ID_HoaDon = db.Column(db.Integer, primary_key=True)
    ID_HopDong = db.Column(db.Integer, db.ForeignKey('HopDongThue.ID_HopDong'),nullable=True)
    ID_Phong = db.Column(db.Integer, db.ForeignKey('PhongTro.ID_Phong'),nullable=True)
    NgayTao = db.Column(db.Date, nullable=False)
    ThangNam = db.Column(db.String(7), nullable=False)      
    SoTien= db.Column(db.Numeric(10, 2), nullable=False)
    TrangThaiThanhToan = db.Column(db.String(50), nullable=False)    
    ChiTietDichVu = db.Column(db.String(255), nullable=True)   
    ID_ChiTietDichVu = db.Column(db.Integer, db.ForeignKey('ChiTietDichVu.ID_ChiTietDichVu'),nullable=True)
    TongSoTien = db.Column(db.Numeric(10, 2), nullable=False)

    phong = db.relationship('PhongTro', backref='hoadon')
    hd = db.relationship('HopDong', backref='hoadon')
    ctdv = db.relationship('ChiTietDichVu', backref='hoadon')
    
    
class ThanhToan(db.Model):
    __tablename__ = 'ThanhToan'
    
    ID_ThanhToan = db.Column(db.Integer, primary_key=True)
    ID_HoaDon = db.Column(db.Integer, db.ForeignKey('HoaDon.ID_HoaDon'),nullable=True)
    NgayThanhToan = db.Column(db.Date, nullable=False)
    SoTien= db.Column(db.Numeric(10, 2), nullable=False)
    PhuongThuc = db.Column(db.String(50), nullable=False)    
    SoTienConLai = db.Column(db.Numeric(10, 2), nullable=False)

    hoadon = db.relationship('HoaDon', backref='thanhtoan')

    
@app.route('/bill')
def bill():
    hoa_don = HoaDon.query.all()
    return render_template('AD_bill.html',hoa_don=hoa_don)

@app.route('/delete_bill', methods=['POST'])
def delete_bill():
    bill_id = request.form.get('id', type=int)
    bill = HoaDon.query.get(bill_id)
    if bill:
        db.session.delete(bill)
        db.session.commit()
        return jsonify(success=True), 200
    else:
        return jsonify(success=False, message="Hóa đơn không tồn tại."), 404


@app.route('/payment')
def payment():
    thanh_toan = ThanhToan.query.all()
    return render_template('AD_payment.html',thanh_toan=thanh_toan)   

@app.route('/get_contract_details', methods=['GET'])
def get_contract_details():
    contract_id = request.args.get('id', type=int)
    contract = HopDong.query.get(contract_id)
    return jsonify({
        'ID_HopDong': contract.ID_HopDong,
        'NgayBatDau': contract.NgayBatDau,
        'NgayKetThuc': contract.NgayKetThuc,
        'TienDatCoc': contract.TienDatCoc,
        'TrangThai': contract.TrangThai,
        'ID_Phong1': contract.ID_Phong,
        'ID_KhachHang': contract.ID_KhachHang
    })

@app.route('/get_service_details', methods=['GET'])
def get_service_details():
    service_id = request.args.get('id', type=int)
    service = ChiTietDichVu.query.get(service_id)
    return jsonify({
        'ID_ChiTietDichVu': service.ID_ChiTietDichVu,
        'ID_Phong': service.ID_Phong,
        'ThangNam': service.ThangNam,
        'SoDien': service.SoDien,  
        'SoNuoc': service.SoNuoc, 
        'Internet': service.Internet,
        'VeSinh': service.VeSinh,
        'BaoVe': service.BaoVe,
        'TongTienDichVu': service.TongTienDichVu
    })

    
@app.route('/get_bill_details', methods=['GET'])
def get_bill_details():
    bill_id = request.args.get('id', type=int)
    bill = HoaDon.query.get(bill_id)
    return jsonify({
        'ID_HoaDon': bill.ID_HoaDon,
        'ID_HopDong': bill.ID_HopDong,
        'ID_Phong': bill.ID_Phong,
        'NgayTao': bill.NgayTao,
        'ThangNam': bill.ThangNam,
        'SoTien': bill.SoTien,
        'TrangThaiThanhToan': bill.TrangThaiThanhToan,
        'ChiTietDichVu': bill.ChiTietDichVu,
        'ID_ChiTietDichVu': bill.ID_ChiTietDichVu,
        'TongSoTien': bill.TongSoTien
    })
    
@app.route('/delete_payment', methods=['POST'])
def delete_payment():
    payment_id = request.form.get('id', type=int)
    payment = ThanhToan.query.get(payment_id)
    if payment:
        db.session.delete(payment)
        db.session.commit()
        return jsonify({}), 200
    else:
        return jsonify({}), 404
    
@app.route('/dashbroard')
def dashbroard():
    return render_template('AD_dashbroard.html')  

@app.route('/cus_contract')
def cus_contract():
    if 'user_id' in session:
        user_id = session['user_id']
        hop_dong = HopDong.query.filter_by(ID_KhachHang=user_id).all()
        return render_template('CUS_contract.html', hop_dong=hop_dong)
    else:
        return render_template('CUS_contract.html', hop_dong=None)
    

@app.route('/cus_service')
def cus_service():
    dich_vu = DichVu.query.all()
    return render_template('CUS_service.html',dich_vu=dich_vu)

@app.route('/cus_bill')
def cus_bill():
    if 'user_id' in session:
        user_id = session['user_id']
        hop_dong = HopDong.query.filter_by(ID_KhachHang=user_id).all()
        hoa_don = []
        for hd in hop_dong:
            hoa_don += HoaDon.query.filter_by(ID_HopDong=hd.ID_HopDong).all()
        return render_template('CUS_bill.html', hoa_don=hoa_don)
    else:
        return render_template('CUS_bill.html', hoa_don=None) 

@app.route('/cus_customer')
def cus_customer():
    if 'user_id' in session:
        user_id = session['user_id']
        user_info = KhachHang.query.filter_by(ID_KhachHang=user_id).first()
        return render_template('CUS_customer.html', user_info=user_info)
    else:
        return redirect(url_for('login'))


@app.route('/cus_edit_customer', methods=['GET', 'POST'])
def cus_edit_customer():
    if 'user_id' in session:
        user_id = session['user_id']
        user_info = KhachHang.query.filter_by(ID_KhachHang=user_id).first()
        if user_info:
            if request.method == 'POST':
                user_info.TenKhachHang = request.form['TenKhachHang']
                user_info.GioiTinh = request.form['GioiTinh']
                NgaySinh_text = request.form['NgaySinh']
                NgaySinh = datetime.strptime(NgaySinh_text, '%d/%m/%Y').strftime('%Y-%m-%d')
                user_info.NgaySinh = NgaySinh
                user_info.SoDienThoai = request.form['SoDienThoai']
                user_info.DiaChi = request.form['DiaChi']
                db.session.commit()
                flash('Thông tin cá nhân đã được cập nhật thành công.', 'success')
                return redirect(url_for('cus_customer'))
            return render_template('CUS_edit-customer.html', user_info=user_info)
    return redirect(url_for('cus_customer'))


@app.route('/cus_change-password')
def cus_change_password():
    return render_template('CUS_change-password.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')

if __name__ == '__main__':
    app.run(debug=True)
