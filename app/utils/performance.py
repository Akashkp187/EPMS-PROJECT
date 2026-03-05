"""
Helpers for computing composite performance scores over time.

We combine goals, reviews (ratings), and KPI achievements into a single
0–100 performance score per period (month) for a given employee.
"""
from datetime import datetime
from typing import List, Tuple, Optional

from sqlalchemy import func

from app import db
from app.models import Goal, Review, KPITarget

# Default component weights for the composite score.
# You can tune these to match HR policy as long as they sum to 1.0.
# Current policy:
#   - Reviews: 30%
#   - Goals:   30%
#   - KPIs:    40%
GOAL_WEIGHT = 0.3
REVIEW_WEIGHT = 0.3
KPI_WEIGHT = 0.4


def _clamp(value: Optional[float], minimum: float = 0.0, maximum: float = 100.0) -> Optional[float]:
    if value is None:
        return None
    return max(minimum, min(maximum, float(value)))


def compute_user_performance_series(
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_points: int = 12,
) -> List[Tuple[str, float]]:
    """
    Compute a monthly performance series for a user.

    For each month we:
    - Take avg goal progress (%)
    - Take avg review rating (1–5) and scale to 0–100
    - Take avg KPI achievement (actual/target*100), capped at 0–100
    Then combine using weights (defaults):
        score = 0.3 * review_score + 0.3 * goal_score + 0.4 * kpi_score
    Only metrics that exist for that month are used, with weights re-normalized.

    Returns a list of (label, score) ordered by time ascending, where label is like "Jan 24".
    """
    # Goals: average progress by month (updated_at)
    goals_q = db.session.query(
        func.strftime("%Y-%m", Goal.updated_at).label("month"),
        func.avg(Goal.progress).label("avg_progress"),
    ).filter(Goal.user_id == user_id)

    # Reviews: average rating by month (period_end)
    reviews_q = db.session.query(
        func.strftime("%Y-%m", Review.period_end).label("month"),
        func.avg(Review.rating).label("avg_rating"),
    ).filter(Review.user_id == user_id, Review.rating.isnot(None))

    # KPI targets: average achievement % by month (period_end)
    kpi_q = db.session.query(
        func.strftime("%Y-%m", KPITarget.period_end).label("month"),
        func.avg((KPITarget.actual_value / KPITarget.target_value) * 100.0).label(
            "avg_achievement"
        ),
    ).filter(
        KPITarget.user_id == user_id,
        KPITarget.actual_value.isnot(None),
        KPITarget.target_value > 0,
    )

    if start_date is not None:
        goals_q = goals_q.filter(Goal.updated_at >= start_date)
        reviews_q = reviews_q.filter(Review.period_end >= start_date)
        kpi_q = kpi_q.filter(KPITarget.period_end >= start_date)
    if end_date is not None:
        goals_q = goals_q.filter(Goal.updated_at <= end_date)
        reviews_q = reviews_q.filter(Review.period_end <= end_date)
        kpi_q = kpi_q.filter(KPITarget.period_end <= end_date)

    goals_rows = goals_q.group_by("month").order_by("month").all()
    reviews_rows = reviews_q.group_by("month").order_by("month").all()
    kpi_rows = kpi_q.group_by("month").order_by("month").all()

    goals_by_month = {row.month: float(row.avg_progress or 0.0) for row in goals_rows}
    reviews_by_month = {row.month: float(row.avg_rating or 0.0) for row in reviews_rows}
    kpi_by_month = {row.month: float(row.avg_achievement or 0.0) for row in kpi_rows}

    all_months = sorted(set(goals_by_month) | set(reviews_by_month) | set(kpi_by_month))
    if not all_months:
        return []

    # Optionally limit to the most recent N months
    if max_points and len(all_months) > max_points:
        all_months = all_months[-max_points:]

    series: List[Tuple[str, float]] = []

    for month_key in all_months:
        components = []
        weights = []

        # Goals
        if month_key in goals_by_month:
            goal_score = _clamp(goals_by_month[month_key], 0.0, 100.0)
            if goal_score is not None:
                components.append(goal_score)
                weights.append(GOAL_WEIGHT)

        # Reviews (rating 1–5 scaled to 0–100)
        if month_key in reviews_by_month:
            avg_rating = reviews_by_month[month_key]
            review_score = _clamp((avg_rating / 5.0) * 100.0, 0.0, 100.0)
            if review_score is not None:
                components.append(review_score)
                weights.append(REVIEW_WEIGHT)

        # KPI (achievement % capped 0–100)
        if month_key in kpi_by_month:
            kpi_score = _clamp(kpi_by_month[month_key], 0.0, 100.0)
            if kpi_score is not None:
                components.append(kpi_score)
                weights.append(KPI_WEIGHT)

        if not components or not weights:
            continue

        total_weight = sum(weights)
        score = sum(c * w for c, w in zip(components, weights)) / total_weight

        # Convert "YYYY-MM" to a friendly label like "Jan 24"
        try:
            dt = datetime.strptime(month_key + "-01", "%Y-%m-%d")
            label = dt.strftime("%b %y")
        except ValueError:
            label = month_key

        series.append((label, round(score, 1)))

    return series


def compute_user_latest_score(
    user_id: int,
    months: int = 3,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Optional[float]:
    """
    Single aggregate performance score for a user (average of last N months).
    Returns 0–100 or None if no data.
    """
    from datetime import timedelta
    if end_date is None:
        end_date = datetime.utcnow()
    if start_date is None:
        start_date = end_date - timedelta(days=months * 31)
    series = compute_user_performance_series(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        max_points=months,
    )
    if not series:
        return None
    scores = [s for _, s in series]
    return round(sum(scores) / len(scores), 1)

