<div align="center">
  <img src="anh/foxanimelogo.jpg" alt="FoxAnime Logo" width="150" height="150" style="border-radius: 50%; box-shadow: 0 0 15px rgba(163,230,53,0.5);">
  
  <h1>🌸 FOXANIME 🌸</h1>
  
  <p><em>Nền tảng xem Anime trực tuyến mượt mà, giao diện hiện đại và tối ưu trải nghiệm người dùng!</em></p>
  
  <p>
    <a href="https://foxanime.top/"><b>🌐 Trải Nghiệm Trực Tiếp Tại FoxAnime.Top</b></a>
  </p>

</div>

---

## 📖 Giới thiệu (Introduction)
**FoxAnime** là một dự án Web Streaming Anime cá nhân được phát triển với mục đích tạo ra một không gian xem phim chất lượng cao. Dự án không chỉ dừng lại ở giao diện người dùng (Client) với thiết kế UI/UX hiện đại (Glassmorphism), mà còn tích hợp một hệ thống Quản trị viên (Admin Dashboard) mạnh mẽ, tự động hóa nhiều quy trình thao tác dữ liệu.

## ✨ Tính năng nổi bật (Key Features)

### 👤 Dành cho Người xem (Client-side)
*   📺 **Trải nghiệm xem phim thông minh:** Tích hợp tính năng ghi nhớ thời gian xem dở (Resume watching) và tự động chuyển tập kế tiếp (Auto-next) kể cả khi dùng Iframe.
*   🔐 **Xác thực người dùng:** Đăng nhập an toàn, chống lỗi trình duyệt với Google Auth (Hybrid Login: Popup/Redirect).
*   💬 **Tương tác sôi động:** Đánh giá sao (Rating), bình luận theo thời gian thực (Real-time Comments) và khả năng cập nhật Avatar thông qua Link URL.
*   📚 **Thư viện cá nhân:** Tính năng "Thích" giúp người dùng lưu trữ các bộ phim yêu thích vào thư viện riêng.
*   🔍 **Tìm kiếm & Lọc dữ liệu:** Thanh tìm kiếm trực tiếp (Live Search), lọc anime theo Thể loại, Mùa (Season), và Lịch chiếu trong tuần.
*   📱 **Thiết kế Responsive:** Giao diện tương thích hoàn hảo trên mọi thiết bị (Mobile, Tablet, Desktop) với Tailwind CSS.

### ⚙️ Dành cho Quản trị viên (Admin Panel)
*   📊 **Dashboard Thống kê:** Quản lý tổng số lượng phim, tập phim và theo dõi lượt xem/like tổng quan.
*   🛠️ **Quản lý Database:** Thêm, sửa, xóa Anime và Tập phim dễ dàng. Hỗ trợ xử lý ảnh Poster/Banner trực tiếp sang định dạng Base64.
*   🚀 **Auto/Bulk Import:** Hỗ trợ ánh xạ dữ liệu hàng loạt từ API JSON bên ngoài và tính năng dán danh sách hàng loạt Link M3U8/MP4/Iframe để tạo tập phim nhanh chóng.
*   🖼️ **Hero Slider Management:** Giao diện điều khiển Slider trang chủ cho phép Admin tùy ý hiển thị ngẫu nhiên hoặc chỉ định thủ công các bộ phim nổi bật.

## 🛠️ Công nghệ sử dụng (Tech Stack)

**Frontend:**
*   HTML5, CSS3, JavaScript (ES6+ Modules)
*   [Tailwind CSS](https://tailwindcss.com/) (Styling)
*   [Swiper.js](https://swiperjs.com/) (Touch Slider)
*   [Ionicons](https://ionic.io/ionicons) & [FontAwesome](https://fontawesome.com/) (Icons)

**Backend & Services:**
*   [Firebase Firestore](https://firebase.google.com/docs/firestore) (NoSQL Realtime Database)
*   [Firebase Authentication](https://firebase.google.com/docs/auth) (Google Login & Anonymous Auth)
*   [Vercel](https://vercel.com/) (Hosting & Deployment)

## 🚀 Cài đặt để chạy cục bộ (Run Locally)

1. **Clone kho lưu trữ này về máy:**
   ```bash
   git clone [https://github.com/your-username/foxanime.git](https://github.com/your-username/foxanime.git)
   

**Thiết lập Firebase:**
 * Tạo một dự án trên Firebase Console.
 * Kích hoạt Firestore Database và Authentication (Bật Google Sign-in và Anonymous).
 * Thay thế FIREBASE_DEFAULT_CONFIG trong file index.html và admin.html bằng config của bạn.
 
**Mở dự án:**
 * Sử dụng Live Server extension trong VSCode (hoặc bất kỳ local server nào) để mở file index.html.

**👨‍💻 Tác giả (Author):**
* FoxST (Nguyễn Văn Hải) - Sinh viên CNTT @ Trường Đại học Phạm Văn Đồng

* Email Liên hệ: haistrem6792@gmail.com

* Trang web: foxanime.top
