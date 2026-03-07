from django.core.management.base import BaseCommand

from characters.models import Character
from missions.models import BossBattle, BossBattlePhase, Mission, MissionReward
from rewards.models import Badge
from story.models import Scene, StoryArc


def _scene(order, title, bg, chars, bubbles, motions=None, music='', sfx=None,
           next_action='next', action_payload=None):
    return {
        'order': order,
        'title': title,
        'background_key': bg,
        'characters_on_screen': chars,
        'bubbles': bubbles,
        'motions': motions or [],
        'music_key': music,
        'sfx_keys': sfx or [],
        'next_action': next_action,
        'action_payload': action_payload or {},
    }


def _char(character, position, expression='neutral', enter_animation='fade_in'):
    return {'character': character, 'position': position, 'expression': expression,
            'enter_animation': enter_animation}


def _bubble(character, text, bubble_type='speech', typing_speed='normal'):
    return {'character': character, 'text': text, 'bubble_type': bubble_type,
            'typing_speed': typing_speed}


def _motion(motion_type, trigger='on_enter', duration_ms=500, intensity=1.0):
    return {'type': motion_type, 'trigger': trigger, 'duration_ms': duration_ms,
            'intensity': intensity}


# ───────────────────────────────────────────────────────────────────────
# ARC DEFINITIONS — World 1
# ───────────────────────────────────────────────────────────────────────

