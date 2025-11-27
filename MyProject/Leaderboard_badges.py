from .models import Badges, StudentBadge, Leaderboard
from django.contrib.auth.models import User
from celery import shared_task

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def award_badge(user: User, badge_type: str):
    """
    Awards a badge of type `badge_type` to the given user if not already awarded.
    """
    try:
        badge = Badges.objects.get(type=badge_type)
    except Badges.DoesNotExist:
        print(f"Badge type '{badge_type}' not found.")
        return

    already_awarded = StudentBadge.objects.filter(user=user, badge=badge).exists()

    if not already_awarded:
        StudentBadge.objects.create(user=user, badge=badge)
        print(f" Badge '{badge.name}' awarded to {user.username}.")
    else:
        print(f"ℹ {user.username} already has the '{badge.name}' badge.")
@shared_task
def add_points(user: User, points: int):
    """
    Adds points to the user's leaderboard entry.
    """
    leaderboard_entry, created = Leaderboard.objects.get_or_create(user=user)
    leaderboard_entry.points += points
    leaderboard_entry.save()
    print(f"Added {points} points to {user.username}. Total points: {leaderboard_entry.points}")