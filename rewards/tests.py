import datetime as dt
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, RequestFactory, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import ChildPreferences, ChildProfile, ParentUser
from characters.models import Character
from core.utils import (
    check_rank_up,
    complete_mission,
    get_current_rank,
    get_next_rank,
    update_streak,
)
from missions.models import Mission, MissionProgress
from academy.models import Lesson, LearningTrack, LessonProgress
from rewards.models import ActivityLog, Badge, EarnedBadge, Rank


def _create_parent(email='parent@test.com'):
    user = ParentUser.objects.create_user(
        username=email, email=email, password='testpass123', name='Test Parent'
    )
    return user


def _create_child(parent, nickname='TestChild'):
    from django.contrib.auth.hashers import make_password
    child = ChildProfile.objects.create(
        parent=parent,
        nickname=nickname,
        pin=make_password('1234'),
        avatar_character='byte',
    )
    ChildPreferences.objects.create(child=child)
    return child


def _create_character():
    return Character.objects.create(
        slug='byte',
        name='Byte',
        title='Logic Guide',
        description='Helps with logic',
        backstory='A friendly guide',
        quote='Let us code!',
        primary_color='#000',
        secondary_color='#111',
        bg_color='#222',
        order=1,
    )


def _create_mission(character, slug='mission-1', num=1, xp=50, unlock_after=None):
    return Mission.objects.create(
        id=slug,
        num=num,
        title=f'Mission {num}',
        description=f'Description for mission {num}',
        long_description=f'Long description for mission {num}',
        character=character,
        difficulty='easy',
        xp=xp,
        skills=['logic'],
        mentor_tip='tip',
        why_learn_this='because',
        estimated_minutes=10,
        starter_code='print("hello")',
        language='python',
        is_active=True,
        unlock_after=unlock_after,
    )


def _seed_ranks():
    ranks_data = [
        {'slug': 'code-rookie', 'name': 'Code Rookie', 'title': 'Just Getting Started', 'emoji': '🌱', 'min_missions': 0, 'color': '#94A3B8', 'order': 1},
        {'slug': 'code-cadet', 'name': 'Code Cadet', 'title': 'Learning the Basics', 'emoji': '⭐', 'min_missions': 3, 'color': '#60A5FA', 'order': 2},
        {'slug': 'code-explorer', 'name': 'Code Explorer', 'title': 'Discovering New Worlds', 'emoji': '🚀', 'min_missions': 6, 'color': '#34D399', 'order': 3},
        {'slug': 'code-hero', 'name': 'Code Hero', 'title': 'Defending the Digital World', 'emoji': '🦸', 'min_missions': 10, 'color': '#F59E0B', 'order': 4},
        {'slug': 'code-master', 'name': 'Code Master', 'title': 'Master of the Code', 'emoji': '👑', 'min_missions': 15, 'color': '#F97316', 'order': 5},
        {'slug': 'code-shero', 'name': 'Code SHERO', 'title': 'Ultimate Digital Hero', 'emoji': '💎', 'min_missions': 20, 'color': '#7B2D8E', 'order': 6},
    ]
    for r in ranks_data:
        Rank.objects.update_or_create(slug=r['slug'], defaults=r)


def _seed_streak_badges():
    streak_badges = [
        ('streak-3-day', '3-Day Streak', '3-day streak milestone!', '🔥', 'common', 'streak'),
        ('streak-5-day', '5-Day Streak', '5-day streak milestone!', '🔥🔥', 'common', 'streak'),
        ('streak-7-day', 'Week Warrior', '7-day streak milestone!', '⚡', 'rare', 'streak'),
        ('streak-14-day', 'Two-Week Champion', '14-day streak milestone!', '💪', 'rare', 'streak'),
        ('streak-30-day', 'Monthly Master', '30-day streak milestone!', '🏆', 'epic', 'streak'),
        ('streak-60-day', 'Unstoppable', '60-day streak milestone!', '🌟', 'epic', 'streak'),
        ('streak-100-day', 'Legendary Streak', '100-day streak milestone!', '💎', 'legendary', 'streak'),
    ]
    for badge_id, name, desc, emoji, rarity, category in streak_badges:
        Badge.objects.update_or_create(
            id=badge_id,
            defaults={'name': name, 'description': desc, 'emoji': emoji, 'rarity': rarity, 'category': category},
        )


def _get_child_client(parent, child):
    """Create an API client authenticated as a child."""
    client = APIClient()
    refresh = RefreshToken.for_user(parent)
    refresh['child_id'] = str(child.id)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


