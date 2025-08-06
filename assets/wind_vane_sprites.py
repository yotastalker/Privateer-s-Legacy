#!/usr/bin/env python3
"""
Privateers Legacy - Wind Vane Sprite Generation
Creates wind vane sprites for different wind strengths
"""

import pygame
import math

def create_wind_vane_light():
    """Create light wind vane sprite"""
    size = 30
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Light gray color for light wind
    color = (180, 180, 180, 200)
    
    # Main shaft
    pygame.draw.line(surface, color, (size//2, 5), (size//2, size-5), 2)
    
    # Two small branches
    branch_length = 8
    for i in range(2):
        y_pos = 8 + i * 10
        # Left branch
        pygame.draw.line(surface, color, 
                        (size//2, y_pos), 
                        (size//2 - branch_length, y_pos - 3), 1)
        # Right branch
        pygame.draw.line(surface, color, 
                        (size//2, y_pos), 
                        (size//2 + branch_length, y_pos - 3), 1)
    
    # Arrow head
    arrow_points = [
        (size//2, 5),
        (size//2 - 4, 12),
        (size//2 + 4, 12)
    ]
    pygame.draw.polygon(surface, color, arrow_points)
    
    return surface

def create_wind_vane_medium():
    """Create medium wind vane sprite"""
    size = 40
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Medium blue-gray for medium wind
    color = (150, 180, 200, 220)
    
    # Main shaft (thicker)
    pygame.draw.line(surface, color, (size//2, 5), (size//2, size-5), 3)
    
    # Three branches
    branch_length = 12
    for i in range(3):
        y_pos = 8 + i * 8
        # Left branch
        pygame.draw.line(surface, color, 
                        (size//2, y_pos), 
                        (size//2 - branch_length, y_pos - 4), 2)
        # Right branch
        pygame.draw.line(surface, color, 
                        (size//2, y_pos), 
                        (size//2 + branch_length, y_pos - 4), 2)
    
    # Larger arrow head
    arrow_points = [
        (size//2, 5),
        (size//2 - 6, 14),
        (size//2 + 6, 14)
    ]
    pygame.draw.polygon(surface, color, arrow_points)
    
    return surface

def create_wind_vane_strong():
    """Create strong wind vane sprite"""
    size = 50
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Bright cyan for strong wind
    color = (0, 200, 255, 240)
    
    # Main shaft (thick)
    pygame.draw.line(surface, color, (size//2, 5), (size//2, size-5), 4)
    
    # Five branches
    branch_length = 15
    for i in range(5):
        y_pos = 8 + i * 6
        # Left branch (thicker)
        pygame.draw.line(surface, color, 
                        (size//2, y_pos), 
                        (size//2 - branch_length, y_pos - 5), 3)
        # Right branch (thicker)
        pygame.draw.line(surface, color, 
                        (size//2, y_pos), 
                        (size//2 + branch_length, y_pos - 5), 3)
    
    # Large arrow head
    arrow_points = [
        (size//2, 5),
        (size//2 - 8, 16),
        (size//2 + 8, 16)
    ]
    pygame.draw.polygon(surface, color, arrow_points)
    
    # Add wind streaks for strong wind effect
    streak_color = (100, 220, 255, 150)
    for i in range(3):
        streak_x = size//2 + 20 + i * 3
        pygame.draw.line(surface, streak_color, 
                        (streak_x, 10), (streak_x + 8, 15), 1)
    
    return surface

def create_wave_sprites():
    """Create wave sprites for different wind strengths"""
    sprites = {}
    
    # Light waves
    light_surface = pygame.Surface((100, 20), pygame.SRCALPHA)
    light_color = (0, 100, 150, 80)
    for x in range(0, 100, 20):
        y = 10 + int(3 * math.sin(x * 0.1))
        pygame.draw.circle(light_surface, light_color, (x, y), 3)
    sprites['light'] = light_surface
    
    # Medium waves
    medium_surface = pygame.Surface((100, 30), pygame.SRCALPHA)
    medium_color = (0, 120, 180, 100)
    for x in range(0, 100, 15):
        y = 15 + int(5 * math.sin(x * 0.08))
        pygame.draw.circle(medium_surface, medium_color, (x, y), 4)
    sprites['medium'] = medium_surface
    
    # Strong waves
    strong_surface = pygame.Surface((100, 40), pygame.SRCALPHA)
    strong_color = (0, 140, 220, 120)
    for x in range(0, 100, 12):
        y = 20 + int(8 * math.sin(x * 0.06))
        pygame.draw.circle(strong_surface, strong_color, (x, y), 6)
    sprites['strong'] = strong_surface
    
    return sprites

def save_sprites_as_images():
    """Save sprites as PNG files (optional - for debugging)"""
    import os
    
    # Create assets directory if it doesn't exist
    assets_dir = "/Users/chrismckearn/Privateer's Legacy/assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    # Save wind vane sprites
    light_vane = create_wind_vane_light()
    medium_vane = create_wind_vane_medium()
    strong_vane = create_wind_vane_strong()
    
    pygame.image.save(light_vane, os.path.join(assets_dir, "wind_vane_light.png"))
    pygame.image.save(medium_vane, os.path.join(assets_dir, "wind_vane_medium.png"))
    pygame.image.save(strong_vane, os.path.join(assets_dir, "wind_vane_strong.png"))
    
    # Save wave sprites
    wave_sprites = create_wave_sprites()
    for strength, sprite in wave_sprites.items():
        pygame.image.save(sprite, os.path.join(assets_dir, f"waves_{strength}.png"))
    
    print("Wind vane and wave sprites saved to assets directory")

# Initialize pygame for sprite creation
pygame.init()

if __name__ == "__main__":
    save_sprites_as_images()
    pygame.quit()
