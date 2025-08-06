#!/usr/bin/env python3
"""
Privateers Legacy - Dock Menu System
Enhanced docking functionality with trading, repairs, and crew recruitment
"""

import pygame
import random
import math

class Commodity:
    """Represents a tradeable commodity"""
    
    def __init__(self, name, base_price, price_variation=0.3):
        """Initialize commodity with name and price range"""
        self.name = name
        self.base_price = base_price
        self.price_variation = price_variation
        self.current_price = self.generate_price()
        self.quantity_available = random.randint(10, 50)
    
    def generate_price(self):
        """Generate current market price with variation"""
        variation = random.uniform(-self.price_variation, self.price_variation)
        return int(self.base_price * (1 + variation))
    
    def refresh_price(self):
        """Refresh commodity price (called when docking)"""
        self.current_price = self.generate_price()
        self.quantity_available = random.randint(10, 50)

class DockMenu:
    """Enhanced dock menu with trading, repairs, and crew recruitment"""
    
    def __init__(self):
        """Initialize dock menu system"""
        self.active = False
        self.current_menu = "main"  # main, trade, repair, crew
        self.selected_option = 0
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.menu_font = pygame.font.Font(None, 32)
        self.info_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Colors
        self.colors = {
            'background': (0, 0, 0, 200),
            'border': (255, 255, 255),
            'title': (255, 255, 0),
            'selected': (255, 255, 0),
            'normal': (255, 255, 255),
            'info': (200, 200, 200),
            'success': (0, 255, 0),
            'error': (255, 0, 0),
            'gold': (255, 215, 0)
        }
        
        # Available commodities
        self.commodities = [
            Commodity("Sugar", 15, 0.4),
            Commodity("Rum", 25, 0.3),
            Commodity("Tobacco", 20, 0.5),
            Commodity("Cotton", 12, 0.3),
            Commodity("Spices", 35, 0.6),
            Commodity("Coffee", 18, 0.4),
            Commodity("Cocoa", 22, 0.5),
            Commodity("Indigo", 30, 0.4)
        ]
        
        # Current trading commodities (3 random ones)
        self.current_commodities = []
        self.player_cargo = {}  # Player's cargo hold
        self.max_cargo = 100
        
        # Menu state
        self.message = ""
        self.message_timer = 0
        self.message_color = (255, 255, 255)
        
        # Trading state
        self.selected_commodity = 0
        self.trade_quantity = 1
        
    def activate(self, ship_crew_system, player_gold):
        """Activate dock menu and refresh market"""
        self.active = True
        self.current_menu = "main"
        self.selected_option = 0
        
        # Refresh market with 3 random commodities
        self.current_commodities = random.sample(self.commodities, 3)
        for commodity in self.current_commodities:
            commodity.refresh_price()
        
        # Initialize cargo if empty
        if not self.player_cargo:
            for commodity in self.commodities:
                self.player_cargo[commodity.name] = 0
    
    def deactivate(self):
        """Deactivate dock menu"""
        self.active = False
        self.current_menu = "main"
        self.message = ""
    
    def handle_input(self, event, ship_crew_system, player_stats):
        """Handle keyboard input for dock menu"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if self.current_menu == "main":
                return self.handle_main_menu_input(event, ship_crew_system, player_stats)
            elif self.current_menu == "trade":
                return self.handle_trade_menu_input(event, player_stats)
            elif self.current_menu == "repair":
                return self.handle_repair_menu_input(event, ship_crew_system, player_stats)
            elif self.current_menu == "crew":
                return self.handle_crew_menu_input(event, ship_crew_system, player_stats)
        
        return None
    
    def handle_main_menu_input(self, event, ship_crew_system, player_stats):
        """Handle main menu input"""
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % 4
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % 4
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            if self.selected_option == 0:  # Trade Goods
                self.current_menu = "trade"
                self.selected_commodity = 0
                self.trade_quantity = 1
            elif self.selected_option == 1:  # Repair Ship
                self.current_menu = "repair"
            elif self.selected_option == 2:  # Recruit Crew
                self.current_menu = "crew"
            elif self.selected_option == 3:  # Leave Port
                self.deactivate()
                return "leave_port"
        elif event.key == pygame.K_ESCAPE:
            self.deactivate()
            return "leave_port"
        
        return None
    
    def handle_trade_menu_input(self, event, player_stats):
        """Handle trade menu input"""
        if event.key == pygame.K_UP:
            self.selected_commodity = (self.selected_commodity - 1) % len(self.current_commodities)
        elif event.key == pygame.K_DOWN:
            self.selected_commodity = (self.selected_commodity + 1) % len(self.current_commodities)
        elif event.key == pygame.K_LEFT:
            self.trade_quantity = max(1, self.trade_quantity - 1)
        elif event.key == pygame.K_RIGHT:
            self.trade_quantity = min(10, self.trade_quantity + 1)
        elif event.key == pygame.K_b:  # Buy
            return self.buy_commodity(player_stats)
        elif event.key == pygame.K_s:  # Sell
            return self.sell_commodity(player_stats)
        elif event.key == pygame.K_ESCAPE:
            self.current_menu = "main"
        
        return None
    
    def handle_repair_menu_input(self, event, ship_crew_system, player_stats):
        """Handle repair menu input"""
        if event.key == pygame.K_r:  # Repair
            return self.repair_ship(player_stats)
        elif event.key == pygame.K_ESCAPE:
            self.current_menu = "main"
        
        return None
    
    def handle_crew_menu_input(self, event, ship_crew_system, player_stats):
        """Handle crew menu input"""
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % 3
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % 3
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            if self.selected_option == 0:  # Recruit 1 crew
                return self.recruit_crew(ship_crew_system, player_stats, 1)
            elif self.selected_option == 1:  # Recruit 3 crew
                return self.recruit_crew(ship_crew_system, player_stats, 3)
            elif self.selected_option == 2:  # Recruit 5 crew
                return self.recruit_crew(ship_crew_system, player_stats, 5)
        elif event.key == pygame.K_ESCAPE:
            self.current_menu = "main"
        
        return None
    
    def buy_commodity(self, player_stats):
        """Buy selected commodity"""
        commodity = self.current_commodities[self.selected_commodity]
        total_cost = commodity.current_price * self.trade_quantity
        
        # Check if player has enough gold
        if player_stats['gold'] < total_cost:
            self.show_message("Not enough gold!", self.colors['error'])
            return None
        
        # Check cargo space
        current_cargo = sum(self.player_cargo.values())
        if current_cargo + self.trade_quantity > self.max_cargo:
            self.show_message("Not enough cargo space!", self.colors['error'])
            return None
        
        # Check commodity availability
        if commodity.quantity_available < self.trade_quantity:
            self.show_message("Not enough in stock!", self.colors['error'])
            return None
        
        # Execute trade
        player_stats['gold'] -= total_cost
        self.player_cargo[commodity.name] += self.trade_quantity
        commodity.quantity_available -= self.trade_quantity
        
        self.show_message(f"Bought {self.trade_quantity} {commodity.name} for {total_cost} gold", 
                         self.colors['success'])
        
        return {'action': 'buy', 'commodity': commodity.name, 'quantity': self.trade_quantity, 'cost': total_cost}
    
    def sell_commodity(self, player_stats):
        """Sell selected commodity"""
        commodity = self.current_commodities[self.selected_commodity]
        
        # Check if player has commodity
        if self.player_cargo.get(commodity.name, 0) < self.trade_quantity:
            self.show_message("You don't have enough to sell!", self.colors['error'])
            return None
        
        # Execute trade
        total_value = commodity.current_price * self.trade_quantity
        player_stats['gold'] += total_value
        self.player_cargo[commodity.name] -= self.trade_quantity
        commodity.quantity_available += self.trade_quantity
        
        self.show_message(f"Sold {self.trade_quantity} {commodity.name} for {total_value} gold", 
                         self.colors['success'])
        
        return {'action': 'sell', 'commodity': commodity.name, 'quantity': self.trade_quantity, 'value': total_value}
    
    def repair_ship(self, player_stats):
        """Repair ship health"""
        max_health = 100
        current_health = player_stats['health']
        
        if current_health >= max_health:
            self.show_message("Ship is already at full health!", self.colors['info'])
            return None
        
        # Calculate repair cost (10 gold per 10 health points)
        health_to_repair = max_health - current_health
        repair_cost = (health_to_repair // 10) * 10 + (10 if health_to_repair % 10 > 0 else 0)
        
        if player_stats['gold'] < repair_cost:
            self.show_message("Not enough gold for repairs!", self.colors['error'])
            return None
        
        # Execute repair
        player_stats['gold'] -= repair_cost
        player_stats['health'] = max_health
        
        self.show_message(f"Ship repaired for {repair_cost} gold!", self.colors['success'])
        
        return {'action': 'repair', 'cost': repair_cost, 'health_restored': health_to_repair}
    
    def recruit_crew(self, ship_crew_system, player_stats, count):
        """Recruit crew members"""
        cost_per_crew = 25
        total_cost = cost_per_crew * count
        
        # Check if player has enough gold
        if player_stats['gold'] < total_cost:
            self.show_message("Not enough gold to recruit crew!", self.colors['error'])
            return None
        
        # Check crew capacity
        current_crew = ship_crew_system.get_crew_count()
        max_crew = ship_crew_system.max_crew
        
        if current_crew + count > max_crew:
            available_slots = max_crew - current_crew
            self.show_message(f"Only {available_slots} crew slots available!", self.colors['error'])
            return None
        
        # Execute recruitment
        player_stats['gold'] -= total_cost
        
        # Add crew members (simplified - you might want to integrate with your crew system)
        recruited = 0
        for _ in range(count):
            if ship_crew_system.get_crew_count() < ship_crew_system.max_crew:
                # This would need to integrate with your actual crew system
                recruited += 1
        
        self.show_message(f"Recruited {recruited} crew members for {total_cost} gold!", 
                         self.colors['success'])
        
        return {'action': 'recruit', 'count': recruited, 'cost': total_cost}
    
    def show_message(self, text, color):
        """Show a temporary message"""
        self.message = text
        self.message_color = color
        self.message_timer = 3.0  # Show for 3 seconds
    
    def update(self, dt):
        """Update dock menu (for message timer)"""
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
    
    def draw(self, screen, ship_crew_system, player_stats):
        """Draw the dock menu"""
        if not self.active:
            return
        
        screen_width, screen_height = screen.get_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill(self.colors['background'])
        screen.blit(overlay, (0, 0))
        
        # Main menu panel
        panel_width = 600
        panel_height = 500
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        # Panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 220))
        pygame.draw.rect(panel_surface, self.colors['border'], 
                        (0, 0, panel_width, panel_height), 3)
        screen.blit(panel_surface, (panel_x, panel_y))
        
        if self.current_menu == "main":
            self.draw_main_menu(screen, panel_x, panel_y, panel_width, panel_height, 
                              ship_crew_system, player_stats)
        elif self.current_menu == "trade":
            self.draw_trade_menu(screen, panel_x, panel_y, panel_width, panel_height, player_stats)
        elif self.current_menu == "repair":
            self.draw_repair_menu(screen, panel_x, panel_y, panel_width, panel_height, player_stats)
        elif self.current_menu == "crew":
            self.draw_crew_menu(screen, panel_x, panel_y, panel_width, panel_height, 
                              ship_crew_system, player_stats)
        
        # Draw message if active
        if self.message and self.message_timer > 0:
            message_surface = self.info_font.render(self.message, True, self.message_color)
            message_rect = message_surface.get_rect(center=(screen_width // 2, screen_height - 50))
            screen.blit(message_surface, message_rect)
    
    def draw_main_menu(self, screen, x, y, width, height, ship_crew_system, player_stats):
        """Draw main dock menu"""
        # Title
        title = self.title_font.render("PORT OF CALL", True, self.colors['title'])
        title_rect = title.get_rect(center=(x + width // 2, y + 50))
        screen.blit(title, title_rect)
        
        # Menu options
        options = [
            "1. Trade Goods",
            "2. Repair Ship",
            "3. Recruit Crew",
            "4. Leave Port"
        ]
        
        for i, option in enumerate(options):
            color = self.colors['selected'] if i == self.selected_option else self.colors['normal']
            option_surface = self.menu_font.render(option, True, color)
            screen.blit(option_surface, (x + 50, y + 120 + i * 40))
        
        # Player stats
        stats_y = y + 300
        stats = [
            f"Gold: {player_stats['gold']}",
            f"Health: {player_stats['health']}/100",
            f"Crew: {ship_crew_system.get_crew_count()}/{ship_crew_system.max_crew}",
            f"Cargo: {sum(self.player_cargo.values())}/{self.max_cargo}"
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = self.info_font.render(stat, True, self.colors['info'])
            screen.blit(stat_surface, (x + 50, stats_y + i * 25))
        
        # Instructions
        instructions = [
            "Use UP/DOWN arrows to navigate",
            "Press ENTER or SPACE to select",
            "Press ESC to leave port"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.small_font.render(instruction, True, self.colors['info'])
            screen.blit(inst_surface, (x + 300, y + 350 + i * 20))
    
    def draw_trade_menu(self, screen, x, y, width, height, player_stats):
        """Draw trading menu"""
        # Title
        title = self.title_font.render("TRADING POST", True, self.colors['title'])
        title_rect = title.get_rect(center=(x + width // 2, y + 30))
        screen.blit(title, title_rect)
        
        # Commodity list
        for i, commodity in enumerate(self.current_commodities):
            color = self.colors['selected'] if i == self.selected_commodity else self.colors['normal']
            
            # Commodity info
            commodity_text = f"{commodity.name}: {commodity.current_price}g each (Stock: {commodity.quantity_available})"
            commodity_surface = self.menu_font.render(commodity_text, True, color)
            screen.blit(commodity_surface, (x + 30, y + 80 + i * 60))
            
            # Player's cargo
            player_amount = self.player_cargo.get(commodity.name, 0)
            cargo_text = f"You have: {player_amount}"
            cargo_surface = self.info_font.render(cargo_text, True, self.colors['info'])
            screen.blit(cargo_surface, (x + 50, y + 105 + i * 60))
        
        # Trade controls
        controls_y = y + 280
        trade_text = f"Quantity: {self.trade_quantity}"
        trade_surface = self.menu_font.render(trade_text, True, self.colors['normal'])
        screen.blit(trade_surface, (x + 30, controls_y))
        
        # Instructions
        instructions = [
            "UP/DOWN: Select commodity",
            "LEFT/RIGHT: Change quantity",
            "B: Buy   S: Sell",
            "ESC: Back to main menu"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.small_font.render(instruction, True, self.colors['info'])
            screen.blit(inst_surface, (x + 30, y + 320 + i * 20))
        
        # Player gold
        gold_text = f"Gold: {player_stats['gold']}"
        gold_surface = self.info_font.render(gold_text, True, self.colors['gold'])
        screen.blit(gold_surface, (x + 400, controls_y))
    
    def draw_repair_menu(self, screen, x, y, width, height, player_stats):
        """Draw repair menu"""
        # Title
        title = self.title_font.render("SHIP REPAIRS", True, self.colors['title'])
        title_rect = title.get_rect(center=(x + width // 2, y + 50))
        screen.blit(title, title_rect)
        
        # Ship status
        current_health = player_stats['health']
        max_health = 100
        health_text = f"Current Health: {current_health}/{max_health}"
        health_surface = self.menu_font.render(health_text, True, self.colors['normal'])
        screen.blit(health_surface, (x + 50, y + 120))
        
        # Health bar
        bar_width = 300
        bar_height = 20
        bar_x = x + 50
        bar_y = y + 160
        
        # Background bar
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        
        # Health fill
        health_ratio = current_health / max_health
        fill_width = int(bar_width * health_ratio)
        health_color = (0, 255, 0) if health_ratio > 0.7 else (255, 255, 0) if health_ratio > 0.3 else (255, 0, 0)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, fill_width, bar_height))
        
        # Repair info
        if current_health < max_health:
            health_to_repair = max_health - current_health
            repair_cost = (health_to_repair // 10) * 10 + (10 if health_to_repair % 10 > 0 else 0)
            
            cost_text = f"Repair Cost: {repair_cost} gold (10 gold per 10 health)"
            cost_surface = self.info_font.render(cost_text, True, self.colors['info'])
            screen.blit(cost_surface, (x + 50, y + 220))
            
            # Repair button
            repair_text = "Press R to repair ship"
            repair_color = self.colors['success'] if player_stats['gold'] >= repair_cost else self.colors['error']
            repair_surface = self.menu_font.render(repair_text, True, repair_color)
            screen.blit(repair_surface, (x + 50, y + 260))
        else:
            full_text = "Ship is at full health!"
            full_surface = self.menu_font.render(full_text, True, self.colors['success'])
            screen.blit(full_surface, (x + 50, y + 220))
        
        # Player gold
        gold_text = f"Gold: {player_stats['gold']}"
        gold_surface = self.info_font.render(gold_text, True, self.colors['gold'])
        screen.blit(gold_surface, (x + 50, y + 320))
        
        # Instructions
        inst_text = "ESC: Back to main menu"
        inst_surface = self.small_font.render(inst_text, True, self.colors['info'])
        screen.blit(inst_surface, (x + 50, y + 400))
    
    def draw_crew_menu(self, screen, x, y, width, height, ship_crew_system, player_stats):
        """Draw crew recruitment menu"""
        # Title
        title = self.title_font.render("CREW RECRUITMENT", True, self.colors['title'])
        title_rect = title.get_rect(center=(x + width // 2, y + 50))
        screen.blit(title, title_rect)
        
        # Current crew status
        current_crew = ship_crew_system.get_crew_count()
        max_crew = ship_crew_system.max_crew
        crew_text = f"Current Crew: {current_crew}/{max_crew}"
        crew_surface = self.menu_font.render(crew_text, True, self.colors['normal'])
        screen.blit(crew_surface, (x + 50, y + 100))
        
        # Recruitment options
        options = [
            "1. Recruit 1 crew member (25 gold)",
            "2. Recruit 3 crew members (75 gold)",
            "3. Recruit 5 crew members (125 gold)"
        ]
        
        for i, option in enumerate(options):
            color = self.colors['selected'] if i == self.selected_option else self.colors['normal']
            option_surface = self.menu_font.render(option, True, color)
            screen.blit(option_surface, (x + 50, y + 150 + i * 40))
        
        # Available slots
        available_slots = max_crew - current_crew
        slots_text = f"Available slots: {available_slots}"
        slots_surface = self.info_font.render(slots_text, True, self.colors['info'])
        screen.blit(slots_surface, (x + 50, y + 280))
        
        # Player gold
        gold_text = f"Gold: {player_stats['gold']}"
        gold_surface = self.info_font.render(gold_text, True, self.colors['gold'])
        screen.blit(gold_surface, (x + 50, y + 320))
        
        # Instructions
        instructions = [
            "UP/DOWN: Select option",
            "ENTER/SPACE: Recruit",
            "ESC: Back to main menu"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.small_font.render(instruction, True, self.colors['info'])
            screen.blit(inst_surface, (x + 50, y + 370 + i * 20))
    
    def get_cargo_summary(self):
        """Get summary of player's cargo"""
        return {name: quantity for name, quantity in self.player_cargo.items() if quantity > 0}