def _get_parent_client(parent):
    """Create an API client authenticated as a parent."""
    client = APIClient()
    refresh = RefreshToken.for_user(parent)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


class RankProgressionTest(TestCase):
    """Test 1: Rank progression - complete missions and verify rank changes."""

    def setUp(self):
        _seed_ranks()
        self.parent = _create_parent()
        self.child = _create_child(self.parent)
        self.character = _create_character()

    def test_rank_progression_rookie_to_cadet_to_explorer(self):
        # Start at Rookie (0 missions)
        rank = get_current_rank(self.child)
        self.assertEqual(rank.slug, 'code-rookie')

        # Complete 3 missions to reach Cadet
        missions = []
        for i in range(1, 7):
            m = _create_mission(self.character, slug=f'mission-{i}', num=i)
            missions.append(m)
            MissionProgress.objects.create(child=self.child, mission=m, status='available')

        for i in range(3):
            complete_mission(self.child, missions[i])

        self.child.refresh_from_db()
        rank = get_current_rank(self.child)
        self.assertEqual(rank.slug, 'code-cadet')
        self.assertEqual(self.child.current_rank.slug, 'code-cadet')

        # Complete 3 more → Explorer
        for i in range(3, 6):
            complete_mission(self.child, missions[i])

        self.child.refresh_from_db()
        rank = get_current_rank(self.child)
        self.assertEqual(rank.slug, 'code-explorer')

    def test_next_rank(self):
        result = get_next_rank(self.child)
        # With 0 missions, next rank is Code Cadet (3 missions)
        self.assertIsNotNone(result)
        self.assertEqual(result['rank'].slug, 'code-cadet')
        self.assertEqual(result['missions_needed'], 3)


class StreakBadgesTest(TestCase):
    """Test 2: Streak badges - simulate consecutive days and verify badges awarded."""

    def setUp(self):
        _seed_streak_badges()
        self.parent = _create_parent()
        self.child = _create_child(self.parent)

    def test_streak_milestone_badges(self):
        today = timezone.now().date()

        for day in range(7):
            current_date = today + timedelta(days=day)
            # Set last_active_date to simulate consecutive days
            if day > 0:
                self.child.last_active_date = current_date - timedelta(days=1)
            else:
                self.child.last_active_date = None
            self.child.save(update_fields=['last_active_date'])

            with patch('core.utils.timezone') as mock_tz:
                mock_tz.now.return_value = dt.datetime(
                    current_date.year, current_date.month, current_date.day,
                    12, 0, 0, tzinfo=dt.timezone.utc
                )
                update_streak(self.child)
                self.child.refresh_from_db()

        self.assertEqual(self.child.streak, 7)

        # Check badges earned
        earned_slugs = set(EarnedBadge.objects.filter(child=self.child).values_list('badge_id', flat=True))
        self.assertIn('streak-3-day', earned_slugs)
        self.assertIn('streak-5-day', earned_slugs)
        self.assertIn('streak-7-day', earned_slugs)

        # Verify XP bonuses (3*5 + 5*5 + 7*5 = 15 + 25 + 35 = 75)
        streak_xp = ActivityLog.objects.filter(
            child=self.child, type='badge_earned',
            description__icontains='streak milestone'
        ).aggregate(total=Sum('xp_earned'))['total'] or 0
        self.assertEqual(streak_xp, 75)

    def test_streak_reset(self):
        """Streak resets when a day is missed."""
        today = timezone.now().date()

        # Day 1
        self.child.last_active_date = None
        self.child.save()
        with patch('core.utils.timezone') as mock_tz:
            mock_tz.now.return_value = dt.datetime(
                today.year, today.month, today.day, 12, 0, 0, tzinfo=dt.timezone.utc
            )
            update_streak(self.child)
            self.child.refresh_from_db()
            self.assertEqual(self.child.streak, 1)

        # Skip two days
        future = today + timedelta(days=3)
        with patch('core.utils.timezone') as mock_tz:
            mock_tz.now.return_value = dt.datetime(
                future.year, future.month, future.day, 12, 0, 0, tzinfo=dt.timezone.utc
            )
            update_streak(self.child)
            self.child.refresh_from_db()
            self.assertEqual(self.child.streak, 1)  # Reset


from django.db.models import Sum


