from datetime import date, timedelta

from django.utils import timezone

from rewards.models import ActivityLog, EarnedBadge

XP_PER_LEVEL = 200
RANKS = [
    (0, 'Code Rookie'),
    (2, 'Code Cadet'),
    (5, 'Code Explorer'),
    (10, 'Code Champion'),
    (15, 'Code Legend'),
    (18, 'Code SHERO'),
]


def xp_for_level(level: int) -> int:
    return level * XP_PER_LEVEL


def check_level_up(child):
    required = xp_for_level(child.level)
    if child.xp >= required:
        child.level += 1
        child.save(update_fields=['level'])
        ActivityLog.objects.create(
            child=child,
            type='level_up',
            title=f'Reached Level {child.level}!',
            description="You're getting stronger, SHERO!",
        )
        return True
    return False


def update_streak(child):
    today = date.today()
    if child.last_active_date == today:
        return
    if child.last_active_date == today - timedelta(days=1):
        child.streak += 1
    else:
        child.streak = 1
    child.last_active_date = today
    child.save(update_fields=['streak', 'last_active_date'])
    if child.streak in (3, 5, 7, 14, 30):
        ActivityLog.objects.create(
            child=child,
            type='streak',
            title=f'{child.streak}-Day Streak!',
            description=f"You've been coding for {child.streak} days straight",
        )


def get_rank(missions_completed: int) -> str:
    rank = 'Code Rookie'
    for threshold, title in RANKS:
        if missions_completed >= threshold:
            rank = title
    return rank


def is_arc_completed(child, arc):
    """Return True if the child has viewed every scene in the arc."""
    from story.models import SceneProgress

    if not arc or not child:
        return True
    total = arc.scenes.count()
    if total == 0:
        return True
    viewed = SceneProgress.objects.filter(child=child, scene__arc=arc).count()
    return viewed >= total


def complete_mission(child, mission):
    from missions.models import Mission, MissionProgress

    progress = MissionProgress.objects.get(child=child, mission=mission)
    progress.status = 'completed'
    progress.progress = 100
    progress.completed_at = timezone.now()
    progress.save()

    child.xp += mission.xp
    child.save(update_fields=['xp'])

    for reward in mission.rewards.filter(type='badge').select_related('badge'):
        EarnedBadge.objects.get_or_create(child=child, badge=reward.badge)
        ActivityLog.objects.create(
            child=child,
            type='badge_earned',
            title=f'Earned "{reward.badge.name}" Badge',
            description=reward.badge.description,
        )

    ActivityLog.objects.create(
        child=child,
        type='mission_completed',
        title=f'Completed "{mission.title}"',
        description=mission.description,
        xp_earned=mission.xp,
    )
    check_level_up(child)
    update_streak(child)

    for next_mission in Mission.objects.filter(unlock_after=mission):
        MissionProgress.objects.get_or_create(child=child, mission=next_mission, defaults={'status': 'available'})
