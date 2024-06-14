const express = require('express');
const sql = require('mssql');
const moment = require('moment');
const app = express();
const cors = require('cors');
const bcrypt = require('bcrypt');
const crypto = require('crypto');
const session = require('express-session');
const {raw} = require("express");
app.use(cors({
    origin: 'http://localhost:63342', // URL của frontend
    credentials: true
}));
app.use(express.json());

app.use(session({
    secret: 'ireone01',
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false } // Đặt là true nếu sử dụng HTTPS
}));
const config = {
    user: 'sa',
    password: '12345',
    server: 'IRE-ONCE\\IREONE01',
    database: 'x1',
    options: {
        encrypt: true,
        trustServerCertificate: true
    }
};

// Hàm gọi stored procedure để thêm dữ liệu
async function addDataToDatabase() {
    try {
        let pool = await sql.connect(config);
        await pool.request().execute('sp_ThemChiTietDichVuTheoThang');
        console.log('Stored procedure executed successfully');
    } catch (err) {
        console.error('SQL error', err);
    }
}

// Thiết lập interval để gọi stored procedure mỗi 30 giây
// setInterval(addDataToDatabase, 5000);
async function getDoanhThuTheoQuy(){
    try{
        await sql.connect(config);
        const result = await sql.query('SELECT * FROM HoaDon');
        const HoaDonData=result.recordset;
        const doanhThuTheoNamQuyTang = {};
        HoaDonData.forEach(hoaDon => {
            const phong = hoaDon.TenPhong;
            const doanhThu = hoaDon.TongSoTien; // Giả sử có trường doanh thu trong hóa đơn
            const thang = new Date(hoaDon.NgayTao).getMonth() + 1;
            const nam = new Date(hoaDon.NgayTao).getFullYear();

            if (!doanhThuTheoNamQuyTang[nam]) {
                doanhThuTheoNamQuyTang[nam] = {
                    Q1: { T1: 0, T2: 0, T3: 0, T4: 0 },
                    Q2: { T1: 0, T2: 0, T3: 0, T4: 0 },
                    Q3: { T1: 0, T2: 0, T3: 0, T4: 0 },
                    Q4: { T1: 0, T2: 0, T3: 0, T4: 0 }
                };
            }
            const tang = parseInt(phong.charAt(0)); // Lấy số tầng từ mã phòng

            let quy;
            if (thang <= 3) {
                quy = 'Q1';
            } else if (thang <= 6) {
                quy = 'Q2';
            } else if (thang <= 9) {
                quy = 'Q3';
            } else if (thang <= 12) {
                quy = 'Q4';
            }

            if (quy) {
                if (tang === 1) {
                    doanhThuTheoNamQuyTang[nam][quy].T1 += doanhThu;
                } else if (tang === 2) {
                    doanhThuTheoNamQuyTang[nam][quy].T2 += doanhThu;
                } else if (tang === 3) {
                    doanhThuTheoNamQuyTang[nam][quy].T3 += doanhThu;
                } else if (tang === 4) {
                    doanhThuTheoNamQuyTang[nam][quy].T4 += doanhThu;
                }
            }
        });
        return doanhThuTheoNamQuyTang;
    } catch (err) {
        console.error('Lỗi khi kết nối hoặc truy vấn:', err);
    }
    }
