
CREATE TABLE PhongTro (
    ID_Phong INT PRIMARY KEY IDENTITY(1,1),
    TenPhong VARCHAR(100) NOT NULL,
    GiaThue DECIMAL(10,2) NOT NULL,
    DienTich FLOAT NOT NULL,
    TinhTrang BIT NOT NULL, -- 1: Đã thuê, 0: Chưa thuê
    SoNguoiToiDa INT NOT NULL,
    DacDiem VARCHAR(255),
    Images VARCHAR(MAX) -- URL của hình ảnh phòng trọ
);


--INSERT INTO KhachHang (TenKhachHang, GioiTinh, NgaySinh, DiaChi, SoDienThoai, TenDangNhap, MatKhau, Email, VaiTro, ID_Phong)
--VALUES ('Admin1', 'Nam', '1980-01-01', '456 Duong DEF, Quan 2, TP. HCM', '0987654321', 'admin1', HASHBYTES('SHA2_256', '123'), 'admin1@example.com', 1, NULL);


CREATE TABLE KhachHang (
    ID_KhachHang INT PRIMARY KEY IDENTITY(1,1),
    TenKhachHang VARCHAR(100) NOT NULL,
    GioiTinh VARCHAR(10) NOT NULL,
    NgaySinh DATE NOT NULL,
    DiaChi VARCHAR(255) NOT NULL,
    SoDienThoai VARCHAR(15) NOT NULL,
    DaThuePhong BIT NOT NULL DEFAULT 0,
    TenDangNhap VARCHAR(50) NOT NULL UNIQUE,
    MatKhau VARCHAR(255) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    NgayTao DATE NOT NULL DEFAULT GETDATE(),
	VaiTro INT NULL,
    ID_Phong INT NULL,
	 SoPhong INT,
    FOREIGN KEY (ID_Phong) REFERENCES PhongTro(ID_Phong)
);



CREATE TABLE DichVu (
    ID_DichVu INT PRIMARY KEY IDENTITY(1,1),
    TenDichVu VARCHAR(100) NOT NULL,
    GiaDichVu DECIMAL(10,2) NOT NULL
);

CREATE TABLE ChiTietDichVu (
    ID_ChiTietDichVu INT PRIMARY KEY IDENTITY(1,1),
    ID_Phong INT,
	TenPhong VARCHAR(100),
    ThangNam VARCHAR(7) NOT NULL,
    SoDien DECIMAL(20, 2) NULL, 
    SoNuoc DECIMAL(20, 2) NULL, 
    ID_Internet INT NOT NULL,
    ID_VeSinh INT NOT NULL, 
    ID_BaoVe INT NOT NULL, 
	TongTienDichVu DECIMAL(20, 2),
    FOREIGN KEY (ID_Phong) REFERENCES PhongTro(ID_Phong),
    FOREIGN KEY (ID_Internet) REFERENCES DichVu(ID_DichVu),
    FOREIGN KEY (ID_VeSinh) REFERENCES DichVu(ID_DichVu),
    FOREIGN KEY (ID_BaoVe) REFERENCES DichVu(ID_DichVu)
);

CREATE TABLE HopDongThue (
    ID_HopDong INT PRIMARY KEY IDENTITY(1,1),
    NgayBatDau DATE NOT NULL,
    NgayKetThuc DATE NOT NULL,
    TienDatCoc DECIMAL(10,2) NOT NULL,
    TrangThai VARCHAR(50) NOT NULL,
    ID_Phong INT,
    ID_KhachHang INT,
    FOREIGN KEY (ID_Phong) REFERENCES PhongTro(ID_Phong),
    FOREIGN KEY (ID_KhachHang) REFERENCES KhachHang(ID_KhachHang)
);

CREATE TABLE HoaDon (
    ID_HoaDon INT PRIMARY KEY IDENTITY(1,1),
    ID_HopDong INT,
	ID_Phong INT,
	TenPhong VARCHAR(100),
    NgayTao DATE NOT NULL,
    ThangNam VARCHAR(7) NOT NULL,
    SoTien DECIMAL(20, 2) NOT NULL,
    TrangThaiThanhToan VARCHAR(50) NOT NULL,
    ChiTietDichVu VARCHAR(255),
	 ID_ChiTietDichVu INT,
	  TongSoTien DECIMAL(20, 2) ,
	 	FOREIGN KEY (ID_ChiTietDichVu) REFERENCES ChiTietDichVu(ID_ChiTietDichVu),
    FOREIGN KEY (ID_HopDong) REFERENCES HopDongThue(ID_HopDong),
	FOREIGN KEY (ID_Phong) REFERENCES PhongTro(ID_Phong)
);

