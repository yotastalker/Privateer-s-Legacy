#!/usr/bin/env python3
"""
Privateers Legacy - Wind UI System
Visual wind and water feedback for realistic sailing
"""

import pygame
import math
import random

class WindParticle:
    """Individual wind particle for visual effect"""
    
    def __init__(self, x, y, wind_direction, wind_speed):
        """Initialize wind particle"""
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        
        # Movement based on wind
        wind_rad = math.radians(wind_direction)
        speed_factor = wind_speed * 0.5  # Scale for visual effect
        
        self.velocity_x = math.cos(wind_rad) * speed_factor
        self.velocity_y = math.sin(wind_rad) * speed_factor
        
        # Visual properties
        self.size = random.randint(2, 4)
        self.alpha = random.randint(100, 200)
        self.lifetime = random.uniform(3.0, 6.0)
        self.age = 0.0
        
    def update(self, dt):
        """Update particle position and age"""
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.age += dt
        
        # Fade out over time
        fade_factor = 1.0 - (self.age / self.lifetime)
        self.alpha = int(200 * max(0, fade_factor))
        
        return self.age < self.lifetime
    
    def draw(self, screen):
        """Draw the wind particle"""
        if self.alpha > 0:
            # Create surface for alpha blending
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color = (255, 255, 255, self.alpha)
            pygame.draw.circle(particle_surface, color, (self.size, self.size), self.size)
            screen.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

