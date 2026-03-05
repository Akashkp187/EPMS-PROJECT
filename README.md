# EPMS – Employee Performance Management System

A professional-grade Employee Performance Management System with modern UI (glass morphism, dark/light theme), GSAP animations, and image-rich layouts.

## Features

- **Authentication** – Login, register, session management, role-based access (Admin, Manager, Employee)
- **Dashboard** – Stats, goals, performance trend chart, quick actions, activity timeline
- **Goals** – Create, edit, track progress
- **Performance reviews** – Create and manage reviews (managers)
- **360° Feedback** – Give and receive peer/manager feedback
- **1:1 Meetings** – Schedule and manage one-on-ones
- **Departments** – Manage departments (admin)
- **Training** – Browse and enroll in training
- **KPI** – Define KPIs and view targets
- **Notifications** – In-app notifications
- **Profile & settings** – Edit profile, avatar upload, change password
- **Analytics** – Organization-wide stats

## Tech stack

- **Backend:** Flask 3, SQLAlchemy 2, Flask-Login, Flask-Migrate
- **Frontend:** HTML/CSS/JS, GSAP (animations), Chart.js (dashboard chart)
- **UI:** Glass morphism, Outfit font, dark/light theme, responsive layout
- **Images:** Unsplash (hero and card imagery)

## Setup

1. **Create virtual environment and install dependencies**

   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **Initialize database and seed demo data**

   ```bash
   set FLASK_APP=run.py
   flask init-db
   flask seed
   ```

3. **Run the app**

   ```bash
   python run.py
   ```

   Open http://localhost:5000

## Demo accounts (after seed)

| Role    | Email               | Password   |
|---------|---------------------|------------|
| Admin   | admin@epms.local    | admin123   |
| Manager | manager@epms.local   | manager123 |
| Employee| employee@epms.local | employee123 |

## Roles (Admin, Manager, Employee)

- **Admin** – Full access: manage departments, training, KPIs, and all employees.
- **Manager** – Manage **direct reports** only: employee list, reviews, 1:1 meetings. Cannot manage departments, training, or KPIs.
- **Employee** – Own goals, feedback, profile, and participation in reviews/meetings/training. No management of others.

See **[ROLES.md](ROLES.md)** for a detailed comparison and what each role can and cannot do.

## Project structure

```
DBMS_EPMS/
├── app/
│   ├── __init__.py       # App factory
│   ├── models/           # User, Department, Goal, Review, etc.
│   ├── routes/           # Blueprints (auth, dashboard, employees, ...)
│   ├── templates/        # Jinja2 templates
│   ├── static/
│   │   ├── css/main.css  # Glass UI, theme, layout
│   │   ├── js/app.js     # GSAP, theme toggle, search
│   │   └── uploads/      # User avatars
│   └── utils/            # Decorators (admin_required, manager_required)
├── config.py
├── run.py                # CLI: init-db, seed
└── requirements.txt
```

## License

MIT.
