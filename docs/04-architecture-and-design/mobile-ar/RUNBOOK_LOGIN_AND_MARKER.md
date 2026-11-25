# Huong dan chay: Xay dung Dang nhap va Nhan dien Marker tren Mobile (ARIMMS)

## 1. Yeu cau moi truong
- Node.js >= 20.x va npm
- Expo SDK 58 (entry point ./index.tsx)
- Thiet bi di dong cai san Expo Go (cung mang Wi-Fi/LAN voi may tinh)
- Backend Flask (port 5002) khi can kiem thu API that

## 2. Bien moi truong (.env)
EXPO_PUBLIC_API_BASE_URL=http://192.168.1.80:5002
EXPO_PUBLIC_POLL_INTERVAL_MS=4000
EXPO_PUBLIC_STALE_THRESHOLD_SEC=30
EXPO_PUBLIC_ALLOW_SIM_FALLBACK=true

## 3. Cac buoc khoi chay
1. Vao thu muc docs/04-architecture-and-design/mobile-ar
2. Chay: npx expo start --clear (hoac --port 8082 --clear neu 8081 ban)
3. Quet ma QR bang Expo Go tren iPhone

## 4. Kiem thu Dang nhap & Marker
- Dang nhap qua LoginScreen / AuthContext (tech@arimms.local) va di qua ProtectedStack
- Chon nhanh MKR-NODE-01 / MKR-NODE-02 hoac nhap ma Marker tren ScannerScreen
- Kiem tra doi Marker hoac bam Mat dau thi xoa du lieu Node cu ngay lap tuc