class WaveEffect:
    """Animated wave overlay moving with wind"""
    
    def __init__(self, screen_width, screen_height):
        """Initialize wave effect"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.wave_offset = 0.0
        self.wave_speed = 20.0  # Pixels per second
        
    def update(self, dt, wind_direction, wind_speed):
        """Update wave animation"""
        # Wave movement based on wind
        wind_rad = math.radians(wind_direction)
        wave_velocity_x = math.cos(wind_rad) * self.wave_speed * (wind_speed / 10.0)
        
        self.wave_offset += wave_velocity_x * dt
        self.wave_offset = self.wave_offset % 100  # Reset to prevent overflow
    
    def draw(self, screen):
        """Draw animated wave overlay"""
        wave_color = (0, 100, 150, 50)  # Semi-transparent blue
        wave_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Draw wave lines
        for y in range(0, self.screen_height, 20):
            for x in range(0, self.screen_width, 100):
                wave_x = x + int(self.wave_offset)
                if wave_x < self.screen_width:
                    pygame.draw.line(wave_surface, wave_color, 
                                   (wave_x, y), (wave_x + 30, y), 2)
        
        screen.blit(wave_surface, (0, 0))

class CompassDisplay:
    """Professional compass display with wind overlay"""
    
    def __init__(self, x, y, radius=50):
        """Initialize compass display"""
        self.x = x
        self.y = y
        self.radius = radius
        
        # Colors
        self.colors = {
            'background': (0, 0, 0, 180),
            'border': (255, 255, 255),
            'cardinal': (255, 255, 0),
            'intercardinal': (200, 200, 200),
            'ship_needle': (255, 0, 0),
            'wind_needle': (0, 255, 255),
            'text': (255, 255, 255)
        }
        
        # Font
        self.font = pygame.font.Font(None, 16)
        
    def draw(self, screen, navigation_data):
        """Draw compass with ship heading and wind direction"""
        # Create compass surface
        compass_size = (self.radius + 30) * 2
        compass_surface = pygame.Surface((compass_size, compass_size), pygame.SRCALPHA)
        center = compass_size // 2
        
        # Background circle
        pygame.draw.circle(compass_surface, self.colors['background'], 
                          (center, center), self.radius)
        pygame.draw.circle(compass_surface, self.colors['border'], 
                          (center, center), self.radius, 2)
        
        # Draw cardinal directions
        directions = [
            (0, "N", True), (45, "NE", False), (90, "E", True), (135, "SE", False),
            (180, "S", True), (225, "SW", False), (270, "W", True), (315, "NW", False)
        ]
        
        for angle, label, is_cardinal in directions:
            color = self.colors['cardinal'] if is_cardinal else self.colors['intercardinal']
            
            # Calculate position
            angle_rad = math.radians(angle - 90)  # Adjust so 0° is North
            outer_x = center + int(self.radius * 0.9 * math.cos(angle_rad))
            outer_y = center + int(self.radius * 0.9 * math.sin(angle_rad))
            inner_x = center + int(self.radius * 0.7 * math.cos(angle_rad))
            inner_y = center + int(self.radius * 0.7 * math.sin(angle_rad))
            
            # Draw tick mark
            pygame.draw.line(compass_surface, color, (outer_x, outer_y), (inner_x, inner_y), 2)
            
            # Draw label
            text = self.font.render(label, True, color)
            text_rect = text.get_rect(center=(outer_x, outer_y))
            
            # Adjust text position to be outside the circle
            offset_x = int(12 * math.cos(angle_rad))
            offset_y = int(12 * math.sin(angle_rad))
            text_rect.center = (outer_x + offset_x, outer_y + offset_y)
            
            compass_surface.blit(text, text_rect)
        
        # Draw wind direction needle (cyan)
        wind_rad = math.radians(navigation_data.wind_direction - 90)
        wind_end_x = center + int(self.radius * 0.8 * math.cos(wind_rad))
        wind_end_y = center + int(self.radius * 0.8 * math.sin(wind_rad))
        
        pygame.draw.line(compass_surface, self.colors['wind_needle'], 
                        (center, center), (wind_end_x, wind_end_y), 3)
        
        # Draw ship heading needle (red)
        heading_rad = math.radians(navigation_data.ship_heading - 90)
        heading_end_x = center + int(self.radius * 0.6 * math.cos(heading_rad))
        heading_end_y = center + int(self.radius * 0.6 * math.sin(heading_rad))
        
        pygame.draw.line(compass_surface, self.colors['ship_needle'], 
                        (center, center), (heading_end_x, heading_end_y), 4)
        
        # Draw center dot
        pygame.draw.circle(compass_surface, self.colors['ship_needle'], 
                          (center, center), 4)
        
        # Blit to main screen
        screen.blit(compass_surface, (self.x - compass_size // 2, self.y - compass_size // 2))
        
        # Draw compass info below
        info_y = self.y + self.radius + 20
        
        # Ship heading
        heading_text = f"HDG: {navigation_data.ship_heading:.0f}° ({navigation_data.get_compass_bearing()})"
        heading_surface = self.font.render(heading_text, True, self.colors['text'])
        heading_rect = heading_surface.get_rect(center=(self.x, info_y))
        screen.blit(heading_surface, heading_rect)
        
        # Wind info
        wind_text = f"Wind: {navigation_data.wind_direction:.0f}° @ {navigation_data.wind_speed:.1f}kts"
        wind_surface = self.font.render(wind_text, True, self.colors['wind_needle'])
        wind_rect = wind_surface.get_rect(center=(self.x, info_y + 15))
        screen.blit(wind_surface, wind_rect)

class SpeedDisplay:
    """Ship speed and sailing information display"""
    
    def __init__(self, x, y):
        """Initialize speed display"""
        self.x = x
        self.y = y
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
    def draw(self, screen, navigation_data):
        """Draw speed and sailing information"""
        # Speed display
        speed_text = f"Speed: {navigation_data.ship_speed:.1f} kts"
        speed_color = (0, 255, 0) if navigation_data.ship_speed > 2 else (255, 255, 0) if navigation_data.ship_speed > 0 else (255, 0, 0)
        speed_surface = self.font.render(speed_text, True, speed_color)
        screen.blit(speed_surface, (self.x, self.y))
        
        # Point of sail
        point_text = f"Point of Sail: {navigation_data.point_of_sail}"
        point_color = navigation_data.get_point_of_sail_color()
        point_surface = self.font.render(point_text, True, point_color)
        screen.blit(point_surface, (self.x, self.y + 25))
        
        # Wind description
        wind_desc_text = f"Wind: {navigation_data.wind_description}"
        wind_surface = self.small_font.render(wind_desc_text, True, (200, 200, 200))
        screen.blit(wind_surface, (self.x, self.y + 50))
        
        # Apparent wind angle
        apparent_text = f"Apparent Wind: {navigation_data.apparent_wind_angle:.0f}°"
        apparent_surface = self.small_font.render(apparent_text, True, (200, 200, 200))
        screen.blit(apparent_surface, (self.x, self.y + 70))

class WindParticleSystem:
    """Manages wind particle effects"""
    
    def __init__(self, screen_width, screen_height):
        """Initialize particle system"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particles = []
        self.spawn_timer = 0.0
        self.spawn_interval = 0.5  # Spawn particles every 0.5 seconds
        
    def update(self, dt, wind_direction, wind_speed):
        """Update particle system"""
        # Update existing particles
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Spawn new particles
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self.spawn_particles(wind_direction, wind_speed)
    
    def spawn_particles(self, wind_direction, wind_speed):
        """Spawn new wind particles"""
        # Spawn particles from upwind edge of screen
        wind_rad = math.radians(wind_direction + 180)  # Opposite direction for spawn
        
        # Determine spawn edge based on wind direction
        if 45 <= wind_direction < 135:  # Wind from east, spawn from left
            spawn_x = -10
            spawn_y = random.randint(0, self.screen_height)
        elif 135 <= wind_direction < 225:  # Wind from south, spawn from top
            spawn_x = random.randint(0, self.screen_width)
            spawn_y = -10
        elif 225 <= wind_direction < 315:  # Wind from west, spawn from right
            spawn_x = self.screen_width + 10
            spawn_y = random.randint(0, self.screen_height)
        else:  # Wind from north, spawn from bottom
            spawn_x = random.randint(0, self.screen_width)
            spawn_y = self.screen_height + 10
        
        # Create 2-4 particles per spawn
        for _ in range(random.randint(2, 4)):
            particle = WindParticle(
                spawn_x + random.randint(-20, 20),
                spawn_y + random.randint(-20, 20),
                wind_direction,
                wind_speed
            )
            self.particles.append(particle)
    
    def draw(self, screen):
        """Draw all wind particles"""
        for particle in self.particles:
            particle.draw(screen)

