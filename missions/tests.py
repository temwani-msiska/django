import uuid

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import ChildProfile, ParentUser
from characters.models import Character
from missions.models import (
    BossBattle, BossBattlePhase, BossBattleProgress,
    Mission, MissionProgress, MissionStep, StepProgress,
)
from story.models import Scene, SceneProgress, StoryArc


def _create_child():
    parent = ParentUser.objects.create_user(
        email=f'test-{uuid.uuid4().hex[:8]}@example.com',
        username=f'user-{uuid.uuid4().hex[:8]}',
        password='TestPass123!',
        name='Test Parent',
    )
    return ChildProfile.objects.create(
        parent=parent, nickname=f'Kid-{uuid.uuid4().hex[:6]}',
        pin=make_password('1234'), avatar_character='byte',
    )


def _child_token(child):
    token = AccessToken.for_user(child.parent)
    token['child_id'] = str(child.id)
    return str(token)


def _create_char():
    char, _ = Character.objects.get_or_create(
        slug='test-char', defaults={'name': 'TestChar', 'title': 'Test', 'order': 1}
    )
    return char


def _create_mission(**kwargs):
    char = _create_char()
    defaults = {
        'id': f'test-mission-{uuid.uuid4().hex[:6]}', 'num': 1,
        'title': 'Test Mission', 'description': 'Test', 'long_description': 'Test',
        'character': char, 'difficulty': 'Beginner', 'xp': 100, 'coins': 20,
        'skills': ['HTML'], 'starter_code': '', 'language': 'html', 'is_active': True,
        'estimated_minutes': 10, 'mentor_tip': 'Tip', 'why_learn_this': 'Why',
    }
    defaults.update(kwargs)
    return Mission.objects.create(**defaults)


def _create_mission_with_steps(num_steps=3):
    mission = _create_mission()
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

        resp = client.post(f'/api/missions/{mission.id}/start')
        self.assertEqual(resp.status_code, 200)

        for i in range(1, 4):
            resp = client.post(
                f'/api/missions/{mission.id}/steps/{i}/submit',
                {'answer': {'selected_index': 0}}, format='json',
            )
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(resp.data['passed'])

        self.assertTrue(resp.data['mission_completed'])

        child.refresh_from_db()
        self.assertEqual(child.xp, 100)

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


class BossBattleFlowTest(TestCase):
    """Test boss battle: start -> submit phases -> verify completion."""

    def setUp(self):
        self.child = _create_child()
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(self.child)}')

        self.char = _create_char()
        self.mission = _create_mission(id='boss-test', num=99)
        self.boss = BossBattle.objects.create(
            mission=self.mission, title='Test Boss', total_phases=3, xp_bonus=200,
        )
        for phase_num in range(1, 4):
            BossBattlePhase.objects.create(
                boss_battle=self.boss, phase_number=phase_num,
                leader_character=self.char,
                title=f'Phase {phase_num}',
                challenge_type='multiple_choice',
                content={
                    'question': 'Pick 0', 'options': ['A', 'B'], 'correct_index': 0,
                },
                intro_dialogue=[{'character': 'byte', 'text': 'Go!'}],
                success_dialogue=[{'character': 'byte', 'text': 'Nice!'}],
            )

    def test_boss_battle_full_flow(self):
        # Start boss
        resp = self.client.post(f'/api/missions/{self.mission.id}/boss/start')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['title'], 'Test Boss')
        self.assertEqual(resp.data['progress']['status'], 'in_progress')

        # Phase 1 correct
        resp = self.client.post(
            f'/api/missions/{self.mission.id}/boss/phase/1/submit',
            {'answer': {'selected_index': 0}}, format='json',
        )
        self.assertTrue(resp.data['passed'])
        self.assertFalse(resp.data['boss_completed'])
        self.assertEqual(resp.data['next_phase'], 2)

        # Phase 2 correct
        resp = self.client.post(
            f'/api/missions/{self.mission.id}/boss/phase/2/submit',
            {'answer': {'selected_index': 0}}, format='json',
        )
        self.assertTrue(resp.data['passed'])
        self.assertEqual(resp.data['next_phase'], 3)

        # Phase 3 correct -> boss complete
        resp = self.client.post(
            f'/api/missions/{self.mission.id}/boss/phase/3/submit',
            {'answer': {'selected_index': 0}}, format='json',
        )
        self.assertTrue(resp.data['passed'])
        self.assertTrue(resp.data['boss_completed'])
        self.assertEqual(resp.data['xp_bonus'], 200)

        # Verify progress
        bp = BossBattleProgress.objects.get(child=self.child, boss_battle=self.boss)
        self.assertEqual(bp.status, 'completed')

        # Verify mission completed + XP
        self.child.refresh_from_db()
        # mission.xp (100) + boss xp_bonus (200) = 300
        self.assertEqual(self.child.xp, 300)

        mp = MissionProgress.objects.get(child=self.child, mission=self.mission)
        self.assertEqual(mp.status, 'completed')


