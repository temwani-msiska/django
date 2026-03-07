import uuid

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import ChildProfile, ParentUser
from story.models import Scene, SceneProgress, StoryArc
from story.schemas import validate_scene_data


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


class SceneSchemaValidationTest(TestCase):
    """Test validate_scene_data catches valid and invalid scene JSON."""

    def _make_scene(self, **kwargs):
        arc = StoryArc.objects.create(
            id=f'test-arc-{uuid.uuid4().hex[:6]}', title='Test', arc_type='prologue', order=1,
        )
        defaults = {
            'arc': arc, 'order': 1, 'title': 'Test Scene',
            'background_key': 'shero_hq',
            'characters_on_screen': [{'character': 'byte', 'position': 'left'}],
            'bubbles': [{'character': 'byte', 'text': 'Hello'}],
            'motions': [],
            'next_action': 'next', 'action_payload': {},
        }
        defaults.update(kwargs)
        return Scene(**defaults)

    def test_valid_scene_passes(self):
        scene = self._make_scene()
        errors = validate_scene_data(scene)
        self.assertEqual(errors, [])

    def test_invalid_characters_on_screen_not_list(self):
        scene = self._make_scene(characters_on_screen="not a list")
        errors = validate_scene_data(scene)
        self.assertIn('characters_on_screen must be a list', errors)

    def test_missing_character_field(self):
        scene = self._make_scene(characters_on_screen=[{'position': 'left'}])
        errors = validate_scene_data(scene)
        self.assertTrue(any("missing required field 'character'" in e for e in errors))

    def test_missing_position_field(self):
        scene = self._make_scene(characters_on_screen=[{'character': 'byte'}])
        errors = validate_scene_data(scene)
        self.assertTrue(any("missing required field 'position'" in e for e in errors))

    def test_invalid_bubbles_not_list(self):
        scene = self._make_scene(bubbles="not a list")
        errors = validate_scene_data(scene)
        self.assertIn('bubbles must be a list', errors)

    def test_missing_bubble_text(self):
        scene = self._make_scene(bubbles=[{'character': 'byte'}])
        errors = validate_scene_data(scene)
        self.assertTrue(any("missing required field 'text'" in e for e in errors))

    def test_invalid_motions_not_list(self):
        scene = self._make_scene(motions="not a list")
        errors = validate_scene_data(scene)
        self.assertIn('motions must be a list', errors)

    def test_missing_motion_type(self):
        scene = self._make_scene(motions=[{'trigger': 'on_enter'}])
        errors = validate_scene_data(scene)
        self.assertTrue(any("missing required field 'type'" in e for e in errors))

    def test_choice_without_choices_payload(self):
        scene = self._make_scene(next_action='choice', action_payload={})
        errors = validate_scene_data(scene)
        self.assertTrue(any("'choices' list" in e for e in errors))

    def test_choice_with_valid_payload(self):
        scene = self._make_scene(
            next_action='choice',
            action_payload={'choices': [{'text': 'Go left', 'next_scene_order': 2}]},
        )
        errors = validate_scene_data(scene)
        self.assertEqual(errors, [])

    def test_challenge_without_step_type(self):
        scene = self._make_scene(next_action='challenge', action_payload={'content': {}})
        errors = validate_scene_data(scene)
        self.assertTrue(any("'step_type'" in e for e in errors))

    def test_challenge_without_content(self):
        scene = self._make_scene(next_action='challenge', action_payload={'step_type': 'multiple_choice'})
        errors = validate_scene_data(scene)
        self.assertTrue(any("'content'" in e for e in errors))


class SceneChoiceBranchingTest(TestCase):
    """Test scene choice branching endpoint."""

    def setUp(self):
        self.child = _create_child()
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {_child_token(self.child)}')

        self.arc = StoryArc.objects.create(
            id='choice-arc', title='Choice Arc', arc_type='prologue', order=1,
        )
        self.scene1 = Scene.objects.create(
            arc=self.arc, order=1, title='Fork in the Road',
            background_key='shero_hq',
            characters_on_screen=[{'character': 'byte', 'position': 'center'}],
            bubbles=[{'character': 'byte', 'text': 'Which way?'}],
            next_action='choice',
            action_payload={
                'choices': [
                    {'text': 'Go left', 'next_scene_order': 2},
                    {'text': 'Go right', 'next_scene_order': 3},
                ],
            },
        )
        self.scene2 = Scene.objects.create(
            arc=self.arc, order=2, title='Left Path',
            background_key='code_forest',
            characters_on_screen=[{'character': 'byte', 'position': 'left'}],
            bubbles=[{'character': 'byte', 'text': 'You went left!'}],
            next_action='next',
        )
        self.scene3 = Scene.objects.create(
            arc=self.arc, order=3, title='Right Path',
            background_key='data_river',
            characters_on_screen=[{'character': 'byte', 'position': 'right'}],
            bubbles=[{'character': 'byte', 'text': 'You went right!'}],
            next_action='end',
        )

    def test_choice_returns_correct_scene(self):
        resp = self.client.post(
            f'/api/story/scenes/{self.scene1.id}/choice',
            {'choice_index': 0}, format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['title'], 'Left Path')

    def test_choice_second_option(self):
        resp = self.client.post(
            f'/api/story/scenes/{self.scene1.id}/choice',
            {'choice_index': 1}, format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['title'], 'Right Path')

    def test_choice_marks_scene_viewed(self):
        self.client.post(
            f'/api/story/scenes/{self.scene1.id}/choice',
            {'choice_index': 0}, format='json',
        )
        self.assertTrue(
            SceneProgress.objects.filter(child=self.child, scene=self.scene1).exists()
        )

    def test_choice_on_non_choice_scene_fails(self):
        resp = self.client.post(
            f'/api/story/scenes/{self.scene2.id}/choice',
            {'choice_index': 0}, format='json',
        )
        self.assertEqual(resp.status_code, 400)

    def test_invalid_choice_index(self):
        resp = self.client.post(
            f'/api/story/scenes/{self.scene1.id}/choice',
            {'choice_index': 99}, format='json',
        )
        self.assertEqual(resp.status_code, 400)
