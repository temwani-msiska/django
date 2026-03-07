from django.core.management.base import BaseCommand

from characters.models import Character
from story.models import Scene, StoryArc


VALID_BACKGROUNDS = {
    'shero_hq', 'broken_internet', 'corrupted_city', 'code_forest',
    'data_river', 'glitch_lair', 'byte_lab', 'pixel_studio',
    'nova_workshop', 'boss_arena', 'digital_void', 'internet_highway',
    'website_ruins', 'server_room', 'firewall_gate',
}


def char(character, position, expression='neutral', enter_animation='fade_in', exit_animation='none', scale=1.0, z_index=1):
    return {
        'character': character,
        'position': position,
        'expression': expression,
        'enter_animation': enter_animation,
        'exit_animation': exit_animation,
        'scale': scale,
        'z_index': z_index,
    }


def bubble(character, text, bubble_type='speech', typing_speed='normal', delay_ms=0, auto_advance=False, auto_advance_delay_ms=3000):
    return {
        'character': character,
        'text': text,
        'bubble_type': bubble_type,
        'typing_speed': typing_speed,
        'delay_ms': delay_ms,
        'auto_advance': auto_advance,
        'auto_advance_delay_ms': auto_advance_delay_ms,
    }


def motion(motion_type, trigger='on_enter', trigger_index=0, duration_ms=500, intensity=1.0):
    return {
        'type': motion_type,
        'trigger': trigger,
        'trigger_index': trigger_index,
        'duration_ms': duration_ms,
        'intensity': intensity,
    }


ARCS = [
    {
        'id': 'world-1-prologue',
        'title': 'The Digital Tremor',
        'arc_type': 'prologue',
        'order': 1,
        'description': 'Byte, Pixel, and Nova arrive in a sleeping internet and discover Dr. Glitch’s plan.',
        'scenes': [
            {'order': 1, 'title': 'The Tremor', 'background_key': 'broken_internet', 'characters_on_screen': [char('narrator', 'center')], 'bubbles': [bubble('narrator', 'Deep in the heart of the internet, something terrible has happened…', 'narration')], 'motions': [motion('screen_shake', duration_ms=800)], 'next_action': 'next'},
            {'order': 2, 'title': 'The Source Plains', 'background_key': 'broken_internet', 'characters_on_screen': [char('byte', 'left', 'determined', 'slide_left'), char('pixel', 'center', 'worried'), char('nova', 'right', 'surprised', 'slide_right')], 'bubbles': [bubble('byte', 'What happened here? The whole system is offline!'), bubble('pixel', 'Everything is so grey… all the color is gone!'), bubble('nova', 'My sensors are picking up a strange signal. Something big caused this.')], 'motions': [], 'next_action': 'next'},
            {'order': 3, 'title': 'Dr. Glitch Reveal', 'background_key': 'glitch_lair', 'characters_on_screen': [char('dr_glitch', 'center', 'angry', 'glitch')], 'bubbles': [bubble('dr_glitch', 'Mwahaha! Welcome to MY internet now, little heroes!', 'shout'), bubble('dr_glitch', 'I’ve replaced all the world’s websites with pictures of… MY FACE!'), bubble('dr_glitch', 'Soon, the entire internet will be one giant ‘404 Error’ and I’ll be the only one who knows the password!')], 'motions': [motion('glitch_effect', duration_ms=1000, intensity=1.5)], 'sfx_keys': ['glitch'], 'next_action': 'next'},
            {'order': 4, 'title': 'The Challenge', 'background_key': 'broken_internet', 'characters_on_screen': [char('byte', 'left', 'determined'), char('pixel', 'center', 'determined'), char('nova', 'right', 'determined')], 'bubbles': [bubble('byte', 'We can’t let him get away with this!'), bubble('pixel', 'The internet needs color, creativity, and code!'), bubble('nova', 'And we’re the ones who can fix it. Together!')], 'motions': [motion('flash', trigger='on_bubble', trigger_index=2, duration_ms=300)], 'next_action': 'next'},
            {'order': 5, 'title': 'Team Assembly', 'background_key': 'shero_hq', 'characters_on_screen': [char('byte', 'left', 'happy'), char('pixel', 'center', 'happy'), char('nova', 'right', 'happy')], 'bubbles': [bubble('narrator', 'And so, three young heroes stepped forward to save the digital world…', 'narration'), bubble('byte', 'I’ll handle the logic and fix the structures!'), bubble('pixel', 'I’ll bring back the color and design!'), bubble('nova', 'And I’ll figure out the commands and traps!')], 'motions': [], 'next_action': 'next'},
            {'order': 6, 'title': 'The Gateway', 'background_key': 'internet_highway', 'characters_on_screen': [char('byte', 'center', 'thinking')], 'bubbles': [bubble('byte', 'Look! The Gateway Robot is powered down. We need to wake it up first.'), bubble('narrator', 'The first challenge awaits… but first, they need to learn the most important thing: how to run code.', 'narration')], 'motions': [], 'next_action': 'next'},
            {'order': 7, 'title': 'The Mission Ahead', 'background_key': 'internet_highway', 'characters_on_screen': [char('byte', 'left', 'determined'), char('pixel', 'right', 'determined')], 'bubbles': [bubble('pixel', 'So we just press the Run Code button?'), bubble('byte', 'It’s the first step to fixing everything. Every SHERO starts by running their first line of code!')], 'motions': [], 'next_action': 'next'},
            {'order': 8, 'title': 'Let’s Go', 'background_key': 'shero_hq', 'characters_on_screen': [char('byte', 'left', 'happy'), char('pixel', 'center', 'happy'), char('nova', 'right', 'happy')], 'bubbles': [bubble('narrator', 'The adventure begins now. Are you ready, SHERO?', 'narration')], 'motions': [motion('particles', trigger='on_exit', duration_ms=2000)], 'next_action': 'end'},
        ],
    },
]


