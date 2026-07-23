import os
import json
import time
import resend # Động cơ phản lực mới thay cho smtplib!
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Lấy chìa khóa từ két sắt GitHub Secrets
FIREBASE_CREDS_JSON = os.environ.get("FIREBASE_CREDENTIALS")
resend.api_key = os.environ.get("RESEND_API_KEY")

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
    
    # --- TUỆ NHÃN: ĐỌC TRẠNG THÁI VÀ SỐ TẬP ĐỂ TẠO "VĂN MẪU" ---
    status = data.get("status", "dang-chieu")
    episodes = data.get("episodes", [])
    ep_count = len(episodes)
    
    if status == "sap-chieu":
        badge_text = "🔥 PHIM SẮP CHIẾU"
        badge_color = "#fbbf24" # Vàng
        desc_text = "Phim mới sắp cập bến, lót dép hóng ngay!"
        subject_prefix = "[Sắp Chiếu]"
    elif ep_count > 0:
        badge_text = f"✨ CẬP NHẬT: TẬP {ep_count}"
        badge_color = "#00ffaa" # Xanh Neon
        desc_text = f"Vừa cập nhật Tập {ep_count} nóng hổi, xem ngay!"
        subject_prefix = f"[Tập {ep_count}]"
    else:
        badge_text = "🎉 PHIM MỚI LÊN SÓNG"
        badge_color = "#ff69b4" # Hồng
        desc_text = "Siêu phẩm vừa cập bến FoxAnime, cày ngay cho nóng!"
        subject_prefix = "[Phim Mới]"
    # -----------------------------------------------------------
    
   # Lấy link ảnh từ database
    raw_image = data.get("posterUrl") or data.get("poster") or data.get("image") or ""
    
    # Màng lọc bảo vệ và lách luật Hotlink của các web nguồn
    if raw_image.startswith("data:image") or raw_image.strip() == "":
        movie_image = "https://i.imgur.com/Q99M0L5.png" 
    else:
        # Ép qua Proxy để Gmail chịu hiển thị ảnh
        movie_image = f"https://wsrv.nl/?url={raw_image}"

    movies_to_announce.append({
        "id": movie.id,
        "ref": movie.reference,
        "name": movie_name,
        "genre": movie_genre,
        "image": movie_image,
        "badge_text": badge_text,
        "badge_color": badge_color,
        "desc_text": desc_text,
        "subject_prefix": subject_prefix
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

# Gửi mail thông báo bằng động cơ Resend
try:
    # --- THIẾT KẾ THẺ BÀI: Tích hợp Văn mẫu tự động ---
    movie_cards_html = ""
    for m in movies_to_announce:
        movie_cards_html += f"""
        <div style="background-color: #1e1346; border-radius: 12px; border: 1px solid #5d3f9e; overflow: hidden; max-width: 320px; margin: 0 auto 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); font-family: Arial, sans-serif; text-align: left;">
            
            <img src="{m['image']}" style="width: 100%; height: auto; display: block; border-bottom: 2px solid #5d3f9e;" alt="{m['name']}">
            
            <div style="padding: 15px;">
                <!-- Huy hiệu Văn mẫu -->
                <div style="display: inline-block; background-color: {m['badge_color']}20; color: {m['badge_color']}; border: 1px solid {m['badge_color']}; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-bottom: 10px; letter-spacing: 0.5px;">
                    {m['badge_text']}
                </div>
                
                <h3 style="color: #e0e7ff; font-size: 20px; font-weight: bold; margin: 0 0 5px 0; line-height: 1.3;">{m['name']}</h3>
                <p style="color: #94a3b8; font-size: 13px; margin: 0 0 10px 0; line-height: 1.5;">{m['genre']}</p>
                
                <!-- Lời chào mời riêng cho từng loại -->
                <p style="color: #ff69b4; font-size: 14px; font-weight: bold; margin: 0;">
                    👉 {m['desc_text']}
                </p>
            </div>
            
        </div>
        """

    # TIÊU ĐỀ BIẾN HÌNH: Có thêm thẻ [Tập Mới] hay [Sắp Chiếu]
    first_movie = movies_to_announce[0]
    subject_line = f"🎉 FoxAnime: {first_movie['subject_prefix']} {first_movie['name']} đã có mặt!"
    
    # Phần nội dung body HTML siêu xinh xắn
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; background-color: #f4f4f9; padding: 20px; margin: 0;">
        <div style="background-color: #ffffff; padding: 30px 20px; border-radius: 15px; max-width: 600px; margin: auto; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center;">
          <h2 style="color: #4CAF50; font-size: 26px; margin-bottom: 10px;">Oha-yooo! 🐾✨</h2>
          <p style="font-size: 16px; color: #555; margin-bottom: 30px;">Trạm tin tức <strong>FoxAnime</strong> vừa bắt được tín hiệu nóng hổi dành cho cậu nè:</p>
          
          <!-- NHÚNG DANH SÁCH CARD VÀO ĐÂY -->
          {movie_cards_html}
          
          <p style="font-size: 16px; color: #555; margin-top: 30px;">Mau mau chuẩn bị bắp nước và truy cập pháo đài ngay thôi!</p>
          <div style="margin-top: 30px; margin-bottom: 30px;">
            <a href="https://foxanime.top" style="background-color: #a3e635; color: #000000; padding: 14px 30px; text-decoration: none; font-weight: bold; font-size: 18px; border-radius: 30px; display: inline-block; box-shadow: 0 4px 6px rgba(163, 230, 53, 0.3);">🍿 Khám Phá Ngay 🍿</a>
          </div>
          
          <!-- Tấm bùa hộ mệnh chống Spam -->
          <hr style="border: none; border-top: 1px solid #eee; margin-bottom: 15px;">
          <p style="font-size: 12px; color: #999; margin: 0;">
            Bạn nhận được thư này vì đã đăng ký nhận thông báo từ FoxAnime.<br>
            Nếu không muốn nhận thư nữa, cậu có thể <a href="https://foxanime.top" style="color: #4CAF50; text-decoration: underline;">nhấn vào đây để hủy đăng ký</a>.
          </p>
        </div>
      </body>
    </html>
    """

    for recipient_email in email_list:
        # Lắp ráp tên lửa Resend
        params = {
            "from": "FoxAnime 🦊 <thongbao@foxanime.top>", # Đã đổi sang hòm thư VIP!
            "to": [recipient_email],
            "subject": subject_line,
            "html": body
        }
        
        # Khai hỏa!
        email = resend.Emails.send(params)
        
        # Bắt Bé Bot đi ngủ 2 giây để tránh kẹt xe hệ thống!
        time.sleep(2)
    
    print("Đã gửi mail thành công bằng động cơ phản lực Resend!")

    # Đánh dấu phim đã thông báo xong (lật cờ thành True)
    for m in movies_to_announce:
        m["ref"].update({"isNotified": True})
        print(f"Đã cập nhật trạng thái isNotified=True cho: {m['name']}")

except Exception as e:
    print(f"Huhu, tên lửa Resend xịt khói rồi cậu chủ ơi: {e}")
