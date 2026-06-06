# Django Portfolio

A dynamic personal portfolio for MD Mahbubur Rahman. Profile content, experience, education, skills, social links, highlights, blog posts, and contact messages are managed from Django admin.

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

Admin is available at `http://127.0.0.1:8000/admin/`.