ARCS = [
    # 1. Prologue
    {
        'id': 'world-1-prologue', 'title': 'The Rise of Dr. Glitch',
        'description': 'Something strange is happening on the internet. Screens glitch, pages break, and a mysterious villain emerges.',
        'arc_type': 'prologue', 'order': 1,
        'scenes': [
            _scene(1, 'The Internet at Peace', 'shero_hq',
                   [_char('narrator', 'center')],
                   [_bubble('narrator', 'Welcome to the internet — a vast, beautiful world of code.', 'narration'),
                    _bubble('narrator', 'Websites sparkle. Apps hum. Everything works perfectly.', 'narration')],
                   music='music-peaceful'),
            _scene(2, 'Meet the SHEROs', 'shero_hq',
                   [_char('byte', 'left', 'happy', 'slide_left'),
                    _char('pixel', 'center', 'happy', 'fade_in'),
                    _char('nova', 'right', 'happy', 'slide_right')],
                   [_bubble('narrator', 'Three young coders protect this digital world...', 'narration'),
                    _bubble('byte', "I'm Byte! I love building things with HTML!", 'speech'),
                    _bubble('pixel', "I'm Pixel! I make everything look beautiful with CSS!", 'speech'),
                    _bubble('nova', "And I'm Nova! I bring things to life with JavaScript!", 'speech')],
                   music='music-hero-theme'),
            _scene(3, 'The First Glitch', 'broken_internet',
                   [_char('narrator', 'center')],
                   [_bubble('narrator', 'But one day... something went wrong.', 'narration', 'slow'),
                    _bubble('narrator', 'Screens started flickering. Websites began to break.', 'narration')],
                   [_motion('screen_shake', 'on_bubble', 500, 0.8),
                    _motion('glitch_effect', 'on_enter', 1000)],
                   music='music-tension'),
            _scene(4, 'Dr. Glitch Appears', 'corrupted_city',
                   [_char('dr_glitch', 'center', 'angry', 'glitch')],
                   [_bubble('dr_glitch', 'Ha ha ha! I am Dr. Glitch!', 'shout', 'fast'),
                    _bubble('dr_glitch', "I've scrambled every line of code on the internet!", 'speech'),
                    _bubble('dr_glitch', 'No one can stop me now!', 'shout')],
                   [_motion('screen_shake', 'on_enter', 800, 1.5),
                    _motion('flash', 'on_bubble', 300)],
                   music='music-villain'),
            _scene(5, 'The Internet Breaks', 'broken_internet',
                   [_char('dr_glitch', 'right', 'happy'),
                    _char('narrator', 'left')],
                   [_bubble('narrator', 'Websites crumbled. Links stopped working.', 'narration'),
                    _bubble('narrator', 'The internet was falling apart...', 'narration', 'slow')],
                   [_motion('glitch_effect', 'on_enter', 2000)]),
            _scene(6, 'A Call for Help', 'shero_hq',
                   [_char('byte', 'left', 'worried'),
                    _char('pixel', 'center', 'worried'),
                    _char('nova', 'right', 'determined')],
                   [_bubble('byte', 'The internet is breaking! We need help!', 'speech'),
                    _bubble('pixel', "Dr. Glitch's bugs are everywhere!", 'speech'),
                    _bubble('nova', "We can't do this alone...", 'speech')]),
            _scene(7, 'We Need a SHERO', 'shero_hq',
                   [_char('byte', 'left', 'determined'),
                    _char('pixel', 'center', 'determined'),
                    _char('nova', 'right', 'determined')],
                   [_bubble('byte', 'We need someone who can learn to code.', 'speech'),
                    _bubble('pixel', 'Someone brave and creative...', 'speech'),
                    _bubble('nova', 'We need a SHERO!', 'shout')],
                   [_motion('particles', 'on_bubble', 1500)],
                   music='music-hopeful'),
            _scene(8, 'That SHERO Is You', 'shero_hq',
                   [_char('byte', 'left', 'happy', 'bounce'),
                    _char('pixel', 'center', 'happy', 'bounce'),
                    _char('nova', 'right', 'happy', 'bounce')],
                   [_bubble('narrator', 'That SHERO... is YOU.', 'narration', 'slow'),
                    _bubble('narrator', 'Your coding adventure begins now!', 'narration')],
                   [_motion('particles', 'on_enter', 2000),
                    _motion('flash', 'on_bubble', 500)],
                   music='music-hero-theme', next_action='end'),
        ],
    },

    # 2. Mission 1 intro — Byte discovers first broken webpage
    {
        'id': 'mission-1-intro', 'title': 'The Broken Webpage',
        'description': 'Byte discovers the first corrupted webpage and needs your help to understand HTML.',
        'arc_type': 'mission_intro', 'order': 2,
        'scenes': [
            _scene(1, 'Byte Finds a Broken Page', 'website_ruins',
                   [_char('byte', 'left', 'worried', 'slide_left')],
                   [_bubble('byte', "SHERO! I've found something terrible!", 'speech'),
                    _bubble('byte', 'This webpage is completely broken. The HTML is corrupted!', 'speech')],
                   [_motion('glitch_effect', 'on_enter', 800)]),
            _scene(2, 'What Is HTML?', 'byte_lab',
                   [_char('byte', 'left', 'happy')],
                   [_bubble('byte', 'HTML is the language that builds webpages.', 'speech'),
                    _bubble('byte', 'Think of it like the skeleton of a website!', 'speech'),
                    _bubble('byte', "Tags like <h1> and <p> tell the browser what to show.", 'speech')]),
            _scene(3, 'The Mission', 'byte_lab',
                   [_char('byte', 'left', 'determined')],
                   [_bubble('byte', "We need to fix this page. I'll teach you the HTML tags.", 'speech'),
                    _bubble('byte', "Let's start with headings and paragraphs!", 'speech')]),
            _scene(4, 'Ready to Code', 'byte_lab',
                   [_char('byte', 'left', 'happy', 'bounce')],
                   [_bubble('byte', "You've got this, SHERO! Let's fix the internet!", 'shout')],
                   [_motion('particles', 'on_bubble', 1000)],
                   next_action='end'),
        ],
    },

    # 3. Mission 1 outro
    {
        'id': 'mission-1-outro', 'title': 'First Page Restored',
        'description': 'The first webpage is fixed! But Dr. Glitch notices...',
        'arc_type': 'mission_outro', 'order': 3,
        'scenes': [
            _scene(1, 'Page Restored!', 'website_ruins',
                   [_char('byte', 'left', 'happy', 'bounce')],
                   [_bubble('byte', 'You did it! The webpage is working again!', 'shout'),
                    _bubble('byte', 'The HTML tags are all in the right place!', 'speech')],
                   [_motion('particles', 'on_enter', 1500)]),
            _scene(2, 'Dr. Glitch Watches', 'glitch_lair',
                   [_char('dr_glitch', 'center', 'angry')],
                   [_bubble('dr_glitch', 'What?! Someone fixed my corrupted page?', 'shout'),
                    _bubble('dr_glitch', 'No matter... I have MANY more bugs planted!', 'speech')],
                   [_motion('screen_shake', 'on_bubble', 500)]),
            _scene(3, 'Onward!', 'shero_hq',
                   [_char('byte', 'left', 'determined'),
                    _char('pixel', 'right', 'happy')],
                   [_bubble('byte', "Great work! But there's more to fix.", 'speech'),
                    _bubble('pixel', "I think I've found something too... the styles are all wrong!", 'speech')],
                   next_action='end'),
        ],
    },

    # 4. Mission 2 intro — Pixel finds corrupted styles
    {
        'id': 'mission-2-intro', 'title': 'Corrupted Styles',
        'description': 'Pixel discovers that all the CSS styles have been scrambled.',
        'arc_type': 'mission_intro', 'order': 4,
        'scenes': [
            _scene(1, 'Pixel Spots the Problem', 'pixel_studio',
                   [_char('pixel', 'center', 'worried', 'slide_right')],
                   [_bubble('pixel', 'SHERO, look! All the colours are wrong!', 'speech'),
                    _bubble('pixel', 'Dr. Glitch has scrambled the CSS styles!', 'speech')]),
            _scene(2, 'What Is CSS?', 'pixel_studio',
                   [_char('pixel', 'center', 'happy')],
                   [_bubble('pixel', 'CSS is what makes webpages beautiful!', 'speech'),
                    _bubble('pixel', 'It controls colours, fonts, and layouts.', 'speech')]),
            _scene(3, 'Time to Style', 'pixel_studio',
                   [_char('pixel', 'center', 'determined')],
                   [_bubble('pixel', "Let's fix these styles together!", 'shout'),
                    _bubble('pixel', "I'll show you how CSS properties work.", 'speech')],
                   [_motion('particles', 'on_bubble', 1000)],
                   next_action='end'),
        ],
    },

    # 5. Mission 2 outro — Styles restored, Code Bugs appear
    {
        'id': 'mission-2-outro', 'title': 'Styles Restored',
        'description': 'The styles are back! But new Code Bugs are crawling around...',
        'arc_type': 'mission_outro', 'order': 5,
        'scenes': [
            _scene(1, 'Beautiful Again', 'pixel_studio',
                   [_char('pixel', 'center', 'happy', 'bounce')],
                   [_bubble('pixel', 'The colours are back! Everything looks gorgeous!', 'shout')],
                   [_motion('particles', 'on_enter', 1500)]),
            _scene(2, 'Code Bugs!', 'corrupted_city',
                   [_char('pixel', 'left', 'surprised'),
                    _char('nova', 'right', 'worried')],
                   [_bubble('pixel', 'Wait... what are those crawling things?', 'whisper'),
                    _bubble('nova', "Those are Code Bugs! Dr. Glitch's little minions!", 'speech')],
                   [_motion('glitch_effect', 'on_bubble', 600)]),
            _scene(3, 'Nova Takes the Lead', 'shero_hq',
                   [_char('nova', 'center', 'determined')],
                   [_bubble('nova', "I'll handle this next one. I can sense a logic anomaly.", 'speech')],
                   next_action='end'),
        ],
    },

    # 6. Mission 3 intro — Nova detects a logic anomaly
    {
        'id': 'mission-3-intro', 'title': 'The Logic Anomaly',
        'description': 'Nova senses something wrong with the logic layer of the internet.',
        'arc_type': 'mission_intro', 'order': 6,
        'scenes': [
            _scene(1, 'Nova Investigates', 'nova_workshop',
                   [_char('nova', 'center', 'thinking', 'fade_in')],
                   [_bubble('nova', 'Something is wrong with the logic circuits...', 'thought'),
                    _bubble('nova', 'The conditions and loops are all tangled!', 'speech')]),
            _scene(2, 'What Is Logic?', 'nova_workshop',
                   [_char('nova', 'center', 'happy')],
                   [_bubble('nova', 'Logic is how computers make decisions.', 'speech'),
                    _bubble('nova', 'If-else statements, loops, functions — they power everything!', 'speech')]),
            _scene(3, 'Debug the Logic', 'nova_workshop',
                   [_char('nova', 'center', 'determined')],
                   [_bubble('nova', "Time to untangle these bugs. Let's think step by step!", 'speech')],
                   [_motion('particles', 'on_bubble', 1000)]),
            _scene(4, 'Go Time!', 'nova_workshop',
                   [_char('nova', 'center', 'happy', 'bounce')],
                   [_bubble('nova', "I believe in you, SHERO! Let's fix this!", 'shout')],
                   next_action='end'),
        ],
    },

    # 7. Mission 3 outro — Anomaly fixed, trail leads deeper
    {
        'id': 'mission-3-outro', 'title': 'Trail Deeper',
        'description': 'The anomaly is fixed, but the trail leads to Dr. Glitch\'s deeper systems.',
        'arc_type': 'mission_outro', 'order': 7,
        'scenes': [
            _scene(1, 'Anomaly Fixed', 'nova_workshop',
                   [_char('nova', 'center', 'happy')],
                   [_bubble('nova', 'The logic circuits are working again!', 'speech')],
                   [_motion('particles', 'on_enter', 1000)]),
            _scene(2, 'A Deeper Trail', 'data_river',
                   [_char('nova', 'left', 'thinking'),
                    _char('byte', 'right', 'worried')],
                   [_bubble('nova', "I found something... Dr. Glitch's bugs go much deeper.", 'speech'),
                    _bubble('byte', "We need to keep going. The internet depends on us.", 'speech')]),
            _scene(3, 'Team Regroups', 'shero_hq',
                   [_char('byte', 'left', 'determined'),
                    _char('pixel', 'center', 'determined'),
                    _char('nova', 'right', 'determined')],
                   [_bubble('byte', "Let's keep pushing forward!", 'shout')],
                   next_action='end'),
        ],
    },

    # 8. Mission 4 intro — Corrupted gallery
    {
        'id': 'mission-4-intro', 'title': 'The Corrupted Gallery',
        'description': 'The team discovers a gallery of images that have been scrambled.',
        'arc_type': 'mission_intro', 'order': 8,
        'scenes': [
            _scene(1, 'Broken Images', 'website_ruins',
                   [_char('pixel', 'left', 'worried')],
                   [_bubble('pixel', 'All the images in this gallery are broken!', 'speech'),
                    _bubble('pixel', 'The image tags have been corrupted by Dr. Glitch.', 'speech')]),
            _scene(2, 'Fix the Gallery', 'pixel_studio',
                   [_char('pixel', 'center', 'determined')],
                   [_bubble('pixel', "We need to fix the <img> tags and restore the gallery.", 'speech'),
                    _bubble('pixel', "I'll show you how images work in HTML!", 'speech')]),
            _scene(3, "Let's Go!", 'pixel_studio',
                   [_char('pixel', 'center', 'happy', 'bounce')],
                   [_bubble('pixel', 'Ready, SHERO? Time to bring these images back!', 'shout')],
                   next_action='end'),
        ],
    },

    # 9. Mission 5 intro — Navigation broken
    {
        'id': 'mission-5-intro', 'title': 'Broken Navigation',
        'description': 'The navigation system is completely scrambled.',
        'arc_type': 'mission_intro', 'order': 9,
        'scenes': [
            _scene(1, 'Lost in the Web', 'internet_highway',
                   [_char('byte', 'left', 'worried')],
                   [_bubble('byte', 'The navigation links are all broken!', 'speech'),
                    _bubble('byte', 'Nobody can find their way around anymore.', 'speech')]),
            _scene(2, 'Links and Lists', 'byte_lab',
                   [_char('byte', 'center', 'happy')],
                   [_bubble('byte', "Links connect pages together. They use the <a> tag.", 'speech'),
                    _bubble('byte', "And lists organise content with <ul> and <li>.", 'speech')]),
            _scene(3, 'Fix the Nav!', 'byte_lab',
                   [_char('byte', 'center', 'determined')],
                   [_bubble('byte', "Let's rebuild the navigation!", 'shout')],
                   next_action='end'),
        ],
    },

    # 10. World 1 interlude — between missions 5 and 6
    {
        'id': 'world-1-interlude', 'title': 'The Team Reflects',
        'description': 'Between missions, the SHEROs reflect on their progress.',
        'arc_type': 'interlude', 'order': 10,
        'scenes': [
            _scene(1, 'A Moment of Rest', 'shero_hq',
                   [_char('byte', 'left', 'happy'),
                    _char('pixel', 'center', 'happy'),
                    _char('nova', 'right', 'happy')],
                   [_bubble('byte', "We've come so far! Five missions complete!", 'speech'),
                    _bubble('pixel', 'The internet is slowly coming back to life.', 'speech')]),
            _scene(2, 'Dr. Glitch Is Watching', 'glitch_lair',
                   [_char('dr_glitch', 'center', 'thinking')],
                   [_bubble('dr_glitch', 'These SHEROs are stronger than I thought...', 'thought'),
                    _bubble('dr_glitch', 'Time for my ultimate plan!', 'speech')],
                   [_motion('screen_shake', 'on_bubble', 400)]),
            _scene(3, 'Back to Work', 'shero_hq',
                   [_char('nova', 'center', 'determined')],
                   [_bubble('nova', "Something big is coming. We need to be ready.", 'speech')],
                   next_action='end'),
        ],
    },

    # 11. Mission 6 intro — Scrambled links
    {
        'id': 'mission-6-intro', 'title': 'Scrambled Links',
        'description': 'All the hyperlinks on the internet are pointing to the wrong places.',
        'arc_type': 'mission_intro', 'order': 11,
        'scenes': [
            _scene(1, 'Wrong Destinations', 'internet_highway',
                   [_char('pixel', 'left', 'surprised')],
                   [_bubble('pixel', 'All the links are pointing to the wrong pages!', 'speech'),
                    _bubble('pixel', 'Clicking "Home" takes you to "Contact". It\'s chaos!', 'speech')]),
            _scene(2, 'Understanding Links', 'pixel_studio',
                   [_char('pixel', 'center', 'happy')],
                   [_bubble('pixel', 'The href attribute tells a link where to go.', 'speech'),
                    _bubble('pixel', "Dr. Glitch changed all the href values!", 'speech')]),
            _scene(3, 'Fix Them All!', 'pixel_studio',
                   [_char('pixel', 'center', 'determined')],
                   [_bubble('pixel', "Let's reconnect every link to the right page!", 'shout')],
                   next_action='end'),
        ],
    },

    # 12. Mission 7 intro — Secret message
    {
        'id': 'mission-7-intro', 'title': 'The Hidden Message',
        'description': 'A secret message is hidden in the code, left by a mysterious ally.',
        'arc_type': 'mission_intro', 'order': 12,
        'scenes': [
            _scene(1, 'A Clue in the Code', 'server_room',
                   [_char('nova', 'left', 'surprised')],
                   [_bubble('nova', "Wait... there's a hidden message in this code!", 'whisper'),
                    _bubble('nova', 'Someone left us a clue about Dr. Glitch!', 'speech')]),
            _scene(2, 'HTML Comments', 'nova_workshop',
                   [_char('nova', 'center', 'happy')],
                   [_bubble('nova', 'HTML comments are hidden messages in code.', 'speech'),
                    _bubble('nova', 'They look like this: <!-- secret message -->', 'speech')]),
            _scene(3, 'Decode It!', 'nova_workshop',
                   [_char('nova', 'center', 'determined')],
                   [_bubble('nova', "Let's find all the hidden messages!", 'shout')],
                   next_action='end'),
        ],
    },

    # 13. Mission 8 intro — Dr. Glitch's firewall
    {
        'id': 'mission-8-intro', 'title': "Dr. Glitch's Firewall",
        'description': "The team reaches Dr. Glitch's firewall — a wall of corrupted code.",
        'arc_type': 'mission_intro', 'order': 13,
        'scenes': [
            _scene(1, 'The Firewall', 'firewall_gate',
                   [_char('byte', 'left', 'worried'),
                    _char('pixel', 'center', 'worried'),
                    _char('nova', 'right', 'worried')],
                   [_bubble('byte', "It's Dr. Glitch's firewall!", 'speech'),
                    _bubble('pixel', 'A wall of corrupted code blocking our path!', 'speech')],
                   [_motion('glitch_effect', 'on_enter', 1000)]),
            _scene(2, 'Breaking Through', 'firewall_gate',
                   [_char('nova', 'center', 'thinking')],
                   [_bubble('nova', 'We need to fix the code in the firewall to break through.', 'speech'),
                    _bubble('nova', 'Each section has different bugs to fix.', 'speech')]),
            _scene(3, 'Team Effort', 'firewall_gate',
                   [_char('byte', 'left', 'determined'),
                    _char('pixel', 'center', 'determined'),
                    _char('nova', 'right', 'determined')],
                   [_bubble('byte', 'HTML structure!', 'speech'),
                    _bubble('pixel', 'CSS styles!', 'speech'),
                    _bubble('nova', 'Logic and integration!', 'speech')]),
            _scene(4, 'Breach the Wall!', 'firewall_gate',
                   [_char('byte', 'left', 'determined', 'bounce'),
                    _char('pixel', 'center', 'determined', 'bounce'),
                    _char('nova', 'right', 'determined', 'bounce')],
                   [_bubble('narrator', "Together, the SHEROs attack the firewall!", 'narration')],
                   [_motion('explosion', 'on_bubble', 1000)],
                   next_action='end'),
        ],
    },

    # 14. Mission 9 intro — Final push
    {
        'id': 'mission-9-intro', 'title': 'The Final Push',
        'description': "The SHEROs prepare for the confrontation with Dr. Glitch.",
        'arc_type': 'mission_intro', 'order': 14,
        'scenes': [
            _scene(1, 'Beyond the Firewall', 'digital_void',
                   [_char('byte', 'left', 'surprised'),
                    _char('pixel', 'center', 'surprised'),
                    _char('nova', 'right', 'surprised')],
                   [_bubble('byte', "We're through! But look...", 'whisper'),
                    _bubble('pixel', "Dr. Glitch's lair is just ahead.", 'speech')],
                   [_motion('glitch_effect', 'on_enter', 500)]),
            _scene(2, 'Preparing for Battle', 'shero_hq',
                   [_char('byte', 'left', 'determined'),
                    _char('pixel', 'center', 'determined'),
                    _char('nova', 'right', 'determined')],
                   [_bubble('nova', 'We need to sharpen our skills before the final battle.', 'speech'),
                    _bubble('byte', 'One more challenge to prove we are ready.', 'speech')]),
            _scene(3, 'SHERO Review', 'shero_hq',
                   [_char('byte', 'left', 'happy'),
                    _char('pixel', 'center', 'happy'),
                    _char('nova', 'right', 'happy')],
                   [_bubble('pixel', 'HTML, CSS, logic — we know it all now!', 'speech'),
                    _bubble('nova', 'Time for the final review mission.', 'speech')]),
            _scene(4, 'Ready!', 'shero_hq',
                   [_char('byte', 'left', 'determined', 'bounce'),
                    _char('pixel', 'center', 'determined', 'bounce'),
                    _char('nova', 'right', 'determined', 'bounce')],
                   [_bubble('narrator', 'The SHEROs are ready for the final push!', 'narration')],
                   [_motion('particles', 'on_enter', 1500)],
                   next_action='end'),
        ],
    },

    # 15. Boss battle intro
    {
        'id': 'boss-battle-intro', 'title': "Dr. Glitch's Last Stand",
        'description': "The SHEROs confront Dr. Glitch in his digital lair.",
        'arc_type': 'mission_intro', 'order': 15,
        'scenes': [
            _scene(1, "Dr. Glitch's Lair", 'glitch_lair',
                   [_char('byte', 'left', 'determined'),
                    _char('pixel', 'center', 'determined'),
                    _char('nova', 'right', 'determined')],
                   [_bubble('narrator', 'The SHEROs have reached the heart of the corruption.', 'narration', 'slow')],
                   [_motion('glitch_effect', 'on_enter', 1500)],
                   music='music-boss'),
            _scene(2, 'Dr. Glitch Confrontation', 'boss_arena',
                   [_char('dr_glitch', 'center', 'angry', 'glitch')],
                   [_bubble('dr_glitch', "So, you've made it this far!", 'shout'),
                    _bubble('dr_glitch', "But you'll NEVER defeat my ultimate bugs!", 'speech')],
                   [_motion('screen_shake', 'on_enter', 1000, 1.5)],
                   music='music-boss'),
            _scene(3, 'The Challenge', 'boss_arena',
                   [_char('dr_glitch', 'right', 'angry'),
                    _char('byte', 'left', 'determined')],
                   [_bubble('dr_glitch', 'I challenge you to fix three impossible bugs!', 'shout'),
                    _bubble('byte', "We accept! SHEROs never back down!", 'shout')],
                   [_motion('flash', 'on_bubble', 500)]),
            _scene(4, 'Phase 1 — Byte Steps Up', 'boss_arena',
                   [_char('byte', 'center', 'determined')],
                   [_bubble('byte', "I'll handle the HTML! Let's fix this structure!", 'speech'),
                    _bubble('narrator', 'Phase 1: HTML Repair begins!', 'narration')],
                   [_motion('zoom_in', 'on_bubble', 800)]),
            _scene(5, 'Phase 2 — Pixel Steps Up', 'boss_arena',
                   [_char('pixel', 'center', 'determined')],
                   [_bubble('pixel', "My turn! I'll fix the corrupted styles!", 'speech'),
                    _bubble('narrator', 'Phase 2: CSS Restoration begins!', 'narration')]),
            _scene(6, 'Phase 3 — Nova Steps Up', 'boss_arena',
                   [_char('nova', 'center', 'determined')],
                   [_bubble('nova', "Final phase! I'll integrate everything!", 'speech'),
                    _bubble('narrator', 'Phase 3: The Final Integration!', 'narration')],
                   [_motion('flash', 'on_enter', 500)],
                   next_action='end'),
        ],
    },

    # 16. Boss battle victory
    {
        'id': 'boss-battle-victory', 'title': 'Internet Restored!',
        'description': 'Dr. Glitch is defeated and the internet is saved!',
        'arc_type': 'mission_outro', 'order': 16,
        'scenes': [
            _scene(1, 'Dr. Glitch Defeated', 'boss_arena',
                   [_char('dr_glitch', 'center', 'surprised')],
                   [_bubble('dr_glitch', "No! This can't be! My bugs... they're all fixed!", 'shout'),
                    _bubble('dr_glitch', "You... you really ARE a SHERO!", 'speech')],
                   [_motion('screen_shake', 'on_enter', 1000),
                    _motion('explosion', 'on_bubble', 800)]),
            _scene(2, 'The Internet Heals', 'internet_highway',
                   [_char('narrator', 'center')],
                   [_bubble('narrator', 'The internet begins to heal...', 'narration', 'slow'),
                    _bubble('narrator', 'Websites come back online. Colours return. Links work again.', 'narration')],
                   [_motion('particles', 'on_enter', 2000)],
                   music='music-victory'),
            _scene(3, 'SHEROs Celebrate', 'shero_hq',
                   [_char('byte', 'left', 'happy', 'bounce'),
                    _char('pixel', 'center', 'happy', 'bounce'),
                    _char('nova', 'right', 'happy', 'bounce')],
                   [_bubble('byte', 'We did it! The internet is saved!', 'shout'),
                    _bubble('pixel', 'And it looks MORE beautiful than ever!', 'speech'),
                    _bubble('nova', 'All thanks to our amazing SHERO!', 'speech')],
                   [_motion('particles', 'on_enter', 2000)],
                   music='music-celebration'),
            _scene(4, 'SHERO Badge', 'shero_hq',
                   [_char('byte', 'left', 'happy'),
                    _char('pixel', 'center', 'happy'),
                    _char('nova', 'right', 'happy')],
                   [_bubble('narrator', 'You have earned the ultimate badge: Code SHERO!', 'narration'),
                    _bubble('narrator', 'But this is just the beginning of your coding journey...', 'narration')],
                   [_motion('flash', 'on_bubble', 500),
                    _motion('particles', 'on_enter', 3000)]),
            _scene(5, 'To Be Continued', 'shero_hq',
                   [_char('narrator', 'center')],
                   [_bubble('narrator', 'World 1 Complete! Your adventure continues in World 2...', 'narration', 'slow')],
                   [_motion('code_rain', 'on_enter', 3000)],
                   next_action='end'),
        ],
    },
]