# Generated arcs 2-21
ARCS.extend([
    {'id': 'mission-1-intro', 'title': 'Welcome SHERO', 'arc_type': 'mission_intro', 'order': 2, 'description': 'Find the Run Code button to wake the world.', 'scenes': [
        {'order': 1, 'title': 'Arrival', 'background_key': 'broken_internet', 'characters_on_screen': [char('byte', 'left', 'determined'), char('pixel', 'center', 'worried'), char('nova', 'right', 'surprised')], 'bubbles': [bubble('narrator', 'The SHEROs land in the Source Plains. The system is in a deep sleep.', 'narration')], 'motions': [], 'next_action': 'next'},
        {'order': 2, 'title': 'Powered Down', 'background_key': 'internet_highway', 'characters_on_screen': [char('byte', 'center', 'thinking'), char('pixel', 'left', 'worried'), char('nova', 'right', 'thinking')], 'bubbles': [bubble('byte', 'The Gateway Robot is offline, and this fog is hiding everything!'), bubble('nova', 'Power levels are almost zero.')], 'motions': [motion('zoom_in', duration_ms=700)], 'next_action': 'next'},
        {'order': 3, 'title': 'First Lesson', 'background_key': 'internet_highway', 'characters_on_screen': [char('byte', 'center', 'determined')], 'bubbles': [bubble('byte', 'We need to find the Run Code button. Running code sends energy into the system!')], 'motions': [], 'next_action': 'next'},
        {'order': 4, 'title': 'Ready', 'background_key': 'broken_internet', 'characters_on_screen': [char('byte', 'left', 'happy'), char('pixel', 'center', 'happy'), char('nova', 'right', 'happy')], 'bubbles': [bubble('nova', 'Ready? Let’s wake up the internet!')], 'motions': [motion('particles', duration_ms=1200)], 'next_action': 'end'},
    ]},
    {'id': 'mission-1-outro', 'title': 'The Internet Stirs', 'arc_type': 'mission_outro', 'order': 3, 'description': 'The robot wakes, but something is still wrong.', 'scenes': [
        {'order': 1, 'title': 'System Wake', 'background_key': 'internet_highway', 'characters_on_screen': [char('byte', 'left', 'happy'), char('pixel', 'center', 'happy'), char('nova', 'right', 'happy')], 'bubbles': [bubble('narrator', 'A surge of light powers the Gateway Robot. The fog begins to fade!', 'narration')], 'motions': [motion('flash', duration_ms=350), motion('particles', duration_ms=1200)], 'next_action': 'next'},
        {'order': 2, 'title': 'Speech Error', 'background_key': 'internet_highway', 'characters_on_screen': [char('byte', 'center', 'worried')], 'bubbles': [bubble('narrator', 'The robot blinks and tries to speak: “404 Error… 404 Error…”', 'narration'), bubble('byte', 'Uh-oh. Its speech chip is scrambled.')], 'motions': [], 'next_action': 'next'},
        {'order': 3, 'title': 'Next Mission', 'background_key': 'internet_highway', 'characters_on_screen': [char('byte', 'center', 'determined')], 'bubbles': [bubble('byte', 'The digital world is waking up, but it’s missing its voice! We need to fix the greetings next!')], 'motions': [], 'next_action': 'end'},
    ]},
    {'id': 'mission-2-intro', 'title': 'The Scrambled Speech', 'arc_type': 'mission_intro', 'order': 4, 'description': 'Byte finds garbled HTML in the robot’s voice system.', 'scenes': [
        {'order': 1, 'title': '404 Error', 'background_key': 'internet_highway', 'characters_on_screen': [char('byte', 'left', 'thinking'), char('narrator', 'right')], 'bubbles': [bubble('narrator', 'The Gateway Robot keeps sputtering: “404 Error…”', 'narration'), bubble('byte', 'Time for my logic goggles!')], 'motions': [], 'next_action': 'next'},
        {'order': 2, 'title': 'Hidden Layer', 'background_key': 'byte_lab', 'characters_on_screen': [char('byte', 'center', 'determined')], 'bubbles': [bubble('byte', 'I can see the hidden text layer. It’s garbled HTML!')], 'motions': [motion('zoom_in', duration_ms=600)], 'next_action': 'next'},
        {'order': 3, 'title': 'Fixing Voice', 'background_key': 'internet_highway', 'characters_on_screen': [char('byte', 'center', 'determined')], 'bubbles': [bubble('byte', 'I need to code a proper HTML header so the robot can talk!')], 'motions': [], 'next_action': 'end'},
    ]},
    {'id': 'mission-2-outro', 'title': 'Hello SHERO!', 'arc_type': 'mission_outro', 'order': 5, 'description': 'The robot speaks, but the world still needs structure.', 'scenes': [
        {'order': 1, 'title': 'First Greeting', 'background_key': 'internet_highway', 'characters_on_screen': [char('byte', 'left', 'happy'), char('pixel', 'center', 'happy'), char('nova', 'right', 'happy')], 'bubbles': [bubble('narrator', 'The robot smiles and says, “Hello SHERO!”', 'narration')], 'motions': [motion('particles', duration_ms=1300)], 'next_action': 'next'},
        {'order': 2, 'title': 'Blank Sign', 'background_key': 'website_ruins', 'characters_on_screen': [char('byte', 'center', 'thinking')], 'bubbles': [bubble('byte', 'Wait… this sign is blank. The website has no structure!')], 'motions': [], 'next_action': 'next'},
        {'order': 3, 'title': 'Hook', 'background_key': 'website_ruins', 'characters_on_screen': [char('byte', 'center', 'determined')], 'bubbles': [bubble('byte', 'Great job! But look at this sign… it’s totally blank!')], 'motions': [], 'next_action': 'end'},
    ]},
    {'id': 'mission-3-intro', 'title': 'The Library of Info', 'arc_type': 'mission_intro', 'order': 6, 'description': 'The team finds shattered page structure blocks.', 'scenes': [
        {'order': 1, 'title': 'Broken Library', 'background_key': 'website_ruins', 'characters_on_screen': [char('byte', 'left', 'worried'), char('pixel', 'center', 'surprised'), char('nova', 'right', 'worried')], 'bubbles': [bubble('narrator', 'The Library of Info is a mess. Digital building blocks are scattered everywhere.', 'narration')], 'motions': [], 'next_action': 'next'},
        {'order': 2, 'title': 'Byte Analyzes', 'background_key': 'website_ruins', 'characters_on_screen': [char('byte', 'center', 'thinking')], 'bubbles': [bubble('byte', 'No title, no structure, no direction. I can rebuild this if we place the blocks in order.')], 'motions': [], 'next_action': 'next'},
        {'order': 3, 'title': 'Rebuild Time', 'background_key': 'server_room', 'characters_on_screen': [char('byte', 'center', 'determined')], 'bubbles': [bubble('byte', 'Let’s restore the page structure and put the title block back on top!')], 'motions': [motion('pan_right', duration_ms=650)], 'next_action': 'end'},
    ]},
    {'id': 'mission-3-outro', 'title': 'Structure Restored', 'arc_type': 'mission_outro', 'order': 7, 'description': 'Structure returns but color is gone.', 'scenes': [
        {'order': 1, 'title': 'Order Restored', 'background_key': 'server_room', 'characters_on_screen': [char('byte', 'left', 'happy'), char('pixel', 'center', 'thinking')], 'bubbles': [bubble('byte', 'Structure restored! The page knows where it is again.')], 'motions': [motion('flash', duration_ms=300)], 'next_action': 'next'},
        {'order': 2, 'title': 'Need Pixel', 'background_key': 'broken_internet', 'characters_on_screen': [char('pixel', 'center', 'determined')], 'bubbles': [bubble('byte', 'The structure is back, but everything is so… grey. Pixel, can you help us out?')], 'motions': [], 'next_action': 'end'},
    ]},
    {'id': 'mission-4-intro', 'title': 'A World Without Color', 'arc_type': 'mission_intro', 'order': 8, 'description': 'Pixel prepares to restore style.', 'scenes': [
        {'order': 1, 'title': 'Grey Everywhere', 'background_key': 'broken_internet', 'characters_on_screen': [char('pixel', 'center', 'worried')], 'bubbles': [bubble('pixel', 'Everything looks like a dusty chalkboard… no color, no sparkle!')], 'motions': [], 'next_action': 'next'},
        {'order': 2, 'title': 'Stolen Spark', 'background_key': 'pixel_studio', 'characters_on_screen': [char('pixel', 'left', 'surprised'), char('dr_glitch', 'right', 'angry', 'glitch')], 'bubbles': [bubble('pixel', 'My Design Spark is gone!'), bubble('dr_glitch', 'Catch me if you can, artists!', 'shout')], 'motions': [motion('glitch_effect', duration_ms=900)], 'next_action': 'next'},
        {'order': 3, 'title': 'Pixel Steps Up', 'background_key': 'pixel_studio', 'characters_on_screen': [char('pixel', 'center', 'determined')], 'bubbles': [bubble('pixel', 'I’ll use CSS to bring color back. Let’s paint this world with code!')], 'motions': [motion('particles', duration_ms=900)], 'next_action': 'end'},
    ]},
    {'id': 'mission-4-outro', 'title': 'Color Returns', 'arc_type': 'mission_outro', 'order': 9, 'description': 'Color blooms but one page is not enough.', 'scenes': [
        {'order': 1, 'title': 'Bloom', 'background_key': 'corrupted_city', 'characters_on_screen': [char('pixel', 'center', 'happy'), char('byte', 'left', 'happy'), char('nova', 'right', 'happy')], 'bubbles': [bubble('narrator', 'With one line of CSS, the world blooms with vibrant color again!', 'narration')], 'motions': [motion('particles', duration_ms=1400)], 'next_action': 'next'},
        {'order': 2, 'title': 'Need More Pages', 'background_key': 'website_ruins', 'characters_on_screen': [char('pixel', 'center', 'thinking')], 'bubbles': [bubble('pixel', 'Now that’s style! But there’s only one page here. We need a whole school site!')], 'motions': [], 'next_action': 'end'},
    ]},
    {'id': 'mission-5-intro', 'title': 'Cyber Academy', 'arc_type': 'mission_intro', 'order': 10, 'description': 'Students need their homepage back.', 'scenes': [
        {'order': 1, 'title': 'Missing Homepage', 'background_key': 'website_ruins', 'characters_on_screen': [char('pixel', 'left', 'worried'), char('byte', 'center', 'thinking'), char('nova', 'right', 'worried')], 'bubbles': [bubble('narrator', 'At Cyber Academy, students are confused. The homepage has vanished!', 'narration')], 'motions': [], 'next_action': 'next'},
        {'order': 2, 'title': 'Take Charge', 'background_key': 'pixel_studio', 'characters_on_screen': [char('pixel', 'center', 'determined')], 'bubbles': [bubble('pixel', 'I’ve got this. A heading and paragraphs will guide everyone back to class.')], 'motions': [], 'next_action': 'next'},
        {'order': 3, 'title': 'Build Time', 'background_key': 'website_ruins', 'characters_on_screen': [char('pixel', 'center', 'happy')], 'bubbles': [bubble('pixel', 'Let’s build the Cyber Academy homepage!')], 'motions': [motion('zoom_in', duration_ms=700)], 'next_action': 'end'},
    ]},
    {'id': 'mission-5-outro', 'title': 'Something Flickers', 'arc_type': 'mission_outro', 'order': 11, 'description': 'A new glitch appears.', 'scenes': [
        {'order': 1, 'title': 'Page Complete', 'background_key': 'website_ruins', 'characters_on_screen': [char('pixel', 'center', 'happy')], 'bubbles': [bubble('pixel', 'Homepage complete! Students can find their lessons again!')], 'motions': [motion('particles', duration_ms=1100)], 'next_action': 'next'},
        {'order': 2, 'title': 'Glitch Flicker', 'background_key': 'digital_void', 'characters_on_screen': [char('dr_glitch', 'center', 'angry', 'glitch')], 'bubbles': [bubble('narrator', 'A strange glitch flickers across the screen...', 'narration'), bubble('dr_glitch', 'Hehehe, time for my code bugs!', 'shout')], 'motions': [motion('glitch_effect', duration_ms=900), motion('screen_shake', duration_ms=500)], 'next_action': 'next'},
        {'order': 3, 'title': 'Transition to Byte', 'background_key': 'byte_lab', 'characters_on_screen': [char('byte', 'center', 'determined')], 'bubbles': [bubble('byte', 'Something is breaking our code. I’ll debug this!')], 'motions': [], 'next_action': 'end'},
    ]},
    {'id': 'mission-6-intro', 'title': 'The Code Bug Appears', 'arc_type': 'mission_intro', 'order': 12, 'description': 'Byte faces a bracket-chewing Code Bug.', 'scenes': [
        {'order': 1, 'title': 'Bug Entrance', 'background_key': 'server_room', 'characters_on_screen': [char('dr_glitch', 'far_right', 'happy', 'glitch'), char('byte', 'left', 'surprised')], 'bubbles': [bubble('narrator', 'A Code Bug bursts out, chewing on brackets!', 'narration'), bubble('dr_glitch', 'Snack time for my bugs!', 'shout')], 'motions': [motion('glitch_effect', duration_ms=900), motion('screen_shake', duration_ms=500)], 'next_action': 'next'},
        {'order': 2, 'title': 'Digital Slime', 'background_key': 'server_room', 'characters_on_screen': [char('byte', 'center', 'thinking')], 'bubbles': [bubble('byte', 'Digital Slime is covering the tags. No panic — I’ll inspect each line.')], 'motions': [], 'next_action': 'next'},
        {'order': 3, 'title': 'Stay Calm', 'background_key': 'byte_lab', 'characters_on_screen': [char('byte', 'center', 'determined')], 'bubbles': [bubble('byte', 'Debugging means finding errors one clue at a time. We can do this, SHERO.')], 'motions': [], 'next_action': 'next'},
        {'order': 4, 'title': 'Fix the Tags', 'background_key': 'server_room', 'characters_on_screen': [char('byte', 'center', 'determined')], 'bubbles': [bubble('byte', 'Let’s repair these broken tags before the bug eats the whole page!')], 'motions': [motion('zoom_in', duration_ms=650)], 'next_action': 'end'},
    ]},
    {'id': 'mission-6-outro', 'title': 'Bug Escaped', 'arc_type': 'mission_outro', 'order': 13, 'description': 'The bug flees to the Action Zone.', 'scenes': [
        {'order': 1, 'title': 'Almost Caught', 'background_key': 'server_room', 'characters_on_screen': [char('byte', 'left', 'happy'), char('nova', 'right', 'surprised')], 'bubbles': [bubble('byte', 'Gotcha— wait! It slipped free!'), bubble('narrator', 'The Code Bug races toward the Action Zone.', 'narration')], 'motions': [motion('pan_right', duration_ms=550)], 'next_action': 'next'},
        {'order': 2, 'title': 'Need a Trap', 'background_key': 'firewall_gate', 'characters_on_screen': [char('nova', 'center', 'determined')], 'bubbles': [bubble('nova', 'Got him! But the bug escaped into the Action Zone. We need a way to catch it!')], 'motions': [], 'next_action': 'end'},
    ]},
    {'id': 'mission-7-intro', 'title': 'The Trap', 'arc_type': 'mission_intro', 'order': 14, 'description': 'Nova builds a trigger button.', 'scenes': [
        {'order': 1, 'title': 'Action Zone Trap', 'background_key': 'firewall_gate', 'characters_on_screen': [char('nova', 'center', 'thinking')], 'bubbles': [bubble('nova', 'This high-tech trap is perfect… except it has no trigger!')], 'motions': [], 'next_action': 'next'},
        {'order': 2, 'title': 'Nova Idea', 'background_key': 'nova_workshop', 'characters_on_screen': [char('nova', 'center', 'happy')], 'bubbles': [bubble('nova', 'A button can activate the net launcher. Click = catch!')], 'motions': [motion('zoom_in', duration_ms=600)], 'next_action': 'next'},
        {'order': 3, 'title': 'Code the Trigger', 'background_key': 'nova_workshop', 'characters_on_screen': [char('nova', 'center', 'determined')], 'bubbles': [bubble('nova', 'Let’s code the button and arm the trap!')], 'motions': [], 'next_action': 'end'},
    ]},
    {'id': 'mission-8-intro', 'title': 'The Maze', 'arc_type': 'mission_intro', 'order': 15, 'description': 'Nova guides the robot with command sequences.', 'scenes': [
        {'order': 1, 'title': 'Maze Entrance', 'background_key': 'code_forest', 'characters_on_screen': [char('nova', 'left', 'happy'), char('byte', 'center', 'thinking'), char('pixel', 'right', 'worried')], 'bubbles': [bubble('nova', 'Robot Companion is ready!'), bubble('narrator', 'The maze is full of obstacles left by Dr. Glitch.', 'narration')], 'motions': [], 'next_action': 'next'},
        {'order': 2, 'title': 'Sequence Matters', 'background_key': 'code_forest', 'characters_on_screen': [char('nova', 'center', 'determined')], 'bubbles': [bubble('nova', 'If we use commands in the right order, we can navigate safely.')], 'motions': [], 'next_action': 'next'},
        {'order': 3, 'title': 'Command Time', 'background_key': 'code_forest', 'characters_on_screen': [char('nova', 'center', 'determined')], 'bubbles': [bubble('nova', 'Move, turn, move — let’s guide our robot through the maze!')], 'motions': [motion('pan_left', duration_ms=700)], 'next_action': 'end'},
    ]},
    {'id': 'mission-8-outro', 'title': 'Path Cleared', 'arc_type': 'mission_outro', 'order': 16, 'description': 'The team reaches the internet core.', 'scenes': [
        {'order': 1, 'title': 'Exit Reached', 'background_key': 'code_forest', 'characters_on_screen': [char('nova', 'center', 'happy')], 'bubbles': [bubble('nova', 'Path cleared! Robot Companion reached the exit!')], 'motions': [motion('particles', duration_ms=1000)], 'next_action': 'next'},
        {'order': 2, 'title': 'To the Core', 'background_key': 'internet_highway', 'characters_on_screen': [char('byte', 'left', 'determined'), char('pixel', 'center', 'determined'), char('nova', 'right', 'determined')], 'bubbles': [bubble('byte', 'We’ve made it to the center of the internet.'), bubble('nova', 'Time to show Dr. Glitch what SHEROs are made of!')], 'motions': [], 'next_action': 'end'},
    ]},
    {'id': 'mission-9-intro', 'title': 'A Beacon of Hope', 'arc_type': 'mission_intro', 'order': 17, 'description': 'The team creates a hope message before the final fight.', 'scenes': [
        {'order': 1, 'title': 'Before the Final Fight', 'background_key': 'shero_hq', 'characters_on_screen': [char('byte', 'left', 'thinking'), char('pixel', 'center', 'determined'), char('nova', 'right', 'thinking')], 'bubbles': [bubble('byte', 'Before we face Dr. Glitch, people need hope.'), bubble('pixel', 'Let’s build a SHERO HQ page as a beacon!')], 'motions': [], 'next_action': 'next'},
        {'order': 2, 'title': 'Message of Hope', 'background_key': 'pixel_studio', 'characters_on_screen': [char('pixel', 'center', 'happy')], 'bubbles': [bubble('pixel', 'Our page will say: “I am a SHERO.” Every coder will see it!')], 'motions': [motion('particles', duration_ms=900)], 'next_action': 'next'},
        {'order': 3, 'title': 'Build Beacon', 'background_key': 'shero_hq', 'characters_on_screen': [char('pixel', 'center', 'determined')], 'bubbles': [bubble('pixel', 'Let’s combine HTML and CSS to light up the internet!')], 'motions': [], 'next_action': 'end'},
    ]},
    {'id': 'mission-9-outro', 'title': 'Dr. Glitch at the Core', 'arc_type': 'mission_outro', 'order': 18, 'description': 'The beacon shines; Dr. Glitch is spotted.', 'scenes': [
        {'order': 1, 'title': 'Beacon Lit', 'background_key': 'shero_hq', 'characters_on_screen': [char('byte', 'left', 'happy'), char('pixel', 'center', 'happy'), char('nova', 'right', 'happy')], 'bubbles': [bubble('narrator', 'The SHERO page glows like a beacon across the network!', 'narration')], 'motions': [motion('particles', duration_ms=1200)], 'next_action': 'next'},
        {'order': 2, 'title': 'Core Threat', 'background_key': 'boss_arena', 'characters_on_screen': [char('dr_glitch', 'center', 'angry', 'glitch')], 'bubbles': [bubble('narrator', 'Dr. Glitch appears at the Core, trying to delete everything!', 'narration')], 'motions': [motion('glitch_effect', duration_ms=1000), motion('screen_shake', duration_ms=550)], 'next_action': 'next'},
        {'order': 3, 'title': 'Assemble', 'background_key': 'boss_arena', 'characters_on_screen': [char('byte', 'left', 'determined'), char('pixel', 'center', 'determined'), char('nova', 'right', 'determined')], 'bubbles': [bubble('byte', 'Look! Dr. Glitch is at the Core! Team, assemble!')], 'motions': [motion('flash', duration_ms=300)], 'next_action': 'end'},
    ]},
    {'id': 'boss-battle-intro', 'title': 'The Final Showdown', 'arc_type': 'mission_intro', 'order': 19, 'description': 'The SHEROs face Dr. Glitch at the Digital Core.', 'scenes': [
        {'order': 1, 'title': 'Digital Core', 'background_key': 'boss_arena', 'characters_on_screen': [char('byte', 'left', 'determined'), char('pixel', 'center', 'determined'), char('nova', 'right', 'determined')], 'bubbles': [bubble('narrator', 'The team arrives at the Digital Core. A golden circuit tree is covered in purple Glitch Goo.', 'narration')], 'motions': [], 'next_action': 'next'},
        {'order': 2, 'title': 'Glitch-Glider', 'background_key': 'boss_arena', 'characters_on_screen': [char('dr_glitch', 'center', 'angry', 'glitch')], 'bubbles': [bubble('dr_glitch', 'Mwahaha! You’re too late, SHEROs!', 'shout'), bubble('dr_glitch', 'I’ve replaced all the world’s websites with pictures of… MY FACE!'), bubble('dr_glitch', 'Soon, the entire internet will be one giant ‘404 Error’ and I’ll be the only one who knows the password!')], 'motions': [motion('glitch_effect', duration_ms=900), motion('screen_shake', duration_ms=600)], 'next_action': 'next'},
        {'order': 3, 'title': 'Team Response', 'background_key': 'boss_arena', 'characters_on_screen': [char('byte', 'left', 'determined'), char('pixel', 'center', 'determined'), char('nova', 'right', 'determined')], 'bubbles': [bubble('byte', 'Not on our watch, Dr. Glitch!'), bubble('pixel', 'The internet belongs to everyone!'), bubble('nova', 'And we’ve got the code to prove it!')], 'motions': [], 'next_action': 'next'},
        {'order': 4, 'title': 'Attack', 'background_key': 'boss_arena', 'characters_on_screen': [char('dr_glitch', 'center', 'angry', 'glitch')], 'bubbles': [bubble('dr_glitch', 'Then try and stop me! Tag-Tornado, GO!', 'shout')], 'motions': [motion('screen_shake', duration_ms=600), motion('code_rain', duration_ms=1500)], 'next_action': 'next'},
        {'order': 5, 'title': 'Strategy', 'background_key': 'boss_arena', 'characters_on_screen': [char('byte', 'left', 'determined'), char('pixel', 'center', 'determined'), char('nova', 'right', 'determined')], 'bubbles': [bubble('byte', 'We need to work together! I’ll handle the HTML structures!'), bubble('pixel', 'I’ll bring back the colors!'), bubble('nova', 'And I’ll set the logic trap! Let’s do this!')], 'motions': [motion('zoom_in', duration_ms=500)], 'next_action': 'next'},
        {'order': 6, 'title': 'Battle Mode', 'background_key': 'boss_arena', 'characters_on_screen': [char('narrator', 'center')], 'bubbles': [bubble('narrator', 'SHERO Battle Mode: ACTIVATED!', 'narration')], 'motions': [motion('flash', duration_ms=300), motion('particles', duration_ms=1400)], 'next_action': 'end'},
    ]},
    {'id': 'boss-battle-victory', 'title': 'Internet Restored', 'arc_type': 'mission_outro', 'order': 20, 'description': 'Dr. Glitch is defeated and the internet is restored.', 'scenes': [
        {'order': 1, 'title': 'Beam Hit', 'background_key': 'boss_arena', 'characters_on_screen': [char('dr_glitch', 'center', 'surprised', 'glitch')], 'bubbles': [bubble('narrator', 'The Gravity Beam catches the Glitch-Glider. Dr. Glitch spins wildly!', 'narration')], 'motions': [motion('flash', duration_ms=300), motion('explosion', duration_ms=800), motion('particles', duration_ms=1200)], 'next_action': 'next'},
        {'order': 2, 'title': 'Villain Exit', 'background_key': 'boss_arena', 'characters_on_screen': [char('dr_glitch', 'center', 'angry', 'glitch')], 'bubbles': [bubble('dr_glitch', 'Curse you, Code SHEROs! You haven’t seen the last of me!', 'shout'), bubble('dr_glitch', 'I still haven’t taught you about… ARRAYS! Or DATABASES! I’ll be back!')], 'motions': [motion('glitch_effect', duration_ms=1000)], 'next_action': 'next'},
        {'order': 3, 'title': 'World Heals', 'background_key': 'internet_highway', 'characters_on_screen': [char('narrator', 'center')], 'bubbles': [bubble('narrator', 'The digital world began to heal. Color returned. Websites came back online. The internet was saved.', 'narration')], 'motions': [motion('particles', duration_ms=1600), motion('zoom_out', duration_ms=1000)], 'next_action': 'next'},
        {'order': 4, 'title': 'Crowning', 'background_key': 'shero_hq', 'characters_on_screen': [char('byte', 'left', 'happy'), char('pixel', 'center', 'happy'), char('nova', 'right', 'happy')], 'bubbles': [bubble('narrator', 'INTERNET RESTORED! NEW RANK ACHIEVED: OFFICIAL CODE SHERO.', 'narration'), bubble('byte', 'We did it! We actually did it!'), bubble('pixel', 'The internet is beautiful again!'), bubble('nova', 'And it’s all because we worked together!')], 'motions': [motion('particles', duration_ms=1500)], 'next_action': 'next'},
        {'order': 5, 'title': 'World 2 Hook', 'background_key': 'internet_highway', 'characters_on_screen': [char('byte', 'left', 'thinking'), char('nova', 'center', 'determined'), char('pixel', 'right', 'happy')], 'bubbles': [bubble('byte', 'Wait… I’m picking up a signal from “Creative Island”…'), bubble('byte', 'It looks like Dr. Glitch left more bugs there.'), bubble('nova', 'Ready to go, team?'), bubble('pixel', 'Always!')], 'motions': [], 'next_action': 'end'},
    ]},
    {'id': 'world-1-interlude', 'title': 'Halfway There', 'arc_type': 'interlude', 'order': 21, 'description': 'A midpoint reflection before danger rises.', 'scenes': [
        {'order': 1, 'title': 'Progress Check', 'background_key': 'shero_hq', 'characters_on_screen': [char('byte', 'left', 'happy'), char('pixel', 'center', 'happy'), char('nova', 'right', 'happy')], 'bubbles': [bubble('narrator', 'Halfway through World 1, the SHEROs pause to reflect on their progress.', 'narration'), bubble('byte', 'We restored structure and color.'), bubble('pixel', 'And we helped people find their pages again!')], 'motions': [motion('particles', duration_ms=900)], 'next_action': 'next'},
        {'order': 2, 'title': 'Warning Signal', 'background_key': 'digital_void', 'characters_on_screen': [char('nova', 'center', 'worried'), char('dr_glitch', 'far_right', 'angry', 'glitch')], 'bubbles': [bubble('nova', 'I’m detecting a rising glitch swarm ahead…'), bubble('dr_glitch', 'My Code Bugs are just getting started!', 'shout')], 'motions': [motion('glitch_effect', duration_ms=800)], 'next_action': 'next'},
        {'order': 3, 'title': 'Stay Ready', 'background_key': 'shero_hq', 'characters_on_screen': [char('byte', 'left', 'determined'), char('pixel', 'center', 'determined'), char('nova', 'right', 'determined')], 'bubbles': [bubble('byte', 'Great coders stay calm under pressure.'), bubble('pixel', 'Great creators keep trying!'), bubble('nova', 'Great explorers face the unknown. Let’s keep going, SHERO!')], 'motions': [motion('flash', duration_ms=280)], 'next_action': 'end'},
    ]},
])