async function getKpiData() {
    try {
        // Tạo kết nối cơ sở dữ liệu sử dụng mssql
        await sql.connect(config);

        // Truy xuất dữ liệu từ bảng KPI
        const result = await sql.query('SELECT * FROM KPI');
        const kpiData = result.recordset;

        // Chuyển đổi định dạng datetime
        kpiData.forEach(row => {
            row.ThoiGian = moment(row.ThoiGian);
            row.Year = row.ThoiGian.year();
            row.Quarter = row.ThoiGian.quarter();
        });

        const result1 = await sql.query('SELECT * FROM HoaDon');
        const HoaDonData=result1.recordset;
        // Tính toán tổng doanh thu
        const totalRevenue = HoaDonData.reduce((sum, row) => sum + row.TongSoTien, 0);


        kpiData.forEach(row => {
            row.SoHopDongDuocThue = row.SoHopDongGiaHan + row.SoHopDongMoi;
        });

         kpiData.forEach(row =>{
               row.TyLeTaiKy=(row.SoHopDongGiaHan/(row.SoHopDongDuocThue))*100;
          });
        const tyletaiky =(kpiData.TyLeTaiKy/kpiData.SoHopDongDuocThue)*100;

        return {
            df_kpi: kpiData,
            total_revenue: totalRevenue,



        };
    } catch (err) {
        console.error(err);
        throw err;
    }
}

app.get('/', async (req, res) => {
    try {
        const data = await getKpiData();
        res.json(data);
    } catch (err) {
        res.status(500).send('Server error');
    }
});
app.get('/DoanhThuQuy',async (req,res) =>{
   try{
       const data =await getDoanhThuTheoQuy();
       res.json(data);
   }catch (err) {
       res.status(500).send('Server error');
   }
});
async function getDataPhong(){
    try{
        await sql.connect(config);
        const a= await sql.query('SELECT * FROM PhongTro');
        const PhongTroData= a.recordset;
        return PhongTroData;
    }catch (e) {
        console.error('loi get phong',e)
    }
}
app.get('/Phong',async (req,res) =>{
    try{
        const data =await getDataPhong();
        res.json(data);
    }catch(err){
        res.status(500).send('Server error');
    }
});
app.get('/Phong/:id', async (req, res) => {
    const id = parseInt(req.params.id);

    try {

        await sql.connect(config);
        const result = await sql.query`SELECT * FROM PhongTro WHERE ID_Phong = ${id}`;
        const phong = result.recordset[0];

        if (phong) {
            res.json(phong);
        } else {
            res.status(404).send('Phòng không tồn tại');
        }
    } catch (err) {
        console.error('SQL error', err);
        res.status(500).send('Đã xảy ra lỗi khi truy vấn cơ sở dữ liệu');
    }
});

async function getNguoiDung(){
    try {
        await sql.connect(config);
        const a = await sql.query('SELECT * FROM KhachHang');
        const KhachHangData = a.recordset;
        return KhachHangData;
    }catch(e){
        console.error('error khach hang',e);
    }
}
app.get('/KhachHang',async (req,res) =>{
    try {
        const data =await getNguoiDung();
        res.json(data);
    }catch(e){
        console.log('server error');
    }
});
async function getHopDong(){
    try {
        await sql.connect(config);
        const a = await sql.query('SELECT * FROM HopDongThue');
        const HopDongThuedata = a.recordset;
        return HopDongThuedata;
    }catch(e){
        console.error('error Hopdong ',e);
    }
}
app.get('/HopDong',async  (req,res)=>{
   try {
       const data = await getHopDong();
       res.json(data);
   }catch(e){
       console.log('error hop dong');
   }
});
app.get('/HopDong/:id', async (req, res) => {
    const id_khachhang = parseInt(req.params.id);

    try {
        await sql.connect(config);
        const result = await sql.query`SELECT * FROM HopDongThue WHERE ID_KhachHang = ${id_khachhang}`;
        const contracts = result.recordset;

        if (contracts.length > 0) {
            res.json(contracts);
        } else {
            res.status(404).send('Không tìm thấy hợp đồng nào cho khách hàng này');
        }
    } catch (err) {
        console.error('SQL error', err);
        res.status(500).send('Đã xảy ra lỗi khi truy vấn cơ sở dữ liệu');
    }
});
app.get('/HoaDon/:id',async (req,res) =>{
    const id_HoaDon = parseInt(req.params.id);
    try {
        await sql.connect(config);
        const result =await sql.query`SELECT * FROM HoaDon WHERE ID_HopDong = ${id_HoaDon}`;
        const hoadondata = result.recordset;
        if(hoadondata.length>0){
            res.json(hoadondata);
        }else{
            res.status(404).send('khong tim thay hoa don');

    }
} catch (err) {
        console.log('sql error', err);
        res.status(500).send('loi truy vaan sql');
    }
});
app.delete('/KhachHang/:id', async (req, res) => {
    const id = parseInt(req.params.id);

    try {
        let pool = await sql.connect(config);
        const result = await pool.request()
            .input('ID_KhachHang', sql.Int, id)
            .query('DELETE FROM KhachHang WHERE ID_KhachHang = @ID_KhachHang');

        if (result.rowsAffected[0] === 0) {
            res.status(404).json({ message: 'Khách hàng không tồn tại' });
        } else {
            res.json({ message: 'Khách hàng đã được xoá' });
        }
    } catch (err) {
        console.error('SQL error', err);
        res.status(500).send('Server error');
    }
});

