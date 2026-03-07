from django.test import TestCase

from playground.validators import validate_code, validate_step_answer


class ValidateCodeTest(TestCase):
    """Unit test validate_code with various modes."""

    def test_contains_mode(self):
        self.assertTrue(validate_code('<h1>Hello</h1>', {'mode': 'contains', 'expected': '<h1>'}))
        self.assertFalse(validate_code('<p>Hello</p>', {'mode': 'contains', 'expected': '<h1>'}))

    def test_contains_case_insensitive(self):
        self.assertTrue(validate_code('<H1>Hello</H1>', {'mode': 'contains', 'expected': '<h1>'}))

    def test_contains_all_mode(self):
        self.assertTrue(validate_code('<h1>Hi</h1><p>Text</p>', {'mode': 'contains_all', 'expected': ['<h1>', '<p>']}))
        self.assertFalse(validate_code('<h1>Hi</h1>', {'mode': 'contains_all', 'expected': ['<h1>', '<p>']}))

    def test_equals_mode(self):
        self.assertTrue(validate_code('hello', {'mode': 'equals', 'expected': 'hello'}))
        self.assertTrue(validate_code('  hello  ', {'mode': 'equals', 'expected': 'hello'}))
        self.assertFalse(validate_code('world', {'mode': 'equals', 'expected': 'hello'}))

    def test_regex_mode(self):
        self.assertTrue(validate_code('<h1>anything</h1>', {'mode': 'regex', 'expected': r'<h1>.*</h1>'}))
        self.assertFalse(validate_code('<p>stuff</p>', {'mode': 'regex', 'expected': r'<h1>.*</h1>'}))

    def test_unknown_mode(self):
        self.assertFalse(validate_code('code', {'mode': 'unknown', 'expected': 'code'}))


class ValidateStepAnswerTest(TestCase):
    """Unit test validate_step_answer with edge cases."""

    def test_explanation_always_passes(self):
        result = validate_step_answer('explanation', {'text': 'Hello'}, {})
        self.assertTrue(result['passed'])

    def test_story_always_passes(self):
        result = validate_step_answer('story', {'dialogue': []}, {})
        self.assertTrue(result['passed'])

    def test_reflection_always_passes(self):
        result = validate_step_answer('reflection', {'question': 'Q', 'type': 'free_text'}, {'text': ''})
        self.assertTrue(result['passed'])

    def test_multiple_choice_correct(self):
        result = validate_step_answer('multiple_choice', {'correct_index': 2}, {'selected_index': 2})
        self.assertTrue(result['passed'])

    def test_multiple_choice_incorrect(self):
        result = validate_step_answer('multiple_choice', {'correct_index': 0}, {'selected_index': 1})
        self.assertFalse(result['passed'])

    def test_true_false_correct(self):
        result = validate_step_answer('true_false', {'correct_answer': True}, {'selected': True})
        self.assertTrue(result['passed'])

    def test_true_false_incorrect(self):
        result = validate_step_answer('true_false', {'correct_answer': True}, {'selected': False})
        self.assertFalse(result['passed'])

    def test_fill_in_case_insensitive(self):
        result = validate_step_answer('fill_in', {'answer': 'p', 'case_sensitive': False}, {'text': 'P'})
        self.assertTrue(result['passed'])

    def test_fill_in_case_sensitive(self):
        result = validate_step_answer('fill_in', {'answer': 'p', 'case_sensitive': True}, {'text': 'P'})
        self.assertFalse(result['passed'])

    def test_fill_in_with_whitespace(self):
        result = validate_step_answer('fill_in', {'answer': 'p', 'case_sensitive': False}, {'text': '  p  '})
        self.assertTrue(result['passed'])

    def test_drag_and_drop_correct(self):
        result = validate_step_answer('drag_and_drop', {'correct_order': [0, 1, 2]}, {'order': [0, 1, 2]})
        self.assertTrue(result['passed'])

    def test_drag_and_drop_incorrect(self):
        result = validate_step_answer('drag_and_drop', {'correct_order': [0, 1, 2]}, {'order': [2, 1, 0]})
        self.assertFalse(result['passed'])

    def test_code_editor_challenge(self):
        content = {'validation': {'mode': 'contains', 'expected': 'color'}}
        result = validate_step_answer('code_editor_challenge', content, {'code': 'h1 { color: red; }'})
        self.assertTrue(result['passed'])

    def test_debugging_step(self):
        content = {'validation': {'mode': 'contains', 'expected': '</h1>'}}
        result = validate_step_answer('debugging', content, {'code': '<h1>Hello</h1>'})
        self.assertTrue(result['passed'])

    def test_speech_bubble_fill(self):
        content = {'answer': 'color', 'case_sensitive': False}
        result = validate_step_answer('speech_bubble_fill', content, {'text': 'Color'})
        self.assertTrue(result['passed'])

    def test_empty_code_submission(self):
        content = {'validation': {'mode': 'contains', 'expected': '<h1>'}}
        result = validate_step_answer('guided_coding', content, {'code': ''})
        self.assertFalse(result['passed'])

    def test_feedback_messages(self):
        result = validate_step_answer('multiple_choice', {'correct_index': 0}, {'selected_index': 0})
        self.assertIn(result['feedback'], [
            "Great job! That's correct!", "Your code looks perfect!", "Well done, SHERO!",
            "Amazing work! You nailed it!", "Fantastic! Keep it up!", "You're a coding superstar!",
        ])