CREATE TABLE ThanhToan (
    ID_ThanhToan INT PRIMARY KEY IDENTITY(1,1),
    ID_HoaDon INT,
    NgayThanhToan DATE NOT NULL,
    SoTien DECIMAL(20, 2) NOT NULL,
    PhuongThuc VARCHAR(50) NOT NULL,
    FOREIGN KEY (ID_HoaDon) REFERENCES HoaDon(ID_HoaDon),
	SoTienConLai DECIMAL(20, 2) NOT NULL DEFAULT 0
);

CREATE TABLE KPI (
    ID_KPI INT PRIMARY KEY IDENTITY(1,1),
    ThoiGian DATE NOT NULL,
    TongDoanhThu DECIMAL(20, 2) NOT NULL,
    TongChiPhi DECIMAL(20, 2) NOT NULL,
    TyLeLapDay DECIMAL(20, 2) NOT NULL,
    SoHopDongMoi INT NOT NULL,
    SoHopDongGiaHan INT NOT NULL,
    SoPhongTrong INT NOT NULL,
    SoYeuCauBaoTri INT NOT NULL DEFAULT 0,
	TangTruongDoanhThu VARCHAR(255) 
);



-- có tác dụng để lấy tháng bắt đầu từ 2020-01
CREATE TABLE CurrentMonth (
    CurrentMonth DATE
);
--INSERT INTO CurrentMonth (CurrentMonth) VALUES ('2020-01-01');
------------------------------------------------------------------
CREATE TRIGGER SetVaiTro
ON KhachHang
AFTER INSERT
AS
BEGIN
    UPDATE KhachHang
    SET VaiTro = 0
    FROM KhachHang kh
    INNER JOIN inserted i ON kh.ID_KhachHang = i.ID_KhachHang
    WHERE i.VaiTro IS NULL;
END;

CREATE TRIGGER after_insert_or_update_khach_hang
ON KhachHang
AFTER INSERT, UPDATE
AS
BEGIN
    UPDATE kh
    SET kh.SoPhong = p.TenPhong
     
    FROM KhachHang kh
    INNER JOIN PhongTro p ON kh.ID_Phong = p.ID_Phong
    WHERE kh.ID_KhachHang IN (SELECT ID_KhachHang FROM inserted);
END;


CREATE TRIGGER after_update_phong
ON PhongTro
AFTER UPDATE
AS
BEGIN
    UPDATE kh
    SET kh.SoPhong = inserted.TenPhong
       
    FROM KhachHang kh
    INNER JOIN inserted ON kh.ID_Phong = inserted.ID_Phong
    WHERE inserted.TenPhong <> kh.SoPhong; -- Chỉ cập nhật nếu có thay đổi
END;

