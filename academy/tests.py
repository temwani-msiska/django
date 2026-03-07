import uuid

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from academy.models import LearningTrack, Lesson, LessonProgress, LessonStep, LessonStepProgress
from accounts.models import ChildProfile, ParentUser


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


def _create_lesson_with_steps(num_steps=3):
    track = LearningTrack.objects.create(
        id=f'test-track-{uuid.uuid4().hex[:6]}', title='Test Track',
        description='Test', icon='T', color='#000', order=1,
    )
    lesson = Lesson.objects.create(
        id=f'test-lesson-{uuid.uuid4().hex[:6]}', track=track,
        title='Test Lesson', description='Test', duration='5 min', order=1,
    )
    steps = []
    for i in range(1, num_steps + 1):
        step = LessonStep.objects.create(
            lesson=lesson, number=i,
            step_type='multiple_choice', title=f'Step {i}',
            content={'question': 'Pick 0', 'options': ['A', 'B'], 'correct_index': 0},
            is_required=True,
        )
        steps.append(step)
    return lesson, steps


class LessonStepProgressionTest(TestCase):
    """Test lesson step progression: start -> submit all steps -> lesson complete."""

    def test_full_lesson_progression(self):
        child = _create_child()
        lesson, steps = _create_lesson_with_steps(3)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        # Start lesson
        resp = client.post(f'/api/academy/lessons/{lesson.id}/start')
        self.assertEqual(resp.status_code, 200)

        # Step 1 should be active
        progress = LessonStepProgress.objects.get(child=child, step=steps[0])
        self.assertEqual(progress.status, 'active')

        # Submit correct answer to step 1
        resp = client.post(
            f'/api/academy/lessons/{lesson.id}/steps/1/submit',
            {'answer': {'selected_index': 0}}, format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['passed'])
        self.assertTrue(resp.data['step_completed'])
        self.assertFalse(resp.data['lesson_completed'])

        # Step 2 should now be active
        progress2 = LessonStepProgress.objects.get(child=child, step=steps[1])
        self.assertEqual(progress2.status, 'active')

        # Submit step 2
        resp = client.post(
            f'/api/academy/lessons/{lesson.id}/steps/2/submit',
            {'answer': {'selected_index': 0}}, format='json',
        )
        self.assertTrue(resp.data['passed'])
        self.assertFalse(resp.data['lesson_completed'])

        # Submit step 3 -> lesson should complete
        resp = client.post(
            f'/api/academy/lessons/{lesson.id}/steps/3/submit',
            {'answer': {'selected_index': 0}}, format='json',
        )
        self.assertTrue(resp.data['passed'])
        self.assertTrue(resp.data['lesson_completed'])

        # Verify lesson progress
        lp = LessonProgress.objects.get(child=child, lesson=lesson)
        self.assertTrue(lp.completed)

        # Verify XP awarded
        child.refresh_from_db()
        self.assertEqual(child.xp, 50)


class StepValidationPerTypeTest(TestCase):
    """Test step validation for each step_type with correct and incorrect answers."""

    def setUp(self):
        self.child = _create_child()
        self.track = LearningTrack.objects.create(
            id='val-track', title='Val', description='', icon='V', color='#000', order=1,
        )
        self.lesson = Lesson.objects.create(
            id='val-lesson', track=self.track, title='Val Lesson',
            description='', duration='5 min', order=1,
        )
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(self.child)}')
        # Start lesson
        self.client.post(f'/api/academy/lessons/{self.lesson.id}/start')

    def _create_step(self, number, step_type, content):
        return LessonStep.objects.create(
            lesson=self.lesson, number=number, step_type=step_type,
            title=f'Test {step_type}', content=content,
        )

    def test_multiple_choice_correct(self):
        self._create_step(1, 'multiple_choice', {
            'question': 'Q?', 'options': ['A', 'B'], 'correct_index': 0,
        })
        resp = self.client.post(
            f'/api/academy/lessons/{self.lesson.id}/steps/1/submit',
            {'answer': {'selected_index': 0}}, format='json',
        )
        self.assertTrue(resp.data['passed'])

    def test_multiple_choice_incorrect(self):
        self._create_step(1, 'multiple_choice', {
            'question': 'Q?', 'options': ['A', 'B'], 'correct_index': 0,
        })
        resp = self.client.post(
            f'/api/academy/lessons/{self.lesson.id}/steps/1/submit',
            {'answer': {'selected_index': 1}}, format='json',
        )
        self.assertFalse(resp.data['passed'])

    def test_fill_in_case_insensitive(self):
        self._create_step(1, 'fill_in', {
            'template': 'The ___ tag', 'answer': 'p', 'case_sensitive': False,
        })
        resp = self.client.post(
            f'/api/academy/lessons/{self.lesson.id}/steps/1/submit',
            {'answer': {'text': 'P'}}, format='json',
        )
        self.assertTrue(resp.data['passed'])

    def test_guided_coding_contains(self):
        self._create_step(1, 'guided_coding', {
            'prompt': 'Write heading', 'starter_code': '', 'language': 'html',
            'validation': {'mode': 'contains', 'expected': '<h1>'},
        })
        resp = self.client.post(
            f'/api/academy/lessons/{self.lesson.id}/steps/1/submit',
            {'answer': {'code': '<h1>Hello</h1>'}}, format='json',
        )
        self.assertTrue(resp.data['passed'])

    def test_guided_coding_fail(self):
        self._create_step(1, 'guided_coding', {
            'prompt': 'Write heading', 'starter_code': '', 'language': 'html',
            'validation': {'mode': 'contains', 'expected': '<h1>'},
        })
        resp = self.client.post(
            f'/api/academy/lessons/{self.lesson.id}/steps/1/submit',
            {'answer': {'code': '<p>Hello</p>'}}, format='json',
        )
        self.assertFalse(resp.data['passed'])

    def test_reflection_always_passes(self):
        self._create_step(1, 'reflection', {
            'question': 'What did you learn?', 'type': 'free_text',
        })
        resp = self.client.post(
            f'/api/academy/lessons/{self.lesson.id}/steps/1/submit',
            {'answer': {'text': 'I learned a lot!'}}, format='json',
        )
        self.assertTrue(resp.data['passed'])


class LessonDetailEndpointTest(TestCase):
    """Test lesson detail endpoint returns steps with per-child status."""

    def test_lesson_detail_with_steps(self):
        child = _create_child()
        lesson, steps = _create_lesson_with_steps(3)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        resp = client.get(f'/api/academy/lessons/{lesson.id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['steps']), 3)
        self.assertEqual(resp.data['step_count'], 3)
        self.assertEqual(resp.data['completed_steps'], 0)

        # All steps should be locked initially
        for step_data in resp.data['steps']:
            self.assertEqual(step_data['status'], 'locked')


class DraftSaveLoadTest(TestCase):
    """Test draft save and load for lesson steps."""

    def test_save_and_load_draft(self):
        child = _create_child()
        lesson, steps = _create_lesson_with_steps(1)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(child)}')

        # Save draft
        resp = client.put(
            f'/api/academy/lessons/{lesson.id}/steps/1/draft',
            {'code': '<h1>My Draft</h1>'}, format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['saved'])

        # Load draft
        resp = client.get(f'/api/academy/lessons/{lesson.id}/steps/1/draft')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['draft']['draft_code'], '<h1>My Draft</h1>')