class Command(BaseCommand):
    help = 'Seed World 1 story arcs and scenes'

    def handle(self, *args, **options):
        if Character.objects.filter(slug__in=['byte', 'pixel', 'nova']).count() != 3:
            self.stdout.write(self.style.ERROR('Missing characters. Run seed_characters first.'))
            return

        arc_count = 0
        scene_count = 0
        for arc_data in ARCS:
            arc, _ = StoryArc.objects.update_or_create(
                id=arc_data['id'],
                defaults={
                    'title': arc_data['title'],
                    'arc_type': arc_data['arc_type'],
                    'order': arc_data['order'],
                    'is_active': True,
                    'description': arc_data['description'],
                },
            )
            arc_count += 1

            for scene_data in arc_data['scenes']:
                if scene_data['background_key'] not in VALID_BACKGROUNDS:
                    raise ValueError(f"Invalid background_key {scene_data['background_key']} in {arc.id}")

                Scene.objects.update_or_create(
                    arc=arc,
                    order=scene_data['order'],
                    defaults={
                        'title': scene_data['title'],
                        'background_key': scene_data['background_key'],
                        'characters_on_screen': scene_data['characters_on_screen'],
                        'bubbles': scene_data['bubbles'],
                        'motions': scene_data.get('motions', []),
                        'sfx_keys': scene_data.get('sfx_keys', []),
                        'music_key': scene_data.get('music_key', ''),
                        'next_action': scene_data['next_action'],
                        'action_payload': scene_data.get('action_payload', {}),
                    },
                )
                scene_count += 1

            Scene.objects.filter(arc=arc).exclude(order__in=[s['order'] for s in arc_data['scenes']]).delete()

        self.stdout.write(self.style.SUCCESS(f'Seeded {arc_count} arcs and {scene_count} scenes for World 1.'))