async function getDichVu(){
    try {
        await sql.connect(config);
        const a =await sql.query('SELECT * FROM DichVu');
        const DichVudata = a.recordset;
        return DichVudata;
    }catch(e){
        console.error('error DichVu',e);
    }
}
app.get('/DichVu',async (req,res)=>{
    try {
        const data = await getDichVu();
        res.json(data);
    }catch(e){
        console.log('error dichvu');
    }
});
async function getChiTietDichVu(){
    try {
        await sql.connect(config);
        const a= await sql.query('SELECT * FROM ChiTietDichVu');
        const ChiTietDichVudata = a.recordset;
        return ChiTietDichVudata;
    }catch(e){
        console.log('error chitiet dich vu',e);
    }
}
app.get('/ChiTietDichVu',async (req,res)=>{
try {
    const data = await getChiTietDichVu();
    res.json(data);
}catch (e){
    console.log('error chitiet dich vu');
}
})
app.post('/register', async (req, res) => {
    const { TenKhachHang, GioiTinh, NgaySinh, DiaChi, SoDienThoai, TenDangNhap, MatKhau, Email, ID_Phong } = req.body;


    try {

        await sql.connect(config);

        const hashedPassword = await bcrypt.hash(MatKhau, 10);

        const result = await sql.query`
            INSERT INTO KhachHang (TenKhachHang, GioiTinh, NgaySinh, DiaChi, SoDienThoai, TenDangNhap, MatKhau, Email, VaiTro, ID_Phong)
            VALUES (${TenKhachHang}, ${GioiTinh}, ${NgaySinh}, ${DiaChi}, ${SoDienThoai}, ${TenDangNhap}, ${hashedPassword}, ${Email}, 0, ${ID_Phong})
        `;

        res.status(201).send('Đăng ký thành công');
    } catch (err) {
        console.error('Lỗi khi đăng ký khách hàng:', err);
        res.status(500).send(`Đã xảy ra lỗi khi đăng ký khách hàng: ${err.message}`);
    }
});
// mã hóa mật khẩu bằng SHA2_256
function hashPasswordSHA256(password) {
    return crypto.createHash('sha256').update(password).digest('hex');
}
async function comparePasswordSHA256(inputPassword, hashedPassword) {
    const inputPasswordHash = hashPasswordSHA256(inputPassword);
    return inputPasswordHash === hashedPassword.toLowerCase();
}
app.post('/login', async (req, res) => {
    const { TenDangNhap, MatKhau } = req.body;

    try {
        await sql.connect(config);
        const result = await sql.query`SELECT * FROM KhachHang WHERE TenDangNhap = ${TenDangNhap}`;
        const user = result.recordset[0];

        if (!user) {
            return res.status(400).send('Tên đăng nhập hoặc mật khẩu không đúng');
        }

        let passwordMatch;
        if (user.MatKhau.startsWith('$2b$')) { // Kiểm tra nếu mật khẩu đã mã hóa bằng bcrypt
            passwordMatch = await bcrypt.compare(MatKhau, user.MatKhau);
        } else { // Giả sử mật khẩu đã mã hóa bằng SHA2_256
            passwordMatch = await comparePasswordSHA256(MatKhau, user.MatKhau);
        }

        if (!passwordMatch) {
            return res.status(400).send('Tên đăng nhập hoặc mật khẩu không đúng');
        }

        // Thiết lập session
        req.session.user = { id: user.ID_KhachHang, username: user.TenDangNhap, vaitro: user.VaiTro };
        res.status(200).json({ message: 'Đăng nhập thành công', vaitro: user.VaiTro });
    } catch (err) {
        console.error('Lỗi khi đăng nhập:', err);
        res.status(500).send(`Đã xảy ra lỗi khi đăng nhập: ${err.message}`);
    }
});
app.get('/userinfo', (req, res) => {
    if (req.session.user) {
        const userInfo = req.session.user;
        sql.connect(config, (err) => {
            if (err) {
                console.log('Connection error', err);
                return res.status(500).send('Database connection error');
            }
            const request = new sql.Request();
            request.input('ID_KhachHang', sql.Int, userInfo.id);
            request.query('SELECT * FROM KhachHang WHERE ID_KhachHang = @ID_KhachHang', (err, result) => {
                if (err) {
                    console.log('Query error', err);
                    return res.status(500).send('Database query error');
                }
                if (result.recordset.length > 0) {
                    res.json(result.recordset[0]);
                } else {
                    res.status(404).send('User not found');
                }
            });
        });
    } else {
        res.status(401).send('Người dùng chưa đăng nhập');
    }
});
async function getHoaDon(){
    try {
        await sql.connect(config);
        const  a= await sql.query('SELECT * FROM HoaDon');
        const  HoaDondata = a.recordset;
        return HoaDondata;
    }catch(e){
        console.log('error HoaDon',e);
    }
}
app.get('/HoaDon',async (req, res) => {
    try {
        const a = await getHoaDon();
        res.json(a);
    } catch (e) {
        console.log('error hoa don');
    }
})
app.post('/logout', (req, res) => {
    req.session.destroy(err => {
        if (err) {
            return res.status(500).send('Đăng xuất thất bại');
        }
        res.clearCookie('connect.sid', { path: '/' }); // Xóa cookie session
        res.status(200).send('Đăng xuất thành công');
    });
});

