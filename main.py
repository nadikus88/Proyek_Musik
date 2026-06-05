import pygame
import os
import math
import random
from mutagen.mp3 import MP3

# 1. INISIALISASI
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 450, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Premium Player 2026 - All Features Unlocked")

# 2. PALET WARNA
BG_BLACK = (14, 15, 20)
CARD_BG = (24, 26, 36)
NEON_PURPLE = (157, 78, 221)
NEON_BLUE = (0, 180, 216)
WHITE = (248, 249, 250)
GRAY_TEXT = (130, 134, 150)
DARK_GRAY = (40, 44, 58)

FONT_NAME = pygame.font.get_default_font()
font_title = pygame.font.Font(FONT_NAME, 24)
font_subtitle = pygame.font.Font(FONT_NAME, 16)
font_small = pygame.font.Font(FONT_NAME, 13)

# 3. DIRECTORY SETUP
MUSIC_DIR = "musik"
COVER_DIR = "cover"
for f in [MUSIC_DIR, COVER_DIR]:
    if not os.path.exists(f): os.makedirs(f)

playlist = [file for file in os.listdir(MUSIC_DIR) if file.endswith('.mp3')]

if not playlist:
    playlist = ["Asmalibrasi.mp3", "Fill My Sunshine.mp3", "See You Again.mp3"]
    USING_DUMMY = True
else:
    USING_DUMMY = False

# 4. PLAYER STATE VARIABLES
VIEW_HOME = 0
VIEW_PLAYER = 1
current_view = VIEW_HOME

current_index = 0
is_playing = False
is_paused = False
is_shuffle = False
is_repeat = 0 # 0: Off, 1: Repeat All, 2: Repeat One
volume = 0.7
pygame.mixer.music.set_volume(volume)

song_total_length = 240 
current_pos_seconds = 0

