# Medical AI Professional Platform

ოთხი რეალური TensorFlow/Keras მოდელი ერთ Flask სისტემაში:

- Ophthalmology — 4 classes
- Dentistry — 5 classes
- Radiology — binary sigmoid
- Dermatology — 22 classes, EfficientNetB3, Top-5

## ფუნქციები

- Login / Register
- პროფესიონალური Dashboard
- მოდელის ავტომატური არჩევა
- REST API
- History SQLite-ში
- PDF report
- Prometheus metrics (`/metrics`)
- Docker / Docker Compose
- GitHub Actions CI
- Lazy model loading

## Windows-ზე გაშვება

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

გახსენი:

```text
http://127.0.0.1:5000
```

## Docker

```bash
docker compose up --build
```

გახსენი:

```text
http://127.0.0.1:8080
```

## REST API

ავტორიზებული session-ით:

```text
POST /api/v1/predict/ophthalmology
POST /api/v1/predict/dentistry
POST /api/v1/predict/radiology
POST /api/v1/predict/dermatology
```

multipart/form-data ველი:

```text
image=<file>
```

## უსაფრთხოების შენიშვნა

Production-ში შეცვალე `SECRET_KEY`, გამოიყენე HTTPS, PostgreSQL და cloud object storage.

ეს სისტემა სასწავლო/კვლევითი მიზნებისთვისაა და არ წარმოადგენს სამედიცინო მოწყობილობას ან დიაგნოსტიკურ სისტემას.
