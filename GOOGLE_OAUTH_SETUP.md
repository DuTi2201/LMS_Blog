# Hướng dẫn thiết lập Google OAuth 2.0 cho LMS Blog Platform

## Bước 1: Tạo Google Cloud Project

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Đăng nhập bằng tài khoản Google của bạn
3. Tạo project mới hoặc chọn project hiện có
4. Ghi nhớ Project ID

## Bước 2: Kích hoạt Google+ API

1. Trong Google Cloud Console, đi tới **APIs & Services** > **Library**
2. Tìm kiếm "Google+ API" hoặc "People API"
3. Click **Enable** để kích hoạt API

## Bước 3: Tạo OAuth 2.0 Credentials

1. Đi tới **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. Nếu chưa có OAuth consent screen, bạn sẽ được yêu cầu tạo:
   - Chọn **External** user type
   - Điền thông tin ứng dụng:
     - App name: `LMS Blog Platform`
     - User support email: email của bạn
     - Developer contact information: email của bạn
   - Thêm scopes: `email`, `profile`, `openid`
   - Thêm test users nếu cần

4. Tạo OAuth client ID:
   - Application type: **Web application**
   - Name: `LMS Blog Platform Web Client`
   
   **Authorized JavaScript origins** (Frontend URLs):
   - `http://localhost:3000` (Next.js frontend development server)
   - `http://127.0.0.1:3000` (Alternative localhost)
   - Đây là nơi JavaScript code chạy (frontend React/Next.js)
   
   **Authorized redirect URIs** (Backend callback URLs):
   - `http://localhost:8001/api/v1/auth/google-login` (Backend FastAPI endpoint)
   - `http://127.0.0.1:8001/api/v1/auth/google-login` (Alternative localhost)
   - Đây là nơi Google sẽ redirect sau khi user authorize (backend endpoint)
   
   **Lưu ý quan trọng:** 
   - Với Google ID Token flow hiện tại, Authorized redirect URIs có thể **không cần thiết**
   - Nếu Google yêu cầu, hãy thêm các URLs trên
   - Endpoint `/api/v1/auth/google-login` nhận Google ID token từ frontend (không phải redirect callback)

5. Click **CREATE**

## Bước 4: Lấy Client ID và Client Secret

1. Sau khi tạo thành công, bạn sẽ thấy popup với:
   - **Client ID**: Dạng `xxxxx.apps.googleusercontent.com`
   - **Client Secret**: Chuỗi ký tự ngẫu nhiên

2. Copy cả hai giá trị này

## Bước 5: Cập nhật Environment Variables

### Backend (.env)
```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret
```

### Frontend (.env.local)
```bash
# Google OAuth Configuration
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
```

## Bước 6: Test Google Login

1. Restart cả backend và frontend servers
2. Mở ứng dụng tại `http://localhost:3000`
3. Click vào nút Login
4. Thử click "Continue with Google"
5. Bạn sẽ được redirect tới Google OAuth flow

## Giải thích chi tiết về OAuth URLs

### Authorized JavaScript Origins vs Authorized Redirect URIs

**1. Authorized JavaScript Origins (Frontend)**
- **Mục đích**: Xác định domain nào được phép load Google OAuth JavaScript SDK
- **Sử dụng**: Frontend (React/Next.js) load Google Sign-In button
- **Ví dụ**: `http://localhost:3000`
- **Tương ứng**: Frontend application domain
- **Lưu ý**: Chỉ cần domain, không cần path cụ thể

**2. Authorized Redirect URIs (Backend)**
- **Mục đích**: URL mà Google sẽ redirect user sau khi authorize
- **Sử dụng**: Backend (FastAPI) nhận authorization code từ Google
- **Ví dụ**: `http://localhost:8001/api/v1/auth/google-login` (với ID Token flow hiện tại)
- **Tương ứng**: Backend API endpoint
- **Lưu ý**: Phải là URL đầy đủ với path cụ thể

### Luồng hoạt động Google OAuth

**Lưu ý:** Hệ thống LMS hiện tại sử dụng **Google ID Token** thay vì traditional OAuth flow.

1. **Frontend** (localhost:3000): User click "Sign in with Google"
2. **Google**: Hiển thị popup OAuth và user đăng nhập/authorize
3. **Google**: Trả về **ID Token** trực tiếp cho frontend (không redirect)
4. **Frontend**: Gửi ID Token đến **Backend** endpoint `/api/v1/auth/google-login`
5. **Backend**: Verify ID Token với Google để lấy thông tin user
6. **Backend**: Kiểm tra user đã được admin tạo trong hệ thống chưa
7. **Backend**: Tạo JWT access token và refresh token cho user
8. **Frontend**: Nhận JWT tokens và đăng nhập user vào ứng dụng

**Điểm khác biệt quan trọng:**
- Không cần redirect URIs thực sự vì Google trả token trực tiếp
- Frontend xử lý toàn bộ Google authentication
- Backend chỉ verify token và tạo session

## Lưu ý quan trọng

- **Bảo mật**: Không commit Client Secret vào git repository
- **Domain**: Trong production, cần thêm domain thực tế vào Authorized origins
- **Verification**: Google có thể yêu cầu verify ứng dụng nếu có nhiều users
- **Quotas**: Kiểm tra API quotas và limits
- **HTTPS**: Production phải sử dụng HTTPS cho cả frontend và backend URLs

## Troubleshooting

### Lỗi "redirect_uri_mismatch"
- Kiểm tra Authorized redirect URIs trong Google Console
- Đảm bảo URL chính xác (http vs https, port number)

### Lỗi "invalid_client"
- Kiểm tra Client ID có đúng không
- Đảm bảo API đã được enable

### Nút Google không hiển thị
- Kiểm tra NEXT_PUBLIC_GOOGLE_CLIENT_ID trong .env.local
- Kiểm tra browser console có lỗi JavaScript không
- Đảm bảo Google SDK được load thành công

## Demo Client ID (chỉ để test)

Nếu bạn muốn test nhanh mà chưa tạo Google project, có thể sử dụng demo Client ID:
```
1234567890-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com
```

**Lưu ý**: Demo Client ID này không hoạt động thực tế, chỉ để UI hiển thị nút Google login.