app.post('/rent', async (req, res) => {
    const { TenDangNhap, MatKhau, ID_Phong } = req.body;

    try {
        // Kết nối đến SQL Server
        await sql.connect(config);

        // Tìm người dùng theo tên đăng nhập
        const result = await sql.query`
            SELECT * FROM KhachHang WHERE TenDangNhap = ${TenDangNhap}
        `;
        const user = result.recordset[0];

        if (!user) {
            return res.status(400).send('Tên đăng nhập hoặc mật khẩu không đúng');
        }

        // Kiểm tra mật khẩu
        const passwordMatch = await bcrypt.compare(MatKhau, user.MatKhau);
        if (!passwordMatch) {
            return res.status(400).send('Tên đăng nhập hoặc mật khẩu không đúng');
        }

        // Cập nhật trạng thái phòng
        await sql.query`
            UPDATE PhongTro SET TinhTrang = 1 WHERE ID_Phong = ${ID_Phong}
        `;

        // Cập nhật thông tin khách hàng
        await sql.query`
            UPDATE KhachHang SET DaThuePhong = 1, ID_Phong = ${ID_Phong} WHERE ID_KhachHang = ${user.ID_KhachHang}
        `;

        res.status(200).send('Phòng đã được thuê thành công');
    } catch (err) {
        console.error('Lỗi khi thuê phòng:', err);
        res.status(500).send(`Đã xảy ra lỗi khi thuê phòng: ${err.message}`);
    }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
