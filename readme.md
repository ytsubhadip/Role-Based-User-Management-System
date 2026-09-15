
```
role_based_user_management/
│
├── app/
│   │
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── database.py
│   ├── config.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── admin.py
│   │   ├── teacher.py
│   │   └── student.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── registration.py
│   │   ├── admin.py
│   │   ├── teacher.py
│   │   └── student.py
│   │
│   ├── dependencies/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── roles.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── otp_service.py
│   │   ├── email_service.py
│   │   ├── password_service.py
│   │   └── user_service.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── security.py
│       ├── otp.py
│       └── password.py
│
├── templates/
│   │
│   ├── base.html
│   │
│   ├── auth/
│   │   ├── login.html
│   │   ├── registration.html
│   │   ├── verify_otp.html
│   │   ├── change_password.html
│   │   └── forgot_password.html
│   │
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   ├── create_user.html
│   │   ├── edit_user.html
│   │   ├── students.html
│   │   ├── teachers.html
│   │   └── assign_teacher.html
│   │
│   ├── teacher/
│   │   ├── dashboard.html
│   │   ├── students.html
│   │   ├── student_detail.html
│   │   └── edit_student.html
│   │
│   └── student/
│       ├── dashboard.html
│       ├── profile.html
│       └── teacher.html
│
├── static/
│   │
│   ├── css/
│   │   ├── style.css
│   │   ├── auth.css
│   │   ├── admin.css
│   │   ├── teacher.css
│   │   └── student.css
│   │
│   ├── js/
│   │   ├── auth.js
│   │   ├── registration.js
│   │   ├── otp.js
│   │   ├── admin.js
│   │   ├── teacher.js
│   │   └── student.js
│   │
│   └── images/
│       └── default-profile.png
│
├── alembic/
│   ├── versions/
│   │   └── ...
│   ├── env.py
│   └── script.py.mako
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_registration.py
│   ├── test_admin.py
│   ├── test_teacher.py
│   ├── test_student.py
│   └── test_permissions.py
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
├── README.md
└── Procfile

```