# 5. CORE FUNCTIONS & VEKTOR IKON
def get_circular_cover(song_name, size):
    base_name = os.path.splitext(song_name)[0]
    cover_path = os.path.join(COVER_DIR, f"{base_name}.png")
    default_path = os.path.join(COVER_DIR, "default.png")
    path = cover_path if os.path.exists(cover_path) else default_path
    
    try:
        img = pygame.image.load(path).convert_alpha()
    except:
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        img.fill(CARD_BG)
        pygame.draw.circle(img, NEON_PURPLE, (size//2, size//2), size//2 - 4, 4)
        return img
        
    img = pygame.transform.smoothscale(img, (size, size))
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (size // 2, size // 2), size // 2)
    
    circular_img = pygame.Surface((size, size), pygame.SRCALPHA)
    circular_img.blit(img, (0, 0))
    circular_img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return circular_img

def format_time(seconds):
    return f"{seconds // 60:02d}:{seconds % 60:02d}"

def play_song(index):
    global current_index, is_playing, is_paused, song_total_length, current_pos_seconds
    current_index = index
    current_pos_seconds = 0
    song_name = playlist[current_index]
    
    if not USING_DUMMY:
        try:
            audio = MP3(os.path.join(MUSIC_DIR, song_name))
            song_total_length = int(audio.info.length)
            pygame.mixer.music.load(os.path.join(MUSIC_DIR, song_name))
            pygame.mixer.music.play()
            is_playing = True
            is_paused = False
        except:
            song_total_length = 180
    else:
        song_total_length = 255
        is_playing = True
        is_paused = False

def handle_auto_next():
    if is_repeat == 2:
        play_song(current_index)
    elif is_shuffle:
        play_song(random.randint(0, len(playlist) - 1))
    else:
        play_song((current_index + 1) % len(playlist))

# --- FUNGSI MENGGAMBAR IKON GEOMETRI ---
def draw_shuffle_icon(surface, color, cx, cy, size):
    """Menggambar dua panah bersilang (Shuffle)"""
    w = size // 2
    h = size // 3
    # Jalur Atas ke Bawah
    pygame.draw.line(surface, color, (cx - w, cy - h), (cx - w//3, cy - h), 2)
    pygame.draw.line(surface, color, (cx - w//3, cy - h), (cx + w//3, cy + h), 2)
    pygame.draw.line(surface, color, (cx + w//3, cy + h), (cx + w, cy + h), 2)
    # Jalur Bawah ke Atas
    pygame.draw.line(surface, color, (cx - w, cy + h), (cx - w//3, cy + h), 2)
    pygame.draw.line(surface, color, (cx - w//3, cy + h), (cx + w//3, cy - h), 2)
    pygame.draw.line(surface, color, (cx + w//3, cy - h), (cx + w, cy - h), 2)
    # Kepala Panah Atas
    pygame.draw.polygon(surface, color, [(cx + w, cy - h - 4), (cx + w, cy - h + 4), (cx + w + 5, cy - h)])
    # Kepala Panah Bawah
    pygame.draw.polygon(surface, color, [(cx + w, cy + h - 4), (cx + w, cy + h + 4), (cx + w + 5, cy + h)])

def draw_repeat_icon(surface, color, cx, cy, size, repeat_mode):
    """Menggambar panah melingkar persegi panjang (Repeat)"""
    w = size // 2
    h = size // 3
    # Menggambar bodi jalur memutar
    pygame.draw.lines(surface, color, False, [
        (cx - w + 4, cy), (cx - w, cy), (cx - w, cy - h), 
        (cx + w, cy - h), (cx + w, cy + h), (cx - w, cy + h), (cx - w, cy + 2)
    ], 2)
    # Kepala panah
    pygame.draw.polygon(surface, color, [(cx - w - 4, cy + 3), (cx - w + 4, cy + 3), (cx - w, cy - 2)])
    
    # Jika mode Repeat One, munculkan angka 1 kecil di tengahnya
    if repeat_mode == 2:
        txt = font_small.render("1", True, color)
        surface.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))

def draw_play_icon(surface, color, center_x, center_y, size, playing):
    if not playing:
        points = [(center_x - size//3, center_y - size//2), (center_x - size//3, center_y + size//2), (center_x + size//2, center_y)]
        pygame.draw.polygon(surface, color, points)
    else:
        w = size // 4
        pygame.draw.rect(surface, color, (center_x - w - w//2, center_y - size//2, w, size))
        pygame.draw.rect(surface, color, (center_x + w//2, center_y - size//2, w, size))

def draw_next_icon(surface, color, x, y, size, flip=False):
    d = 1 if not flip else -1
    p1 = [(x - d*(size//3), y - size//2), (x - d*(size//3), y + size//2), (x + d*(size//2), y)]
    pygame.draw.polygon(surface, color, p1)
    if not flip:
        pygame.draw.rect(surface, color, (x + size//2 + 2, y - size//2, 4, size))
    else:
        pygame.draw.rect(surface, color, (x - size//2 - 6, y - size//2, 4, size))

# 6. APP MAIN LOOP
running = True
clock = pygame.time.Clock()
CUSTOM_TIMER = pygame.USEREVENT + 1
pygame.time.set_timer(CUSTOM_TIMER, 1000)

while running:
    screen.fill(BG_BLACK)
    mouse_pos = pygame.mouse.get_pos()
    
    # -------------------------------------------------------------
    # TAMPILAN 1: HOME SCREEN
    # -------------------------------------------------------------
    if current_view == VIEW_HOME:
        lbl = font_subtitle.render("2026 Premium Music Player", True, WHITE)
        screen.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, 40))
        
        # Penentuan warna aktif/tidak
        s_color = NEON_BLUE if is_shuffle else GRAY_TEXT
        r_color = NEON_PURPLE if is_repeat > 0 else GRAY_TEXT
        
        shuffle_center = (150, 120)
        repeat_center = (300, 120)
        
        # Render Lingkaran Shuffle
        pygame.draw.circle(screen, CARD_BG, shuffle_center, 28)
        pygame.draw.circle(screen, s_color, shuffle_center, 26, 2)
        draw_shuffle_icon(screen, s_color, shuffle_center[0], shuffle_center[1], 20)
        txt_s = font_small.render("Shuffle", True, s_color)
        screen.blit(txt_s, (shuffle_center[0] - txt_s.get_width() // 2, shuffle_center[1] + 38))
        
        # Render Lingkaran Repeat
        pygame.draw.circle(screen, CARD_BG, repeat_center, 28)
        pygame.draw.circle(screen, r_color, repeat_center, 26, 2)
        draw_repeat_icon(screen, r_color, repeat_center[0], repeat_center[1], 20, is_repeat)
        
        lbl_rep = "Repeat 1" if is_repeat == 2 else "Repeat All" if is_repeat == 1 else "Repeat"
        txt_r = font_small.render(lbl_rep, True, r_color)
        screen.blit(txt_r, (repeat_center[0] - txt_r.get_width() // 2, repeat_center[1] + 38))

        # List Musik
        lbl_recent = font_subtitle.render("Daftar Lagu Kamu", True, WHITE)
        screen.blit(lbl_recent, (30, 220))
        
        song_cards = []
        for i, name in enumerate(playlist):
            y_pos = 260 + (i * 85)
            if y_pos > HEIGHT - 110: break
            
            card_rect = pygame.Rect(30, y_pos, WIDTH - 60, 70)
            song_cards.append((card_rect, i))
            
            b_color = DARK_GRAY if card_rect.collidepoint(mouse_pos) else CARD_BG
            pygame.draw.rect(screen, b_color, card_rect, border_radius=14)
            
            thumb = get_circular_cover(name, 50)
            screen.blit(thumb, (45, y_pos + 10))
            
            clean_name = name.replace(".mp3", "")
            title_t = font_subtitle.render(clean_name[:24] + "..." if len(clean_name) > 24 else clean_name, True, WHITE)
            screen.blit(title_t, (110, y_pos + 16))
            
            sub_text = "Sedang diputar" if current_index == i and is_playing else "Klik untuk memutar"
            sub_t = font_small.render(sub_text, True, NEON_BLUE if current_index == i else GRAY_TEXT)
            screen.blit(sub_t, (110, y_pos + 40))

        # Bottom Bar
        bottom_bar = pygame.Rect(0, HEIGHT - 85, WIDTH, 85)
        pygame.draw.rect(screen, CARD_BG, bottom_bar)
        pygame.draw.line(screen, NEON_PURPLE, (0, HEIGHT - 85), (WIDTH, HEIGHT - 85), 2)
        
        active_title = playlist[current_index].replace(".mp3", "")
        mini_lbl = font_small.render(f"Memutar: {active_title[:22]}", True, WHITE)
        screen.blit(mini_lbl, (25, HEIGHT - 52))
        
        open_btn = pygame.Rect(WIDTH - 140, HEIGHT - 58, 110, 32)
        pygame.draw.rect(screen, NEON_PURPLE, open_btn, border_radius=8)
        open_txt = font_small.render("BUKA PLAYER", True, WHITE)
        screen.blit(open_txt, (open_btn.centerx - open_txt.get_width() // 2, open_btn.centery - open_txt.get_height() // 2))

    # -------------------------------------------------------------
    # TAMPILAN 2: PREMIUM PLAYER SCREEN
    # -------------------------------------------------------------
    elif current_view == VIEW_PLAYER:
        back_btn = pygame.Rect(25, 40, 40, 40)
        if back_btn.collidepoint(mouse_pos):
            pygame.draw.circle(screen, CARD_BG, back_btn.center, 20)
        pygame.draw.polygon(screen, WHITE, [(45, 60), (55, 50), (55, 70)])
        pygame.draw.rect(screen, WHITE, (53, 57, 10, 6))
        
        pygame.draw.circle(screen, (34, 23, 48), (WIDTH // 2, 270), 142)
        pygame.draw.circle(screen, NEON_PURPLE, (WIDTH // 2, 270), 132, 3)
        
        large_cover = get_circular_cover(playlist[current_index], 250)
        screen.blit(large_cover, (WIDTH // 2 - 125, 145))
        
        song_name = playlist[current_index].replace(".mp3", "")
        title_surf = font_title.render(song_name[:22] + "..." if len(song_name) > 22 else song_name, True, WHITE)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 440))
        
        artist_text = "Premium Local Stream"
        if is_shuffle: artist_text += " • Shuffle"
        if is_repeat == 1: artist_text += " • Loop All"
        elif is_repeat == 2: artist_text += " • Loop 1"
        
        artist_surf = font_subtitle.render(artist_text, True, NEON_BLUE)
        screen.blit(artist_surf, (WIDTH // 2 - artist_surf.get_width() // 2, 480))
        
        # Progress Timeline
        track_y = 550
        track_start_x = 40
        track_width = WIDTH - 80
        
        progress_ratio = current_pos_seconds / max(1, song_total_length)
        current_slider_x = track_start_x + int(track_width * progress_ratio)
        
        track_rect_area = pygame.Rect(track_start_x, track_y - 12, track_width, 24)
        pygame.draw.line(screen, DARK_GRAY, (track_start_x, track_y), (track_start_x + track_width, track_y), 4)
        pygame.draw.line(screen, NEON_PURPLE, (track_start_x, track_y), (current_slider_x, track_y), 6)
        pygame.draw.circle(screen, WHITE, (current_slider_x, track_y), 7)
        
        screen.blit(font_small.render(format_time(current_pos_seconds), True, GRAY_TEXT), (40, track_y + 14))
        screen.blit(font_small.render(format_time(song_total_length), True, GRAY_TEXT), (WIDTH - 40 - font_small.size(format_time(song_total_length))[0], track_y + 14))
        
        # Volume Bar
        vol_x, vol_y, vol_w, vol_h = WIDTH - 30, 160, 6, 120
        vol_rect_area = pygame.Rect(vol_x - 10, vol_y, 25, vol_h)
        pygame.draw.rect(screen, DARK_GRAY, (vol_x, vol_y, vol_w, vol_h), border_radius=3)
        current_vol_h = int(vol_h * volume)
        pygame.draw.rect(screen, NEON_BLUE, (vol_x, vol_y + (vol_h - current_vol_h), vol_w, current_vol_h), border_radius=3)
        pygame.draw.circle(screen, WHITE, (vol_x + 3, vol_y + (vol_h - current_vol_h)), 6)
        
        # Tombol Kontrol
        prev_rect = pygame.Rect(WIDTH // 2 - 100, 620, 40, 40)
        p_color = NEON_BLUE if prev_rect.collidepoint(mouse_pos) else WHITE
        draw_next_icon(screen, p_color, prev_rect.centerx, prev_rect.centery, 18, flip=True)
        
        play_center = (WIDTH // 2, 640)
        dist_play = math.hypot(mouse_pos[0] - play_center[0], mouse_pos[1] - play_center[1])
        p_radius = 34 if dist_play > 32 else 37
        pygame.draw.circle(screen, WHITE, play_center, p_radius)
        
        is_active_playing = is_playing and not is_paused
        draw_play_icon(screen, BG_BLACK, play_center[0], play_center[1], 20, is_active_playing)
        
        next_rect = pygame.Rect(WIDTH // 2 + 60, 620, 40, 40)
        n_color = NEON_BLUE if next_rect.collidepoint(mouse_pos) else WHITE
        draw_next_icon(screen, n_color, next_rect.centerx, next_rect.centery, 18, flip=False)

    # -------------------------------------------------------------
    # 7. EVENT HANDLING
    # -------------------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == CUSTOM_TIMER:
            if is_playing and not is_paused:
                current_pos_seconds += 1
                if current_pos_seconds >= song_total_length:
                    handle_auto_next()
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if current_view == VIEW_HOME:
                    # Deteksi Klik Menu Shuffle
                    if math.hypot(event.pos[0] - shuffle_center[0], event.pos[1] - shuffle_center[1]) < 28:
                        is_shuffle = not is_shuffle
                    # Deteksi Klik Menu Repeat
                    if math.hypot(event.pos[0] - repeat_center[0], event.pos[1] - repeat_center[1]) < 28:
                        is_repeat = (is_repeat + 1) % 3
                        
                    for card_rect, index in song_cards:
                        if card_rect.collidepoint(event.pos):
                            play_song(index)
                            current_view = VIEW_PLAYER
                    if open_btn.collidepoint(event.pos):
                        current_view = VIEW_PLAYER
                        
                elif current_view == VIEW_PLAYER:
                    if back_btn.collidepoint(event.pos):
                        current_view = VIEW_HOME
                        
                    if math.hypot(event.pos[0] - play_center[0], event.pos[1] - play_center[1]) < 35:
                        if is_playing:
                            if is_paused: pygame.mixer.music.unpause(); is_paused = False
                            else: pygame.mixer.music.pause(); is_paused = True
                        else:
                            play_song(current_index)
                            
                    if next_rect.collidepoint(event.pos):
                        play_song((current_index + 1) % len(playlist))
                    if prev_rect.collidepoint(event.pos):
                        play_song((current_index - 1) % len(playlist))
                        
                    if track_rect_area.collidepoint(event.pos):
                        clicked_x = event.pos[0] - track_start_x
                        new_ratio = clicked_x / track_width
                        new_ratio = max(0.0, min(1.0, new_ratio))
                        current_pos_seconds = int(new_ratio * song_total_length)
                        if not USING_DUMMY and is_playing:
                            pygame.mixer.music.set_pos(current_pos_seconds)
                            
                    if vol_rect_area.collidepoint(event.pos):
                        clicked_y = event.pos[1] - vol_y
                        vol_ratio = 1.0 - (clicked_y / vol_h)
                        volume = max(0.0, min(1.0, vol_ratio))
                        pygame.mixer.music.set_volume(volume)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()