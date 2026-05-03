"""
Trap Music Generator
Generates and plays trap beats with 808 bass, hi-hats, snare and melodies.
"""

import pygame
import numpy as np
import random
import sys
import os

# Audio settings
SAMPLE_RATE = 44100
CHANNELS = 1
BUFFER_SIZE = 512

# UI constants
SCREEN_W, SCREEN_H = 1100, 720
GRID_COLS = 16
STEP_SIZE = 48
GRID_X = 60
GRID_Y = 200
CELL_W = 52
CELL_H = 36
ROW_GAP = 10

# Colors
BG       = (10, 10, 18)
PANEL    = (20, 20, 35)
ACCENT1  = (180, 60, 255)   # purple
ACCENT2  = (0, 220, 150)    # cyan-green
BEAT_ON  = (220, 60, 240)
BEAT_OFF = (35, 35, 55)
PLAYHEAD = (255, 220, 0)
TEXT_COL = (220, 220, 240)
DIM_TEXT = (100, 100, 130)
BTN_ON   = (80, 200, 100)
BTN_OFF  = (60, 60, 90)
BTN_HOV  = (100, 100, 140)

TRACK_NAMES = ["KICK", "808", "SNARE", "CLAP", "HAT-C", "HAT-O", "PERC"]
TRACK_COLORS = [
    (255, 80, 80),    # kick - red
    (180, 60, 255),   # 808 - purple
    (60, 180, 255),   # snare - blue
    (255, 180, 60),   # clap - orange
    (60, 255, 180),   # closed hat - green
    (255, 255, 80),   # open hat - yellow
    (200, 100, 200),  # perc - pink
]

TRAP_SCALES = {
    "Minor": [0, 2, 3, 5, 7, 8, 10],
    "Pentatonic": [0, 3, 5, 7, 10],
    "Diminished": [0, 2, 3, 5, 6, 8, 9, 11],
    "Phrygian": [0, 1, 3, 5, 7, 8, 10],
}

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


# ─────────────── Audio synthesis ───────────────

def make_sine(freq, duration, volume=0.8, fade_out=True):
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    wave = np.sin(2 * np.pi * freq * t) * volume
    if fade_out:
        env = np.exp(-t * (5 / duration))
        wave *= env
    wave = np.clip(wave, -1, 1)
    return (wave * 32767).astype(np.int16)


def make_808(freq=60, duration=0.8, volume=0.9):
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    # pitch envelope: starts higher and drops to freq
    pitch_env = np.exp(-t * 8) * freq * 1.5 + freq
    phase = np.cumsum(2 * np.pi * pitch_env / SAMPLE_RATE)
    wave = np.sin(phase) * volume
    # amplitude envelope
    amp = np.exp(-t * (3.5 / duration))
    wave *= amp
    # add slight harmonic
    wave += np.sin(phase * 2) * 0.15 * amp
    wave = np.tanh(wave * 1.5)  # soft clip for warmth
    wave = np.clip(wave, -1, 1)
    return (wave * 32767).astype(np.int16)


def make_kick(duration=0.4, volume=0.9):
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    # pitch from 180Hz down to 40Hz
    freq = 40 + 140 * np.exp(-t * 25)
    phase = np.cumsum(2 * np.pi * freq / SAMPLE_RATE)
    wave = np.sin(phase) * volume
    amp = np.exp(-t * (9 / duration))
    wave *= amp
    # click transient
    click = np.random.randn(min(n, 400)) * 0.3 * np.exp(-np.arange(min(n, 400)) * 0.02)
    wave[:len(click)] += click
    wave = np.clip(wave, -1, 1)
    return (wave * 32767).astype(np.int16)


def make_snare(duration=0.25, volume=0.8):
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    noise = np.random.randn(n) * 0.5
    tone = np.sin(2 * np.pi * 200 * t) * 0.4
    wave = (noise + tone) * volume
    amp = np.exp(-t * (12 / duration))
    wave *= amp
    wave = np.clip(wave, -1, 1)
    return (wave * 32767).astype(np.int16)


def make_clap(duration=0.18, volume=0.75):
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    # layered noise bursts
    wave = np.zeros(n)
    for offset in [0, 0.003, 0.006]:
        start = int(offset * SAMPLE_RATE)
        end = min(n, start + int(0.05 * SAMPLE_RATE))
        chunk_t = t[start:end] - offset
        burst = np.random.randn(end - start) * np.exp(-chunk_t * 40)
        wave[start:end] += burst
    wave *= volume
    # high-pass character
    wave = np.diff(wave, prepend=wave[0]) * 3 + wave * 0.5
    wave = np.clip(wave, -1, 1)
    return (wave * 32767).astype(np.int16)


