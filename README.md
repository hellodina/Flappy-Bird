# Flappy-Bird
App Academy - AI Game Jam

## 🎮 About
A fun, forgiving Flappy Bird style game built with Python and Pygame. Navigate your bird through obstacles and enemies while racking up points!

## 🚀 Quick Start

### Prerequisites
- Python 3.x
- Pygame (installed via requirements.txt)

### Installation & Running
```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python3 game.py
```

## 🕹️ How to Play
- Press **SPACE** or **CLICK** to start the game
- Press **SPACE** during gameplay to make the bird flap upward
- Avoid hitting the pipes/walls and enemies
- Score points by passing through obstacles
- High scores are automatically saved!

## 📁 Project Structure
- `game.py` - Main game file (single-file implementation)
- `config.json` - Game configuration (gravity, speed, gaps, etc.)
- `highscore.txt` - Persistent high score storage
- `assets/` - Game assets (images and sounds)
  - `background.png` - Background image
  - `player.png` - Player sprite
  - `enemy.png` - Enemy sprite
  - Sound effects (flap, gameover, enemy, bg music)

## ⚙️ Configuration
You can adjust game difficulty by editing `config.json`:
- `player_gravity` - How fast the player falls
- `flap_strength` - How high the player jumps
- `obstacle_speed` - How fast obstacles move
- `wall_gap` - Gap size between pipes
- `enemy_speed` - How fast enemies move

## 🎨 Features
- ✨ Parallax scrolling background
- 🎵 Background music and sound effects
- 🏆 Persistent high score system
- 👾 Dynamic enemy spawning
- 🎯 Smooth collision detection
- 🌈 Forgiving, fun gameplay
- 📊 Real-time score display

## 🎓 Game Design
This game is designed to be **slow-paced and forgiving**:
- Player doesn't fall immediately at game start
- Reasonable gaps between obstacles
- Smooth, predictable physics
- Visual feedback for all actions

Enjoy playing! 🎮
