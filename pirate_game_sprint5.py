#!/usr/bin/env python3
"""
Privateers Legacy - Sprint 5 Enhanced Version
Complete Pirates! 1987 experience with dock menu, wind vanes, and enhanced sailing
"""

import pygame
import random
import math
import json
from enum import Enum

# Import our new systems
from dock_menu import DockMenu
from sailing_engine import SailingEngine, WindSystem, NavigationData
from wind_ui import (WindVaneSystem, EnhancedWaveEffect, CompassDisplay, 
                     SpeedDisplay, StallWarning, EnhancedWindDisplay)

# Initialize Pygame
pygame.init()

class GameState(Enum):
    """Game states"""
    MAIN_GAME = 1
    DOCKED = 2

class Ship:
    """Simple ship class for Sprint 5 demo"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.heading = 0  # degrees (0 = North)
        self.current_speed = 0  # knots
        self.width = 30
        self.height = 20
        self.color = (139, 69, 19)  # Brown
        
        # Simple crew system for demo
        self.crew_count = 15
        self.max_crew = 30
        
    def update(self, keys, sailing_engine, wind_system, navigation_data, dt):
        """Update ship with enhanced sailing mechanics"""
        # Handle steering input
        turning_input = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            turning_input = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            turning_input = 1
        
        # Update sailing physics
        sailing_data = sailing_engine.update_ship_physics(
            dt, self.heading, wind_system, turning_input
        )
        
        # Update ship state
        self.heading = sailing_data['new_heading']
        self.current_speed = sailing_data['current_speed']
        
        # Update navigation data
        navigation_data.update(sailing_data, wind_system)
        
        # Calculate movement
        if self.current_speed > 0:
            dx, dy = sailing_engine.calculate_movement(self.current_speed, self.heading, dt)
            self.x += dx
            self.y += dy
            
            # Keep ship within bounds
            self.x = max(50, min(750, self.x))
            self.y = max(50, min(550, self.y))
    
    def draw(self, screen):
        """Draw the ship"""
        # Simple ship representation
        ship_rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                               self.width, self.height)
        pygame.draw.rect(screen, self.color, ship_rect)
        
        # Draw heading indicator
        heading_rad = math.radians(self.heading)
        end_x = self.x + math.sin(heading_rad) * 25
        end_y = self.y - math.cos(heading_rad) * 25
        pygame.draw.line(screen, (255, 255, 255), (self.x, self.y), (end_x, end_y), 3)
    
    def get_distance_to(self, island):
        """Calculate distance to island"""
        return math.sqrt((self.x - island.x)**2 + (self.y - island.y)**2)

class Island:
    """Simple island class"""
    
    def __init__(self, x, y, width=60, height=40):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = (34, 139, 34)  # Forest green
    
    def draw(self, screen):
        """Draw the island"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class CrewSystem:
    """Simple crew system for demo"""
    
    def __init__(self, initial_crew_count=15):
        self.crew_count = initial_crew_count
        self.max_crew = 30
    
    def get_crew_count(self):
        return self.crew_count
    
    def can_recruit(self, count):
        return self.crew_count + count <= self.max_crew
    
    def recruit_crew(self, count):
        if self.can_recruit(count):
            self.crew_count += count
            return True
        return False

