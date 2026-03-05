"""
EPMS - Employee Performance Management System
Run: python run.py  or  flask run
"""
import os
from datetime import date, datetime, timedelta
from pathlib import Path

from app import create_app
from app import db
from app.models import (
    User,
    Department,
    Goal,
    Review,
    Notification,
    KPI,
    Feedback,
    Meeting,
    Training,
    TrainingEnrollment,
    KPITarget,
    Recognition,
)
from app.models.user import Role

app = create_app()

def _maybe_auto_init_and_seed():
    """
    Render free tier doesn't support shell access, so optionally initialize + seed
    the database at startup. Controlled by AUTO_INIT_DB=1.
    """
    if os.environ.get("AUTO_INIT_DB", "").strip() not in {"1", "true", "True", "YES", "yes"}:
        return
    with app.app_context():
        db.create_all()
        # Seed only once
        if not User.query.filter_by(email="admin@epms.local").first():
            try:
                seed()
            except Exception as e:
                # Don't crash the server if seed fails; logs will show the error.
                print(f"AUTO_INIT_DB seed failed: {e}")


_maybe_auto_init_and_seed()


@app.cli.command("init-db")
def init_db():
    """Create tables."""
    db.create_all()
    print("Tables created.")


@app.cli.command("reset-db")
def reset_db():
    """Delete database file (if SQLite) and recreate tables + seed. Stop the server first."""
    uri = app.config.get("SQLALCHEMY_DATABASE_URI") or ""
    if "sqlite" in uri:
        # Close any connections from this process so the file can be deleted
        try:
            db.engine.dispose()
        except Exception:
            pass
        # Path is like sqlite:///C:/path/to/instance/epms.db or sqlite:///e:\path\instance\epms.db
        path = Path(uri.replace("sqlite:///", "").lstrip("/"))
        if path.exists():
            try:
                path.unlink()
                print(f"Removed {path}")
            except OSError as e:
                print(f"Could not remove database file (stop the server first): {e}")
                return
        for suffix in ["-wal", "-shm"]:
            extra = Path(str(path) + suffix)
            if extra.exists():
                try:
                    extra.unlink()
                    print(f"Removed {extra}")
                except OSError:
                    pass
    db.create_all()
    print("Tables created.")
    # Run seed logic
    seed()


@app.cli.command("export-logins")
def export_logins():
    """Write all users (admin, managers, employees) with login info to ALL_LOGIN_CREDENTIALS.txt. Passwords: see LOGIN_CREDENTIALS.md for seed defaults."""
    from pathlib import Path
    from sqlalchemy import case
    lines = [
        "MetricForge (EPMS) – All user login information",
        "=" * 60,
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC",
        "",
        "For default passwords (seed data), see LOGIN_CREDENTIALS.md in the project root.",
        "",
        "Format: Role | Email | Username | Name | Department | Job Title",
        "-" * 60,
    ]
    role_order = case((User.role == Role.ADMIN, 0), (User.role == Role.MANAGER, 1), else_=2)
    for u in User.query.order_by(role_order, User.department_id, User.first_name).all():
        dept = u.department.name if u.department else "—"
        lines.append(f"{u.role.upper()} | {u.email} | {u.username} | {u.full_name} | {dept} | {u.job_title or '—'}")
    text = "\n".join(lines)
    base_dir = Path(app.root_path).parent
    out_path = base_dir / "ALL_LOGIN_CREDENTIALS.txt"
    out_path.write_text(text, encoding="utf-8")
    instance_path = Path(app.instance_path) / "ALL_LOGIN_CREDENTIALS.txt"
    instance_path.write_text(text, encoding="utf-8")
    print(f"Written: {out_path}")