class BossBattleFailureTest(TestCase):
    """Test boss battle failure: wrong answer -> no advancement, defeat dialogue."""

    def test_wrong_answer_returns_defeat_dialogue(self):
        child = _create_child()
        char = _create_char()
        mission = _create_mission(id='boss-fail', num=98)
        boss = BossBattle.objects.create(
            mission=mission, title='Fail Boss', total_phases=2, xp_bonus=100,
            defeat_dialogue=[{'character': 'dr_glitch', 'text': 'You failed!'}],
        )
        BossBattlePhase.objects.create(
            boss_battle=boss, phase_number=1, leader_character=char,
            title='Phase 1', challenge_type='multiple_choice',
            content={'question': 'Pick 0', 'options': ['A', 'B'], 'correct_index': 0},
        )

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        # Start boss
        client.post(f'/api/missions/{mission.id}/boss/start')

        # Submit wrong answer
        resp = client.post(
            f'/api/missions/{mission.id}/boss/phase/1/submit',
            {'answer': {'selected_index': 1}}, format='json',
        )
        self.assertFalse(resp.data['passed'])
        self.assertEqual(resp.data['defeat_dialogue'][0]['text'], 'You failed!')
        self.assertEqual(resp.data['current_phase'], 1)  # not advanced

        # Boss progress still in_progress at phase 1
        bp = BossBattleProgress.objects.get(child=child, boss_battle=boss)
        self.assertEqual(bp.current_phase, 1)
        self.assertEqual(bp.status, 'in_progress')


class ArcGatingTest(TestCase):
    """Test that missions requiring arc completion return 403 when arc is not complete."""

    def test_mission_blocked_by_incomplete_arc(self):
        child = _create_child()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        # Create arc with 2 scenes
        arc = StoryArc.objects.create(
            id='gating-arc', title='Gating Arc', arc_type='prologue', order=1,
        )
        scene1 = Scene.objects.create(
            arc=arc, order=1, title='Scene 1', background_key='shero_hq',
            characters_on_screen=[{'character': 'byte', 'position': 'center'}],
            bubbles=[{'character': 'byte', 'text': 'Hi'}], next_action='next',
        )
        scene2 = Scene.objects.create(
            arc=arc, order=2, title='Scene 2', background_key='shero_hq',
            characters_on_screen=[{'character': 'byte', 'position': 'center'}],
            bubbles=[{'character': 'byte', 'text': 'Bye'}], next_action='end',
        )

        # Create mission requiring this arc
        mission = _create_mission(id='gated-mission', num=50, requires_arc=arc)

        # Try to start mission -> 403
        resp = client.post(f'/api/missions/{mission.id}/start')
        self.assertEqual(resp.status_code, 403)

        # Complete both scenes
        SceneProgress.objects.create(child=child, scene=scene1)
        SceneProgress.objects.create(child=child, scene=scene2)

        # Now start mission -> 200
        resp = client.post(f'/api/missions/{mission.id}/start')
        self.assertEqual(resp.status_code, 200)