class WindVane:
    """Individual wind vane indicator"""
    
    def __init__(self, x, y, wind_direction, wind_speed):
        """Initialize wind vane"""
        self.x = x
        self.y = y
        self.wind_direction = wind_direction
        self.wind_speed = wind_speed
        self.drift_speed = wind_speed * 0.1  # Gentle drift
        self.lifetime = random.uniform(8.0, 12.0)
        self.age = 0.0
        
        # Visual properties based on wind strength
        if wind_speed >= 20:
            self.vane_type = "strong"
            self.size = 25
            self.branches = 5
        elif wind_speed >= 15:
            self.vane_type = "medium"
            self.size = 20
            self.branches = 3
        else:
            self.vane_type = "light"
            self.size = 15
            self.branches = 2
    
    def update(self, dt, current_wind_direction, current_wind_speed):
        """Update wind vane position and properties"""
        self.age += dt
        
        # Update wind direction (vanes respond to wind changes)
        self.wind_direction = current_wind_direction
        self.wind_speed = current_wind_speed
        
        # Gentle drift in wind direction
        wind_rad = math.radians(self.wind_direction)
        self.x += math.cos(wind_rad) * self.drift_speed * dt
        self.y += math.sin(wind_rad) * self.drift_speed * dt
        
        return self.age < self.lifetime
    
    def draw(self, screen):
        """Draw the wind vane"""
        if self.age >= self.lifetime:
            return
        
        # Fade out over time
        fade_factor = 1.0 - (self.age / self.lifetime)
        alpha = int(255 * max(0, fade_factor))
        
        if alpha <= 0:
            return
        
        # Create vane surface for rotation
        vane_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Draw vane shaft
        shaft_color = (200, 200, 200, alpha)
        pygame.draw.line(vane_surface, shaft_color, 
                        (self.size, self.size - self.size // 2), 
                        (self.size, self.size + self.size // 2), 3)
        
        # Draw vane branches
        branch_length = self.size // 3
        for i in range(self.branches):
            branch_y = self.size - self.size // 2 + (i * self.size // self.branches)
            # Left branch
            pygame.draw.line(vane_surface, shaft_color,
                           (self.size, branch_y),
                           (self.size - branch_length, branch_y - branch_length // 2), 2)
            # Right branch
            pygame.draw.line(vane_surface, shaft_color,
                           (self.size, branch_y),
                           (self.size + branch_length, branch_y - branch_length // 2), 2)
        
        # Draw arrow head pointing in wind direction
        arrow_size = 6
        arrow_points = [
            (self.size, self.size - self.size // 2),
            (self.size - arrow_size, self.size - self.size // 2 + arrow_size),
            (self.size + arrow_size, self.size - self.size // 2 + arrow_size)
        ]
        pygame.draw.polygon(vane_surface, shaft_color, arrow_points)
        
        # Rotate vane to match wind direction
        rotated_vane = pygame.transform.rotate(vane_surface, -self.wind_direction + 90)
        
        # Blit to screen
        vane_rect = rotated_vane.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_vane, vane_rect)

class WindVaneSystem:
    """Manages wind vane indicators for strong winds"""
    
    def __init__(self, screen_width, screen_height):
        """Initialize wind vane system"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.wind_vanes = []
        self.spawn_timer = 0.0
        self.spawn_interval = 2.0  # Spawn vanes every 2 seconds during strong wind
        self.strong_wind_threshold = 15.0
        
    def update(self, dt, wind_direction, wind_speed):
        """Update wind vane system"""
        # Update existing vanes
        self.wind_vanes = [vane for vane in self.wind_vanes 
                          if vane.update(dt, wind_direction, wind_speed)]
        
        # Spawn new vanes if wind is strong enough
        if wind_speed > self.strong_wind_threshold:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0.0
                self.spawn_wind_vanes(wind_direction, wind_speed)
        else:
            # Remove vanes if wind drops
            self.wind_vanes = []
    
    def spawn_wind_vanes(self, wind_direction, wind_speed):
        """Spawn new wind vanes across the screen"""
        # Spawn 2-4 vanes randomly across screen
        num_vanes = random.randint(2, 4)
        
        for _ in range(num_vanes):
            # Random position avoiding UI areas
            x = random.randint(100, self.screen_width - 100)
            y = random.randint(100, self.screen_height - 100)
            
            # Avoid overlapping with existing vanes
            too_close = False
            for existing_vane in self.wind_vanes:
                distance = math.sqrt((x - existing_vane.x)**2 + (y - existing_vane.y)**2)
                if distance < 80:  # Minimum distance between vanes
                    too_close = True
                    break
            
            if not too_close:
                vane = WindVane(x, y, wind_direction, wind_speed)
                self.wind_vanes.append(vane)
    
    def draw(self, screen):
        """Draw all wind vanes"""
        for vane in self.wind_vanes:
            vane.draw(screen)

class EnhancedWaveEffect:
    """Enhanced wave effect that responds to wind direction and strength"""
    
    def __init__(self, screen_width, screen_height):
        """Initialize enhanced wave effect"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.wave_offset_x = 0.0
        self.wave_offset_y = 0.0
        self.wave_amplitude = 5
        self.wave_frequency = 0.02
        
    def update(self, dt, wind_direction, wind_speed):
        """Update wave animation based on wind"""
        # Wave movement based on wind direction
        wind_rad = math.radians(wind_direction)
        
        # Scale wave speed with wind strength
        base_speed = 15.0
        wind_factor = min(2.0, wind_speed / 10.0)  # Cap at 2x speed
        wave_speed = base_speed * wind_factor
        
        # Move waves in wind direction
        self.wave_offset_x += math.cos(wind_rad) * wave_speed * dt
        self.wave_offset_y += math.sin(wind_rad) * wave_speed * dt
        
        # Wrap around screen
        self.wave_offset_x = self.wave_offset_x % 100
        self.wave_offset_y = self.wave_offset_y % 100
        
        # Adjust wave properties based on wind strength
        if wind_speed < 5:
            self.wave_amplitude = 2
            self.wave_frequency = 0.01
        elif wind_speed < 12:
            self.wave_amplitude = 5
            self.wave_frequency = 0.02
        else:
            self.wave_amplitude = 8
            self.wave_frequency = 0.03
    
    def draw(self, screen):
        """Draw enhanced wave overlay"""
        # Create wave surface
        wave_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Wave colors based on amplitude (wind strength)
        if self.wave_amplitude <= 2:
            wave_color = (0, 80, 120, 30)  # Light waves
        elif self.wave_amplitude <= 5:
            wave_color = (0, 100, 150, 40)  # Medium waves
        else:
            wave_color = (0, 120, 180, 50)  # Strong waves
        
        # Draw wave pattern
        wave_spacing = 30
        for y in range(-wave_spacing, self.screen_height + wave_spacing, wave_spacing):
            for x in range(-wave_spacing, self.screen_width + wave_spacing, wave_spacing):
                # Calculate wave position with offset
                wave_x = x + int(self.wave_offset_x)
                wave_y = y + int(self.wave_offset_y)
                
                # Add sine wave distortion
                wave_distort = math.sin((wave_x + wave_y) * self.wave_frequency) * self.wave_amplitude
                final_x = wave_x + int(wave_distort)
                final_y = wave_y
                
                # Draw wave line if within screen bounds
                if 0 <= final_x < self.screen_width and 0 <= final_y < self.screen_height:
                    end_x = min(self.screen_width - 1, final_x + 20)
                    pygame.draw.line(wave_surface, wave_color, 
                                   (final_x, final_y), (end_x, final_y), 2)
        
        screen.blit(wave_surface, (0, 0))

class StallWarning:
    """Visual warning when ship is stalled"""
    
    def __init__(self):
        """Initialize stall warning"""
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.flash_timer = 0.0
        
    def update(self, dt):
        """Update warning animation"""
        self.flash_timer += dt
    
    def draw(self, screen, navigation_data, screen_width, screen_height):
        """Draw stall warning if ship is stalled"""
        if not navigation_data.is_stalled:
            return
        
        # Flash effect
        flash_alpha = int(128 + 127 * math.sin(self.flash_timer * 4))
        
        # Warning overlay
        warning_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        warning_color = (255, 0, 0, flash_alpha // 4)
        warning_surface.fill(warning_color)
        screen.blit(warning_surface, (0, 0))
        
        # Warning text
        warning_text = "STALLED - IN NO-GO ZONE"
        warning_surface = self.font.render(warning_text, True, (255, 0, 0))
        warning_rect = warning_surface.get_rect(center=(screen_width // 2, 100))
        screen.blit(warning_surface, warning_rect)
        
        # Instruction text
        instruction_text = "Turn away from the wind to catch it in your sails!"
        instruction_surface = self.small_font.render(instruction_text, True, (255, 255, 0))
        instruction_rect = instruction_surface.get_rect(center=(screen_width // 2, 130))
        screen.blit(instruction_surface, instruction_rect)
        
        # Stall time
        if navigation_data.stall_time > 1:
            time_text = f"Stalled for {navigation_data.stall_time:.1f} seconds"
            time_surface = self.small_font.render(time_text, True, (255, 200, 200))
            time_rect = time_surface.get_rect(center=(screen_width // 2, 160))
            screen.blit(time_surface, time_rect)

class EnhancedWindDisplay:
    """Enhanced wind display with strength and direction info"""
    
    def __init__(self, x, y):
        """Initialize enhanced wind display"""
        self.x = x
        self.y = y
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def draw(self, screen, navigation_data):
        """Draw enhanced wind information"""
        # Wind strength and description
        wind_text = f"Wind: {navigation_data.wind_speed:.1f} knots — {navigation_data.wind_description}"
        wind_surface = self.font.render(wind_text, True, (0, 255, 255))
        screen.blit(wind_surface, (self.x, self.y))
        
        # Point of sail with color coding
        point_text = f"Sailing: {navigation_data.point_of_sail}"
        point_color = navigation_data.get_point_of_sail_color()
        point_surface = self.font.render(point_text, True, point_color)
        screen.blit(point_surface, (self.x, self.y + 25))
        
        # Apparent wind angle
        angle_text = f"Wind Angle: {navigation_data.apparent_wind_angle:.0f}°"
        angle_surface = self.small_font.render(angle_text, True, (200, 200, 200))
        screen.blit(angle_surface, (self.x, self.y + 50))
