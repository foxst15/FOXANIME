# ==============================================================================
# SCRIPT PYTHON: TỰ ĐỘNG LẤY DỮ LIỆU PHIM THỰC TẾ TỪ FIREBASE ĐỂ TẠO RSS FEED & SITEMAP
# Dự án: FOXANIME (foxanime.top)
# ==============================================================================

import os
import json
import datetime
from email.utils import format_datetime
import xml.etree.ElementTree as ET

# Kiểm tra thư viện firebase_admin
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("Vui lòng cài đặt: pip install firebase-admin")
    exit()

def get_real_firestore_db():
    """Khởi tạo kết nối Firebase với cấu hình thực tế của FOXANIME"""
    creds_json = os.environ.get("FIREBASE_CREDENTIALS")
    
    if creds_json:
        # Chạy trên GitHub Actions / Server có Secrets
        cert = json.loads(creds_json)
        cred = credentials.Certificate(cert)
    elif os.path.exists("serviceAccountKey.json"):
        # Chạy Local nếu có file khóa
        cred = credentials.Certificate("serviceAccountKey.json")
    else:
        print("⚠️ Chưa tìm thấy biến môi trường FIREBASE_CREDENTIALS hoặc file serviceAccountKey.json.")
        return None

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    return firestore.client()

def fetch_real_movies_and_generate_rss(output_rss_path="rss.xml", output_sitemap_path="sitemap_v2.xml"):
    db = get_real_firestore_db()
    if not db:
        print("Không thể kết nối Firebase. Tiến trình dừng lại.")
        return

    APP_ID = "default-app-id"
    # Truy vấn collection phim thực tế của FoxAnime
    movies_ref = db.collection("artifacts").document(APP_ID).collection("public").document("data").collection("movies")
    
    print("📡 Đang lấy danh sách phim thực tế từ kho dữ liệu Firebase Firestore...")
    docs = movies_ref.stream()

    real_movies = []
    for doc in docs:
        data = doc.to_dict()
        movie_id = doc.id
        title = data.get("title", "").strip()
        if not title:
            continue

        genre = data.get("genre", "Anime Vietsub")
        desc = data.get("description") or data.get("desc") or f"Xem phim {title} Vietsub HD trên FoxAnime."
        status = data.get("status", "dang-chieu")
        episodes = data.get("episodes", [])
        ep_count = len(episodes)

        # Lấy ngày cập nhật
        raw_time = data.get("updatedAt") or data.get("createdAt")
        if isinstance(raw_time, datetime.datetime):
            pub_date = format_datetime(raw_time)
            iso_date = raw_time.strftime("%Y-%m-%d")
        else:
            now = datetime.datetime.now(datetime.timezone.utc)
            pub_date = format_datetime(now)
            iso_date = now.strftime("%Y-%m-%d")

        # Lấy ảnh poster thật
        raw_image = data.get("posterUrl") or data.get("poster") or data.get("image") or ""
        if raw_image.startswith("data:image") or not raw_image:
            image_url = "https://i.imgur.com/Q99M0L5.png"
        else:
            image_url = raw_image if raw_image.startswith("http") else f"https://wsrv.nl/?url={raw_image}"

        # Badge tiêu đề
        if status == "sap-chieu":
            badge = "Sắp Chiếu"
        elif ep_count > 0:
            badge = f"Tập {ep_count}"
        else:
            badge = "Phim Mới"

        real_movies.append({
            "id": movie_id,
            "title": title,
            "badge": badge,
            "ep_count": ep_count,
            "genre": genre,
            "desc": desc,
            "image": image_url,
            "pub_date": pub_date,
            "iso_date": iso_date
        })

    print(f"✅ Đã tải thành công {len(real_movies)} bộ phim thực tế từ CSDL!")

    # ================= 1. SINH TẬP TIN RSS.XML TỪ DỮ LIỆU THẬT =================
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")

    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "FOXANIME - Cập Nhật Phim Mới Nhất"
    ET.SubElement(channel, "link").text = "https://foxanime.top"
    ET.SubElement(channel, "description").text = "Kênh phân phối dữ liệu các tập phim mới nhất của hệ thống FOXANIME."
    ET.SubElement(channel, "language").text = "vi-VN"
    ET.SubElement(channel, "lastBuildDate").text = format_datetime(datetime.datetime.now(datetime.timezone.utc))
    ET.SubElement(channel, "generator").text = "FOXANIME Realtime RSS Generator"

    atom_link = ET.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", "https://foxanime.top/rss.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    for m in real_movies:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = f"[{m['badge']}] {m['title']}"
        ET.SubElement(item, "link").text = f"https://foxanime.top/#movie/{m['id']}"
        
        guid = ET.SubElement(item, "guid", isPermaLink="false")
        guid.text = f"foxanime-{m['id']}-ep{m['ep_count']}"
        
        ET.SubElement(item, "pubDate").text = m["pub_date"]
        ET.SubElement(item, "category").text = m["genre"]
        
        desc_html = f"""<p><img src="{m['image']}" width="300" style="border-radius:8px;" alt="{m['title']}"/></p><p>{m['desc']}</p><p>👉 <a href="https://foxanime.top/#movie/{m['id']}">Xem phim tại đây</a></p>"""
        ET.SubElement(item, "description").text = desc_html

        ET.SubElement(item, "enclosure", url=m["image"], length="125000", type="image/jpeg")

    tree_rss = ET.ElementTree(rss)
    ET.indent(tree_rss, space="    ", level=0)
    tree_rss.write(output_rss_path, encoding="utf-8", xml_declaration=True)
    print(f"🎉 Đã xuất bản file RSS.XML thực tế với {len(real_movies)} tập phim tại: {output_rss_path}")

    # ================= 2. ĐỒNG BỘ CẢ CÁC URL PHIM THẬT VÀO SITEMAP =================
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    today = datetime.date.today().isoformat()

    # Các trang tĩnh
    static_pages = [
        ("https://foxanime.top/", "daily", "1.0"),
        ("https://foxanime.top/manga/", "daily", "0.9"),
        ("https://foxanime.top/donate.html", "monthly", "0.4"),
        ("https://foxanime.top/dmca.html", "monthly", "0.3"),
        ("https://foxanime.top/privacy.html", "monthly", "0.3"),
        ("https://foxanime.top/terms.html", "monthly", "0.3"),
    ]

    for loc, freq, prio in static_pages:
        url_el = ET.SubElement(urlset, "url")
        ET.SubElement(url_el, "loc").text = loc
        ET.SubElement(url_el, "lastmod").text = today
        ET.SubElement(url_el, "changefreq").text = freq
        ET.SubElement(url_el, "priority").text = prio

    # Thêm từng bộ phim thật vào Sitemap
    for m in real_movies:
        url_el = ET.SubElement(urlset, "url")
        ET.SubElement(url_el, "loc").text = f"https://foxanime.top/#movie/{m['id']}"
        ET.SubElement(url_el, "lastmod").text = m["iso_date"]
        ET.SubElement(url_el, "changefreq").text = "weekly"
        ET.SubElement(url_el, "priority").text = "0.8"

    tree_sitemap = ET.ElementTree(urlset)
    ET.indent(tree_sitemap, space="    ", level=0)
    tree_sitemap.write(output_sitemap_path, encoding="utf-8", xml_declaration=True)
    print(f"🎉 Đã đồng bộ {len(real_movies)} URL phim thật vào Sitemap tại: {output_sitemap_path}")

if __name__ == "__main__":
    fetch_real_movies_and_generate_rss()
