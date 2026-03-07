import random
import re

POSITIVE_MESSAGES = [
    "Great job! That's correct!",
    "Your code looks perfect!",
    "Well done, SHERO!",
    "Amazing work! You nailed it!",
    "Fantastic! Keep it up!",
    "You're a coding superstar!",
]

NEGATIVE_MESSAGES = [
    "Not quite — try again!",
    "Check your code carefully.",
    "Almost there — look at the hint!",
    "So close! Give it another shot.",
    "Keep trying — you've got this!",
    "Not yet, but you're learning!",
]


def _pass_feedback():
    return {"passed": True, "feedback": random.choice(POSITIVE_MESSAGES)}


def _fail_feedback():
    return {"passed": False, "feedback": random.choice(NEGATIVE_MESSAGES)}


def validate_code(code, validation):
    mode = validation.get("mode", "")
    expected = validation.get("expected", "")

    if mode == "contains":
        return expected.lower() in code.lower()
    elif mode == "contains_all":
        return all(e.lower() in code.lower() for e in expected)
    elif mode == "equals":
        return code.strip() == expected.strip()
    elif mode == "regex":
        return bool(re.search(expected, code))
    return False


def validate_step_answer(step_type, content, answer):
    """
    Validates a child's answer against a step's expected result.

    Args:
        step_type: The step type string
        content: The step's content JSONField
        answer: The child's submitted answer (varies by type)

    Returns:
        {"passed": bool, "feedback": str}
    """
    if step_type in ('explanation', 'example', 'story'):
        return _pass_feedback()

    if step_type == 'reflection':
        return _pass_feedback()

    if step_type in ('multiple_choice', 'checkpoint'):
        selected = answer.get('selected_index')
        correct = content.get('correct_index')
        if selected == correct:
            return _pass_feedback()
        return _fail_feedback()

    if step_type == 'true_false':
        selected = answer.get('selected')
        correct = content.get('correct_answer')
        if selected == correct:
            return _pass_feedback()
        return _fail_feedback()

    if step_type in ('fill_in', 'speech_bubble_fill'):
        text = answer.get('text', '')
        expected_answer = content.get('answer', '')
        case_sensitive = content.get('case_sensitive', False)
        if case_sensitive:
            passed = text.strip() == expected_answer.strip()
        else:
            passed = text.strip().lower() == expected_answer.strip().lower()
        return _pass_feedback() if passed else _fail_feedback()

    if step_type in ('guided_coding', 'code_editor_challenge', 'debug_task',
                     'debugging', 'mini_challenge', 'mini_project', 'boss_battle_phase'):
        code = answer.get('code', '')
        validation = content.get('validation', {})
        if not validation:
            return _pass_feedback()
        passed = validate_code(code, validation)
        return _pass_feedback() if passed else _fail_feedback()

    if step_type in ('drag_and_drop', 'command_sequence'):
        order = answer.get('order', [])
        correct_order = content.get('correct_order', [])
        if order == correct_order:
            return _pass_feedback()
        return _fail_feedback()

    if step_type == 'matching':
        pairs = answer.get('pairs', [])
        expected_pairs = content.get('pairs', [])
        expected_set = {(i, i) for i in range(len(expected_pairs))}
        submitted_set = {(p[0], p[1]) for p in pairs} if pairs else set()
        if submitted_set == expected_set:
            return _pass_feedback()
        return _fail_feedback()

    return _fail_feedback()