class ScreenTimeEnforcementTest(TestCase):
    """Test 3: Screen time enforcement middleware."""

    def setUp(self):
        _seed_ranks()
        self.parent = _create_parent()
        self.child = _create_child(self.parent)
        self.child.screen_time_limit_minutes = 30
        self.child.save()
        self.client = _get_child_client(self.parent, self.child)

    def test_screen_time_exceeded_returns_429(self):
        # Create enough activity logs to exceed 30 min limit (11 activities * 3 = 33 min)
        for i in range(11):
            ActivityLog.objects.create(
                child=self.child,
                type='mission_completed',
                title=f'Activity {i}',
                description='test',
                xp_earned=10,
            )

        response = self.client.get('/api/user/progress')
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json()['error'], 'screen_time_exceeded')

    def test_screen_time_not_exceeded(self):
        # Only 3 activities = 9 minutes, under 30 min limit
        for i in range(3):
            ActivityLog.objects.create(
                child=self.child,
                type='mission_completed',
                title=f'Activity {i}',
                description='test',
                xp_earned=10,
            )

        response = self.client.get('/api/user/progress')
        self.assertEqual(response.status_code, 200)
        self.assertIn('X-Screen-Time-Remaining', response)

    def test_screen_time_next_day_resets(self):
        # Create activities dated yesterday
        yesterday = timezone.now() - timedelta(days=1)
        for i in range(15):
            log = ActivityLog.objects.create(
                child=self.child,
                type='mission_completed',
                title=f'Activity {i}',
                description='test',
                xp_earned=10,
            )
            ActivityLog.objects.filter(id=log.id).update(created_at=yesterday)

        # Today should be fine
        response = self.client.get('/api/user/progress')
        self.assertEqual(response.status_code, 200)


class ParentAnalyticsTest(TestCase):
    """Test 4: Parent analytics endpoint accuracy."""

    def setUp(self):
        _seed_ranks()
        self.parent = _create_parent()
        self.child = _create_child(self.parent)
        self.character = _create_character()
        self.client = _get_parent_client(self.parent)

        # Create missions and progress
        self.mission = _create_mission(self.character)
        MissionProgress.objects.create(child=self.child, mission=self.mission, status='available')
        complete_mission(self.child, self.mission)

        # Create lesson and progress
        self.track = LearningTrack.objects.create(id='track-1', title='Track 1', description='test', icon='📚', color='#000')
        self.lesson = Lesson.objects.create(id='lesson-1', track=self.track, title='Lesson 1', description='test', duration='10 min')
        LessonProgress.objects.create(child=self.child, lesson=self.lesson, completed=True, completed_at=timezone.now())

        # Create badge
        badge = Badge.objects.create(id='test-badge', name='Test Badge', description='test', emoji='⭐', rarity='common', category='test')
        EarnedBadge.objects.create(child=self.child, badge=badge)

    def test_analytics_endpoint(self):
        response = self.client.get(f'/api/parent/children/{self.child.id}/analytics')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['overview']['xp'], self.child.xp)
        self.assertEqual(data['overview']['level'], self.child.level)
        self.assertEqual(data['missions']['completed'], 1)
        self.assertEqual(data['missions']['total'], 1)
        self.assertEqual(data['lessons']['completed'], 1)
        self.assertEqual(data['lessons']['total'], 1)
        self.assertGreaterEqual(data['badges']['earned'], 1)

    def test_analytics_wrong_parent(self):
        other_parent = _create_parent(email='other@test.com')
        other_client = _get_parent_client(other_parent)
        response = other_client.get(f'/api/parent/children/{self.child.id}/analytics')
        self.assertEqual(response.status_code, 404)


class ActivityTimelinePaginationTest(TestCase):
    """Test 5: Activity timeline pagination and filters."""

    def setUp(self):
        self.parent = _create_parent()
        self.child = _create_child(self.parent)
        self.client = _get_parent_client(self.parent)

        # Create 50 activity logs
        for i in range(50):
            ActivityLog.objects.create(
                child=self.child,
                type='mission_completed' if i % 2 == 0 else 'badge_earned',
                title=f'Activity {i}',
                description=f'Description {i}',
                xp_earned=10,
            )

    def test_pagination(self):
        response = self.client.get(f'/api/parent/children/{self.child.id}/timeline')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertIn('count', data)
        self.assertEqual(data['count'], 50)

    def test_type_filter(self):
        response = self.client.get(f'/api/parent/children/{self.child.id}/timeline?type=mission_completed')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 25)

    def test_days_filter(self):
        # Move some logs to 10 days ago
        old_logs = ActivityLog.objects.filter(child=self.child).order_by('created_at')[:20]
        old_date = timezone.now() - timedelta(days=10)
        for log in old_logs:
            ActivityLog.objects.filter(id=log.id).update(created_at=old_date)

        response = self.client.get(f'/api/parent/children/{self.child.id}/timeline?days=7')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 30)