# ───────────────────────────────────────────────────────────────────────
# Mission-to-arc mapping
# ───────────────────────────────────────────────────────────────────────
MISSION_ARC_LINKS = {
    # mission_num: (intro_arc_slug, outro_arc_slug or None, requires_arc_slug or None)
    1: ('mission-1-intro', 'mission-1-outro', 'world-1-prologue'),
    2: ('mission-2-intro', None, None),
    3: ('mission-3-intro', 'mission-3-outro', None),
    4: ('mission-4-intro', None, None),
    5: ('mission-5-intro', 'mission-2-outro', None),
    6: ('mission-6-intro', None, None),
    7: ('mission-7-intro', None, None),
    8: ('mission-8-intro', None, None),
    9: ('mission-9-intro', None, None),
    10: ('boss-battle-intro', None, None),
}


class Command(BaseCommand):
    help = 'Seed World 1 story arcs, scenes, boss battle, and link to missions'

    def handle(self, *args, **options):
        # ── Badge ──
        first_badge, _ = Badge.objects.update_or_create(
            id='badge-first-shero',
            defaults={
                'name': 'First SHERO',
                'description': 'Completed your very first SHERO mission!',
                'emoji': '🌟',
                'rarity': 'common',
                'category': 'General',
            },
        )

        # ── Seed all arcs and scenes ──
        total_scenes = 0
        for arc_data in ARCS:
            scenes_data = arc_data.pop('scenes')
            arc, _ = StoryArc.objects.update_or_create(
                id=arc_data['id'],
                defaults={k: v for k, v in arc_data.items() if k != 'id'},
            )
            # Re-add scenes key for potential re-runs
            arc_data['scenes'] = scenes_data

            Scene.objects.filter(arc=arc).delete()
            for s in scenes_data:
                Scene.objects.create(arc=arc, **s)
                total_scenes += 1

            self.stdout.write(f'  Arc "{arc.id}" seeded ({len(scenes_data)} scenes)')

        self.stdout.write(self.style.SUCCESS(
            f'Story arcs seeded ({len(ARCS)} arcs, {total_scenes} scenes)'
        ))

        # ── Link missions to arcs ──
        linked = 0
        for mission_num, (intro_slug, outro_slug, requires_slug) in MISSION_ARC_LINKS.items():
            mission = Mission.objects.filter(num=mission_num).first()
            if not mission:
                self.stdout.write(self.style.WARNING(f'  Mission num={mission_num} not found — skipping'))
                continue

            update_fields = []
            if intro_slug:
                mission.intro_arc_id = intro_slug
                update_fields.append('intro_arc')
            if outro_slug:
                mission.outro_arc_id = outro_slug
                update_fields.append('outro_arc')
            if requires_slug:
                mission.requires_arc_id = requires_slug
                update_fields.append('requires_arc')

            if update_fields:
                mission.save(update_fields=update_fields)
                linked += 1

        # First SHERO badge reward on mission 1
        mission1 = Mission.objects.filter(num=1).first()
        if mission1:
            MissionReward.objects.get_or_create(
                mission=mission1, type='badge', badge=first_badge,
                defaults={'label': first_badge.name, 'value': 1},
            )

        self.stdout.write(self.style.SUCCESS(f'Missions linked to arcs ({linked})'))

        # ── Seed Boss Battle on mission 10 ──
        mission_10 = Mission.objects.filter(num=10).first()
        if not mission_10:
            self.stdout.write(self.style.WARNING('Mission num=10 not found — skipping boss battle'))
            return

        boss_intro = StoryArc.objects.filter(id='boss-battle-intro').first()
        boss_victory = StoryArc.objects.filter(id='boss-battle-victory').first()

        boss, _ = BossBattle.objects.update_or_create(
            mission=mission_10,
            defaults={
                'title': "Dr. Glitch's Final Stand",
                'description': 'Defeat Dr. Glitch by fixing three phases of corrupted code!',
                'total_phases': 3,
                'intro_arc': boss_intro,
                'victory_arc': boss_victory,
                'xp_bonus': 200,
                'defeat_dialogue': [
                    {'character': 'dr_glitch', 'text': "Ha! Your code is no match for my bugs!"},
                    {'character': 'byte', 'text': "Don't give up, SHERO! We can do this!"},
                ],
            },
        )
        BossBattlePhase.objects.filter(boss_battle=boss).delete()

        try:
            byte_char = Character.objects.get(slug='byte')
            pixel_char = Character.objects.get(slug='pixel')
            nova_char = Character.objects.get(slug='nova')
        except Character.DoesNotExist:
            self.stdout.write(self.style.WARNING('Characters not found — skipping boss phases'))
            return

        BossBattlePhase.objects.create(
            boss_battle=boss, phase_number=1, leader_character=byte_char,
            title='Phase 1: HTML Repair',
            description='Fix the corrupted HTML tags!',
            challenge_type='debug_task',
            content={
                'prompt': "Dr. Glitch has corrupted the HTML! Fix the broken tags!",
                'buggy_code': "<h1>SHERO HQ<h2>\n<p>Welcome to our base<p>",
                'language': 'html',
                'validation': {'mode': 'contains_all', 'expected': ['</h1>', '</p>']},
            },
            intro_dialogue=[
                {'character': 'byte', 'text': "I'll handle the structure. Let's fix this HTML!"},
            ],
            success_dialogue=[
                {'character': 'byte', 'text': "HTML restored! But Dr. Glitch isn't done yet..."},
            ],
            health_bar_label='Dr. Glitch',
        )
        BossBattlePhase.objects.create(
            boss_battle=boss, phase_number=2, leader_character=pixel_char,
            title='Phase 2: CSS Restoration',
            description='Restore the corrupted CSS styles!',
            challenge_type='code_editor_challenge',
            content={
                'prompt': "The styles are all wrong! Write CSS to make the heading red and the paragraph blue.",
                'starter_code': "h1 {\n  \n}\np {\n  \n}",
                'language': 'css',
                'validation': {'mode': 'contains_all', 'expected': ['color', 'red', 'blue']},
            },
            intro_dialogue=[
                {'character': 'pixel', 'text': "My turn! I'll make everything beautiful again!"},
            ],
            success_dialogue=[
                {'character': 'pixel', 'text': "Styles restored! The colours are back!"},
            ],
            health_bar_label='Dr. Glitch',
        )
        BossBattlePhase.objects.create(
            boss_battle=boss, phase_number=3, leader_character=nova_char,
            title='Phase 3: The Final Integration',
            description='Put it all together to defeat Dr. Glitch!',
            challenge_type='mini_project',
            content={
                'prompt': "Build a complete page with a styled heading and paragraph to overpower Dr. Glitch!",
                'starter_code': '',
                'language': 'html',
                'validation': {'mode': 'contains_all', 'expected': ['<h1>', '<p>', 'style']},
            },
            intro_dialogue=[
                {'character': 'nova', 'text': "Final phase! Everything we've learned comes together!"},
            ],
            success_dialogue=[
                {'character': 'nova', 'text': "We did it! Dr. Glitch is defeated!"},
                {'character': 'byte', 'text': "The internet is saved!"},
                {'character': 'pixel', 'text': "And it's more beautiful than ever!"},
            ],
            health_bar_label='Dr. Glitch — FINAL',
        )

        self.stdout.write(self.style.SUCCESS(
            f'Boss battle seeded for mission "{mission_10.id}" (3 phases)'
        ))
        self.stdout.write(self.style.SUCCESS('World 1 story seeding complete!'))
