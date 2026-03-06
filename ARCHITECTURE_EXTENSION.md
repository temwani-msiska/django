# Code SHEROs — Backend Architecture Extension Plan

## Status: Review Document
## Date: 2026-03-06

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current Architecture Assessment](#2-current-architecture-assessment)
3. [Model Extensions](#3-model-extensions)
4. [Serializer Plan](#4-serializer-plan)
5. [Endpoint Design](#5-endpoint-design)
6. [Permissions Rules](#6-permissions-rules)
7. [Example API Responses](#7-example-api-responses)
8. [Migration Strategy](#8-migration-strategy)
9. [Implementation Order](#9-implementation-order)
10. [Risks and Tradeoffs](#10-risks-and-tradeoffs)

---

## 1. Executive Summary

This document extends the existing Code SHEROs backend to support a **story-driven gamified coding platform** where Academy (structured learning) and Play (story-based missions) work together. The core principle: **extend, don't rebuild**.

### What stays unchanged
- `ParentUser`, `ChildProfile`, `ChildPreferences` — no changes
- `Character`, `CharacterAbility`, `CharacterStat` — no changes
- `Badge`, `EarnedBadge`, `ActivityLog` — no changes
- `StoryArc`, `Scene`, `SceneProgress` — no changes
- Auth flow (JWT with child_id) — no changes
- Core utilities (`xp_for_level`, `check_level_up`, `update_streak`, `get_rank`) — no changes
- `MissionReward` — no changes

### What gets extended
- `Mission` — add `world`, `lesson`, `lead_character`, `mission_type`, `map_order`, `unlock_rule_json`
- `MissionStep` — add `step_type`, JSON content fields, feedback messages
- `MissionProgress` — add `score` field
- Academy `Lesson` — add `xp_reward`

### What gets created
- `World` model (new, in `missions` app)
- `MissionAnswer` model (new, in `missions` app)
- `LessonStep` model (new, in `academy` app)
- `LessonQuizQuestion` model (new, in `academy` app)
- `TrackProgress` model (new, in `academy` app)
- New API endpoints for Play, Academy detail, and Progress summaries

---

## 2. Current Architecture Assessment

### Strengths
- **Clean separation of concerns**: Each app owns its domain (accounts, missions, story, academy, rewards, characters)
- **Slug-based primary keys** on content models (Mission, Lesson, LearningTrack, StoryArc, Badge, Character) — excellent for URLs and seeding
- **UUID primary keys** on user-generated/progress data — good for security
- **StoryArc system is flexible**: Already supports mission intro/outro/prerequisite arcs via FK on Mission
- **Unlock chain works**: `unlock_after` self-FK on Mission + arc prerequisites already handle linear progression
- **XP/level/streak/rank system is solid**: Simple, effective, production-proven

### Gaps to Address
1. **No World grouping** — missions are flat, no thematic container
2. **MissionStep is passive** — only has `validation_type`/`validation_value`, no interactive step types
3. **No answer tracking** — mission completion is binary (start → complete), no per-step answer history
4. **Academy is thin** — lessons have no content/steps/quizzes, just a title and completion flag
5. **No lesson-to-mission linking** — Academy and Play are completely isolated
6. **No per-child track progress** — only per-lesson completion exists
7. **No journey/progress summary endpoints** — parent dashboard has activity logs but no structured progress view

### Architecture Decisions

**Where do new models live?**

| Model | App | Rationale |
|-------|-----|-----------|
| `World` | `missions` | Worlds group missions; they're part of the Play domain |
| `MissionAnswer` | `missions` | Answers are mission-step submissions |
| `LessonStep` | `academy` | Lesson content belongs to the academy domain |
| `LessonQuizQuestion` | `academy` | Quiz content belongs to the academy domain |
| `TrackProgress` | `academy` | Track-level progress is academy domain |

This avoids creating a new app. Worlds are tightly coupled to missions, and lesson content is tightly coupled to academy.

---

## 3. Model Extensions

### 3.1 World (NEW — `missions/models.py`)

```python
class World(models.Model):
    id = models.SlugField(primary_key=True)            # e.g. "the-broken-internet"
    name = models.CharField(max_length=100)             # "The Broken Internet"
    description = models.TextField()
    primary_character = models.ForeignKey(
        'characters.Character', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='primary_worlds',
    )
    primary_color = models.CharField(max_length=7)      # hex
    secondary_color = models.CharField(max_length=7)    # hex
    skills = models.JSONField(default=list)             # ["html", "css", "javascript"]
    order = models.IntegerField(default=0)
    story_intro_arc = models.ForeignKey(
        'story.StoryArc', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='world_intros',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
```

**Design notes:**
- `primary_character` is thematic (for theming the world map), NOT a lock. All children play all worlds.
- `story_intro_arc` reuses the existing StoryArc system — no new story infrastructure needed.
- Slug PK keeps consistency with Mission, LearningTrack, etc.

### 3.2 Mission Extensions (MODIFY — `missions/models.py`)

Add these fields to the existing `Mission` model:

```python
# --- New fields on Mission ---
world = models.ForeignKey(
    'World', null=True, blank=True,
    on_delete=models.SET_NULL, related_name='missions',
)
lesson = models.ForeignKey(
    'academy.Lesson', null=True, blank=True,
    on_delete=models.SET_NULL, related_name='linked_missions',
    help_text='Completing this lesson unlocks this mission',
)
lead_character = models.ForeignKey(
    'characters.Character', null=True, blank=True,
    on_delete=models.SET_NULL, related_name='led_missions',
    help_text='SHERO who leads this mission (distinct from avatar character)',
)
mission_type = models.CharField(
    max_length=20, default='solo',
    choices=[
        ('solo', 'Solo'),
        ('team', 'Team'),
        ('boss_battle', 'Boss Battle'),
    ],
)
map_order = models.IntegerField(
    default=0,
    help_text='Display order on the world map',
)
unlock_rule_json = models.JSONField(
    null=True, blank=True,
    help_text='Advanced unlock rules: {"type": "lesson_complete", "lesson_id": "html-basics-1"}',
)
```

**Design notes:**
- `world` is nullable so existing 18 missions remain valid without migration data fixes.
- `lead_character` vs existing `character`: The existing `character` field ties missions to a character for filtering (`?character=byte`). `lead_character` represents who leads the *story* of that mission. They can differ — e.g., a World 1 mission might have `character=byte` (for the HTML skill domain) but `lead_character` could be any SHERO depending on the narrative. If the team decides these should merge, `lead_character` can replace `character` in a future cleanup.
- `lesson` FK creates the Academy → Play bridge. When a child completes a lesson, the system can unlock linked missions.
- `unlock_rule_json` allows flexible rules beyond simple `unlock_after` chains. Examples:

```json
{"type": "lesson_complete", "lesson_id": "html-basics-1"}
{"type": "missions_complete", "mission_ids": ["byte-1", "byte-2"]}
{"type": "xp_threshold", "xp": 500}
{"type": "all_of", "rules": [
    {"type": "lesson_complete", "lesson_id": "css-basics-1"},
    {"type": "mission_complete", "mission_id": "pixel-1"}
]}
```

The existing `unlock_after` self-FK stays for simple linear chains. `unlock_rule_json` handles complex rules. Evaluation logic goes in `core/utils.py`.

### 3.3 MissionStep Extensions (MODIFY — `missions/models.py`)

Add these fields to the existing `MissionStep` model:

```python
# --- New fields on MissionStep ---
STEP_TYPE_CHOICES = [
    ('story', 'Story'),
    ('multiple_choice', 'Multiple Choice'),
    ('drag_drop', 'Drag & Drop'),
    ('code_builder', 'Code Builder'),
    ('debug_task', 'Debug Task'),
    ('match_pairs', 'Match Pairs'),
    ('true_false', 'True / False'),
    ('mini_project', 'Mini Project'),
    ('boss_battle_phase', 'Boss Battle Phase'),
]

step_type = models.CharField(
    max_length=30, default='story',
    choices=STEP_TYPE_CHOICES,
)
content_json = models.JSONField(
    null=True, blank=True,
    help_text='Step content payload — structure depends on step_type',
)
ui_config_json = models.JSONField(
    null=True, blank=True,
    help_text='UI rendering hints: layout, theme, animations',
)
correct_answer_json = models.JSONField(
    null=True, blank=True,
    help_text='Expected answer for validation',
)
starter_state_json = models.JSONField(
    null=True, blank=True,
    help_text='Initial state for interactive steps (code, drag items, etc.)',
)
success_message = models.CharField(max_length=200, blank=True)
failure_message = models.CharField(max_length=200, blank=True)
xp_reward = models.IntegerField(default=0, help_text='XP awarded for completing this step')
```

**Design notes:**
- Existing `validation_type` and `validation_value` remain for backward compatibility with the 18 seeded missions.
- `step_type` defaults to `'story'` — existing steps without a type will render as story steps.
- JSON fields are nullable so existing data stays valid.
- `content_json` structure varies by `step_type`. Examples:

```json
// step_type: "multiple_choice"
{
    "question": "What HTML tag creates a paragraph?",
    "options": ["<p>", "<h1>", "<div>", "<span>"],
    "image_key": null
}

// step_type: "drag_drop"
{
    "instruction": "Arrange these tags in the correct order",
    "items": ["<html>", "<head>", "<body>", "</html>"],
    "drop_zones": ["first", "second", "third", "fourth"]
}

// step_type: "code_builder"
{
    "instruction": "Fix the broken HTML",
    "language": "html",
    "starter_code": "<h1>Hello</h2>",
    "test_cases": [{"input": null, "expected_output": "<h1>Hello</h1>"}]
}

// step_type: "boss_battle_phase"
{
    "phase_number": 1,
    "lead_shero": "byte",
    "challenge_type": "code_builder",
    "narrative": "Byte steps forward to repair the HTML!",
    "time_limit_seconds": 120
}
```

### 3.4 MissionAnswer (NEW — `missions/models.py`)

```python
class MissionAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mission_progress = models.ForeignKey(
        MissionProgress, on_delete=models.CASCADE, related_name='answers',
    )
    step = models.ForeignKey(MissionStep, on_delete=models.CASCADE, related_name='answers')
    answer_json = models.JSONField()
    is_correct = models.BooleanField()
    score = models.IntegerField(default=0, help_text='Points earned for this answer')
    attempt_number = models.IntegerField(default=1)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['submitted_at']
```

**Design notes:**
- `attempt_number` allows retry tracking. The frontend can show "Try again!" without losing history.
- `score` is per-answer (partial credit for boss battles, etc.).
- No unique constraint on (mission_progress, step) — children can retry steps.

### 3.5 MissionProgress Extension (MODIFY — `missions/models.py`)

Add one field:

```python
score = models.IntegerField(default=0, help_text='Accumulated score across all steps')
```

### 3.6 LessonStep (NEW — `academy/models.py`)

```python
class LessonStep(models.Model):
    STEP_TYPE_CHOICES = [
        ('text', 'Text'),
        ('code_example', 'Code Example'),
        ('interactive', 'Interactive'),
        ('video', 'Video'),
        ('quiz', 'Quiz'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='steps')
    order = models.IntegerField()
    step_type = models.CharField(max_length=20, choices=STEP_TYPE_CHOICES)
    content = models.TextField(blank=True, help_text='Markdown or plain text content')
    content_json = models.JSONField(
        null=True, blank=True,
        help_text='Structured content for interactive/code steps',
    )
    hint = models.TextField(blank=True)
    xp_reward = models.IntegerField(default=0)

    class Meta:
        ordering = ['lesson', 'order']
        unique_together = ('lesson', 'order')
```

### 3.7 LessonQuizQuestion (NEW — `academy/models.py`)

```python
class LessonQuizQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True / False'),
        ('fill_blank', 'Fill in the Blank'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quiz_questions')
    order = models.IntegerField(default=0)
    question = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    choices_json = models.JSONField(
        null=True, blank=True,
        help_text='["Option A", "Option B", "Option C", "Option D"]',
    )
    correct_answer_json = models.JSONField(
        help_text='{"answer": "Option A"} or {"answer": true}',
    )
    explanation = models.TextField(blank=True)

    class Meta:
        ordering = ['lesson', 'order']
```

### 3.8 Lesson Extension (MODIFY — `academy/models.py`)

Add one field:

```python
xp_reward = models.IntegerField(default=0, help_text='XP awarded on lesson completion')
```

### 3.9 TrackProgress (NEW — `academy/models.py`)

```python
class TrackProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(
        'accounts.ChildProfile', on_delete=models.CASCADE, related_name='track_progress',
    )
    track = models.ForeignKey(LearningTrack, on_delete=models.CASCADE, related_name='child_progress')
    lessons_completed = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('child', 'track')
```

**Design notes:**
- `TrackProgress` is a **denormalized summary** — `lessons_completed` is updated when a lesson is marked complete, rather than counting `LessonProgress` rows every request.
- Could be computed on-the-fly instead. Denormalized version is faster for dashboards.

### 3.10 StoryArc Extension (MODIFY — `story/models.py`)

Add `'world_intro'` and `'boss_battle'` to `arc_type` choices:

```python
arc_type = models.CharField(
    max_length=20,
    choices=[
        ('prologue', 'Prologue'),
        ('world_intro', 'World Intro'),
        ('mission_intro', 'Mission Intro'),
        ('mission_outro', 'Mission Outro'),
        ('interlude', 'Interlude'),
        ('boss_battle', 'Boss Battle'),
    ],
)
```

This is a choices-only change — no schema migration needed, just a data migration to update the choices constraint.

---

## 4. Serializer Plan

### 4.1 Missions App — New/Modified Serializers

```
WorldListSerializer
    fields: id, name, description, primary_character (slug), primary_color,
            secondary_color, skills, order, mission_count, completed_count,
            is_unlocked, story_intro_arc (StoryArcRefSerializer)

WorldDetailSerializer(WorldListSerializer)
    fields: + missions (MissionSummarySerializer, many=True)

MissionSummarySerializer
    fields: id, num, title, difficulty, xp, lead_character (slug),
            mission_type, map_order, status, progress
    (Lightweight — used inside WorldDetailSerializer)

MissionSerializer (EXTEND existing)
    fields: + world, lead_character_slug, mission_type, map_order
    (Keep all existing fields)

MissionStepSerializer (EXTEND existing)
    fields: + step_type, content_json, ui_config_json, starter_state_json,
              success_message, failure_message, xp_reward
    (correct_answer_json is EXCLUDED from read serializers — server-side only)

MissionAnswerSerializer (NEW)
    fields: step, answer_json
    (Write-only — used for POST /play/missions/<id>/submit-step)

MissionAnswerResultSerializer (NEW)
    fields: is_correct, score, success_message, failure_message,
            correct_answer (only revealed after max attempts or on success)
```

### 4.2 Academy App — New/Modified Serializers

```
LearningTrackSerializer (EXTEND existing)
    fields: + total_lessons, completed_lessons, progress_percent

LearningTrackDetailSerializer (NEW)
    fields: all track fields + lessons (LessonDetailSerializer, many=True)

LessonDetailSerializer (NEW)
    fields: all lesson fields + steps (LessonStepSerializer, many=True)
            + quiz_questions (LessonQuizQuestionSerializer, many=True)
            + completed, xp_reward

LessonStepSerializer (NEW)
    fields: id, order, step_type, content, content_json, hint, xp_reward

LessonQuizQuestionSerializer (NEW)
    fields: id, order, question, question_type, choices_json, explanation
    (correct_answer_json excluded from read)

LessonStepSubmitSerializer (NEW)
    fields: step_id, answer_json
    (Write-only — for POST /academy/lessons/<id>/submit-step)

TrackProgressSerializer (NEW)
    fields: track_id, lessons_completed, total_lessons, progress_percent,
            started_at, completed_at
```

### 4.3 Progress/Journey Serializers (in `accounts` or `core`)

```
ChildJourneySerializer (NEW)
    fields:
        profile: {nickname, avatar_character, xp, level, streak, rank}
        academy: {
            tracks_started, tracks_completed, lessons_completed,
            total_lessons, overall_percent
        }
        play: {
            worlds_unlocked, worlds_completed, missions_completed,
            total_missions, current_world
        }
        recent_activity: [ActivityLogSerializer, last 10]
        badges_earned: count
        next_mission: {id, title, world} or null
        next_lesson: {id, title, track} or null
```

---

## 5. Endpoint Design

### 5.1 Play Endpoints (prefix: `/api/play/`)

| Method | Path | View | Description |
|--------|------|------|-------------|
| GET | `/play/worlds` | `WorldListView` | List active worlds with child progress |
| GET | `/play/worlds/<slug>` | `WorldDetailView` | World detail with mission map |
| GET | `/play/missions/<id>` | `MissionDetailView` | Full mission with steps (reuse existing, extend) |
| POST | `/play/missions/<id>/start` | `MissionStartView` | Start mission (reuse existing, extend) |
| POST | `/play/missions/<id>/submit-step` | `MissionSubmitStepView` | Submit answer for a step |
| POST | `/play/missions/<id>/complete` | `MissionCompleteView` | Complete mission (reuse existing, extend) |

**Note:** The existing `/api/missions/` endpoints continue to work. The new `/api/play/` endpoints are **aliases** backed by the same (extended) views. This avoids breaking any existing frontend code. Over time, the frontend migrates to `/api/play/` and the old routes can be deprecated.

### 5.2 Academy Endpoints (prefix: `/api/academy/`)

| Method | Path | View | Description |
|--------|------|------|-------------|
| GET | `/academy/tracks` | `LearningTrackListView` | List tracks with progress (existing, extend serializer) |
| GET | `/academy/tracks/<id>` | `LearningTrackDetailView` | Track detail with lessons, steps, quizzes |
| GET | `/academy/lessons/<id>` | `LessonDetailView` | Lesson detail with steps and quiz |
| POST | `/academy/lessons/<id>/submit-step` | `LessonSubmitStepView` | Submit a lesson step or quiz answer |
| POST | `/academy/lessons/<id>/complete` | `CompleteLessonView` | Complete lesson (existing, extend with XP) |

### 5.3 Progress Endpoints (prefix: `/api/`)

| Method | Path | View | Description |
|--------|------|------|-------------|
| GET | `/user/journey` | `ChildJourneyView` | Child's full journey summary |
| GET | `/parent/children/<id>/journey` | `ParentChildJourneyView` | Parent views child's journey |

### 5.4 Submit-Step Flow (Play)

```
POST /api/play/missions/<mission_id>/submit-step

Request:
{
    "stepId": "<uuid>",
    "answerJson": { ... }      // structure depends on step_type
}

Server-side logic:
1. Get child from JWT
2. Get MissionProgress (must be 'in_progress')
3. Get MissionStep by stepId
4. Validate answer against correct_answer_json
5. Create MissionAnswer record
6. Update StepProgress status
7. Award step XP if correct
8. Update MissionProgress.progress percentage
9. Return result

Response (200):
{
    "isCorrect": true,
    "score": 10,
    "xpEarned": 5,
    "successMessage": "Great job! You fixed the HTML!",
    "progress": 60,
    "nextStepId": "<uuid>" | null
}

Response (200, incorrect):
{
    "isCorrect": false,
    "score": 0,
    "xpEarned": 0,
    "failureMessage": "Not quite — check the closing tag!",
    "attemptsUsed": 2,
    "maxAttempts": 3,
    "progress": 40,
    "hint": "Look at line 3..."
}
```

### 5.5 Submit-Step Flow (Academy)

```
POST /api/academy/lessons/<lesson_id>/submit-step

Request:
{
    "stepId": "<uuid>",
    "answerJson": { ... }
}

Response (200):
{
    "isCorrect": true,
    "xpEarned": 5,
    "explanation": "Correct! The <p> tag creates a paragraph.",
    "nextStepId": "<uuid>" | null
}
```

---

## 6. Permissions Rules

### Existing Permissions (no changes)

| Class | Logic |
|-------|-------|
| `IsParent` | `request.user.is_authenticated` |
| `IsChild` | `hasattr(request, 'child_profile')` |
| `IsParentOfChild` | Parent owns the child via FK |

### Endpoint Permissions

| Endpoint | Permission | Notes |
|----------|-----------|-------|
| `GET /play/worlds` | `IsAuthenticated` | Child context resolved from JWT |
| `GET /play/worlds/<slug>` | `IsAuthenticated` | Child context from JWT |
| `GET /play/missions/<id>` | `IsAuthenticated` | Existing behavior |
| `POST /play/missions/<id>/start` | `IsAuthenticated` | Existing behavior |
| `POST /play/missions/<id>/submit-step` | `IsAuthenticated` | Must have active MissionProgress |
| `POST /play/missions/<id>/complete` | `IsAuthenticated` | Existing behavior |
| `GET /academy/tracks` | `IsAuthenticated` | Existing behavior |
| `GET /academy/tracks/<id>` | `IsAuthenticated` | Child context from JWT |
| `GET /academy/lessons/<id>` | `IsAuthenticated` | Child context from JWT |
| `POST /academy/lessons/<id>/submit-step` | `IsAuthenticated` | Child must be authenticated |
| `POST /academy/lessons/<id>/complete` | `IsAuthenticated` | Existing behavior |
| `GET /user/journey` | `IsAuthenticated` | Child JWT required |
| `GET /parent/children/<id>/journey` | `IsParentOfChild` | Parent must own child |

### Validation Rules (enforced in views, not permissions)

- **Mission start**: Check `unlock_after`, `requires_arc`, and `unlock_rule_json`
- **Step submit**: `MissionProgress.status` must be `'in_progress'`
- **Mission complete**: All required steps must be completed (or enforce minimum score)
- **Lesson complete**: Award XP, update `TrackProgress`, check if linked missions should unlock

---

## 7. Example API Responses

### GET /api/play/worlds

```json
[
    {
        "id": "the-broken-internet",
        "name": "The Broken Internet",
        "description": "Dr. Glitch has broken the internet! The SHEROs must fix it.",
        "primaryCharacter": "byte",
        "primaryColor": "#4A90D9",
        "secondaryColor": "#2C5F8A",
        "skills": ["html", "css", "javascript"],
        "order": 1,
        "missionCount": 10,
        "completedCount": 3,
        "isUnlocked": true,
        "storyIntroArc": {
            "id": "world-1-intro",
            "title": "The Day the Internet Broke",
            "completed": true
        }
    },
    {
        "id": "the-data-dungeon",
        "name": "The Data Dungeon",
        "description": "Data is trapped in the dungeon. Free it with code!",
        "primaryCharacter": "nova",
        "primaryColor": "#9B59B6",
        "secondaryColor": "#6C3483",
        "skills": ["variables", "loops", "logic"],
        "order": 2,
        "missionCount": 10,
        "completedCount": 0,
        "isUnlocked": false,
        "storyIntroArc": null
    }
]
```

### GET /api/play/worlds/the-broken-internet

```json
{
    "id": "the-broken-internet",
    "name": "The Broken Internet",
    "description": "Dr. Glitch has broken the internet! The SHEROs must fix it.",
    "primaryCharacter": "byte",
    "primaryColor": "#4A90D9",
    "secondaryColor": "#2C5F8A",
    "skills": ["html", "css", "javascript"],
    "order": 1,
    "storyIntroArc": {
        "id": "world-1-intro",
        "title": "The Day the Internet Broke",
        "completed": true
    },
    "missions": [
        {
            "id": "w1-mission-1",
            "num": 1,
            "title": "Meet the SHEROs",
            "difficulty": "beginner",
            "xp": 50,
            "leadCharacter": null,
            "missionType": "team",
            "mapOrder": 1,
            "status": "completed",
            "progress": 100
        },
        {
            "id": "w1-mission-2",
            "num": 2,
            "title": "Byte's First Fix",
            "difficulty": "beginner",
            "xp": 75,
            "leadCharacter": "byte",
            "missionType": "solo",
            "mapOrder": 2,
            "status": "in_progress",
            "progress": 40
        },
        {
            "id": "w1-mission-10",
            "num": 10,
            "title": "Boss Battle: Dr. Glitch",
            "difficulty": "hard",
            "xp": 200,
            "leadCharacter": null,
            "missionType": "boss_battle",
            "mapOrder": 10,
            "status": "locked",
            "progress": 0
        }
    ]
}
```

### POST /api/play/missions/w1-mission-2/submit-step

```json
// Request
{
    "stepId": "a1b2c3d4-...",
    "answerJson": {
        "selected": "<p>"
    }
}

// Response (correct)
{
    "isCorrect": true,
    "score": 10,
    "xpEarned": 5,
    "successMessage": "You got it! The <p> tag creates paragraphs!",
    "progress": 60,
    "nextStepId": "e5f6g7h8-..."
}
```

### GET /api/academy/tracks/html-basics

```json
{
    "id": "html-basics",
    "title": "HTML Basics",
    "description": "Learn the building blocks of the web",
    "icon": "🌐",
    "color": "#E74C3C",
    "order": 1,
    "totalLessons": 6,
    "completedLessons": 2,
    "progressPercent": 33,
    "lessons": [
        {
            "id": "html-intro",
            "title": "What is HTML?",
            "description": "Discover the language of the web",
            "duration": "5 min",
            "order": 1,
            "completed": true,
            "xpReward": 20,
            "steps": [
                {
                    "id": "...",
                    "order": 1,
                    "stepType": "text",
                    "content": "HTML stands for HyperText Markup Language...",
                    "contentJson": null,
                    "hint": "",
                    "xpReward": 0
                },
                {
                    "id": "...",
                    "order": 2,
                    "stepType": "interactive",
                    "content": "",
                    "contentJson": {
                        "type": "drag_tags",
                        "instruction": "Drag the tags to build a webpage",
                        "items": ["<html>", "<head>", "<body>"]
                    },
                    "hint": "Start with the outermost tag",
                    "xpReward": 5
                }
            ],
            "quizQuestions": [
                {
                    "id": "...",
                    "order": 1,
                    "question": "What does HTML stand for?",
                    "questionType": "multiple_choice",
                    "choicesJson": [
                        "HyperText Markup Language",
                        "High Tech Modern Language",
                        "Home Tool Markup Language"
                    ],
                    "explanation": "HTML = HyperText Markup Language"
                }
            ]
        }
    ]
}
```

### GET /api/user/journey

```json
{
    "profile": {
        "nickname": "Chanda",
        "avatarCharacter": "byte",
        "xp": 450,
        "level": 3,
        "streak": 5,
        "rank": "Code Explorer"
    },
    "academy": {
        "tracksStarted": 3,
        "tracksCompleted": 1,
        "lessonsCompleted": 12,
        "totalLessons": 44,
        "overallPercent": 27
    },
    "play": {
        "worldsUnlocked": 2,
        "worldsCompleted": 0,
        "missionsCompleted": 7,
        "totalMissions": 20,
        "currentWorld": {
            "id": "the-broken-internet",
            "name": "The Broken Internet",
            "progress": 70
        }
    },
    "recentActivity": [
        {
            "type": "mission_completed",
            "title": "Completed \"Byte's First Fix\"",
            "xpEarned": 75,
            "createdAt": "2026-03-05T14:30:00Z"
        },
        {
            "type": "streak",
            "title": "5-Day Streak!",
            "xpEarned": 0,
            "createdAt": "2026-03-05T14:30:00Z"
        }
    ],
    "badgesEarned": 4,
    "nextMission": {
        "id": "w1-mission-8",
        "title": "Nova's Robot Logic",
        "world": "the-broken-internet"
    },
    "nextLesson": {
        "id": "css-selectors",
        "title": "CSS Selectors",
        "track": "css-basics"
    }
}
```

---

## 8. Migration Strategy

### Phase 1: Schema Migrations (non-breaking)

All new fields on existing models are **nullable** or have **defaults**. This means:

1. `Mission.world` — `null=True` → existing missions get `world=NULL`
2. `Mission.lesson` — `null=True` → existing missions get `lesson=NULL`
3. `Mission.lead_character` — `null=True` → existing missions get `lead_character=NULL`
4. `Mission.mission_type` — `default='solo'` → existing missions become solo
5. `Mission.map_order` — `default=0` → existing missions get `map_order=0`
6. `Mission.unlock_rule_json` — `null=True` → existing missions get `NULL`
7. `MissionStep.step_type` — `default='story'` → existing steps become story type
8. All JSON fields on MissionStep — `null=True` → existing steps get `NULL`
9. `MissionStep.success_message`/`failure_message` — `blank=True` → empty string
10. `MissionProgress.score` — `default=0` → existing progress gets `score=0`
11. `Lesson.xp_reward` — `default=0` → existing lessons get `xp_reward=0`

**Zero data loss. Zero downtime. All existing API responses remain identical.**

### Phase 2: New Models

Create tables for:
- `World`
- `MissionAnswer`
- `LessonStep`
- `LessonQuizQuestion`
- `TrackProgress`

These are additive — no effect on existing data.

### Phase 3: Data Seeding

Create a management command `seed_worlds.py` that:
1. Creates World 1 ("The Broken Internet")
2. Assigns existing missions to World 1 (update `world` FK)
3. Sets `map_order` on existing missions
4. Sets `lead_character` based on existing `character` FK
5. Creates story intro arc for World 1

### Phase 4: New Endpoints

Register new URL patterns. Existing endpoints unchanged.

### Migration Commands

```bash
python manage.py makemigrations missions academy story
python manage.py migrate
python manage.py seed_worlds  # new seeder
```

---

## 9. Implementation Order

### Sprint 1: Foundation (World + Mission Extensions)

1. **Add World model** to `missions/models.py`
2. **Add new fields** to `Mission` model
3. **Add new fields** to `MissionStep` model
4. **Add MissionAnswer** model
5. **Add score field** to `MissionProgress`
6. **Run migrations**
7. **Create `WorldListSerializer` and `WorldDetailSerializer`**
8. **Create `WorldListView` and `WorldDetailView`**
9. **Extend `MissionSerializer`** with new fields
10. **Add `MissionSubmitStepView`** with answer validation
11. **Register `/api/play/` URL patterns**
12. **Create `seed_worlds` management command**
13. **Add `world_intro` and `boss_battle` to StoryArc `arc_type` choices**

### Sprint 2: Academy Extensions

14. **Add `LessonStep` model**
15. **Add `LessonQuizQuestion` model**
16. **Add `TrackProgress` model**
17. **Add `xp_reward` to `Lesson`**
18. **Run migrations**
19. **Create `LessonDetailSerializer`, `LessonStepSerializer`, `LessonQuizQuestionSerializer`**
20. **Create `LearningTrackDetailView` and `LessonDetailView`**
21. **Create `LessonSubmitStepView`**
22. **Extend `CompleteLessonView`** to award XP, update `TrackProgress`, unlock linked missions

### Sprint 3: Progress + Academy-Play Bridge

23. **Add unlock_rule evaluation logic** to `core/utils.py`
24. **Create `ChildJourneySerializer`**
25. **Create `ChildJourneyView` and `ParentChildJourneyView`**
26. **Extend `complete_mission`** in `core/utils.py` to handle `unlock_rule_json`
27. **Extend `CompleteLessonView`** to trigger mission unlocks via `Mission.lesson` FK
28. **Seed lesson steps and quiz questions** for existing 44 lessons

### Sprint 4: Boss Battles + Polish

29. **Add boss battle step logic** (multi-phase validation)
30. **Add boss battle story arcs** (intro/phase transitions/outro)
31. **Seed World 1 missions** with full step content
32. **End-to-end testing** of Academy → Play flow
33. **Performance optimization** (select_related, prefetch_related on new queries)

---

## 10. Risks and Tradeoffs

### Risk 1: JSON Field Flexibility vs. Validation

**Issue:** `content_json`, `correct_answer_json`, etc. are schemaless JSON. Typos in seed data or admin input won't be caught at the database level.

**Mitigation:**
- Add a `clean()` method on `MissionStep` that validates `content_json` structure based on `step_type`
- Create JSON schema definitions per step type in `core/schemas.py` (optional, can use `jsonschema` library)
- Validate in serializers before saving

**Tradeoff accepted:** JSON flexibility is worth it for a content-driven platform. Strict relational modeling of every step type would require 9+ tables and constant migrations for new step types.

### Risk 2: Two Character FKs on Mission

**Issue:** `Mission.character` (existing) and `Mission.lead_character` (new) could cause confusion.

**Mitigation:**
- Document clearly: `character` = skill domain/filtering, `lead_character` = narrative spotlight
- In Sprint 4, evaluate whether `character` can be deprecated in favor of `lead_character` + `world.primary_character`
- If merged, run a data migration to copy `character` → `lead_character` and update serializers

**Tradeoff accepted:** Adding `lead_character` alongside `character` is safer than modifying `character`'s semantics during an active production deployment.

### Risk 3: Denormalized TrackProgress

**Issue:** `TrackProgress.lessons_completed` could drift from actual `LessonProgress` count.

**Mitigation:**
- Always update `TrackProgress` inside the same transaction as `LessonProgress` creation
- Add a `recalculate_track_progress` utility for data repair
- Consider replacing with a computed property if performance is acceptable (for <50 lessons per track, it will be)

**Tradeoff accepted:** Denormalization is premature at this scale. **Recommendation: Start with computed progress (count query) and add `TrackProgress` only if dashboards become slow.** This simplifies the implementation.

### Risk 4: unlock_rule_json Complexity

**Issue:** Complex JSON rule evaluation could have bugs, and rules are hard to debug.

**Mitigation:**
- Start with only 2-3 rule types: `lesson_complete`, `mission_complete`, `xp_threshold`
- Add `all_of`/`any_of` combinators only when needed
- Keep the existing `unlock_after` FK as the primary unlock mechanism
- `unlock_rule_json` is a supplement, not a replacement

### Risk 5: Backward Compatibility of /api/missions/ Endpoints

**Issue:** Extending `MissionSerializer` with new fields could surprise existing frontend clients.

**Mitigation:**
- All new fields are **additive** (new keys in JSON response)
- No existing fields are removed or renamed
- Frontend ignores unknown keys by default (standard JSON practice)
- New fields have sensible defaults (`missionType: "solo"`, `mapOrder: 0`, `world: null`)

### Risk 6: Answer Validation on Server

**Issue:** Validating answers server-side for 9 different step types is non-trivial.

**Mitigation:**
- Create a `validate_answer(step, answer_json)` dispatcher in `core/utils.py`
- Start with exact-match validation for `multiple_choice`, `true_false`, `match_pairs`
- `code_builder` and `debug_task` delegate to the playground execution engine
- `story` steps auto-pass (no wrong answer)
- `drag_drop` uses ordered-list comparison
- `boss_battle_phase` delegates to the sub-challenge type

```python
# core/utils.py
def validate_step_answer(step, answer_json):
    validators = {
        'story': lambda s, a: True,
        'multiple_choice': validate_multiple_choice,
        'true_false': validate_true_false,
        'drag_drop': validate_drag_drop,
        'code_builder': validate_code_builder,
        'debug_task': validate_code_builder,
        'match_pairs': validate_match_pairs,
        'mini_project': validate_code_builder,
        'boss_battle_phase': validate_boss_phase,
    }
    validator = validators.get(step.step_type, lambda s, a: False)
    return validator(step, answer_json)
```

---

## Appendix A: Complete Model Diagram

```
                    ┌──────────────┐
                    │  ParentUser  │
                    └──────┬───────┘
                           │ 1:N
                    ┌──────▼───────┐
                    │ ChildProfile │
                    └──────┬───────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼───────┐
    │MissionProg. │ │LessonProg.  │ │ TrackProg.   │
    └──────┬──────┘ └─────────────┘ └──────────────┘
           │
    ┌──────▼──────┐
    │MissionAnswer│
    └─────────────┘

    ┌─────────┐  1:N  ┌─────────┐  1:N  ┌────────────┐
    │  World  │───────│ Mission │───────│ MissionStep│
    └─────────┘       └────┬────┘       └────────────┘
                           │
                    ┌──────▼──────┐
                    │ MissionRew. │
                    └─────────────┘

    ┌──────────────┐ 1:N ┌────────┐ 1:N ┌────────────┐
    │LearningTrack │────│ Lesson │────│ LessonStep │
    └──────────────┘    └────┬───┘    └────────────┘
                             │ 1:N
                      ┌──────▼────────┐
                      │LessonQuizQ.   │
                      └───────────────┘

    ┌──────────┐ 1:N ┌───────┐
    │ StoryArc │────│ Scene │
    └──────────┘    └───────┘

    Mission ──FK──▶ World
    Mission ──FK──▶ Lesson (academy bridge)
    Mission ──FK──▶ Character (lead_character)
    Mission ──FK──▶ StoryArc (intro/outro/requires)
    World   ──FK──▶ StoryArc (story_intro_arc)
    World   ──FK──▶ Character (primary_character)
```

---

## Appendix B: URL Configuration

```python
# missions/urls.py (extend)
urlpatterns += [
    path('play/worlds', WorldListView.as_view()),
    path('play/worlds/<slug:slug>', WorldDetailView.as_view()),
    path('play/missions/<slug:id>', MissionDetailView.as_view()),
    path('play/missions/<slug:id>/start', MissionStartView.as_view()),
    path('play/missions/<slug:id>/submit-step', MissionSubmitStepView.as_view()),
    path('play/missions/<slug:id>/complete', MissionCompleteView.as_view()),
]

# academy/urls.py (extend)
urlpatterns += [
    path('academy/tracks/<slug:id>', LearningTrackDetailView.as_view()),
    path('academy/lessons/<slug:id>', LessonDetailView.as_view()),
    path('academy/lessons/<slug:id>/submit-step', LessonSubmitStepView.as_view()),
]

# accounts/urls.py (extend)
urlpatterns += [
    path('user/journey', ChildJourneyView.as_view()),
    path('parent/children/<uuid:id>/journey', ParentChildJourneyView.as_view()),
]
```

---

## Appendix C: Revised core/utils.py Functions

```python
# New function: evaluate unlock rules
def evaluate_unlock_rule(child, rule_json):
    """Evaluate a JSON unlock rule for a child. Returns True if unlocked."""
    if not rule_json:
        return True

    rule_type = rule_json.get('type')

    if rule_type == 'lesson_complete':
        from academy.models import LessonProgress
        return LessonProgress.objects.filter(
            child=child, lesson_id=rule_json['lesson_id'], completed=True
        ).exists()

    if rule_type == 'mission_complete':
        from missions.models import MissionProgress
        return MissionProgress.objects.filter(
            child=child, mission_id=rule_json['mission_id'], status='completed'
        ).exists()

    if rule_type == 'xp_threshold':
        return child.xp >= rule_json['xp']

    if rule_type == 'all_of':
        return all(evaluate_unlock_rule(child, r) for r in rule_json['rules'])

    if rule_type == 'any_of':
        return any(evaluate_unlock_rule(child, r) for r in rule_json['rules'])

    return False


# Extended: complete_lesson (new)
def complete_lesson(child, lesson):
    """Complete a lesson, award XP, update track progress, unlock linked missions."""
    from academy.models import LessonProgress, TrackProgress
    from missions.models import Mission, MissionProgress

    progress, _ = LessonProgress.objects.get_or_create(child=child, lesson=lesson)
    if progress.completed:
        return  # already completed

    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save()

    # Award XP
    if lesson.xp_reward > 0:
        child.xp += lesson.xp_reward
        child.save(update_fields=['xp'])
        check_level_up(child)

    # Activity log
    ActivityLog.objects.create(
        child=child,
        type='lesson_completed',
        title=f'Completed "{lesson.title}"',
        description=lesson.description,
        xp_earned=lesson.xp_reward,
    )

    update_streak(child)

    # Unlock linked missions
    for mission in Mission.objects.filter(lesson=lesson):
        MissionProgress.objects.get_or_create(
            child=child, mission=mission, defaults={'status': 'available'}
        )
```
