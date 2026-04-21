# Dashboard Thống Kê Bán Hàng

Ứng dụng Flask + SQLite theo dõi đơn hàng, doanh thu, sản phẩm bán chạy và KPI bán hàng.

## Tính năng

- Lưu khách hàng và đơn hàng bằng SQLite
- Dashboard doanh thu, số đơn, giá trị trung bình
- REST API top sản phẩm và danh sách đơn mới nhất

## Công nghệ

- Python 3.11+
- Flask
- SQLite
- Pytest
- HTML/CSS dashboard

## Chạy dự án

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Mặc định ứng dụng chạy ở `http://localhost:5004`.

## API chính

- `GET /health` - kiểm tra trạng thái ứng dụng
- `GET /api/stats` - thống kê tổng quan
- `GET /api/items` - danh sách dữ liệu mới nhất

## Kiểm thử

```bash
python -m pytest -q
```

## Cấu trúc

```text
.
├── app.py
├── requirements.txt
├── templates/index.html
├── static/style.css
└── tests/test_app.py
```

Dự án này sử dụng SQLite nội bộ và tự tạo dữ liệu mẫu khi khởi động.
