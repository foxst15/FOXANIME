// Tên của bộ nhớ đệm (Sau này cậu chủ update web thì đổi tên này thành v2, v3 nha)
const CACHE_NAME = 'foxanime-offline-v1';

// Danh sách "lương thực" cô người máy cần giấu vào kho để xài lúc mất mạng
const urlsToCache = [
    '/',
    '/index.html',
    '/anh/foxanimelogo.jpg',
    '/anh/foxanimecanhbao.jpg',
    '/anh/bannerxemphim.png'
];

// Sự kiện 1: Khi cô người máy được cài đặt -> Đi gom đồ cất vào kho
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('📦 Bé Lôi đã lén giấu giao diện Offline vào kho rồi nha!');
                return cache.addAll(urlsToCache);
            })
    );
});

// Sự kiện 2: Dọn dẹp rác cũ (Nếu cậu chủ update phiên bản mới)
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('🧹 Bé Lôi đang quét dọn kho cũ...', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Sự kiện 3: Gác cổng! Bắt tất cả các luồng tải dữ liệu
self.addEventListener('fetch', event => {
    event.respondWith(
        // Cố gắng chạy ra ngoài Internet lấy dữ liệu như bình thường...
        fetch(event.request).catch(() => {
            // ...Á á! Rớt mạng rồi! Mở kho đồ ra lấy hàng chữa cháy thôi!
            return caches.match(event.request).then(response => {
                // Trả về file tương ứng trong kho, nếu không có thì ném file index.html ra để hiện bảng lỗi 5XX
                return response || caches.match('/index.html');
            });
        })
    );
});
