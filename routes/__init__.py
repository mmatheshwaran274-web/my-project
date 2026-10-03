import logging
from database.database import db
from database.models import ActivityHistory

logger = logging.getLogger(__name__)


def record_activity(user_id: int, activity_type: str, description: str):
    """
    Utility helper to log actions into ActivityHistory for the authenticated user.
    """
    if not user_id:
        return
    try:
        activity = ActivityHistory(
            user_id=user_id,
            activity_type=activity_type,
            description=description
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to record activity log: {e}")
