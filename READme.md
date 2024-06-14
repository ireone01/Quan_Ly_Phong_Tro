# Web Phòng Trọ

Web Phòng Trọ là một ứng dụng web quản lý phòng trọ, giúp người dùng dễ dàng tìm kiếm, quản lý và theo dõi thông tin về các phòng trọ.

## Tính Năng

- Đăng ký và đăng nhập cho người dùng và quản trị viên
- Quản lý thông tin phòng trọ: tên phòng, diện tích, giá thuê, số người tối đa, tình trạng phòng, hình ảnh phòng
- Quản lý hợp đồng thuê phòng: ngày bắt đầu, ngày kết thúc, tiền đặt cọc, trạng thái
- Quản lý dịch vụ đi kèm: điện, nước, vệ sinh, bảo vệ, internet
- Tìm kiếm và lọc phòng trọ theo các tiêu chí
- Giao diện quản trị cho admin để thêm, sửa, xóa phòng trọ và dịch vụ

## Tính Năng

### Trang Chủ
![Trang Chủ](../templates/trachu.png)
![Trang Chủ](../templates/trangchu.png)

### Quản Lý Phòng Trọ
![Quản Lý Phòng Trọ](../template/QuanLyPhongTro.png)

### Quản Lý Hợp Đồng
![Quản Lý Hợp Đồng](../template/QuanLyHopDong.png)

### Quản Lý người thuê
![Quản Lý Dịch Vụ](../template/QuanLyNguoiDung.png)

## Công Nghệ Sử Dụng

- Frontend: HTML, CSS, JavaScript, Bootstrap
- Backend: Node.js, Express.js
- Cơ sở dữ liệu: Microsoft SQL Server
- Framework khác: jQuery, DataTables

## Yêu Cầu Hệ Thống

- Node.js v14.x trở lên
- Microsoft SQL Server
- Trình duyệt web hiện đại (Chrome, Firefox, Safari, Edge)

## Cài Đặt

1. **Clone repository:**

    ```bash
    git clone https://github.com/your-username/web-phong-tro.git
    cd web-phong-tro
    ```

2. **Cài đặt các gói phụ thuộc:**

    ```bash
    npm install
    ```

3. **Cấu hình cơ sở dữ liệu:**

    - Mở file `config/database.js` và cập nhật thông tin cấu hình cơ sở dữ liệu của bạn.
    - Đảm bảo rằng cơ sở dữ liệu Microsoft SQL Server đang chạy và có các bảng cần thiết.

4. **Chạy ứng dụng:**

    ```bash
    npm start
    ```

5. **Truy cập ứng dụng:**

   Mở trình duyệt web và truy cập `http://localhost:63342`

## Sử Dụng

### Đăng Ký và Đăng Nhập

- Người dùng có thể đăng ký tài khoản mới hoặc đăng nhập nếu đã có tài khoản.
- Quản trị viên có thể đăng nhập để truy cập giao diện quản trị.

### Quản Lý Phòng Trọ

- Quản trị viên có thể thêm, sửa, xóa thông tin phòng trọ.
- Người dùng có thể tìm kiếm và xem chi tiết thông tin phòng trọ.

### Quản Lý Hợp Đồng

- Quản trị viên có thể thêm, sửa, xóa hợp đồng thuê phòng.
- Người dùng có thể xem thông tin hợp đồng của mình.

### Quản Lý Dịch Vụ

- Quản trị viên có thể thêm, sửa, xóa dịch vụ đi kèm phòng trọ.
- Người dùng có thể xem thông tin các dịch vụ đi kèm phòng trọ.

## Đóng Góp

Nếu bạn muốn đóng góp cho dự án, vui lòng tạo Pull Request trên GitHub hoặc liên hệ với chúng tôi qua email.

## Liên Hệ

- Tên: Nguyễn Quang Huy
- Email: nguyen.quang.huy@example.com

Cảm ơn bạn đã sử dụng Web Phòng Trọ!