def make_hihat_closed(duration=0.06, volume=0.6):
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    noise = np.random.randn(n)
    # bandpass: high freq character
    from numpy.fft import rfft, irfft
    spec = rfft(noise)
    freqs = np.fft.rfftfreq(n, 1 / SAMPLE_RATE)
    spec[freqs < 6000] = 0
    noise = irfft(spec, n)
    amp = np.exp(-t * (35 / duration))
    wave = noise * amp * volume
    wave = np.clip(wave, -1, 1)
    return (wave * 32767).astype(np.int16)


def make_hihat_open(duration=0.22, volume=0.5):
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    noise = np.random.randn(n)
    from numpy.fft import rfft, irfft
    spec = rfft(noise)
    freqs = np.fft.rfftfreq(n, 1 / SAMPLE_RATE)
    spec[freqs < 5000] = 0
    noise = irfft(spec, n)
    amp = np.exp(-t * (5 / duration))
    wave = noise * amp * volume
    wave = np.clip(wave, -1, 1)
    return (wave * 32767).astype(np.int16)


def make_perc(duration=0.12, volume=0.55):
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    freq = 400 + 300 * np.exp(-t * 30)
    wave = np.sin(2 * np.pi * freq * t) * volume
    noise = np.random.randn(n) * 0.25
    wave = (wave + noise) * np.exp(-t * (18 / duration))
    wave = np.clip(wave, -1, 1)
    return (wave * 32767).astype(np.int16)


def make_melody_note(freq, duration, volume=0.5):
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    # sawtooth + sub
    phase = (t * freq) % 1.0
    saw = (2 * phase - 1) * volume
    sub = np.sin(2 * np.pi * freq * 0.5 * t) * volume * 0.4
    wave = saw + sub
    # ADSR-like envelope
    attack = int(0.01 * SAMPLE_RATE)
    release = int(0.15 * SAMPLE_RATE)
    env = np.ones(n)
    env[:attack] = np.linspace(0, 1, attack)
    env[n - release:] = np.linspace(1, 0, release)
    wave *= env
    # lowpass approximation via cumsum smoothing
    wave = np.convolve(wave, np.ones(8) / 8, mode='same')
    wave = np.clip(wave, -1, 1)
    return (wave * 32767).astype(np.int16)


# ─────────────── Pattern generation ───────────────

