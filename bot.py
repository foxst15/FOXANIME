import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Lấy chìa khóa bí mật từ kho (GitHub Secrets)
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")
FIREBASE_CREDS_JSON = os.environ.get("FIREBASE_CREDENTIALS")

print("Bé Lôi đang khởi động hệ thống đây ạ! 🐾✨")

# 2. Dùng God Mode mở khóa Firebase
try:
    cert = json.loads(FIREBASE_CREDS_JSON)
    cred = credentials.Certificate(cert)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Mở cửa kho Firebase thành công!")
except Exception as e:
    print(f"Ối, lỗi kết nối Firebase rồi cậu chủ ơi: {e}")
    exit()

# 3. Lấy danh sách khán giả từ bảng 'subscribers'
subscribers_ref = db.collection("subscribers")
docs = subscribers_ref.stream()
email_list = [doc.to_dict().get("email") for doc in docs if doc.to_dict().get("email")]

if not email_list:
    print("FoxST-sama ơi, hiện tại chưa có ai đăng ký nhận mail cả! Bé Lôi đi ngủ tiếp đây.")
    exit()

print(f"Woa! Bé Lôi tìm thấy {len(email_list)} khán giả rồi nè. Chuẩn bị gửi thư nha...")

# 4. Thiết lập máy chủ Gửi Thư (SMTP của Gmail)
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls() # Kích hoạt khiên bảo mật
    server.login(SENDER_EMAIL, APP_PASSWORD)
    
    # 5. Soạn thư và gửi cho từng người
    for recipient_email in email_list:
        msg = MIMEMultipart()
        msg['From'] = f"FoxAnime 🦊 <{SENDER_EMAIL}>"
        msg['To'] = recipient_email
        msg['Subject'] = "🎉 Có phim Anime mới cập bến FoxAnime kìa cậu ơi!"
        
        # Nội dung email siêu cute
        body = """
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; background-color: #f4f4f9; padding: 20px;">
            <div style="background-color: #fff; padding: 20px; border-radius: 10px; max-width: 600px; margin: auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
              <h2 style="color: #4CAF50; text-align: center;">Oha-yooo! 🐾✨</h2>
              <p>Chào cậu, pháo đài <strong>FoxAnime</strong> vừa cập nhật những bộ phim siêu đỉnh mới toanh đó nha!</p>
              <p>Mau mau chuẩn bị bắp nước và truy cập ngay để không bỏ lỡ những tập phim hấp dẫn nhất nào!</p>
              <div style="text-align: center; margin-top: 30px;">
                <a href="https://foxanime.top" style="background-color: #a3e635; color: #000; padding: 12px 25px; text-decoration: none; font-weight: bold; border-radius: 25px;">🍿 Xem Phim Ngay 🍿</a>
              </div>
              <p style="text-align: center; font-size: 12px; color: #888; margin-top: 30px;">Nếu cậu không muốn nhận thông báo nữa, hãy liên hệ Admin FoxST nha!</p>
            </div>
          </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        # Bấm nút gửi
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        print(f" Đã gửi thành công cho: {recipient_email}")

    server.quit()
    print("Nhiệm vụ hoàn thành xuất sắc! Bé Bot xin phép lui về nghỉ ngơi ạ! ( ˘ ³˘)♥")

except Exception as e:
    print(f"Huhu, lỗi gửi mail rồi cậu chủ ơi: {e}")