/*
UPDATE kh
SET kh.SoPhong = p.TenPhong
FROM KhachHang kh
INNER JOIN PhongTro p ON kh.ID_Phong = p.ID_Phong;

*/
/*DROP PROCEDURE IF EXISTS sp_CapNhatTongTienDichVu;*/
--SELECT * FROM ChiTietDichVu;
/*chúng ta cần thêm đúng giá trị của các id ở bảng dịch vụ vào đây*/
/*DELETE FROM HopDong;
DBCC CHECKIDENT ('HopDong', RESEED, 0);*/
-- Tạo trigger để cập nhật TongTienDichVu trực tiếp trên bảng HopDongThue
CREATE TRIGGER trg_CapNhatTongTienDichVu
ON HopDongThue
AFTER INSERT, UPDATE
AS
BEGIN
    DECLARE @GiaDien DECIMAL(10,2);
    DECLARE @GiaNuoc DECIMAL(10,2);
    DECLARE @GiaInternet DECIMAL(10,2);
    DECLARE @GiaVeSinh DECIMAL(10,2);
    DECLARE @GiaBaoVe DECIMAL(10,2);
    DECLARE @CurrentMonth DATE;

    -- Lấy giá trị từ bảng DichVu
    SELECT @GiaDien = GiaDichVu FROM DichVu WHERE ID_DichVu = 1;
    SELECT @GiaNuoc = GiaDichVu FROM DichVu WHERE ID_DichVu = 2;
    SELECT @GiaInternet = GiaDichVu FROM DichVu WHERE ID_DichVu = 3;
    SELECT @GiaVeSinh = GiaDichVu FROM DichVu WHERE ID_DichVu = 4;
    SELECT @GiaBaoVe = GiaDichVu FROM DichVu WHERE ID_DichVu = 5;

    -- Lấy tháng hiện tại từ bảng CurrentMonth
    SELECT @CurrentMonth = CurrentMonth FROM CurrentMonth;

    -- Chèn dữ liệu mới vào bảng ChiTietDichVu cho các phòng có hợp đồng thuê nhưng chưa có dữ liệu trong ChiTietDichVu
    INSERT INTO ChiTietDichVu (ID_Phong, ThangNam, SoDien, SoNuoc, ID_Internet, ID_VeSinh, ID_BaoVe, TongTienDichVu)
    SELECT 
        ht.ID_Phong,
        FORMAT(@CurrentMonth, 'yyyy-MM') AS ThangNam, -- Tháng năm hiện tại
        ROUND((50 + (RAND(CAST(NEWID() AS VARBINARY)) * (100 - 50))), 2) AS SoDien, -- giá trị ngẫu nhiên từ 50 đến 100
        ROUND((50 + (RAND(CAST(NEWID() AS VARBINARY)) * (100 - 50))), 2) AS SoNuoc, -- giá trị ngẫu nhiên từ 50 đến 100
        (SELECT ID_DichVu FROM DichVu WHERE TenDichVu = 'Internet') AS ID_Internet,
        (SELECT ID_DichVu FROM DichVu WHERE TenDichVu = 'VeSinh') AS ID_VeSinh,
        (SELECT ID_DichVu FROM DichVu WHERE TenDichVu = 'BaoVe') AS ID_BaoVe,
        ISNULL(ROUND((50 + (RAND(CAST(NEWID() AS VARBINARY)) * (100 - 50))), 2), 0) * @GiaDien + 
        ISNULL(ROUND((50 + (RAND(CAST(NEWID() AS VARBINARY)) * (100 - 50))), 2), 0) * @GiaNuoc + 
        @GiaInternet + @GiaVeSinh + @GiaBaoVe AS TongTienDichVu
    FROM HopDongThue ht
    WHERE NOT EXISTS (
        SELECT 1 FROM ChiTietDichVu ctdv
        WHERE ctdv.ID_Phong = ht.ID_Phong
        AND ctdv.ThangNam = FORMAT(@CurrentMonth, 'yyyy-MM')
    );
END;

CREATE TRIGGER trg_UpdateTenPhong
ON ChiTietDichVu
AFTER INSERT, UPDATE
AS
BEGIN
    UPDATE ctdv
    SET TenPhong = pt.TenPhong
    FROM inserted i
    JOIN ChiTietDichVu ctdv ON i.ID_ChiTietDichVu = ctdv.ID_ChiTietDichVu
    JOIN PhongTro pt ON ctdv.ID_Phong = pt.ID_Phong;
END;
--DROP PROCEDURE IF EXISTS sp_ThemChiTietDichVuTheoThang;
-- procedure này chúng ta sẽ gọi từ trên web để nó sẽ cập nhật thêm dữ liệu liên tục
CREATE PROCEDURE sp_ThemChiTietDichVuTheoThang
AS
BEGIN
   DECLARE @GiaDien DECIMAL(10,2);
    DECLARE @GiaNuoc DECIMAL(10,2);
    DECLARE @GiaInternet DECIMAL(10,2);
    DECLARE @GiaVeSinh DECIMAL(10,2);
    DECLARE @GiaBaoVe DECIMAL(10,2);
    DECLARE @CurrentMonth DATE;
    DECLARE @NextMonth DATE;

    -- Lấy giá trị từ bảng DichVu
    SELECT @GiaDien = GiaDichVu FROM DichVu WHERE ID_DichVu = 1;
    SELECT @GiaNuoc = GiaDichVu FROM DichVu WHERE ID_DichVu = 2;
    SELECT @GiaInternet = GiaDichVu FROM DichVu WHERE ID_DichVu = 3;
    SELECT @GiaVeSinh = GiaDichVu FROM DichVu WHERE ID_DichVu = 4;
    SELECT @GiaBaoVe = GiaDichVu FROM DichVu WHERE ID_DichVu = 5;

    -- Lấy tháng hiện tại từ bảng CurrentMonth
    SELECT @CurrentMonth = CurrentMonth FROM CurrentMonth;

    -- Tính tháng tiếp theo
    SET @NextMonth = DATEADD(MONTH, 1, @CurrentMonth);

    -- Chèn dữ liệu mới vào bảng ChiTietDichVu cho các phòng có hợp đồng thuê nhưng chưa có dữ liệu trong ChiTietDichVu
    INSERT INTO ChiTietDichVu (ID_Phong, ThangNam, SoDien, SoNuoc, ID_Internet, ID_VeSinh, ID_BaoVe, TongTienDichVu,TenPhong)
    SELECT 
        pt.ID_Phong,
        FORMAT(@CurrentMonth, 'yyyy-MM') AS ThangNam, -- Tháng năm hiện tại
        ROUND((50 + (RAND(CAST(NEWID() AS VARBINARY)) * (100 - 50))), 2) AS SoDien, -- giá trị ngẫu nhiên từ 50 đến 100
        ROUND((50 + (RAND(CAST(NEWID() AS VARBINARY)) * (100 - 50))), 2) AS SoNuoc, -- giá trị ngẫu nhiên từ 50 đến 100
        (SELECT ID_DichVu FROM DichVu WHERE TenDichVu = 'Internet') AS ID_Internet,
        (SELECT ID_DichVu FROM DichVu WHERE TenDichVu = 'VeSinh') AS ID_VeSinh,
        (SELECT ID_DichVu FROM DichVu WHERE TenDichVu = 'BaoVe') AS ID_BaoVe,
        ISNULL(ROUND((50 + (RAND(CAST(NEWID() AS VARBINARY)) * (100 - 50))), 2), 0) * @GiaDien + 
        ISNULL(ROUND((50 + (RAND(CAST(NEWID() AS VARBINARY)) * (100 - 50))), 2), 0) * @GiaNuoc + 
        @GiaInternet + @GiaVeSinh + @GiaBaoVe AS TongTienDichVu,
		pt.TenPhong
    FROM PhongTro pt
    WHERE pt.TinhTrang = 1; -- Chỉ chọn những phòng có TinhTrang = 1 (đã thuê)


	UPDATE CurrentMonth
    SET CurrentMonth = @NextMonth;
