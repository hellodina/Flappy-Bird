#!/usr/bin/env python3
"""
Flappy Bird Style Game
A fun, forgiving Flappy Bird clone built with Pygame
"""

import pygame
import json
import sys
import os
import random

# ============================================================================
# INITIALIZATION & SETUP
# ============================================================================

pygame.init()
pygame.mixer.init()

# ============================================================================
# CONFIGURATION LOADING
# ============================================================================

def load_config():
    """Load game configuration from config.json with safe defaults"""
    default_config = {
        "screen_width": 800,
        "screen_height": 600,
        "player_gravity": 0.25,
        "flap_strength": -6.5,
        "obstacle_speed": 4,
        "wall_gap": 170,
        "enemy_speed": 3
    }
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, 'r') as f:
            loaded_config = json.load(f)
            # Merge with defaults, preferring loaded values
            default_config.update(loaded_config)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load config.json, using defaults: {e}")
    
    return default_config

# Load configuration
config = load_config()

# Extract configuration values
SCREEN_WIDTH = config.get("screen_width", 800)
SCREEN_HEIGHT = config.get("screen_height", 600)
GRAVITY = config.get("player_gravity", 0.25)
FLAP_STRENGTH = config.get("flap_strength", -6.5)
OBSTACLE_SPEED = config.get("obstacle_speed", 4)
WALL_GAP = config.get("wall_gap", 170)
ENEMY_SPEED = config.get("enemy_speed", 3)

# Game constants
FPS = 60
GROUND_HEIGHT = 100
PLAYER_SIZE = 50
OBSTACLE_WIDTH = 80
OBSTACLE_SPAWN_INTERVAL = 90  # Frames between obstacles
ENEMY_SPAWN_INTERVAL = 180  # Frames between enemies

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)

# ============================================================================
# ASSET LOADING
# ============================================================================

def load_and_scale_image(filename, size):
    """Load an image from assets folder and scale it to the specified size"""
    try:
        asset_path = os.path.join(os.path.dirname(__file__), "assets", filename)
        image = pygame.image.load(asset_path)
        return pygame.transform.scale(image, size)
    except (FileNotFoundError, pygame.error) as e:
        print(f"Warning: Could not load {filename}: {e}")
        # Return a colored surface as fallback
        surf = pygame.Surface(size)
        surf.fill((255, 0, 255))  # Magenta for missing textures
        return surf

def load_sound(filename):
    """Load a sound from assets folder"""
    try:
        asset_path = os.path.join(os.path.dirname(__file__), "assets", filename)
        return pygame.mixer.Sound(asset_path)
    except (FileNotFoundError, pygame.error) as e:
        print(f"Warning: Could not load {filename}: {e}")
        return None

