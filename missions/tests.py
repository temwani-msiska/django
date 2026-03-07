import uuid

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import ChildProfile, ParentUser
from characters.models import Character
from missions.models import Mission, MissionProgress, MissionStep, StepProgress


def _create_child():
    parent = ParentUser.objects.create_user(
        email=f'test-{uuid.uuid4().hex[:8]}@example.com',
        username=f'user-{uuid.uuid4().hex[:8]}',
        password='TestPass123!',
        name='Test Parent',
    )
    child = ChildProfile.objects.create(
        parent=parent, nickname=f'Kid-{uuid.uuid4().hex[:6]}',
        pin=make_password('1234'), avatar_character='byte',
    )
    return child


def _child_token(child):
    token = AccessToken.for_user(child.parent)
    token['child_id'] = str(child.id)
    return str(token)


def _create_mission_with_steps(num_steps=3):
    char, _ = Character.objects.get_or_create(
        slug='test-char', defaults={'name': 'TestChar', 'title': 'Test', 'order': 1}
    )
    mission = Mission.objects.create(
        id=f'test-mission-{uuid.uuid4().hex[:6]}', num=1,
        title='Test Mission', description='Test', long_description='Test',
        character=char, difficulty='Beginner', xp=100, coins=20,
        skills=['HTML'], starter_code='', language='html', is_active=True,
        estimated_minutes=10, mentor_tip='Tip', why_learn_this='Why',
    )
    steps = []
    for i in range(1, num_steps + 1):
        step = MissionStep.objects.create(
            mission=mission, num=i,
            step_type='multiple_choice', title=f'Step {i}',
            description=f'Step {i}', validation_type='', validation_value='',
            content={'question': 'Pick 0', 'options': ['A', 'B'], 'correct_index': 0},
        )
        steps.append(step)
    return mission, steps


class MissionStepSubmissionTest(TestCase):
    """Test mission step submission: start -> submit all -> mission completes with XP."""

    def test_full_mission_step_progression(self):
        child = _create_child()
        mission, steps = _create_mission_with_steps(3)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        # Start mission
        resp = client.post(f'/api/missions/{mission.id}/start')
        self.assertEqual(resp.status_code, 200)

        # Submit all steps
        for i in range(1, 4):
            resp = client.post(
                f'/api/missions/{mission.id}/steps/{i}/submit',
                {'answer': {'selected_index': 0}}, format='json',
            )
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(resp.data['passed'])

        # Last step should complete the mission
        self.assertTrue(resp.data['mission_completed'])

        # Verify XP awarded
        child.refresh_from_db()
        self.assertEqual(child.xp, 100)

        # Verify mission progress
        mp = MissionProgress.objects.get(child=child, mission=mission)
        self.assertEqual(mp.status, 'completed')
        self.assertEqual(mp.progress, 100)

    def test_incorrect_answer_does_not_advance(self):
        child = _create_child()
        mission, steps = _create_mission_with_steps(2)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        client.post(f'/api/missions/{mission.id}/start')

        resp = client.post(
            f'/api/missions/{mission.id}/steps/1/submit',
            {'answer': {'selected_index': 1}}, format='json',
        )
        self.assertFalse(resp.data['passed'])
        self.assertFalse(resp.data['mission_completed'])