END;

EXEC sp_ThemChiTietDichVuTheoThang;
SELECT * FROM PhongTro;
SELECT * FROM KhachHang;
SELECT * FROM ChiTietDichVu;
SELECT * FROM HopDongThue;
SELECT * FROM KPI;
/*DELETE FROM KPI;
DBCC CHECKIDENT ('KPI', RESEED, 0);
DELETE FROM HoaDon;
DBCC CHECKIDENT ('HoaDon', RESEED, 0);
DELETE FROM ChiTietDichVu;
DBCC CHECKIDENT ('ChiTietDichVu', RESEED, 0);*/

-- -------------------------------------------------------------


CREATE PROCEDURE CapNhatTinhTrangPhongTro
AS
BEGIN
    -- Cập nhật trạng thái phòng thành 'Đã có người thuê' (true) khi có hợp đồng thuê
    UPDATE pt
    SET pt.TinhTrang = 1
    FROM PhongTro pt
    WHERE EXISTS (SELECT 1 FROM HopDongThue h WHERE h.ID_Phong = pt.ID_Phong);

    -- Cập nhật trạng thái phòng thành 'Chưa ai thuê' (false) khi không có hợp đồng thuê
    UPDATE pt
    SET pt.TinhTrang = 0
    FROM PhongTro pt
    WHERE NOT EXISTS (SELECT 1 FROM HopDongThue h WHERE h.ID_Phong = pt.ID_Phong);
END;
-- EXEC CapNhatTinhTrangPhongTro;

CREATE TRIGGER trg_UpdatePhongTroStatus
ON HopDongThue
AFTER INSERT, UPDATE
AS
BEGIN
    -- Cập nhật trạng thái phòng thành 'Đã có người thuê' (true) khi có hợp đồng thuê mới
    UPDATE pt
    SET pt.TinhTrang = 1
    FROM PhongTro pt
    JOIN inserted i ON pt.ID_Phong = i.ID_Phong;
END;

CREATE TRIGGER trg_UpdatePhongTroStatusOnDelete
ON HopDongThue
AFTER DELETE
AS
BEGIN

    
    UPDATE pt
    SET pt.TinhTrang = 0
    FROM PhongTro pt
    LEFT JOIN deleted d ON pt.ID_Phong = d.ID_Phong
    LEFT JOIN HopDongThue h ON pt.ID_Phong = h.ID_Phong
    WHERE h.ID_HopDong IS NULL AND d.ID_Phong IS NOT NULL;

    UPDATE kh
    SET kh.DaThuePhong = 0
    FROM KhachHang kh
    LEFT JOIN deleted d ON kh.ID_KhachHang = d.ID_KhachHang
    LEFT JOIN HopDongThue h ON kh.ID_KhachHang = h.ID_KhachHang
    WHERE h.ID_HopDong IS NULL AND d.ID_KhachHang IS NOT NULL;
END;