# Initialize display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Load and scale images
background_img = load_and_scale_image("background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
player_img = load_and_scale_image("player.png", (PLAYER_SIZE, PLAYER_SIZE))
enemy_img = load_and_scale_image("enemy.png", (60, 60))

# Load sounds
flap_sound = load_sound("flap.mp3")
gameover_sound = load_sound("gameover.mp3")
enemy_sound = load_sound("enemy.mp3")

# Load background music
try:
    bg_music_path = os.path.join(os.path.dirname(__file__), "assets", "bg.mp3")
    pygame.mixer.music.load(bg_music_path)
    pygame.mixer.music.set_volume(0.3)
except (FileNotFoundError, pygame.error) as e:
    print(f"Warning: Could not load background music: {e}")

# ============================================================================
# HIGH SCORE MANAGEMENT
# ============================================================================

def load_high_score():
    """Load high score from highscore.txt"""
    highscore_path = os.path.join(os.path.dirname(__file__), "highscore.txt")
    try:
        with open(highscore_path, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def save_high_score(score):
    """Save high score to highscore.txt"""
    highscore_path = os.path.join(os.path.dirname(__file__), "highscore.txt")
    try:
        with open(highscore_path, 'w') as f:
            f.write(str(score))
    except IOError as e:
        print(f"Warning: Could not save high score: {e}")

# ============================================================================
# GAME CLASSES
# ============================================================================

class Player:
    """Player character with physics and animation"""
    
    def __init__(self):
        self.x = SCREEN_WIDTH // 4
        self.y = SCREEN_HEIGHT // 2 - 50  # Start slightly above center
        self.velocity = 0
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.image = player_img
        self.started = False  # Player doesn't fall until game starts
        
    def flap(self):
        """Make the player flap upward"""
        self.velocity = FLAP_STRENGTH
        self.started = True
        if flap_sound:
            flap_sound.play()
    
    def update(self):
        """Update player position with gravity"""
        if self.started:
            self.velocity += GRAVITY
            self.y += self.velocity
            
            # Keep player on screen (with some margin)
            if self.y < 0:
                self.y = 0
                self.velocity = 0
    
    def draw(self, surface):
        """Draw the player"""
        surface.blit(self.image, (self.x, self.y))
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def reset(self):
        """Reset player to initial state"""
        self.y = SCREEN_HEIGHT // 2 - 50
        self.velocity = 0
        self.started = False


class Obstacle:
    """Pipe/wall obstacle with top and bottom parts"""
    
    def __init__(self, x):
        self.x = x
        self.width = OBSTACLE_WIDTH
        
        # Random gap position (with margins to keep it visible)
        min_gap_y = 150
        max_gap_y = SCREEN_HEIGHT - GROUND_HEIGHT - WALL_GAP - 50
        self.gap_y = random.randint(min_gap_y, max_gap_y)
        
        self.scored = False
        
    def update(self):
        """Move obstacle from right to left"""
        self.x -= OBSTACLE_SPEED
    
    def draw(self, surface):
        """Draw top and bottom pipes"""
        # Top pipe
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        pygame.draw.rect(surface, (34, 139, 34), top_rect)  # Green
        pygame.draw.rect(surface, (0, 100, 0), top_rect, 3)  # Dark green border
        
        # Bottom pipe
        bottom_y = self.gap_y + WALL_GAP
        bottom_height = SCREEN_HEIGHT - GROUND_HEIGHT - bottom_y
        bottom_rect = pygame.Rect(self.x, bottom_y, self.width, bottom_height)
        pygame.draw.rect(surface, (34, 139, 34), bottom_rect)
        pygame.draw.rect(surface, (0, 100, 0), bottom_rect, 3)
    
    def is_off_screen(self):
        """Check if obstacle has moved off the left side of screen"""
        return self.x + self.width < 0
    
    def collides_with(self, player):
        """Check collision with player"""
        player_rect = player.get_rect()
        
        # Top pipe collision
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        if player_rect.colliderect(top_rect):
            return True
        
        # Bottom pipe collision
        bottom_y = self.gap_y + WALL_GAP
        bottom_height = SCREEN_HEIGHT - GROUND_HEIGHT - bottom_y
        bottom_rect = pygame.Rect(self.x, bottom_y, self.width, bottom_height)
        if player_rect.colliderect(bottom_rect):
            return True
        
        return False


class Enemy:
    """Enemy sprite that moves across the screen"""
    
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.y = random.randint(100, SCREEN_HEIGHT - GROUND_HEIGHT - 100)
        self.width = 60
        self.height = 60
        self.image = enemy_img
        
    def update(self):
        """Move enemy from right to left"""
        self.x -= ENEMY_SPEED
    
    def draw(self, surface):
        """Draw the enemy"""
        surface.blit(self.image, (self.x, self.y))
    
    def is_off_screen(self):
        """Check if enemy has moved off the left side of screen"""
        return self.x + self.width < 0
    
    def collides_with(self, player):
        """Check collision with player"""
        player_rect = player.get_rect()
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(enemy_rect)


# ============================================================================
# RENDERING FUNCTIONS
# ============================================================================

def draw_parallax_background(surface, scroll_offset):
    """Draw parallax scrolling background"""
    # Draw background twice for seamless scrolling
    bg_x = -(scroll_offset * 0.5) % SCREEN_WIDTH
    surface.blit(background_img, (bg_x - SCREEN_WIDTH, 0))
    surface.blit(background_img, (bg_x, 0))
    if bg_x < SCREEN_WIDTH:
        surface.blit(background_img, (bg_x + SCREEN_WIDTH, 0))

def draw_ground(surface, scroll_offset):
    """Draw scrolling ground"""
    ground_y = SCREEN_HEIGHT - GROUND_HEIGHT
    ground_rect = pygame.Rect(0, ground_y, SCREEN_WIDTH, GROUND_HEIGHT)
    pygame.draw.rect(surface, (139, 69, 19), ground_rect)  # Brown
    
    # Draw ground pattern for parallax effect
    pattern_width = 50
    offset = int(scroll_offset) % pattern_width
    for i in range(-1, SCREEN_WIDTH // pattern_width + 2):
        x = i * pattern_width - offset
        pygame.draw.line(surface, (101, 67, 33), (x, ground_y), (x, SCREEN_HEIGHT), 2)

def draw_text(surface, text, size, x, y, color=WHITE, center=True):
    """Draw text on screen"""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def show_start_screen():
    """Display start screen and wait for player input"""
    pygame.mixer.music.play(-1)  # Loop background music
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        
        # Draw start screen
        screen.blit(background_img, (0, 0))
        draw_ground(screen, 0)
        
        draw_text(screen, "FLAPPY BIRD", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, WHITE)
        draw_text(screen, "Press SPACE or Click to Start", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)
        draw_text(screen, "Use SPACE to Flap", 28, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, WHITE)
        
        pygame.display.flip()

def show_game_over_screen(score, high_score):
    """Display game over screen"""
    if gameover_sound:
        gameover_sound.play()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        
        # Draw game over screen
        screen.blit(background_img, (0, 0))
        draw_ground(screen, 0)
        
        draw_text(screen, "GAME OVER", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, WHITE)
        draw_text(screen, f"Score: {score}", 48, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)
        draw_text(screen, f"High Score: {high_score}", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, WHITE)
        draw_text(screen, "Press SPACE to Play Again", 28, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120, WHITE)
        
        pygame.display.flip()

# ============================================================================
# MAIN GAME LOOP
# ============================================================================

def main():
    """Main game function"""
    
    # Load high score
    high_score = load_high_score()
    
    # Show start screen
    show_start_screen()
    
    # Game loop
    running = True
    while running:
        # Initialize game state
        player = Player()
        obstacles = []
        enemies = []
        score = 0
        scroll_offset = 0
        frame_count = 0
        game_over = False
        
        # Main gameplay loop
        playing = True
        while playing:
            clock.tick(FPS)
            frame_count += 1
            
            # ================================================================
            # EVENT HANDLING
            # ================================================================
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if not game_over:
                            player.flap()
                        else:
                            playing = False
            
            if not game_over:
                # ============================================================
                # UPDATE GAME OBJECTS
                # ============================================================
                
                # Update player
                player.update()
                
                # Update scroll offset for parallax
                if player.started:
                    scroll_offset += OBSTACLE_SPEED
                
                # Spawn new obstacles
                if player.started and frame_count % OBSTACLE_SPAWN_INTERVAL == 0:
                    obstacles.append(Obstacle(SCREEN_WIDTH))
                
                # Spawn new enemies
                if player.started and frame_count % ENEMY_SPAWN_INTERVAL == 0:
                    enemies.append(Enemy())
                    if enemy_sound:
                        enemy_sound.play()
                
                # Update obstacles
                for obstacle in obstacles[:]:
                    obstacle.update()
                    
                    # Remove off-screen obstacles
                    if obstacle.is_off_screen():
                        obstacles.remove(obstacle)
                    
                    # Check for scoring (player passed the obstacle)
                    if not obstacle.scored and obstacle.x + obstacle.width < player.x:
                        obstacle.scored = True
                        score += 1
                
                # Update enemies
                for enemy in enemies[:]:
                    enemy.update()
                    
                    # Remove off-screen enemies
                    if enemy.is_off_screen():
                        enemies.remove(enemy)
                
                # ============================================================
                # COLLISION DETECTION
                # ============================================================
                
                # Check collision with ground
                if player.y + player.height >= SCREEN_HEIGHT - GROUND_HEIGHT:
                    game_over = True
                
                # Check collision with obstacles
                for obstacle in obstacles:
                    if obstacle.collides_with(player):
                        game_over = True
                        break
                
                # Check collision with enemies
                for enemy in enemies:
                    if enemy.collides_with(player):
                        game_over = True
                        break
            
            # ================================================================
            # RENDERING
            # ================================================================
            
            # Draw parallax background
            draw_parallax_background(screen, scroll_offset)
            
            # Draw game objects
            for obstacle in obstacles:
                obstacle.draw(screen)
            
            for enemy in enemies:
                enemy.draw(screen)
            
            player.draw(screen)
            
            # Draw ground
            draw_ground(screen, scroll_offset)
            
            # Draw score
            draw_text(screen, f"Score: {score}", 36, 100, 30, WHITE, center=False)
            draw_text(screen, f"High: {high_score}", 28, 100, 65, WHITE, center=False)
            
            # Draw game over message
            if game_over:
                draw_text(screen, "GAME OVER", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)
                draw_text(screen, "Press SPACE to Continue", 32, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, WHITE)
                
                # Update high score
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
            
            pygame.display.flip()
        
        # Show game over screen after each game
        show_game_over_screen(score, high_score)
    
    # Cleanup
    pygame.quit()

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
