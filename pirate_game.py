import pygame
import random
import math
import json

# Initialize Pygame
pygame.init()

class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 20
        self.speed = 5
        self.angle = 0  # Ship angle in radians
        self.rotation_speed = 0.1
        self.color = (139, 69, 19)  # Brown color for pirate ship
    
    def update(self, keys):
        """Update ship position and rotation based on key input"""
        if keys[pygame.K_LEFT]:
            self.angle -= self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle += self.rotation_speed
        if keys[pygame.K_UP]:
            # Move forward in the direction the ship is facing
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed
            # Keep ship within screen bounds
            self.x = max(0, min(800 - self.width, self.x))
            self.y = max(0, min(600 - self.height, self.y))
    
    def draw(self, screen):
        """Draw the ship on screen"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def get_distance_to(self, island):
        """Calculate distance between ship center and island center"""
        ship_center_x = self.x + self.width // 2
        ship_center_y = self.y + self.height // 2
        island_center_x = island.x + island.width // 2
        island_center_y = island.y + island.height // 2
        
        return math.sqrt((ship_center_x - island_center_x)**2 + (ship_center_y - island_center_y)**2)

class Cannonball:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 8
        self.radius = 3
        self.color = (64, 64, 64)  # Dark gray
    
    def update(self):
        """Move cannonball forward"""
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
    
    def is_offscreen(self):
        """Check if cannonball is off screen"""
        return self.x < 0 or self.x > 800 or self.y < 0 or self.y > 600
    
    def draw(self, screen):
        """Draw the cannonball"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class EnemyShip:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 15
        self.speed = 2
        self.direction = 1  # 1 for right, -1 for left
        self.color = (139, 0, 0)  # Dark red
    
    def update(self):
        """Move enemy ship back and forth"""
        self.x += self.speed * self.direction
        if self.x <= 0 or self.x >= 800 - self.width:
            self.direction *= -1
    
    def draw(self, screen):
        """Draw the enemy ship"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def collides_with(self, ship):
        """Check collision with player ship"""
        return (self.x < ship.x + ship.width and
                self.x + self.width > ship.x and
                self.y < ship.y + ship.height and
                self.y + self.height > ship.y)

class Island:
    def __init__(self, x, y, width=60, height=40):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = (34, 139, 34)  # Forest green
    
    def draw(self, screen):
        """Draw the island on screen"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class GameState:
    def __init__(self, ship_x, ship_y, gold, health):
        self.ship_x = ship_x
        self.ship_y = ship_y
        self.gold = gold
        self.health = health
    
    def save(self, filename="savegame.json"):
        """Save game state to JSON file"""
        data = {
            "ship_x": self.ship_x,
            "ship_y": self.ship_y,
            "gold": self.gold,
            "health": self.health
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
        print("Game saved!")
    
    @classmethod
    def load(cls, filename="savegame.json"):
        """Load game state from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            print("Game loaded!")
            return cls(data["ship_x"], data["ship_y"], data["gold"], data["health"])
        except FileNotFoundError:
            print("No save file found!")
            return None

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pirate Ship Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.ocean_color = (0, 119, 190)  # Ocean blue
        
        # Create ship at center of screen
        self.ship = Ship(385, 290)
        
        # Game stats
        self.health = 100
        self.gold = 250
        self.ship_name = "The Salty Squid"
        
        # Create 3 random islands
        self.islands = self._generate_islands()
        
        # Cannonballs list
        self.cannonballs = []
        
        # Enemy ships
        self.enemy_ships = self._generate_enemy_ships()
        self.hit_flash = 0
        
        # Font for docking message
        self.font = pygame.font.Font(None, 36)
    
    def _generate_islands(self):
        """Generate 3 randomly placed islands"""
        islands = []
        for _ in range(3):
            # Ensure islands don't spawn too close to ship starting position
            while True:
                x = random.randint(50, 750 - 60)
                y = random.randint(50, 550 - 40)
                # Check if island is far enough from ship start position
                if abs(x - 385) > 100 or abs(y - 290) > 100:
                    islands.append(Island(x, y))
                    break
        return islands
    
    def _generate_enemy_ships(self):
        """Generate 1-3 random enemy ships"""
        enemy_ships = []
        num_enemies = random.randint(1, 3)
        for _ in range(num_enemies):
            x = random.randint(0, 750)
            y = random.randint(100, 500)
            enemy_ships.append(EnemyShip(x, y))
        return enemy_ships
    
    def _check_docking(self):
        """Check if ship is near any island and display docking message"""
        for island in self.islands:
            distance = self.ship.get_distance_to(island)
            if distance < 80:  # Docking range
                print("Press D to dock")
                # Display message on screen too
                text = self.font.render("Press D to dock", True, (255, 255, 255))
                self.screen.blit(text, (300, 50))
                break
    
    def _draw_dock_menu(self):
        """Draw the docking menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Menu text
        menu_items = [
            "DOCKED AT ISLAND",
            "1. Trade goods",
            "2. Repair ship", 
            "3. Leave"
        ]
        
        for i, item in enumerate(menu_items):
            color = (255, 255, 0) if i == 0 else (255, 255, 255)
            text = self.font.render(item, True, color)
            y_pos = 250 + i * 40
            self.screen.blit(text, (300, y_pos))
    
    def _draw_hud(self):
        """Draw the HUD at the top of the screen"""
        hud_font = pygame.font.Font(None, 24)
        
        # Ship name (left)
        name_text = hud_font.render(self.ship_name, True, (255, 255, 255))
        self.screen.blit(name_text, (10, 10))
        
        # Health (center)
        health_text = hud_font.render(f"Health: {self.health}", True, (255, 255, 255))
        self.screen.blit(health_text, (300, 10))
        
        # Gold (right)
        gold_text = hud_font.render(f"Gold: {self.gold}", True, (255, 255, 255))
        self.screen.blit(gold_text, (650, 10))
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if self.paused:
                        if event.key == pygame.K_1:
                            print("Trading goods...")
                            self.paused = False
                        elif event.key == pygame.K_2:
                            print("Repairing ship...")
                            self.paused = False
                        elif event.key == pygame.K_3:
                            print("Leaving island...")
                            self.paused = False
                    else:
                        if event.key == pygame.K_SPACE:
                            # Fire cannonball from ship position
                            cannon_x = self.ship.x + self.ship.width // 2
                            cannon_y = self.ship.y + self.ship.height // 2
                            self.cannonballs.append(Cannonball(cannon_x, cannon_y, self.ship.angle))
                        elif event.key == pygame.K_d:
                            # Check if near island for docking
                            for island in self.islands:
                                if self.ship.get_distance_to(island) < 80:
                                    self.paused = True
                                    break
                        elif event.key == pygame.K_s:
                            # Save game
                            game_state = GameState(self.ship.x, self.ship.y, self.gold, self.health)
                            game_state.save()
                        elif event.key == pygame.K_l:
                            # Load game
                            loaded_state = GameState.load()
                            if loaded_state:
                                self.ship.x = loaded_state.ship_x
                                self.ship.y = loaded_state.ship_y
                                self.gold = loaded_state.gold
                                self.health = loaded_state.health
            
            if not self.paused:
                # Get pressed keys
                keys = pygame.key.get_pressed()
                
                # Update game objects
                self.ship.update(keys)
                
                # Update cannonballs
                for cannonball in self.cannonballs[:]:
                    cannonball.update()
                    if cannonball.is_offscreen():
                        self.cannonballs.remove(cannonball)
                
                # Update enemy ships
                for enemy in self.enemy_ships:
                    enemy.update()
                
                # Check collisions with enemy ships
                for enemy in self.enemy_ships:
                    if enemy.collides_with(self.ship) and self.hit_flash == 0:
                        self.health -= 10
                        self.hit_flash = 30  # Flash for 30 frames
                        print(f"Hit! Health: {self.health}")
                
                # Update hit flash
                if self.hit_flash > 0:
                    self.hit_flash -= 1
            
            # Draw everything
            self.screen.fill(self.ocean_color)  # Ocean background
            
            # Draw islands
            for island in self.islands:
                island.draw(self.screen)
            
            # Draw ship
            self.ship.draw(self.screen)
            
            # Draw cannonballs
            for cannonball in self.cannonballs:
                cannonball.draw(self.screen)
            
            # Draw enemy ships
            for enemy in self.enemy_ships:
                enemy.draw(self.screen)
            
            # Apply hit flash effect
            if self.hit_flash > 0:
                flash_surface = pygame.Surface((800, 600))
                flash_surface.set_alpha(50)
                flash_surface.fill((255, 0, 0))
                self.screen.blit(flash_surface, (0, 0))
            
            # Check for docking
            if not self.paused:
                self._check_docking()
            else:
                self._draw_dock_menu()
            
            # Draw HUD
            self._draw_hud()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()