/*kiểm tra những khách hàng trong bảng khách hàng đã thuê nhà và cập nhật tình trạng trong bảng phòng trọ thành true*/
CREATE TRIGGER trg_CheckDaThuePhong
ON KhachHang
AFTER INSERT, UPDATE
AS
BEGIN
    DECLARE @ID_KhachHang INT;
    DECLARE @ID_Phong INT;
    DECLARE @DaThuePhong BIT;
    DECLARE @NgayBatDau DATE;
    DECLARE @NgayKetThuc DATE;
    DECLARE @CurrentMonth DATE;
    DECLARE @Year INT;
    DECLARE @Month INT;

    -- Lấy giá trị từ bảng inserted
    SELECT @ID_KhachHang = ID_KhachHang, @ID_Phong = ID_Phong, @DaThuePhong = DaThuePhong
    FROM inserted;

    -- Kiểm tra nếu DaThuePhong là True
    IF @DaThuePhong = 1
    BEGIN
        -- Kiểm tra nếu ID_Phong không tồn tại trong bảng HopDongThue
        IF NOT EXISTS (SELECT 1 FROM HopDongThue WHERE ID_Phong = @ID_Phong)
        BEGIN
            -- Lấy tháng hiện tại từ bảng CurrentMonth
            SELECT @CurrentMonth = CurrentMonth FROM CurrentMonth;

            -- Cập nhật TinhTrang trong bảng PhongTro thành True
            UPDATE PhongTro
            SET TinhTrang = 1
            WHERE ID_Phong = @ID_Phong;

            -- Tính NgayBatDau dựa trên CurrentMonth
            SET @NgayBatDau = @CurrentMonth;

            -- Lấy năm và tháng từ NgayBatDau
            SET @Year = YEAR(@NgayBatDau);
            SET @Month = MONTH(@NgayBatDau);

            -- Xác định NgayKetThuc dựa trên tháng
            IF @Month < 4
            BEGIN
                SET @NgayKetThuc = DATEFROMPARTS(@Year, 4, 1);
            END
            ELSE IF @Month < 7
            BEGIN
                SET @NgayKetThuc = DATEFROMPARTS(@Year, 7, 1);
            END
            ELSE IF @Month < 10
            BEGIN
                SET @NgayKetThuc = DATEFROMPARTS(@Year, 10, 1);
            END
            ELSE
            BEGIN
                SET @NgayKetThuc = DATEFROMPARTS(@Year + 1, 1, 1);
            END

            -- Thêm một dòng dữ liệu mới vào bảng HopDong
            INSERT INTO HopDongThue (NgayBatDau, NgayKetThuc, TienDatCoc, TrangThai, ID_Phong, ID_KhachHang)
            VALUES (@NgayBatDau, @NgayKetThuc, 500000, 0, @ID_Phong, @ID_KhachHang);
        END
    END
END;