class EnhancedGame:
    """Enhanced game with Sprint 5 features"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Privateers Legacy - Sprint 5 Enhanced")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = GameState.MAIN_GAME
        
        # Game stats
        self.gold = 500
        self.health = 100
        self.ship_name = "The Salty Squid"
        
        # Colors
        self.ocean_color = (0, 119, 190)
        
        # Create ship
        self.ship = Ship(400, 300)
        self.crew_system = CrewSystem()
        
        # Create islands
        self.islands = [
            Island(150, 150),
            Island(600, 200),
            Island(300, 450)
        ]
        
        # Initialize enhanced sailing systems
        self.sailing_engine = SailingEngine()
        self.wind_system = WindSystem()
        self.navigation_data = NavigationData()
        
        # Initialize enhanced UI systems
        self.dock_menu = DockMenu()
        self.wind_vane_system = WindVaneSystem(800, 600)
        self.wave_effect = EnhancedWaveEffect(800, 600)
        self.compass_display = CompassDisplay(700, 100)
        self.speed_display = SpeedDisplay(10, 200)
        self.stall_warning = StallWarning()
        self.enhanced_wind_display = EnhancedWindDisplay(10, 300)
        
        # State
        self.docked = False
        self.near_island = False
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        print("=== Privateers Legacy - Sprint 5 Enhanced ===")
        print("New Features:")
        print("  D: Dock at nearby islands")
        print("  Enhanced wind visualization with vanes")
        print("  Realistic sailing physics")
        print("  Trading, repairs, and crew recruitment")
        print("Controls:")
        print("  Arrow Keys: Steer ship")
        print("  D: Dock (when near island)")
        print("  ESC: Quit")
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # Handle dock menu if active
                if self.dock_menu.active:
                    player_stats = {
                        'gold': self.gold,
                        'health': self.health
                    }
                    result = self.dock_menu.handle_input(event, self.crew_system, player_stats)
                    if result:
                        if result == "leave_port":
                            self.docked = False
                            self.game_state = GameState.MAIN_GAME
                        elif isinstance(result, dict):
                            # Handle dock menu actions
                            if result['action'] == 'buy':
                                print(f"Bought {result['quantity']} {result['commodity']} for {result['cost']} gold")
                            elif result['action'] == 'sell':
                                print(f"Sold {result['quantity']} {result['commodity']} for {result['value']} gold")
                            elif result['action'] == 'repair':
                                print(f"Ship repaired for {result['cost']} gold")
                            elif result['action'] == 'recruit':
                                self.crew_system.recruit_crew(result['count'])
                                print(f"Recruited {result['count']} crew for {result['cost']} gold")
                            
                            # Update player stats
                            self.gold = player_stats['gold']
                            self.health = player_stats['health']
                    return
                
                # Main game controls
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_d:
                    self.check_docking()
    
    def check_docking(self):
        """Check if player can dock at nearby island"""
        for island in self.islands:
            distance = self.ship.get_distance_to(island)
            if distance < 80:  # Docking range
                if not self.docked:
                    self.docked = True
                    self.game_state = GameState.DOCKED
                    player_stats = {
                        'gold': self.gold,
                        'health': self.health
                    }
                    self.dock_menu.activate(self.crew_system, player_stats)
                    print("Docked at island!")
                return
    
    def update(self, dt):
        """Update game state"""
        if self.game_state == GameState.MAIN_GAME:
            # Update enhanced sailing systems
            self.wind_system.update(dt)
            
            # Get pressed keys
            keys = pygame.key.get_pressed()
            
            # Update ship with enhanced physics
            self.ship.update(keys, self.sailing_engine, self.wind_system, self.navigation_data, dt)
            
            # Update enhanced UI systems
            self.wind_vane_system.update(dt, self.wind_system.true_wind_direction, self.wind_system.true_wind_speed)
            self.wave_effect.update(dt, self.wind_system.true_wind_direction, self.wind_system.true_wind_speed)
            self.stall_warning.update(dt)
            
            # Check proximity to islands
            self.near_island = False
            for island in self.islands:
                if self.ship.get_distance_to(island) < 100:
                    self.near_island = True
                    break
        
        elif self.game_state == GameState.DOCKED:
            # Update dock menu
            self.dock_menu.update(dt)
    
    def draw(self):
        """Draw the game"""
        # Clear screen with ocean
        self.screen.fill(self.ocean_color)
        
        # Draw enhanced wave effects
        self.wave_effect.draw(self.screen)
        
        # Draw islands
        for island in self.islands:
            island.draw(self.screen)
        
        # Draw ship
        self.ship.draw(self.screen)
        
        # Draw wind vanes (for strong wind)
        self.wind_vane_system.draw(self.screen)
        
        # Draw enhanced UI elements
        self.compass_display.draw(self.screen, self.navigation_data)
        self.speed_display.draw(self.screen, self.navigation_data)
        self.enhanced_wind_display.draw(self.screen, self.navigation_data)
        self.stall_warning.draw(self.screen, self.navigation_data, 800, 600)
        
        # Draw dock menu if active
        if self.dock_menu.active:
            player_stats = {
                'gold': self.gold,
                'health': self.health
            }
            self.dock_menu.draw(self.screen, self.crew_system, player_stats)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw docking prompt
        if self.near_island and not self.docked:
            dock_text = self.small_font.render("Press D to dock", True, (255, 255, 0))
            self.screen.blit(dock_text, (350, 50))
        
        pygame.display.flip()
    
    def draw_hud(self):
        """Draw the HUD"""
        # Ship name
        name_text = self.font.render(self.ship_name, True, (255, 255, 255))
        self.screen.blit(name_text, (10, 10))
        
        # Stats
        health_text = self.small_font.render(f"Health: {self.health}", True, (255, 255, 255))
        self.screen.blit(health_text, (10, 50))
        
        gold_text = self.small_font.render(f"Gold: {self.gold}", True, (255, 215, 0))
        self.screen.blit(gold_text, (10, 75))
        
        crew_text = self.small_font.render(f"Crew: {self.crew_system.get_crew_count()}/{self.crew_system.max_crew}", True, (255, 255, 255))
        self.screen.blit(crew_text, (10, 100))
        
        # Wind info
        wind_text = self.small_font.render(f"Wind: {self.wind_system.true_wind_speed:.1f} knots from {self.wind_system.true_wind_direction:.0f}°", True, (0, 255, 255))
        self.screen.blit(wind_text, (10, 125))
        
        # Speed info
        speed_text = self.small_font.render(f"Speed: {self.ship.current_speed:.1f} knots", True, (0, 255, 0))
        self.screen.blit(speed_text, (10, 150))
        
        # Instructions
        if not self.dock_menu.active:
            instructions = [
                "Arrow Keys: Steer",
                "D: Dock at island",
                "ESC: Quit"
            ]
            for i, instruction in enumerate(instructions):
                text = pygame.font.Font(None, 18).render(instruction, True, (200, 200, 200))
                self.screen.blit(text, (10, 550 - i * 15))

# Run the enhanced game
if __name__ == "__main__":
    game = EnhancedGame()
    game.run()
