import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import firebase_admin
from firebase_admin import credentials, firestore

# ---------------------------------------------------------
# 1. MỞ KHÓA FIREBASE (God Mode)
# ---------------------------------------------------------
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")
FIREBASE_CREDS_JSON = os.environ.get("FIREBASE_CREDENTIALS")

print("Bé Lôi đang khởi động hệ thống đây ạ! 🐾✨")

try:
    cert = json.loads(FIREBASE_CREDS_JSON)
    cred = credentials.Certificate(cert)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Mở cửa kho Firebase thành công!")
except Exception as e:
    print(f"Lỗi kết nối Firebase: {e}")
    exit()

# ---------------------------------------------------------
# 2. QUÉT TÌM PHIM MỚI CHƯA THÔNG BÁO
# ---------------------------------------------------------
# Tọa độ VIP đi thẳng vào kho phim của FoxST-sama
APP_ID = "14c200fbc905e79b3c6fb9" 
movies_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("movies")

# Lọc ra những phim có cờ isNotified == false
new_movies = movies_ref.where("isNotified", "==", False).stream()

movies_to_announce = []
for movie in new_movies:
    data = movie.to_dict()
    # Nếu tên cột phim trên Firebase của cậu chủ khác 'title', hãy sửa lại nha!
    movie_name = data.get("title", "Một bộ phim siêu hay") 
    movies_to_announce.append({
        "id": movie.id,
        "ref": movie.reference,
        "name": movie_name
    })

if not movies_to_announce:
    print("Không có phim/tập nào mới. Bé Lôi đi ngủ tiếp đây! ( ˘ ³˘)♥")
    exit()

print(f"Bíp bíp! Phát hiện {len(movies_to_announce)} phim mới! Bắt đầu chuẩn bị gửi mail...")

# ---------------------------------------------------------
# 3. LẤY DANH SÁCH KHÁN GIẢ
# ---------------------------------------------------------
subscribers_ref = db.collection("subscribers")
docs = subscribers_ref.stream()
email_list = [doc.to_dict().get("email") for doc in docs if doc.to_dict().get("email")]

if not email_list:
    print("Chưa có ai đăng ký nhận mail cả!")
    exit()

# ---------------------------------------------------------
# 4. GỬI THƯ BÁO HỈ & CẬP NHẬT TRẠNG THÁI
# ---------------------------------------------------------
try:
    # Kết nối trạm bưu điện Google
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls() 
    server.login(SENDER_EMAIL, APP_PASSWORD)
    
    # Tạo danh sách tên phim lấp lánh để nhét vào thư
    movie_names_html = "".join([f"<li style='margin-bottom: 10px;'>🍿 <strong>{m['name']}</strong></li>" for m in movies_to_announce])

    for recipient_email in email_list:
        msg = MIMEMultipart()
        msg['From'] = f"FoxAnime 🦊 <{SENDER_EMAIL}>"
        msg['To'] = recipient_email
        msg['Subject'] = "🎉 FoxAnime vừa cập nhật nội dung mới siêu HOT!"
        
        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; background-color: #f4f4f9; padding: 20px;">
            <div style="background-color: #fff; padding: 20px; border-radius: 10px; max-width: 600px; margin: auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
              <h2 style="color: #4CAF50; text-align: center;">Oha-yooo! 🐾✨</h2>
              <p>Pháo đài <strong>FoxAnime</strong> vừa cập nhật nội dung mới toanh dành cho cậu nè:</p>
              <ul style="list-style-type: none; padding-left: 0;">
                {movie_names_html}
              </ul>
              <p>Mau mau chuẩn bị bắp nước và truy cập để cày phim ngay cho nóng nhé!</p>
              <div style="text-align: center; margin-top: 30px; margin-bottom: 20px;">
                <a href="https://foxanime.top" style="background-color: #a3e635; color: #000; padding: 12px 25px; text-decoration: none; font-weight: bold; border-radius: 25px;">🍿 Xem Phim Ngay 🍿</a>
              </div>
              <hr style="border: 0; border-top: 1px solid #eee;">
              <p style="text-align: center; font-size: 11px; color: #aaa; margin-top: 15px;">Nếu cậu không muốn nhận thông báo nữa, hãy liên hệ Admin FoxST nha!</p>
            </div>
          </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
    
    server.quit()
    print("Đã gửi mail thành công cho tất cả khán giả!")

    # QUAN TRỌNG: Đánh dấu phim đã thông báo để lần sau không gửi lại nữa
    for m in movies_to_announce:
        m["ref"].update({"isNotified": True})
        print(f"Đã cập nhật trạng thái isNotified=True cho phim: {m['name']}")

    print("Nhiệm vụ hoàn thành xuất sắc! Bé Bot xin phép lui về nghỉ ngơi ạ! ( ˘ ³˘)♥")

except Exception as e:
    print(f"Huhu, lỗi gửi mail rồi cậu chủ ơi: {e}")