/*cập nhật tiền cho bảng hoá đơn*/
--DROP PROCEDURE IF EXISTS sp_UpsertHoaDon;
/*DELETE FROM HoaDon;
DBCC CHECKIDENT ('HoaDon', RESEED, 0);*/
-- SELECT * FROM KPI;
CREATE TRIGGER trg_UpsertHoaDon
ON ChiTietDichVu
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @ID_ChiTietDichVu INT;
    DECLARE @ID_Phong INT;
    DECLARE @ThangNam VARCHAR(7);
    DECLARE @TongTienDichVu DECIMAL(10,2);
    DECLARE @SoTien DECIMAL(10,2);
    DECLARE @NgayTao DATE;
    DECLARE @ID_HopDong INT;
    DECLARE @TenPhong VARCHAR(100);

    -- Temporary table to hold inserted or updated data
    CREATE TABLE #TempChiTietDichVu
    (
        ID_ChiTietDichVu INT,
        ID_Phong INT,
        ThangNam VARCHAR(7),
        TongTienDichVu DECIMAL(10,2),
        TenPhong VARCHAR(100)
    );

    -- Insert new or updated records from ChiTietDichVu into the temporary table
    INSERT INTO #TempChiTietDichVu
    SELECT i.ID_ChiTietDichVu, i.ID_Phong, i.ThangNam, i.TongTienDichVu, pt.TenPhong
    FROM inserted i
    LEFT JOIN HoaDon h ON i.ID_ChiTietDichVu = h.ID_ChiTietDichVu
    JOIN PhongTro pt ON i.ID_Phong = pt.ID_Phong
    WHERE h.ID_ChiTietDichVu IS NULL;

    -- Loop through each record in the temporary table
    WHILE EXISTS (SELECT 1 FROM #TempChiTietDichVu)
    BEGIN
        -- Get the first record from the temporary table
        SELECT TOP 1 @ID_ChiTietDichVu = ID_ChiTietDichVu, 
                     @ID_Phong = ID_Phong, 
                     @ThangNam = ThangNam, 
                     @TongTienDichVu = TongTienDichVu,
                     @TenPhong = TenPhong
        FROM #TempChiTietDichVu;

        -- Lấy giá trị thuê phòng từ bảng PhongTro
        SELECT @SoTien = GiaThue
        FROM PhongTro
        WHERE ID_Phong = @ID_Phong;

        -- Lấy ID_HopDong từ bảng HopDongThue
        SELECT @ID_HopDong = ID_HopDong
        FROM HopDongThue
        WHERE ID_Phong = @ID_Phong;

        -- Tính ngày cuối cùng của ThangNam
        SET @NgayTao = EOMONTH(CAST(@ThangNam + '-01' AS DATE));

        -- Chèn mới vào bảng HoaDon
        INSERT INTO HoaDon (ID_HopDong, NgayTao, ThangNam, SoTien, TrangThaiThanhToan, ChiTietDichVu, ID_ChiTietDichVu, TongSoTien, ID_Phong, TenPhong)
        VALUES (@ID_HopDong, @NgayTao, @ThangNam, @SoTien, 'Chưa thanh toán', CAST(@TongTienDichVu AS VARCHAR(50)), @ID_ChiTietDichVu, @SoTien + @TongTienDichVu, @ID_Phong, @TenPhong);

        -- Ghi nhật ký để kiểm tra
        PRINT 'Inserted new record for ID_Phong: ' + CAST(@ID_Phong AS VARCHAR) + ', ThangNam: ' + @ThangNam;

        -- Xóa bản ghi vừa xử lý khỏi bảng tạm
        DELETE FROM #TempChiTietDichVu WHERE ID_ChiTietDichVu = @ID_ChiTietDichVu;
    END;

    -- Drop the temporary table
    DROP TABLE #TempChiTietDichVu;
END;






--DROP PROCEDURE IF EXISTS ThanhToanHoaDon;
/*CREATE PROCEDURE ThanhToanHoaDon
    @ID_HoaDon INT,
    @SoTien DECIMAL(10,2),
    @PhuongThuc VARCHAR(50) -- Sửa thành VARCHAR(50) cho phù hợp với kiểu dữ liệu của PhuongThuc
AS
BEGIN
    DECLARE @TongSoTien DECIMAL(10,2);
    DECLARE @SoTienConLai DECIMAL(10,2);

    -- Kiểm tra xem ID_HoaDon có tồn tại trong bảng ThanhToan hay không
    IF EXISTS (SELECT 1 FROM ThanhToan WHERE ID_HoaDon = @ID_HoaDon)
    BEGIN
        -- Lấy SoTienConLai hiện tại từ bản ghi gần nhất trong bảng ThanhToan
        SELECT TOP 1 @SoTienConLai = SoTienConLai
        FROM ThanhToan
        WHERE ID_HoaDon = @ID_HoaDon
        ORDER BY NgayThanhToan DESC;

        -- Tính số tiền còn lại
        SET @SoTienConLai = @SoTienConLai - @SoTien;
    END
    ELSE
    BEGIN
        -- Lấy tổng số tiền của hóa đơn từ bảng HoaDon
        SELECT @TongSoTien = TongSoTien
        FROM HoaDon
        WHERE ID_HoaDon = @ID_HoaDon;

        -- Tính số tiền còn lại
        SET @SoTienConLai = @TongSoTien - @SoTien;
    END

    -- Chèn bản ghi mới vào bảng ThanhToan
    INSERT INTO ThanhToan (ID_HoaDon, NgayThanhToan, SoTien, PhuongThuc, SoTienConLai)
    VALUES (@ID_HoaDon, GETDATE(), @SoTien, @PhuongThuc, @SoTienConLai);

    -- Cập nhật trạng thái thanh toán trong bảng HoaDon
    IF @SoTienConLai <= 0
    BEGIN
        UPDATE HoaDon
        SET TrangThaiThanhToan = 'Da Thanh Toan'
        WHERE ID_HoaDon = @ID_HoaDon;
    END
    ELSE
    BEGIN
        UPDATE HoaDon
        SET TrangThaiThanhToan = 'Chua Thanh Toan Het'
        WHERE ID_HoaDon = @ID_HoaDon;
    END
END;

CREATE TRIGGER trg_AfterInsert_ThanhToan
ON ThanhToan
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @ID_HoaDon INT;
    DECLARE @SoTien DECIMAL(10,2);
    DECLARE @PhuongThuc VARCHAR(50);

    -- Lấy giá trị từ bản ghi vừa chèn
    SELECT @ID_HoaDon = ID_HoaDon, 
           @SoTien = SoTien, 
           @PhuongThuc = PhuongThuc
    FROM inserted;

    -- Gọi stored procedure ThanhToanHoaDon
    EXEC ThanhToanHoaDon @ID_HoaDon, @SoTien, @PhuongThuc;
END;
*/
--DROP PROCEDURE IF EXISTS sp_UpdateHopDongThueAndKPI;

/*DELETE FROM KPI;
DBCC CHECKIDENT ('KPI', RESEED, 0);
DELETE FROM HoaDon;
DBCC CHECKIDENT ('HoaDon', RESEED, 0);
DELETE FROM ChiTietDichVu;
DBCC CHECKIDENT ('ChiTietDichVu', RESEED, 0);*/
CREATE PROCEDURE sp_UpdateHopDongThueAndKPI
AS
BEGIN
    DECLARE @CurrentMonth DATE;
    DECLARE @StartDate DATE;
    DECLARE @EndDate DATE;
    DECLARE @SoHopDongGiaHan INT;
    DECLARE @SoHopDongMoi INT;
    DECLARE @LastKPITime DATE;

    -- Lấy tháng hiện tại từ bảng CurrentMonth
    SELECT @CurrentMonth = CurrentMonth FROM CurrentMonth;

    -- Lấy thời gian của bản ghi cuối cùng trong bảng KPI
    SELECT @LastKPITime = MAX(ThoiGian) FROM KPI;

    -- Kiểm tra nếu @LastKPITime là NULL hoặc @LastKPITime + 3 tháng <= @CurrentMonth
    IF @LastKPITime IS NULL OR DATEADD(MONTH, 3, @LastKPITime) <= @CurrentMonth
    BEGIN
        -- Tính toán ngày bắt đầu và ngày kết thúc
        SET @StartDate = @CurrentMonth;
        SET @EndDate = DATEADD(MONTH, 3, @CurrentMonth);

        -- Đếm số lượng hợp đồng sẽ được gia hạn (có ngày kết thúc nhỏ hơn ngày hiện tại trong CurrentMonth)
        SELECT @SoHopDongGiaHan = COUNT(*)
        FROM HopDongThue
        WHERE NgayKetThuc < @CurrentMonth;

        -- Cập nhật thời gian cho các hợp đồng có NgayKetThuc nhỏ hơn CurrentMonth
        UPDATE HopDongThue
        SET NgayBatDau = @StartDate, NgayKetThuc = @EndDate
        WHERE NgayKetThuc < @CurrentMonth;

        -- Đếm số hợp đồng mới và gia hạn dựa vào cột TrangThai
        SELECT @SoHopDongMoi = COUNT(*)
        FROM HopDongThue
        WHERE TrangThai = 0;

        SELECT @SoHopDongGiaHan = COUNT(*)
        FROM HopDongThue
        WHERE TrangThai = 1;

        -- Cập nhật trạng thái của tất cả các hợp đồng về 1
        UPDATE HopDongThue
        SET TrangThai = 1;

        -- Thêm dữ liệu vào bảng KPI với giá trị SoHopDongGiaHan mới
        DECLARE @previousStartDate DATE = DATEADD(MONTH, -3, @CurrentMonth);
        DECLARE @previousEndDate DATE = @CurrentMonth;

        DECLARE @TongDoanhThu DECIMAL(20,2) = 0;
        DECLARE @TongChiPhi DECIMAL(20,2) = 0;
        DECLARE @TyLeLapDay DECIMAL(20,2) = 0;
        DECLARE @SoPhongTrong INT = 0;
        DECLARE @SoYeuCauBaoTri INT = 0;

        SELECT @TongDoanhThu = ISNULL(SUM(TongSoTien), 0)
        FROM HoaDon
        WHERE NgayTao BETWEEN @previousStartDate AND @previousEndDate;

        SET @TongChiPhi = @TongDoanhThu * 0.05;

        DECLARE @SoPhongDaThue INT;
        SELECT @SoPhongDaThue = COUNT(DISTINCT ht.ID_Phong)
        FROM HoaDon h
        JOIN HopDongThue ht ON h.ID_HopDong = ht.ID_HopDong
        WHERE h.NgayTao BETWEEN @previousStartDate AND @CurrentMonth;

        DECLARE @TongSoPhong INT;
        SELECT @TongSoPhong = COUNT(*)
        FROM PhongTro;

        IF @TongSoPhong = 0
            SET @TyLeLapDay = 0;
        ELSE
            SET @TyLeLapDay = (CAST(@SoPhongDaThue AS DECIMAL(20,2)) / @TongSoPhong) * 100;

        -- Tính toán số phòng trống
        SET @SoPhongTrong = @TongSoPhong - @SoPhongDaThue;

        -- Chèn dữ liệu vào bảng KPI
        INSERT INTO KPI (ThoiGian, TongDoanhThu, TongChiPhi, TyLeLapDay, SoHopDongMoi, SoHopDongGiaHan, SoPhongTrong, SoYeuCauBaoTri)
        VALUES (@CurrentMonth, @TongDoanhThu, @TongChiPhi, @TyLeLapDay, @SoHopDongMoi, @SoHopDongGiaHan, @SoPhongTrong, @SoYeuCauBaoTri);
    END
END;

CREATE TRIGGER trg_UpdateKPI_HoaDon
ON HoaDon
AFTER INSERT
AS
BEGIN
    -- Gọi thủ tục lưu trữ để cập nhật KPI
    EXEC sp_UpdateHopDongThueAndKPI;
END;


--DROP PROCEDURE IF EXISTS sp_CalculateRevenueGrowth;
CREATE PROCEDURE sp_CalculateRevenueGrowth
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @currentID INT;
    DECLARE @currentRevenue DECIMAL(20, 2);
    DECLARE @previousID INT;
    DECLARE @previousRevenue DECIMAL(20, 2);
    DECLARE @growth DECIMAL(20, 2);

    -- Kiểm tra và giải phóng con trỏ nếu đã tồn tại
    IF CURSOR_STATUS('global', 'cur') >= 0
    BEGIN
        CLOSE cur;
        DEALLOCATE cur;
    END

    DECLARE cur CURSOR FOR
        SELECT ID_KPI, TongDoanhThu
        FROM KPI;

    OPEN cur;
    FETCH NEXT FROM cur INTO @currentID, @currentRevenue;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Tính ID của quý trước đó
        SET @previousID = @currentID - 4;

        -- Nếu ID của quý trước đó <= 0, tăng trưởng = 100%
        IF @previousID <= 0
        BEGIN
            SET @growth = 100.00;
        END
        ELSE
        BEGIN
            -- Lấy doanh thu của quý trước đó
            SELECT @previousRevenue = TongDoanhThu
            FROM KPI
            WHERE ID_KPI = @previousID;

            -- Nếu không có dữ liệu cho quý trước đó, tăng trưởng = 100%
            IF @previousRevenue IS NULL
            BEGIN
                SET @growth = 100.00;
            END
            ELSE
            BEGIN
                -- Kiểm tra và tránh chia cho số 0
                IF @previousRevenue = 0
                BEGIN
                    SET @growth = 100.00;
                END
                ELSE
                BEGIN
                    -- Tính toán tăng trưởng doanh thu
                    SET @growth = ((@currentRevenue - @previousRevenue) / @previousRevenue) * 100;
                END
            END
        END

        -- Cập nhật giá trị tăng trưởng doanh thu vào bảng KPI
        UPDATE KPI
        SET TangTruongDoanhThu = @growth
        WHERE ID_KPI = @currentID;

        FETCH NEXT FROM cur INTO @currentID, @currentRevenue;
    END

    CLOSE cur;
    DEALLOCATE cur;
END;


-- EXEC sp_CalculateRevenueGrowth;

CREATE TRIGGER trg_CalculateRevenueGrowth
ON KPI
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Gọi stored procedure để tính toán tăng trưởng doanh thu
    EXEC sp_CalculateRevenueGrowth;
END;

SELECT * FROM KPI;



/*
INSERT INTO ThanhToan (ID_HoaDon, NgayThanhToan, SoTien, PhuongThuc)
VALUES (2, '2024-06-30', 490000, 1);

-- Kiểm tra bảng ThanhToan
SELECT * FROM ThanhToan;

-- Kiểm tra bảng HoaDon để xác nhận trạng thái thanh toán đã được cập nhật
SELECT * FROM HoaDon;

DROP PROCEDURE IF EXISTS AddMissingContracts;

ALTER TABLE KPI
DROP COLUMN SoThanhToanCham;


DELETE FROM ThanhToan;
DBCC CHECKIDENT ('ThanhToan', RESEED, 0);
DELETE FROM HoaDon;
DBCC CHECKIDENT ('HoaDon', RESEED, 0);
DELETE FROM HopDongThue;
DBCC CHECKIDENT ('HopDongThue', RESEED, 0);
*/

SELECT name
FROM sys.procedures
