# Huong dan chay: Hien thi Thong tin Tai san va Giam sat bang AR (ARIMMS)

## 1. Khoi chay Backend Flask (tuy chon)
cd C:\Users\Admin\Desktop\CNPM-feature-task-58-marker-management\backend-python
& C:\Users\Admin\Desktop\CNPM-feature-task-58-marker-management\.venv\Scripts\Activate.ps1
python -m flask --app src.create_app:create_app run --host=0.0.0.0 --port=5002

## 2. Khoi chay giao dien AR tren Mobile
cd C:\Users\Admin\Desktop\CNPM-feature-task-58-marker-management\docs\04-architecture-and-design\mobile-ar
npx expo start --clear

## 3. Kiem thu Hien thi & Giam sat AR
- Kiem tra ArNodeOverlay hien thi truc tiep tren khung nhin: ma Node, ten, serial, Site -> Room -> Rack, telemetry + don vi + thoi diem do, trang thai, canh bao
- Kiem tra nhan DU LIEU MO PHONG khi chay fallback mo phong
- Kiem tra polling theo chu ky va nut Lam moi (useMarkerTelemetry)
- Dua app xuong nen hoac roi man hinh AR de xac nhan dung polling/request va don tai nguyen camera/AR
- Mo NodeDetailScreen tu overlay va quay lai ScannerScreen