@app.cli.command("seed")
def seed():
    """Seed demo data: 10 departments, 10 managers, 12 employees per dept, goals, reviews, feedback, meetings, training, KPIs, notifications."""
    from seed_data import (
        DEPARTMENTS,
        MANAGERS,
        EMPLOYEES_BY_DEPT,
        DEPT_PREFIXES,
        GOAL_TEMPLATES,
        REVIEW_TEMPLATES,
        FEEDBACK_COMMENTS,
        MEETING_TITLES,
        TRAINING_PROGRAMS,
        KPI_DEFS,
        NOTIFICATION_TEMPLATES,
    )

    db.create_all()
    if User.query.filter_by(email="admin@epms.local").first():
        print("Seed already applied.")
        return

    today = date.today()
    now = datetime.utcnow()

    # ---- Departments ----
    departments = []
    for name, code, desc, img in DEPARTMENTS:
        d = Department(name=name, code=code, description=desc, image_url=img)
        db.session.add(d)
        departments.append(d)
    db.session.flush()

    # ---- Admin ----
    admin = User(
        email="admin@epms.local",
        username="admin",
        first_name="Admin",
        last_name="User",
        role=Role.ADMIN,
        department_id=departments[0].id,
    )
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.flush()

    # ---- Managers (one per department) ----
    managers = []
    for i, (suffix, first, last, job_title) in enumerate(MANAGERS):
        prefix = DEPT_PREFIXES[i]
        m = User(
            email=f"{prefix}.manager@epms.local",
            username=f"{prefix}.manager",
            first_name=first,
            last_name=last,
            role=Role.MANAGER,
            department_id=departments[i].id,
            manager_id=admin.id,
            job_title=job_title,
        )
        m.set_password("manager123")
        db.session.add(m)
        managers.append(m)
    db.session.flush()

    # ---- Employees (12 per department) ----
    all_employees = []
    for dept_idx, emp_list in enumerate(EMPLOYEES_BY_DEPT):
        prefix = DEPT_PREFIXES[dept_idx]
        mgr = managers[dept_idx]
        dept = departments[dept_idx]
        for email_local, first_name, last_name, job_title in emp_list:
            username = email_local.replace(".", "_")
            emp = User(
                email=f"{email_local}@epms.local",
                username=username,
                first_name=first_name,
                last_name=last_name,
                role=Role.EMPLOYEE,
                department_id=dept.id,
                manager_id=mgr.id,
                job_title=job_title,
                phone="+91 98765 43210" if dept_idx % 2 == 0 else None,
            )
            emp.set_password("password123")
            db.session.add(emp)
            all_employees.append((emp, dept_idx))
    db.session.flush()

    employees_flat = [e[0] for e in all_employees]
    employees_by_dept = [[] for _ in range(len(departments))]
    for emp, dept_idx in all_employees:
        employees_by_dept[dept_idx].append(emp)

    # ---- Goals (3-5 per employee + 2 per manager); vary completed/active and spread completed updated_at for trend charts ----
    for emp, dept_idx in all_employees:
        for j, (title, desc, progress, status, offset) in enumerate(GOAL_TEMPLATES[: 4 + (emp.id % 2)]):
            target_date = None
            if offset is not None:
                target_date = today + timedelta(days=offset) if offset >= 0 else today - timedelta(days=abs(offset))
            # Spread "completed" goals across past 6 months so Goal Completion Trends graph varies by month
            is_completed = status == "completed" or (j % 2 == 0 and emp.id % 3 == 0)
            goal_status = "completed" if is_completed else status
            goal_progress = 100 if is_completed else progress
            updated_at = None
            if is_completed:
                months_ago = (emp.id + j + dept_idx) % 6  # 0-5 months ago
                updated_at = now - timedelta(days=30 * (months_ago + 1))
            g = Goal(
                user_id=emp.id,
                title=title,
                description=desc,
                progress=goal_progress,
                status=goal_status,
                target_date=target_date,
                weight=j + 1,
            )
            if updated_at is not None:
                g.updated_at = updated_at
            db.session.add(g)
    for mgr in managers:
        db.session.add(
            Goal(
                user_id=mgr.id,
                title="Run monthly 1:1s with all reports",
                description="Ensure regular feedback cycles with each team member.",
                progress=50,
                status="active",
                target_date=today + timedelta(days=30),
            )
        )
        db.session.add(
            Goal(
                user_id=mgr.id,
                title="Improve team performance",
                description="Support the team to meet OKRs and remove blockers.",
                progress=35,
                status="active",
                target_date=today + timedelta(days=60),
            )
        )
    # ---- Goals for admin ----
    db.session.add(
        Goal(
            user_id=admin.id,
            title="Drive org-wide performance framework",
            description="Ensure goals, reviews, and KPIs are aligned across departments.",
            progress=70,
            status="active",
            target_date=today + timedelta(days=90),
        )
    )
    db.session.add(
        Goal(
            user_id=admin.id,
            title="Complete system rollout",
            description="Full adoption of EPMS across all teams.",
            progress=40,
            status="active",
            target_date=today + timedelta(days=120),
        )
    )
    db.session.flush()

    # ---- Reviews (2-3 per employee, completed); vary ratings 1-5 so Top Employees & Dept Performance graphs differ ----
    periods = [
        (today - timedelta(days=180), today - timedelta(days=90)),
        (today - timedelta(days=90), today - timedelta(days=1)),
        (today - timedelta(days=270), today - timedelta(days=181)),
    ]
    for emp, dept_idx in all_employees:
        mgr = managers[dept_idx]
        for k, (p_start, p_end) in enumerate(periods[: 2 + (emp.id % 2)]):
            tpl = REVIEW_TEMPLATES[k % len(REVIEW_TEMPLATES)]
            # Full 1-5 spread: different employees and departments get different ratings for graph variation
            rating = 1 + (emp.id + dept_idx * 7 + k * 11) % 5
            db.session.add(
                Review(
                    user_id=emp.id,
                    reviewer_id=mgr.id,
                    period_start=p_start,
                    period_end=p_end,
                    rating=rating,
                    status="completed",
                    submitted_at=now - timedelta(days=30 - k * 15),
                    summary=tpl[0].format(emp_name=emp.full_name),
                    strengths=tpl[1],
                    improvements=tpl[2],
                )
            )
    # ---- Reviews for admin (2 reviews from different managers) and for each manager (reviewed by admin) ----
    eng_mgr = managers[0]
    db.session.add(
        Review(
            user_id=admin.id,
            reviewer_id=eng_mgr.id,
            period_start=periods[0][0],
            period_end=periods[0][1],
            rating=5,
            status="completed",
            submitted_at=now - timedelta(days=20),
            summary="Strong leadership and system oversight.",
            strengths="Strategic vision, cross-department alignment.",
            improvements="Continue scaling best practices.",
        )
    )
    db.session.add(
        Review(
            user_id=admin.id,
            reviewer_id=managers[1].id,
            period_start=periods[1][0],
            period_end=periods[1][1],
            rating=5,
            status="completed",
            submitted_at=now - timedelta(days=10),
            summary="Effective org-wide alignment and rollout of EPMS.",
            strengths="Communication, stakeholder management.",
            improvements="Continue quarterly check-ins with all dept heads.",
        )
    )
    for mgr in managers:  # all managers get a review from admin
        db.session.add(
            Review(
                user_id=mgr.id,
                reviewer_id=admin.id,
                period_start=periods[0][0],
                period_end=periods[0][1],
                rating=3 + (mgr.id % 3),
                status="completed",
                submitted_at=now - timedelta(days=25 + mgr.id % 10),
                summary=f"Solid performance leading {mgr.department.name if mgr.department else 'team'}.",
                strengths="Team engagement, delivery.",
                improvements="Focus on succession planning.",
            )
        )
    db.session.flush()

    # ---- Feedback (peer and manager); varied ratings 1-5 ----
    for dept_idx, emps in enumerate(employees_by_dept):
        mgr = managers[dept_idx]
        for i, emp in enumerate(emps):
            db.session.add(
                Feedback(
                    recipient_id=emp.id,
                    sender_id=mgr.id,
                    feedback_type="manager",
                    rating=1 + (emp.id + dept_idx + i) % 5,
                    comment=FEEDBACK_COMMENTS[(emp.id + dept_idx) % len(FEEDBACK_COMMENTS)],
                    is_anonymous=False,
                    status="submitted",
                )
            )
            peer = emps[(i + 1) % len(emps)]
            db.session.add(
                Feedback(
                    recipient_id=emp.id,
                    sender_id=peer.id,
                    feedback_type="peer",
                    rating=1 + (emp.id + i * 7) % 5,
                    comment=FEEDBACK_COMMENTS[(emp.id + i) % len(FEEDBACK_COMMENTS)],
                    is_anonymous=(i % 3 == 0),
                    status="submitted",
                )
            )
    # ---- Feedback for admin and managers (so they have data on dashboard) ----
    for mgr in managers:  # admin receives feedback from all managers
        db.session.add(
            Feedback(
                recipient_id=admin.id,
                sender_id=mgr.id,
                feedback_type="subordinate",
                rating=4 + (mgr.id % 2),
                comment="Clear direction and support for the team." if mgr.id % 2 == 0 else "Good alignment on priorities and resources.",
                is_anonymous=False,
                status="submitted",
            )
        )
    for mgr in managers:
        db.session.add(
            Feedback(
                recipient_id=mgr.id,
                sender_id=admin.id,
                feedback_type="manager",
                rating=4,
                comment="Keep up the good work leading your department.",
                is_anonymous=False,
                status="submitted",
            )
        )
    db.session.flush()

    # ---- Meetings (2-4 per employee with their manager) ----
    for emp, dept_idx in all_employees:
        mgr = managers[dept_idx]
        for k in range(2 + (emp.id % 3)):
            title, agenda = MEETING_TITLES[k % len(MEETING_TITLES)]
            scheduled = now + timedelta(days=7 * (k + 1), hours=k)
            if k == 0:
                scheduled = now - timedelta(days=14)
            status = "completed" if k == 0 else "scheduled"
            notes = "Discussion completed. Action items documented." if k == 0 else None
            db.session.add(
                Meeting(
                    employee_id=emp.id,
                    manager_id=mgr.id,
                    scheduled_at=scheduled,
                    duration_minutes=30,
                    title=title,
                    agenda=agenda,
                    notes=notes,
                    status=status,
                )
            )
    # ---- Meetings for admin with each manager (1:1s; admin as manager) ----
    for i, mgr in enumerate(managers):
        for k in range(2):  # 1 completed, 1 scheduled per manager
            title, agenda = MEETING_TITLES[k % len(MEETING_TITLES)]
            scheduled = now - timedelta(days=14 - k * 7) if k == 0 else now + timedelta(days=7 * (i + 1), hours=k)
            status = "completed" if k == 0 else "scheduled"
            notes = "Discussion completed. Priorities aligned." if k == 0 else None
            db.session.add(
                Meeting(
                    employee_id=mgr.id,
                    manager_id=admin.id,
                    scheduled_at=scheduled,
                    duration_minutes=30,
                    title=f"1:1 with {mgr.department.name if mgr.department else 'team'} lead",
                    agenda=agenda,
                    notes=notes,
                    status=status,
                )
            )
    db.session.flush()

    # ---- Trainings and enrollments ----
    trainings = []
    for title, desc, provider, duration, status in TRAINING_PROGRAMS:
        t = Training(
            title=title,
            description=desc,
            provider=provider,
            duration_hours=duration,
            status=status,
            start_date=today - timedelta(days=30) if status in ("completed", "in_progress") else today + timedelta(days=14),
            end_date=today + timedelta(days=60),
        )
        db.session.add(t)
        trainings.append(t)
    db.session.flush()

    for t in trainings:
        # Enroll ~30-50% of employees in each training
        for emp, _ in all_employees:
            if (emp.id + t.id) % 3 == 0 or (emp.id + t.id) % 5 == 0:
                status = "completed" if t.status == "completed" and (emp.id % 2 == 0) else "enrolled"
                db.session.add(
                    TrainingEnrollment(
                        training_id=t.id,
                        user_id=emp.id,
                        status=status,
                        completed_at=now - timedelta(days=5) if status == "completed" else None,
                    )
                )
    # Enroll admin and managers in a few trainings so they have dashboard/training data
    for mgr in managers:
        for t in trainings[:3]:  # first 3 trainings
            if (mgr.id + t.id) % 2 == 0:
                status = "completed" if t.status == "completed" else "enrolled"
                db.session.add(
                    TrainingEnrollment(
                        training_id=t.id,
                        user_id=mgr.id,
                        status=status,
                        completed_at=now - timedelta(days=5) if status == "completed" else None,
                    )
                )
    for t in trainings[:2]:  # admin in first 2 trainings
        db.session.add(
            TrainingEnrollment(
                training_id=t.id,
                user_id=admin.id,
                status="completed" if t.status == "completed" else "enrolled",
                completed_at=now - timedelta(days=10) if t.status == "completed" else None,
            )
        )
    db.session.flush()

    # ---- KPIs and KPITargets; multiple periods so KPI Achievement Over Time graph has varied points ----
    kpis_flat = []
    for dept_idx, kpi_list in enumerate(KPI_DEFS):
        dept = departments[dept_idx]
        for name, desc, unit in kpi_list:
            k = KPI(name=name, description=desc, unit=unit, department_id=dept.id)
            db.session.add(k)
            kpis_flat.append((k, dept_idx))
    db.session.flush()

    # 4 quarters in the past so KPI trend chart shows 4 different bars
    kpi_periods = [
        (today - timedelta(days=365), today - timedelta(days=274)),
        (today - timedelta(days=274), today - timedelta(days=183)),
        (today - timedelta(days=183), today - timedelta(days=92)),
        (today - timedelta(days=92), today - timedelta(days=1)),
    ]
    for kpi, dept_idx in kpis_flat:
        emps = employees_by_dept[dept_idx]
        for emp in emps[: 10]:
            for period_idx, (p_start, p_end) in enumerate(kpi_periods):
                target_val = 25.0 + (emp.id % 25) + (period_idx * 5)
                # Vary achievement % by period and employee so graph is not flat
                achievement_pct = 55 + (emp.id + dept_idx + period_idx * 7) % 45  # 55-99%
                actual_val = round(target_val * (achievement_pct / 100.0), 1)
                db.session.add(
                    KPITarget(
                        kpi_id=kpi.id,
                        user_id=emp.id,
                        period_start=p_start,
                        period_end=p_end,
                        target_value=target_val,
                        actual_value=actual_val,
                    )
                )
    # ---- KPI targets for admin and managers (so they have KPI data on dashboard) ----
    if kpis_flat:
        first_kpi = kpis_flat[0][0]
        for period_idx, (p_start, p_end) in enumerate(kpi_periods[:2]):
            db.session.add(
                KPITarget(
                    kpi_id=first_kpi.id,
                    user_id=admin.id,
                    period_start=p_start,
                    period_end=p_end,
                    target_value=100.0,
                    actual_value=85.0 + (period_idx * 5),
                )
            )
        for mgr in managers:
            dept_kpis = [k for k, dept_idx in kpis_flat if departments[dept_idx].id == mgr.department_id]
            if not dept_kpis:
                dept_kpis = [kpis_flat[0][0]]
            kpi_m = dept_kpis[0]
            for period_idx, (p_start, p_end) in enumerate(kpi_periods[:2]):
                db.session.add(
                    KPITarget(
                        kpi_id=kpi_m.id,
                        user_id=mgr.id,
                        period_start=p_start,
                        period_end=p_end,
                        target_value=80.0,
                        actual_value=70.0 + (mgr.id % 15) + (period_idx * 3),
                    )
                )
    db.session.flush()

    # ---- Notifications ----
    for emp in employees_flat:
        for nt in NOTIFICATION_TEMPLATES[: 2 + (emp.id % 3)]:
            db.session.add(
                Notification(
                    user_id=emp.id,
                    title=nt[0],
                    message=nt[1],
                    type=nt[2],
                    is_read=(emp.id % 2 == 0),
                )
            )
    # Notifications for admin and managers (goals, reviews, 1:1s, training)
    for idx, nt in enumerate(NOTIFICATION_TEMPLATES[:4]):
        db.session.add(
            Notification(
                user_id=admin.id,
                title=nt[0],
                message=nt[1],
                type=nt[2],
                is_read=(idx % 2 == 0),
            )
        )
    for mgr in managers:
        for nt in NOTIFICATION_TEMPLATES[: 2 + (mgr.id % 2)]:
            db.session.add(
                Notification(
                    user_id=mgr.id,
                    title=nt[0],
                    message=nt[1],
                    type=nt[2],
                    is_read=(mgr.id % 2 == 0),
                )
            )
    db.session.flush()

    # ---- Recognitions (badges for a few top performers) ----
    for dept_idx, emps in enumerate(employees_by_dept):
        mgr = managers[dept_idx]
        for emp in emps[:2]:  # first 2 per dept get a badge for demo
            db.session.add(
                Recognition(
                    recipient_id=emp.id,
                    sender_id=mgr.id,
                    badge="top_performer",
                    message=f"Outstanding performance in {departments[dept_idx].name} for the quarter.",
                )
            )
    # Recognitions for managers (from admin) so they have recognition data
    for mgr in managers:
        db.session.add(
            Recognition(
                recipient_id=mgr.id,
                sender_id=admin.id,
                badge="department_lead",
                message=f"Strong leadership of {mgr.department.name if mgr.department else 'your team'} this quarter.",
            )
        )
    db.session.flush()

    # ---- Demo accounts: guaranteed top performer and least performer (Engineering) ----
    eng_dept = departments[0]
    eng_mgr = managers[0]
    top_demo = User(
        email="top.performer@epms.local",
        username="top_performer",
        first_name="Alex",
        last_name="Star",
        role=Role.EMPLOYEE,
        department_id=eng_dept.id,
        manager_id=eng_mgr.id,
        job_title="Senior Engineer",
    )
    top_demo.set_password("top123")
    db.session.add(top_demo)
    db.session.flush()
    least_demo = User(
        email="least.performer@epms.local",
        username="least_performer",
        first_name="Sam",
        last_name="Struggles",
        role=Role.EMPLOYEE,
        department_id=eng_dept.id,
        manager_id=eng_mgr.id,
        job_title="Junior Engineer",
    )
    least_demo.set_password("least123")
    db.session.add(least_demo)
    db.session.flush()
    # High scores for top performer: goals 95–100%, reviews 5, KPI achievement high
    for _ in range(3):
        db.session.add(
            Goal(
                user_id=top_demo.id,
                title="Exceed quarterly targets",
                description="Deliver above expectations.",
                progress=95 + (top_demo.id % 5),
                status="completed",
                target_date=today - timedelta(days=30),
                updated_at=now - timedelta(days=15),
            )
        )
    for p_start, p_end in periods[:3]:
        db.session.add(
            Review(
                user_id=top_demo.id,
                reviewer_id=eng_mgr.id,
                period_start=p_start,
                period_end=p_end,
                rating=5,
                status="completed",
                submitted_at=now - timedelta(days=10),
                summary="Exceptional performance.",
                strengths="Leadership, quality.",
                improvements="None.",
            )
        )
    kpi_eng = KPI.query.filter_by(department_id=eng_dept.id).first()
    if kpi_eng:
        for p_start, p_end in kpi_periods[:2]:
            db.session.add(
                KPITarget(
                    kpi_id=kpi_eng.id,
                    user_id=top_demo.id,
                    period_start=p_start,
                    period_end=p_end,
                    target_value=100.0,
                    actual_value=98.0,
                )
            )
    # Low scores for least performer: goals 10–20%, reviews 1–2, KPI low
    for _ in range(2):
        db.session.add(
            Goal(
                user_id=least_demo.id,
                title="Improve delivery",
                description="Needs support.",
                progress=10 + (least_demo.id % 10),
                status="active",
                target_date=today + timedelta(days=60),
            )
        )
    for p_start, p_end in periods[:2]:
        db.session.add(
            Review(
                user_id=least_demo.id,
                reviewer_id=eng_mgr.id,
                period_start=p_start,
                period_end=p_end,
                rating=1 + (least_demo.id % 2),
                status="completed",
                submitted_at=now - timedelta(days=20),
                summary="Needs improvement.",
                strengths="Willing to learn.",
                improvements="Time management, quality.",
            )
        )
    if kpi_eng:
        for p_start, p_end in kpi_periods[:2]:
            db.session.add(
                KPITarget(
                    kpi_id=kpi_eng.id,
                    user_id=least_demo.id,
                    period_start=p_start,
                    period_end=p_end,
                    target_value=100.0,
                    actual_value=25.0,
                )
            )
    db.session.flush()

    db.session.commit()
    print("Seed complete.")
    print("  Departments:", len(departments))
    print("  Managers:", len(managers))
    print("  Employees:", len(employees_flat) + 2)
    print("Log in with:")
    print("  Admin   -> admin@epms.local / admin123")
    print("  Manager -> eng.manager@epms.local / manager123")
    print("  Employee -> sahil.dev@epms.local / password123")
    print("  Top performer (badges, recognition) -> top.performer@epms.local / top123")
    print("  Least performer (support, 1:1, training) -> least.performer@epms.local / least123")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
