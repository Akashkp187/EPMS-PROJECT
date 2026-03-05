"""
Department-wise performance rankings: top performers, low performers, and badge sync.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from app import db
from app.models import User, Department, Recognition, Notification
from app.models.user import Role
from app.utils.performance import compute_user_latest_score


# Number of months used for ranking (same window for top/low).
RANKING_MONTHS = 3
# Score below which we consider "low performer" for support (training + meeting).
LOW_PERFORMER_THRESHOLD = 50.0
# Badge key for top-performer recognition (stored in Recognition.badge).
BADGE_TOP_PERFORMER = "top_performer"
# Display title for badge.
BADGE_TOP_PERFORMER_TITLE = "Top Performer"
# Overall organization-wide top 3.
BADGE_OVERALL_TOP = "overall_top_performer"
BADGE_OVERALL_TOP_TITLE = "Organization Top Performer"


def _current_period_ym() -> str:
    """Current year-month string for idempotent badge awards, e.g. '2025-01'."""
    return datetime.utcnow().strftime("%Y-%m")


def get_employees_with_scores(
    department_id: Optional[int] = None,
    months: int = RANKING_MONTHS,
) -> List[Tuple[User, float]]:
    """
    All employees (role=employee) with a department, with their latest aggregate score.
    Returns list of (user, score) sorted by score descending. Score 0 if no data.
    """
    query = User.query.filter(
        User.role == Role.EMPLOYEE,
        User.is_active.is_(True),
        User.department_id.isnot(None),
    )
    if department_id is not None:
        query = query.filter(User.department_id == department_id)
    users = query.all()
    result = []
    for u in users:
        score = compute_user_latest_score(u.id, months=months)
        result.append((u, score if score is not None else 0.0))
    result.sort(key=lambda x: x[1], reverse=True)
    return result


def get_overall_top_performers(
    top_n: int = 3,
    months: int = RANKING_MONTHS,
) -> List[Tuple[User, float]]:
    """
    Top N performers across the entire organization (all departments).
    Returns list of (user, score) sorted by score descending.
    """
    return get_employees_with_scores(department_id=None, months=months)[:top_n]


def get_top_performers_by_department(
    department_id: Optional[int] = None,
    top_n: int = 3,
    months: int = RANKING_MONTHS,
) -> Dict[int, List[Tuple[User, float]]]:
    """
    Top N performers per department. Keys are department ids; values are
    list of (user, score) for that department (up to top_n).
    If department_id is given, only that department is returned.
    """
    if department_id is not None:
        dept_ids = [department_id]
    else:
        dept_ids = [d.id for d in Department.query.order_by(Department.name).all()]
    out = {}
    for dept_id in dept_ids:
        ranked = get_employees_with_scores(department_id=dept_id, months=months)
        out[dept_id] = ranked[:top_n]
    return out


def get_low_performers_by_department(
    department_id: Optional[int] = None,
    bottom_n: int = 5,
    max_score_below: float = LOW_PERFORMER_THRESHOLD,
    months: int = RANKING_MONTHS,
) -> Dict[int, List[Tuple[User, float]]]:
    """
    Low performers per department: employees in the bottom N of the department
    (by recent performance score). Used for performance support (1:1 + training).
    """
    if department_id is not None:
        dept_ids = [department_id]
    else:
        dept_ids = [d.id for d in Department.query.order_by(Department.name).all()]
    out = {}
    for dept_id in dept_ids:
        ranked = get_employees_with_scores(department_id=dept_id, months=months)
        # Bottom N by rank (lowest scores)
        low = list(reversed(ranked))[:bottom_n]
        out[dept_id] = low
    return out


def _system_sender_id() -> Optional[int]:
    """First admin user id to use as sender for system-awarded recognitions."""
    admin = User.query.filter_by(role=Role.ADMIN, is_active=True).first()
    return admin.id if admin else None


def ensure_top_performer_badges(
    department_id: Optional[int] = None,
    period_ym: Optional[str] = None,
    top_n: int = 3,
    months: int = RANKING_MONTHS,
) -> None:
    """
    For each department (or the given one), ensure top N performers have
    a Recognition (badge=top_performer) and a Notification for this period.
    Idempotent: skips if recipient already has this badge in the same month.
    """
    period_ym = period_ym or _current_period_ym()
    sender_id = _system_sender_id()
    if not sender_id:
        return
    top_by_dept = get_top_performers_by_department(
        department_id=department_id, top_n=top_n, months=months
    )
    for dept_id, performers in top_by_dept.items():
        for user, score in performers:
            # Already awarded this month?
            from sqlalchemy import func
            existing = (
                Recognition.query.filter(
                    Recognition.recipient_id == user.id,
                    Recognition.badge == BADGE_TOP_PERFORMER,
                    func.strftime("%Y-%m", Recognition.created_at) == period_ym,
                )
                .first()
            )
            if existing:
                continue
            rec = Recognition(
                recipient_id=user.id,
                sender_id=sender_id,
                badge=BADGE_TOP_PERFORMER,
                message=f"Top performer in department (score: {score:.0f}/100) for {period_ym}.",
            )
            db.session.add(rec)
            db.session.flush()
            notif = Notification(
                user_id=user.id,
                title=f"You earned: {BADGE_TOP_PERFORMER_TITLE}",
                message=f"Congratulations! You've been recognized as a Top Performer in your department for {period_ym}. Your badge is visible on your profile.",
                type="recognition",
                link="/recognition",
            )
            db.session.add(notif)
    db.session.commit()


def ensure_overall_top_performer_badges(
    period_ym: Optional[str] = None,
    top_n: int = 3,
    months: int = RANKING_MONTHS,
) -> None:
    """
    Ensure the overall top N performers (org-wide) have Recognition with badge=overall_top_performer
    and a Notification. Idempotent per period.
    """
    period_ym = period_ym or _current_period_ym()
    sender_id = _system_sender_id()
    if not sender_id:
        return
    top_list = get_overall_top_performers(top_n=top_n, months=months)
    for rank, (user, score) in enumerate(top_list, 1):
        from sqlalchemy import func
        existing = (
            Recognition.query.filter(
                Recognition.recipient_id == user.id,
                Recognition.badge == BADGE_OVERALL_TOP,
                func.strftime("%Y-%m", Recognition.created_at) == period_ym,
            )
            .first()
        )
        if existing:
            continue
        rec = Recognition(
            recipient_id=user.id,
            sender_id=sender_id,
            badge=BADGE_OVERALL_TOP,
            message=f"Top {rank} in organization (score: {score:.0f}/100) for {period_ym}.",
        )
        db.session.add(rec)
        db.session.flush()
        notif = Notification(
            user_id=user.id,
            title=f"You earned: {BADGE_OVERALL_TOP_TITLE}",
            message=f"Congratulations! You're among the top {top_n} performers organization-wide for {period_ym}. Your badge is visible across the app.",
            type="recognition",
            link="/recognition",
        )
        db.session.add(notif)
    db.session.commit()