class XPBreakdownTest(TestCase):
    """Test 6: XP breakdown endpoint accuracy."""

    def setUp(self):
        _seed_ranks()
        self.parent = _create_parent()
        self.child = _create_child(self.parent)
        self.character = _create_character()
        self.client = _get_child_client(self.parent, self.child)

        # Complete a mission (creates mission_completed log)
        self.mission = _create_mission(self.character, xp=100)
        MissionProgress.objects.create(child=self.child, mission=self.mission, status='available')
        complete_mission(self.child, self.mission)

        # Add some streak XP manually
        _seed_streak_badges()
        ActivityLog.objects.create(
            child=self.child, type='badge_earned',
            title='Earned 3-Day Streak!', description='streak milestone!', xp_earned=15,
        )

    def test_xp_breakdown(self):
        # Need to avoid screen time check - create fresh client after activities
        response = self.client.get('/api/user/xp-breakdown')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['breakdown']['missions'], 100)
        self.assertGreaterEqual(data['breakdown']['streaks'], 15)


class PilotDataExportTest(TestCase):
    """Test 7: Data export for pilot reporting."""

    def setUp(self):
        _seed_ranks()
        self.parent = _create_parent()
        self.child1 = _create_child(self.parent, nickname='Child1')
        self.child2 = _create_child(self.parent, nickname='Child2')
        self.character = _create_character()
        self.client = _get_parent_client(self.parent)

        # Give child1 some progress
        m = _create_mission(self.character)
        MissionProgress.objects.create(child=self.child1, mission=m, status='available')
        complete_mission(self.child1, m)

        badge = Badge.objects.create(id='export-badge', name='Export Badge', description='test', emoji='⭐', rarity='common', category='test')
        EarnedBadge.objects.create(child=self.child1, badge=badge)

    def test_export_data(self):
        response = self.client.get('/api/parent/export')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        # CamelCase renderer converts keys
        self.assertEqual(data['totalChildren'], 2)
        self.assertEqual(len(data['children']), 2)

        # Find child1 data (truncated ID)
        child1_data = next(c for c in data['children'] if c['childId'] == str(self.child1.id)[:8])
        self.assertEqual(child1_data['missionsCompleted'], 1)
        self.assertGreaterEqual(child1_data['badgesEarned'], 1)
        self.assertEqual(child1_data['avatar'], 'byte')

    def test_export_anonymization(self):
        response = self.client.get('/api/parent/export')
        data = response.json()
        for child_data in data['children']:
            # IDs should be truncated to 8 chars
            self.assertEqual(len(child_data['childId']), 8)


class RankUpActivityLogTest(TestCase):
    """Test 8: Rank-up creates ActivityLog entry."""

    def setUp(self):
        _seed_ranks()
        self.parent = _create_parent()
        self.child = _create_child(self.parent)
        self.character = _create_character()

    def test_rank_up_creates_activity_log(self):
        # Complete 3 missions to rank up from Rookie to Cadet
        missions = []
        for i in range(1, 4):
            m = _create_mission(self.character, slug=f'mission-{i}', num=i)
            missions.append(m)
            MissionProgress.objects.create(child=self.child, mission=m, status='available')

        for m in missions:
            complete_mission(self.child, m)

        # Verify rank_up activity log
        rank_up_logs = ActivityLog.objects.filter(child=self.child, type='rank_up')
        self.assertTrue(rank_up_logs.exists())

        latest_rank_log = rank_up_logs.order_by('-created_at').first()
        self.assertIn('Code Cadet', latest_rank_log.title)

    def test_no_duplicate_rank_up(self):
        """Completing more missions without crossing a threshold should not create rank_up log."""
        _seed_ranks()
        m1 = _create_mission(self.character, slug='m1', num=1)
        m2 = _create_mission(self.character, slug='m2', num=2)
        MissionProgress.objects.create(child=self.child, mission=m1, status='available')
        MissionProgress.objects.create(child=self.child, mission=m2, status='available')

        complete_mission(self.child, m1)
        rank_up_count_1 = ActivityLog.objects.filter(child=self.child, type='rank_up').count()

        complete_mission(self.child, m2)
        rank_up_count_2 = ActivityLog.objects.filter(child=self.child, type='rank_up').count()

        # Both are still within Rookie tier (0-2 missions), so no extra rank_up
        self.assertEqual(rank_up_count_1, rank_up_count_2)