DEFAULT_PATTERNS = {
    "Trap Classic": {
        0: [1,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],  # kick
        1: [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],  # 808
        2: [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],  # snare
        3: [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,1,0],  # clap
        4: [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,1],  # hat closed
        5: [0,0,0,0, 0,1,0,0, 0,0,0,0, 0,1,0,0],  # hat open
        6: [0,0,0,1, 0,0,0,0, 0,0,1,0, 0,0,0,0],  # perc
    },
    "Hi-Hat Rolls": {
        0: [1,0,0,0, 0,0,1,0, 0,0,0,0, 1,0,0,0],
        1: [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
        2: [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        3: [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,1,0],
        4: [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1],
        5: [0,0,0,0, 0,0,0,0, 0,1,0,0, 0,0,0,0],
        6: [0,0,1,0, 0,0,0,0, 0,0,0,1, 0,0,0,0],
    },
    "Minimalist": {
        0: [1,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
        1: [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
        2: [0,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
        3: [0,0,0,0, 0,0,0,0, 0,0,0,0, 1,0,0,0],
        4: [1,0,1,1, 0,1,1,0, 1,0,1,1, 0,1,1,0],
        5: [0,0,0,0, 1,0,0,0, 0,0,0,0, 0,0,0,0],
        6: [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    },
}


def random_pattern():
    pattern = {}
    # kick: on beats 1, usually also 9
    k = [0] * 16
    k[0] = 1
    if random.random() > 0.4: k[8] = 1
    if random.random() > 0.6: k[random.choice([3,4,5,6,10,11,12,13])] = 1
    pattern[0] = k

    # 808: sparse, after kick sometimes
    b = [0] * 16
    for i in range(16):
        if k[i] and random.random() > 0.5:
            b[i] = 1
        elif random.random() > 0.85:
            b[i] = 1
    pattern[1] = b

    # snare: beats 4, 12 (trap 2&4 in 16ths)
    s = [0] * 16
    if random.random() > 0.2: s[4] = 1
    if random.random() > 0.2: s[12] = 1
    if random.random() > 0.6: s[random.choice([6,7,14,15])] = 1
    pattern[2] = s

    # clap
    c = [0] * 16
    c[4] = 1 if random.random() > 0.3 else 0
    c[12] = 1 if random.random() > 0.3 else 0
    if random.random() > 0.5: c[random.choice([2,6,10,14])] = 1
    pattern[3] = c

    # hi-hat closed: varies from sparse to dense
    h = [0] * 16
    density = random.choice([0.4, 0.6, 0.8, 1.0])
    for i in range(16):
        h[i] = 1 if random.random() < density else 0
    pattern[4] = h

    # hi-hat open: sparse
    ho = [0] * 16
    for i in range(16):
        if random.random() > 0.85:
            ho[i] = 1
            h[i] = 0  # avoid clash
    pattern[5] = ho

    # perc
    p = [0] * 16
    for i in range(16):
        p[i] = 1 if random.random() > 0.8 else 0
    pattern[6] = p

    return pattern


def generate_melody(scale_name, root_note, n_steps=16, octave=4):
    scale = TRAP_SCALES[scale_name]
    notes = []
    prev = None
    for i in range(n_steps):
        if random.random() > 0.35:
            if prev is not None and random.random() > 0.4:
                # move by step
                idx = scale.index(prev % 12) if (prev % 12) in scale else 0
                step = random.choice([-1, 0, 1])
                idx = max(0, min(len(scale) - 1, idx + step))
                note = root_note + scale[idx] + octave * 12
            else:
                note = root_note + random.choice(scale) + octave * 12
            notes.append(note)
            prev = note
        else:
            notes.append(None)  # rest
    return notes


def midi_to_freq(midi_note):
    return 440.0 * (2 ** ((midi_note - 69) / 12.0))


# ─────────────── Sound bank ───────────────

class SoundBank:
    def __init__(self):
        self.sounds = {}
        self._build()

    def _build(self):
        self.sounds["kick"]  = self._to_sound(make_kick())
        self.sounds["808"]   = {}
        self.sounds["snare"] = self._to_sound(make_snare())
        self.sounds["clap"]  = self._to_sound(make_clap())
        self.sounds["hat_c"] = self._to_sound(make_hihat_closed())
        self.sounds["hat_o"] = self._to_sound(make_hihat_open())
        self.sounds["perc"]  = self._to_sound(make_perc())
        # pre-render 808 notes for common MIDI range
        for midi in range(30, 70):
            freq = midi_to_freq(midi)
            self.sounds["808"][midi] = self._to_sound(make_808(freq))
        # melody notes
        self.sounds["melody"] = {}
        for midi in range(48, 85):
            freq = midi_to_freq(midi)
            self.sounds["melody"][midi] = self._to_sound(make_melody_note(freq, 0.3))

    @staticmethod
    def _to_sound(arr):
        stereo = np.column_stack([arr, arr])
        return pygame.sndarray.make_sound(stereo)

    def play(self, name, midi=None, channel=None):
        if name in ("808", "melody"):
            key = midi if midi is not None else 48
            key = max(30, min(84, key))
            snd = self.sounds[name].get(key)
        else:
            snd = self.sounds.get(name)
        if snd:
            if channel is not None:
                ch = pygame.mixer.Channel(channel)
                ch.play(snd)
            else:
                snd.play()


# ─────────────── UI helpers ───────────────

def draw_rounded_rect(surf, color, rect, r=8):
    pygame.draw.rect(surf, color, rect, border_radius=r)


def draw_text(surf, text, x, y, font, color=TEXT_COL, center=False):
    img = font.render(text, True, color)
    if center:
        x -= img.get_width() // 2
    surf.blit(img, (x, y))


class Button:
    def __init__(self, rect, label, color_on=BTN_ON, color_off=BTN_OFF):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.color_on = color_on
        self.color_off = color_off
        self.active = False
        self.hovered = False

    def draw(self, surf, font):
        color = self.color_on if self.active else (BTN_HOV if self.hovered else self.color_off)
        draw_rounded_rect(surf, color, self.rect, 6)
        text_col = (0, 0, 0) if self.active else TEXT_COL
        draw_text(surf, self.label, self.rect.centerx, self.rect.centery - 7, font, text_col, center=True)

    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            return True
        return False


# ─────────────── Main App ───────────────

class TrapMusicGenerator:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=BUFFER_SIZE)
        pygame.mixer.set_num_channels(32)

        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("TRAP MUSIC GENERATOR")
        self.clock = pygame.time.Clock()

        self.font_lg = pygame.font.SysFont("monospace", 22, bold=True)
        self.font_md = pygame.font.SysFont("monospace", 15, bold=True)
        self.font_sm = pygame.font.SysFont("monospace", 11)

        self.bpm = 140
        self.playing = False
        self.step = 0
        self.step_timer = 0.0
        self.melody_on = True
        self.current_pattern_name = "Trap Classic"
        self.scale_name = "Minor"
        self.root_note = 0  # C
        self.pattern = {i: list(DEFAULT_PATTERNS["Trap Classic"][i]) for i in range(7)}
        self.melody_notes = generate_melody(self.scale_name, self.root_note)
        self.melody_octave = 4

        self.bank = SoundBank()

        # build 808 note for each step (can differ)
        self._regen_808_notes()

        self._build_ui()

    def _regen_808_notes(self):
        scale = TRAP_SCALES[self.scale_name]
        self.bass_notes = []
        for i in range(16):
            midi = self.root_note + random.choice(scale) + 36  # low octave
            self.bass_notes.append(midi)

    def _build_ui(self):
        self.buttons = {}

        # Play / Stop
        self.buttons["play"] = Button((GRID_X, 20, 120, 40), "PLAY", BTN_ON, BTN_OFF)
        self.buttons["stop"] = Button((GRID_X + 130, 20, 120, 40), "STOP", (200, 80, 80), BTN_OFF)
        self.buttons["random"] = Button((GRID_X + 280, 20, 140, 40), "RANDOM BEAT", (100, 60, 200), BTN_OFF)
        self.buttons["melody"] = Button((GRID_X + 440, 20, 160, 40), "MELODY: ON", BTN_ON, BTN_OFF)
        self.buttons["melody"].active = True
        self.buttons["regen_mel"] = Button((GRID_X + 620, 20, 160, 40), "NEW MELODY", (60, 140, 200), BTN_OFF)

        # BPM
        self.bpm_minus = Button((SCREEN_W - 260, 20, 40, 40), "-", (80, 80, 120), BTN_OFF)
        self.bpm_plus  = Button((SCREEN_W - 100, 20, 40, 40), "+", (80, 80, 120), BTN_OFF)

        # Pattern select
        y = 80
        x = GRID_X
        self.pattern_btns = {}
        for name in DEFAULT_PATTERNS:
            btn = Button((x, y, 160, 30), name, (80, 60, 150), BTN_OFF)
            if name == self.current_pattern_name:
                btn.active = True
            self.pattern_btns[name] = btn
            x += 170

        # Scale select
        x = GRID_X
        self.scale_btns = {}
        for name in TRAP_SCALES:
            btn = Button((x, y + 40, 140, 28), name, (50, 120, 80), BTN_OFF)
            if name == self.scale_name:
                btn.active = True
            self.scale_btns[name] = btn
            x += 150

        # Root note
        x = GRID_X + 640
        self.root_minus = Button((x, y + 40, 30, 28), "<", BTN_OFF, BTN_OFF)
        self.root_plus  = Button((x + 110, y + 40, 30, 28), ">", BTN_OFF, BTN_OFF)

    def step_duration(self):
        # duration of one 16th note in seconds
        return 60.0 / (self.bpm * 4)

    def toggle_cell(self, mx, my):
        for row in range(len(TRACK_NAMES)):
            ry = GRID_Y + row * (CELL_H + ROW_GAP)
            for col in range(GRID_COLS):
                rx = GRID_X + col * (CELL_W + 4)
                rect = pygame.Rect(rx, ry, CELL_W, CELL_H)
                if rect.collidepoint(mx, my):
                    self.pattern[row][col] ^= 1
                    return

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._toggle_play()
                if event.key == pygame.K_r:
                    self._random_beat()
                if event.key == pygame.K_UP:
                    self.bpm = min(200, self.bpm + 5)
                if event.key == pygame.K_DOWN:
                    self.bpm = max(60, self.bpm - 5)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                self.toggle_cell(mx, my)
                # buttons
                if self.buttons["play"].handle_click((mx, my)):
                    self._toggle_play()
                if self.buttons["stop"].handle_click((mx, my)):
                    self.playing = False
                    self.step = 0
                if self.buttons["random"].handle_click((mx, my)):
                    self._random_beat()
                if self.buttons["melody"].handle_click((mx, my)):
                    self.melody_on = not self.melody_on
                    self.buttons["melody"].active = self.melody_on
                    self.buttons["melody"].label = "MELODY: ON" if self.melody_on else "MELODY: OFF"
                if self.buttons["regen_mel"].handle_click((mx, my)):
                    self.melody_notes = generate_melody(self.scale_name, self.root_note, octave=self.melody_octave)
                if self.bpm_minus.handle_click((mx, my)):
                    self.bpm = max(60, self.bpm - 5)
                if self.bpm_plus.handle_click((mx, my)):
                    self.bpm = min(200, self.bpm + 5)
                if self.root_minus.handle_click((mx, my)):
                    self.root_note = (self.root_note - 1) % 12
                    self._regen_808_notes()
                    self.melody_notes = generate_melody(self.scale_name, self.root_note, octave=self.melody_octave)
                if self.root_plus.handle_click((mx, my)):
                    self.root_note = (self.root_note + 1) % 12
                    self._regen_808_notes()
                    self.melody_notes = generate_melody(self.scale_name, self.root_note, octave=self.melody_octave)
                for name, btn in self.pattern_btns.items():
                    if btn.handle_click((mx, my)):
                        self._load_pattern(name)
                for name, btn in self.scale_btns.items():
                    if btn.handle_click((mx, my)):
                        self._set_scale(name)
        return True

    def _toggle_play(self):
        self.playing = not self.playing
        self.buttons["play"].active = self.playing
        if not self.playing:
            self.step = 0

    def _random_beat(self):
        self.pattern = random_pattern()
        self._regen_808_notes()
        self.melody_notes = generate_melody(self.scale_name, self.root_note, octave=self.melody_octave)
        for btn in self.pattern_btns.values():
            btn.active = False

    def _load_pattern(self, name):
        src = DEFAULT_PATTERNS[name]
        self.pattern = {i: list(src[i]) for i in range(7)}
        self.current_pattern_name = name
        for n, btn in self.pattern_btns.items():
            btn.active = (n == name)
        self._regen_808_notes()

    def _set_scale(self, name):
        self.scale_name = name
        for n, btn in self.scale_btns.items():
            btn.active = (n == name)
        self.melody_notes = generate_melody(self.scale_name, self.root_note, octave=self.melody_octave)
        self._regen_808_notes()

    def update(self, dt):
        if not self.playing:
            return
        self.step_timer += dt
        dur = self.step_duration()
        if self.step_timer >= dur:
            self.step_timer -= dur
            self._fire_step(self.step)
            self.step = (self.step + 1) % GRID_COLS

    def _fire_step(self, s):
        track_map = {0: "kick", 1: "808", 2: "snare", 3: "clap", 4: "hat_c", 5: "hat_o", 6: "perc"}
        for row, name in track_map.items():
            if self.pattern[row][s]:
                if name == "808":
                    self.bank.play("808", midi=self.bass_notes[s], channel=row)
                else:
                    self.bank.play(name, channel=row)
        # melody
        if self.melody_on and s < len(self.melody_notes):
            note = self.melody_notes[s]
            if note is not None:
                self.bank.play("melody", midi=note, channel=16)

    def draw(self):
        self.screen.fill(BG)
        self._draw_header()
        self._draw_controls()
        self._draw_grid()
        self._draw_melody_row()
        self._draw_footer()
        pygame.display.flip()

    def _draw_header(self):
        title = "TRAP MUSIC GENERATOR"
        draw_text(self.screen, title, SCREEN_W // 2, 8, self.font_lg, ACCENT1, center=True)
        # BPM display
        bpm_x = SCREEN_W - 210
        draw_text(self.screen, "BPM", bpm_x, 10, self.font_sm, DIM_TEXT)
        draw_text(self.screen, str(self.bpm), bpm_x, 28, self.font_lg, ACCENT2)
        self.bpm_minus.draw(self.screen, self.font_md)
        self.bpm_plus.draw(self.screen, self.font_md)

        for btn in self.buttons.values():
            btn.draw(self.screen, self.font_md)

    def _draw_controls(self):
        y = 80
        # Pattern label
        draw_text(self.screen, "PATTERN:", GRID_X - 5, y + 6, self.font_sm, DIM_TEXT)
        x_offset = 70
        for name, btn in self.pattern_btns.items():
            btn.rect.x = GRID_X + x_offset
            btn.rect.y = y
            btn.draw(self.screen, self.font_sm)
            x_offset += 170

        # Scale label
        draw_text(self.screen, "SCALE:", GRID_X - 5, y + 47, self.font_sm, DIM_TEXT)
        x_offset = 60
        for name, btn in self.scale_btns.items():
            btn.rect.x = GRID_X + x_offset
            btn.rect.y = y + 40
            btn.draw(self.screen, self.font_sm)
            x_offset += 150

        # Root note
        rx = GRID_X + 660
        ry = y + 40
        self.root_minus.rect.x = rx
        self.root_minus.rect.y = ry
        self.root_plus.rect.x = rx + 80
        self.root_plus.rect.y = ry
        self.root_minus.draw(self.screen, self.font_md)
        self.root_plus.draw(self.screen, self.font_md)
        draw_text(self.screen, "KEY", rx - 5, ry - 16, self.font_sm, DIM_TEXT)
        draw_text(self.screen, NOTE_NAMES[self.root_note % 12], rx + 35, ry + 4, self.font_md, ACCENT2, center=True)

    def _draw_grid(self):
        for row in range(len(TRACK_NAMES)):
            ry = GRID_Y + row * (CELL_H + ROW_GAP)
            color = TRACK_COLORS[row]

            # Track label
            draw_text(self.screen, TRACK_NAMES[row], GRID_X - 58, ry + 10, self.font_sm, color)

            for col in range(GRID_COLS):
                rx = GRID_X + col * (CELL_W + 4)
                rect = pygame.Rect(rx, ry, CELL_W, CELL_H)

                # beat group shading
                group = col // 4
                shade = 8 if group % 2 == 0 else 0
                base_off = (BEAT_OFF[0] + shade, BEAT_OFF[1] + shade, BEAT_OFF[2] + shade + 10)

                if self.pattern[row][col]:
                    pygame.draw.rect(self.screen, color, rect, border_radius=5)
                    # bright inner
                    inner = rect.inflate(-6, -6)
                    bright = tuple(min(255, c + 60) for c in color)
                    pygame.draw.rect(self.screen, bright, inner, border_radius=3)
                else:
                    pygame.draw.rect(self.screen, base_off, rect, border_radius=5)

                # playhead
                if self.playing and col == self.step:
                    pygame.draw.rect(self.screen, PLAYHEAD, rect, 2, border_radius=5)

                # bar lines every 4
                if col % 4 == 0 and col > 0:
                    pygame.draw.line(self.screen, (50, 50, 80),
                                     (rx - 2, GRID_Y - 5),
                                     (rx - 2, GRID_Y + len(TRACK_NAMES) * (CELL_H + ROW_GAP) - ROW_GAP + 5))

    def _draw_melody_row(self):
        mel_y = GRID_Y + len(TRACK_NAMES) * (CELL_H + ROW_GAP) + 10
        draw_text(self.screen, "MELODY", GRID_X - 58, mel_y + 10, self.font_sm, ACCENT1)
        for i, note in enumerate(self.melody_notes):
            rx = GRID_X + i * (CELL_W + 4)
            rect = pygame.Rect(rx, mel_y, CELL_W, CELL_H)
            if note is not None:
                pygame.draw.rect(self.screen, ACCENT1, rect, border_radius=5)
                name = NOTE_NAMES[note % 12]
                draw_text(self.screen, name, rect.centerx, rect.y + 10, self.font_sm, (0, 0, 0), center=True)
            else:
                pygame.draw.rect(self.screen, BEAT_OFF, rect, border_radius=5)
            if self.playing and i == self.step:
                pygame.draw.rect(self.screen, PLAYHEAD, rect, 2, border_radius=5)

    def _draw_footer(self):
        y = SCREEN_H - 35
        hints = [
            "SPACE: play/stop",
            "R: random beat",
            "↑↓: BPM",
            "Click grid: toggle step",
        ]
        x = GRID_X
        for h in hints:
            draw_text(self.screen, h, x, y, self.font_sm, DIM_TEXT)
            x += 220

        # status
        status = "► PLAYING" if self.playing else "■ STOPPED"
        col = ACCENT2 if self.playing else (150, 80, 80)
        draw_text(self.screen, status, SCREEN_W - 160, y, self.font_md, col)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            running = self.handle_events()
            # hover
            mx, my = pygame.mouse.get_pos()
            for btn in self.buttons.values():
                btn.update_hover((mx, my))
            for btn in self.pattern_btns.values():
                btn.update_hover((mx, my))
            for btn in self.scale_btns.values():
                btn.update_hover((mx, my))
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = TrapMusicGenerator()
    app.run()
