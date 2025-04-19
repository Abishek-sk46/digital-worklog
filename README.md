
# 🧾 Digital Work Log

**Digital Work Log** is a simple and efficient Django-based application that allows users to record daily tasks, manage work hours, and view visual reports through a clean dashboard interface.

---

## 🚀 Features

- 🔐 **User Authentication** – Register, login, and logout securely  
- 📌 **Add/Edit/Delete Logs** – Task title, description, hours spent, and date  
- 📊 **Dashboard** – Visual summary with:
  - Total logs  
  - Total hours  
  - Recent activity  
  - Interactive chart  
- 📅 **Filter Chart Data** – View logs for:
  - Today  
  - Last 7 days  
  - Last 30 days  
  - Last year  
- 🧑‍💼 **Admin Panel Access** – Easily manage users and logs

---

## 🛠 Tech Stack

- **Backend:** Python, Django  
- **Frontend:** HTML, Tailwind CSS, Chart.js  
- **Database:** SQLite (default)  
- **Other:** Django Authentication System

---

## 📸 UI Overview

> 🔹 Clean and responsive UI  
> 🔹 Minimalistic navigation  
> 🔹 Light-themed dashboard  

Screenshots can be added here (optional).

---

## 📂 Folder Structure

```
digitalworklog/
│
├── log_app/
│   ├── migrations/
│   ├── templates/
│   │   ├── log_app/
│   │   └── registration/
│   ├── static/ (optional)
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── digitalworklog/
│   └── settings.py
│
├── db.sqlite3
└── manage.py
```

---

## ⚙️ Setup Instructions

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/digital-worklog.git
   cd digital-worklog
   ```

2. Create a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # or `env\Scripts\activate` on Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the server:
   ```bash
   python manage.py runserver
   ```

7. Open in browser:
   ```
   http://127.0.0.1:8000/
   ```

---

## ✍️ Author

**Abishek S.K**  
College Project | Built with ❤️ using Django  
[GitHub Profile](https://github.com/Abishek-sk46)

---

## 📄 License

This project is for academic use and learning purposes. You’re free to explore and build upon it.
