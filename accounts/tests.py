import uuid

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from academy.models import LearningTrack, Lesson, LessonProgress, LessonStep, LessonStepProgress
from accounts.models import ChildProfile, ParentUser
from characters.models import Character
from missions.models import Mission, MissionProgress


def _create_parent():
    return ParentUser.objects.create_user(
        email=f'test-{uuid.uuid4().hex[:8]}@example.com',
        username=f'user-{uuid.uuid4().hex[:8]}',
        password='TestPass123!',
        name='Test Parent',
    )


def _create_child(parent=None):
    if parent is None:
        parent = _create_parent()
    return ChildProfile.objects.create(
        parent=parent,
        nickname=f'Kid-{uuid.uuid4().hex[:6]}',
        pin=make_password('1234'),
        avatar_character='byte',
    )


def _child_token(child):
    token = AccessToken.for_user(child.parent)
    token['child_id'] = str(child.id)
    return str(token)


def _create_character(slug='byte', name='Byte'):
    char, _ = Character.objects.get_or_create(
        slug=slug,
        defaults={
            'name': name,
            'title': f'{name} the Coder',
            'description': 'A cool SHERO',
            'backstory': '',
            'quote': 'Code on!',
            'primary_color': '#000',
            'secondary_color': '#fff',
            'bg_color': '#eee',
            'order': 1,
        },
    )
    return char


def _create_mission(num, char=None, is_active=True):
    if char is None:
        char = _create_character()
    slug = f'mission-{num}-{uuid.uuid4().hex[:6]}'
    return Mission.objects.create(
        id=slug,
        num=num,
        title=f'Mission {num}',
        description=f'Description for mission {num}',
        long_description='',
        character=char,
        difficulty='Beginner',
        xp=80,
        coins=10,
        mentor_tip='',
        why_learn_this='',
        estimated_minutes=10,
        starter_code='',
        language='html',
        is_active=is_active,
    )


def _create_track_and_lesson(track_suffix=None, lesson_suffix=None):
    suffix = track_suffix or uuid.uuid4().hex[:6]
    track = LearningTrack.objects.create(
        id=f'test-track-{suffix}',
        title='Test Track',
        description='Test',
        icon='T',
        color='#000',
        order=1,
    )
    lesson_suf = lesson_suffix or uuid.uuid4().hex[:6]
    lesson = Lesson.objects.create(
        id=f'test-lesson-{lesson_suf}',
        track=track,
        title='Test Lesson',
        description='Test',
        duration='5 min',
        order=1,
    )
    return track, lesson


class JourneyStateBrandNewTest(TestCase):
    """Brand new child: state=brand_new, recommendedAction points to academy."""

    def test_brand_new_child(self):
        child = _create_child()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        resp = client.get('/api/user/journey')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['state'], 'brand_new')
        self.assertEqual(resp.data['completedMissions'], 0)
        self.assertEqual(resp.data['completedLessons'], 0)
        self.assertEqual(resp.data['recommendedAction']['type'], 'academy')
        self.assertEqual(resp.data['recommendedAction']['href'], '/academy')


class JourneyStateAfterLessonsTest(TestCase):
    """After completing 2 lessons: state=ready_for_missions, recommendedAction points to first mission."""

    def test_ready_for_missions_after_two_lessons(self):
        child = _create_child()
        char = _create_character()
        mission = _create_mission(num=1, char=char)

        # Complete 2 lessons
        _, lesson1 = _create_track_and_lesson()
        _, lesson2 = _create_track_and_lesson()
        LessonProgress.objects.create(child=child, lesson=lesson1, completed=True)
        LessonProgress.objects.create(child=child, lesson=lesson2, completed=True)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        resp = client.get('/api/user/journey')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['state'], 'ready_for_missions')
        self.assertEqual(resp.data['completedLessons'], 2)
        self.assertEqual(resp.data['recommendedAction']['type'], 'mission')
        self.assertIn('/play/world-1/', resp.data['recommendedAction']['href'])


class JourneyStateMidMissionsTest(TestCase):
    """After completing 3 missions: state=between_missions, nextMission shows mission 4."""

    def test_between_missions(self):
        child = _create_child()
        char = _create_character()

        # Create 4 missions
        missions = [_create_mission(num=i, char=char) for i in range(1, 5)]

        # Complete first 3
        for m in missions[:3]:
            MissionProgress.objects.create(child=child, mission=m, status='completed')

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        resp = client.get('/api/user/journey')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['state'], 'between_missions')
        self.assertEqual(resp.data['completedMissions'], 3)
        self.assertIn('nextMission', resp.data)
        self.assertEqual(resp.data['nextMission']['num'], 4)


class JourneyStateBossReadyTest(TestCase):
    """After completing 9 missions: state=boss_ready, recommendedAction points to save-the-internet."""

    def test_boss_ready(self):
        child = _create_child()
        char = _create_character()

        # Create and complete 9 missions
        missions = [_create_mission(num=i, char=char) for i in range(1, 10)]
        for m in missions:
            MissionProgress.objects.create(child=child, mission=m, status='completed')

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        resp = client.get('/api/user/journey')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['state'], 'boss_ready')
        self.assertEqual(resp.data['completedMissions'], 9)
        self.assertEqual(resp.data['recommendedAction']['type'], 'boss')
        self.assertEqual(resp.data['recommendedAction']['href'], '/play/world-1/save-the-internet')


class JourneyStateWorldCompleteTest(TestCase):
    """After completing 10 missions: state=world_complete."""

    def test_world_complete(self):
        child = _create_child()
        char = _create_character()

        # Create and complete 10 missions
        missions = [_create_mission(num=i, char=char) for i in range(1, 11)]
        for m in missions:
            MissionProgress.objects.create(child=child, mission=m, status='completed')

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        resp = client.get('/api/user/journey')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['state'], 'world_complete')
        self.assertEqual(resp.data['completedMissions'], 10)
        self.assertEqual(resp.data['recommendedAction']['type'], 'explore')


class TrackCharacterMappingTest(TestCase):
    """GET /api/academy/tracks returns characterSlug and characterName for each track."""

    def test_tracks_include_character_fields(self):
        char = _create_character(slug='byte', name='Byte')
        track = LearningTrack.objects.create(
            id='test-char-track',
            title='Byte Track',
            description='Test',
            icon='B',
            color='#000',
            order=1,
            character=char,
        )

        child = _create_child()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        resp = client.get('/api/academy/tracks')
        self.assertEqual(resp.status_code, 200)

        # Results may be paginated
        tracks = resp.data.get('results', resp.data) if isinstance(resp.data, dict) else resp.data

        # Find our test track in the response
        track_data = next((t for t in tracks if t['id'] == 'test-char-track'), None)
        self.assertIsNotNone(track_data)
        self.assertEqual(track_data['characterSlug'], 'byte')
        self.assertEqual(track_data['characterName'], 'Byte')

    def test_tracks_without_character_return_none(self):
        LearningTrack.objects.create(
            id='test-no-char-track',
            title='No Char Track',
            description='Test',
            icon='N',
            color='#111',
            order=99,
            character=None,
        )

        child = _create_child()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        resp = client.get('/api/academy/tracks')
        self.assertEqual(resp.status_code, 200)

        tracks = resp.data.get('results', resp.data) if isinstance(resp.data, dict) else resp.data

        track_data = next((t for t in tracks if t['id'] == 'test-no-char-track'), None)
        self.assertIsNotNone(track_data)
        self.assertIsNone(track_data['characterSlug'])
        self.assertIsNone(track_data['characterName'])
