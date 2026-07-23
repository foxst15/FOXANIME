import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

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

# Tọa độ VIP đi thẳng vào kho phim
APP_ID = "default-app-id" 
movies_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("movies")

# --- 📡 BẬT RA ĐA ĐỂ KIỂM TRA ---
all_movies = list(movies_ref.stream())
print(f"Bíp bíp! Ra đa của Bé Lôi đếm được tổng cộng {len(all_movies)} bộ phim trong kho!")
# ------------------------------------------

# Lọc ra những phim có cờ isNotified == false
new_movies = movies_ref.where(filter=FieldFilter("isNotified", "==", False)).stream()

movies_to_announce = []
for movie in new_movies:
    data = movie.to_dict()
    movie_name = data.get("title", "Một bộ phim siêu hay") 
    movie_genre = data.get("genre", "Đang cập nhật thể loại")
    
    # Lấy link ảnh từ database
    raw_image = data.get("posterUrl") or data.get("poster") or data.get("image") or ""
    
    # Màng lọc bảo vệ và lách luật Hotlink của các web nguồn
    if raw_image.startswith("data:image") or raw_image.strip() == "":
        movie_image = "https://i.imgur.com/Q99M0L5.png" 
    else:
        # Ép qua Proxy để Gmail chịu hiển thị ảnh từ nguonc.com
        movie_image = f"https://wsrv.nl/?url={raw_image}"

    movies_to_announce.append({
        "id": movie.id,
        "ref": movie.reference,
        "name": movie_name,
        "genre": movie_genre,
        "image": movie_image
    })

if not movies_to_announce:
    print("Không có phim hoặc tập mới nào cần báo. Bé Lôi đi ngủ tiếp đây! ( ˘ ³˘)♥")
    exit()

print(f"Bíp bíp! Phát hiện {len(movies_to_announce)} nội dung mới! Bắt đầu chuẩn bị gửi mail...")

# Lấy danh sách khán giả
subscribers_ref = db.collection("subscribers")
docs = subscribers_ref.stream()
email_list = [doc.to_dict().get("email") for doc in docs if doc.to_dict().get("email")]

if not email_list:
    print("Chưa có ai đăng ký nhận mail cả!")
    exit()

# Gửi mail thông báo
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls() 
    server.login(SENDER_EMAIL, APP_PASSWORD)
    
    # --- THIẾT KẾ THẺ BÀI TỐI GIẢN ---
    movie_cards_html = ""
    for m in movies_to_announce:
        movie_cards_html += f"""
        <div style="background-color: #1e1346; border-radius: 12px; border: 1px solid #5d3f9e; overflow: hidden; max-width: 320px; margin: 0 auto 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); font-family: Arial, sans-serif; text-align: left;">
            
            <!-- Ảnh Poster (Bọc proxy siêu mượt) -->
            <img src="{m['image']}" style="width: 100%; height: auto; display: block; border-bottom: 2px solid #5d3f9e;" alt="{m['name']}">
            
            <!-- Phần Tên & Thể loại bên dưới -->
            <div style="padding: 15px;">
                <h3 style="color: #e0e7ff; font-size: 20px; font-weight: bold; margin: 0 0 5px 0; line-height: 1.3;">{m['name']}</h3>
                <p style="color: #94a3b8; font-size: 13px; margin: 0; line-height: 1.5;">{m['genre']}</p>
            </div>
            
        </div>
        """

    for recipient_email in email_list:
        msg = MIMEMultipart()
        msg['From'] = f"FoxAnime 🦊 <{SENDER_EMAIL}>"
        msg['To'] = recipient_email
        msg['Subject'] = "🎉 FoxAnime vừa cập nhật tập mới / phim mới siêu HOT!"
        
        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; background-color: #f4f4f9; padding: 20px; margin: 0;">
            <div style="background-color: #ffffff; padding: 30px 20px; border-radius: 15px; max-width: 600px; margin: auto; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center;">
              <h2 style="color: #4CAF50; font-size: 26px; margin-bottom: 10px;">Oha-yooo! 🐾✨</h2>
              <p style="font-size: 16px; color: #555; margin-bottom: 30px;">Pháo đài <strong>FoxAnime</strong> vừa lên sóng nội dung mới toanh dành cho cậu nè:</p>
              
              <!-- NHÚNG DANH SÁCH CARD VÀO ĐÂY -->
              {movie_cards_html}
              
              <p style="font-size: 16px; color: #555; margin-top: 30px;">Mau mau chuẩn bị bắp nước và truy cập để xem ngay cho nóng nhé!</p>
              <div style="margin-top: 30px; margin-bottom: 10px;">
                <a href="https://foxanime.top" style="background-color: #a3e635; color: #000000; padding: 14px 30px; text-decoration: none; font-weight: bold; font-size: 18px; border-radius: 30px; display: inline-block; box-shadow: 0 4px 6px rgba(163, 230, 53, 0.3);">🍿 Xem Phim Ngay 🍿</a>
              </div>
            </div>
          </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
    
    server.quit()
    print("Đã gửi mail thành công cho tất cả khán giả!")

    # Đánh dấu phim đã thông báo xong (lật cờ thành True)
    for m in movies_to_announce:
        m["ref"].update({"isNotified": True})
        print(f"Đã cập nhật trạng thái isNotified=True cho: {m['name']}")

except Exception as e:
    print(f"Huhu, lỗi gửi mail rồi cậu chủ ơi: {e}")
