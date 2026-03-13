from datetime import date, timedelta

from django.utils import timezone

from rewards.models import ActivityLog, Badge, EarnedBadge

XP_PER_LEVEL = 200
RANKS = [
    (0, 'Code Rookie'),
    (2, 'Code Cadet'),
    (5, 'Code Explorer'),
    (10, 'Code Champion'),
    (15, 'Code Legend'),
    (18, 'Code SHERO'),
]

STREAK_MILESTONES = {
    3: 'streak-3-day',
    5: 'streak-5-day',
    7: 'streak-7-day',
    14: 'streak-14-day',
    30: 'streak-30-day',
    60: 'streak-60-day',
    100: 'streak-100-day',
}


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
    today = timezone.now().date()
    if child.last_active_date == today:
        return
    if child.last_active_date == today - timedelta(days=1):
        child.streak += 1
    else:
        child.streak = 1
    child.last_active_date = today
    child.save(update_fields=['streak', 'last_active_date'])

    # Check milestone badges
    if child.streak in STREAK_MILESTONES:
        badge_slug = STREAK_MILESTONES[child.streak]
        badge = Badge.objects.filter(id=badge_slug).first()
        if badge:
            earned, created = EarnedBadge.objects.get_or_create(child=child, badge=badge)
            if created:
                ActivityLog.objects.create(
                    child=child,
                    type='badge_earned',
                    title=f'Earned {badge.name}!',
                    description=f'{child.streak}-day streak milestone!',
                    xp_earned=child.streak * 5,
                )
                child.xp += child.streak * 5
                child.save(update_fields=['xp'])
                check_level_up(child)


def get_rank(missions_completed: int) -> str:
    rank = 'Code Rookie'
    for threshold, title in RANKS:
        if missions_completed >= threshold:
            rank = title
    return rank


def get_current_rank(child):
    """Returns the current Rank object for a child based on completed missions."""
    from missions.models import MissionProgress
    from rewards.models import Rank

    completed = MissionProgress.objects.filter(child=child, status='completed').count()
    return Rank.objects.filter(min_missions__lte=completed).order_by('-min_missions').first()


def get_next_rank(child):
    """Returns the next Rank and missions needed to reach it."""
    from missions.models import MissionProgress
    from rewards.models import Rank

    completed = MissionProgress.objects.filter(child=child, status='completed').count()
    next_rank = Rank.objects.filter(min_missions__gt=completed).order_by('min_missions').first()
    if next_rank:
        return {'rank': next_rank, 'missions_needed': next_rank.min_missions - completed}
    return None


def check_rank_up(child):
    """Check if child has earned a new rank. Returns the new Rank or None."""
    current = get_current_rank(child)
    if current and child.current_rank != current:
        old_rank = child.current_rank
        child.current_rank = current
        child.save(update_fields=['current_rank'])
        ActivityLog.objects.create(
            child=child,
            type='rank_up',
            title=f'Promoted to {current.name}!',
            description=f'You advanced from {old_rank.name if old_rank else "unranked"} to {current.name}!',
            xp_earned=0,
        )
        return current
    return None


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
    check_rank_up(child)

    for next_mission in Mission.objects.filter(unlock_after=mission):
        MissionProgress.objects.get_or_create(child=child, mission=next_mission, defaults={'status': 'available'})
