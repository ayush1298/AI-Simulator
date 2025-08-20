import pygame
import sys
import pygame.math
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Newton's Third Law Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class Slider:
    def __init__(self, position, size, min_value, max_value, current_value, label):
        self.position = pygame.math.Vector2(position)
        self.size = pygame.math.Vector2(size)
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = current_value
        self.label = label
        self.handle_color = BLUE
        self.slider_color = GRAY
        self.is_dragging = False
        self.font = pygame.font.Font(None, 20)

    def draw(self, screen):
        # Draw the slider line
        pygame.draw.line(screen, self.slider_color, self.position, self.position + pygame.math.Vector2(self.size.x, 0), 2)
        
        # Calculate handle position
        handle_x = self.position.x + (self.current_value - self.min_value) / (self.max_value - self.min_value) * self.size.x
        handle_position = (handle_x, self.position.y)

        # Draw the handle
        pygame.draw.circle(screen, self.handle_color, handle_position, 8)

        # Draw the label
        label_surface = self.font.render(f"{self.label}: {self.current_value:.2f}", True, BLACK)
        screen.blit(label_surface, (self.position.x, self.position.y - 25))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                handle_x = self.position.x + (self.current_value - self.min_value) / (self.max_value - self.min_value) * self.size.x
                handle_position = pygame.math.Vector2(handle_x, self.position.y)
                mouse_position = pygame.math.Vector2(event.pos)

                if handle_position.distance_to(mouse_position) <= 10:
                    self.is_dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mouse_x = event.pos[0]
                new_value = self.min_value + (mouse_x - self.position.x) / self.size.x * (self.max_value - self.min_value)
                self.current_value = max(self.min_value, min(new_value, self.max_value))

    def get_value(self):
        return self.current_value

class TextDisplay:
    def __init__(self, position, font_size, color, text=""):
        self.position = pygame.math.Vector2(position)
        self.font = pygame.font.Font(None, font_size)
        self.color = color
        self.text = text

    def set_text(self, text):
        self.text = str(text)

    def draw(self, screen):
        text_surface = self.font.render(self.text, True, self.color)
        screen.blit(text_surface, self.position)

class ForceVector:
    def __init__(self, start_position, force, color, scale):
        self.start_position = pygame.math.Vector2(start_position)
        self.force = pygame.math.Vector2(force)
        self.color = color
        self.scale = scale

    def update(self, start_position, force):
        self.start_position = pygame.math.Vector2(start_position)
        self.force = pygame.math.Vector2(force)

    def draw(self, screen):
        end_position = self.start_position + self.force * self.scale
        pygame.draw.line(screen, self.color, self.start_position, end_position, 2)
        pygame.draw.circle(screen, self.color, end_position, 3) # Draw a dot at the end of the vector.

class Box:
    def __init__(self, mass, velocity, position, width, height, color, friction_coefficient):
        self.mass = mass
        self.velocity = pygame.math.Vector2(velocity)
        self.position = pygame.math.Vector2(position)
        self.width = width
        self.height = height
        self.color = color
        self.friction_coefficient = friction_coefficient
        self.net_force = pygame.math.Vector2(0, 0)

    def update(self, dt):
        # Calculate friction force
        friction_force_magnitude = self.friction_coefficient * self.mass * 9.8  # Assuming g = 9.8 m/s^2
        friction_force = -self.velocity.normalize() * friction_force_magnitude if self.velocity.length() > 0 else pygame.math.Vector2(0, 0)

        # Apply friction
        self.apply_force(friction_force, dt)

        # Update position based on velocity and time delta
        self.position += self.velocity * dt
        
        # Basic boundary collision (prevent box from going off-screen)
        if self.position.x < 0:
            self.position.x = 0
            self.velocity.x = -self.velocity.x  # Reverse x velocity
        if self.position.x + self.width > SCREEN_WIDTH:
            self.position.x = SCREEN_WIDTH - self.width
            self.velocity.x = -self.velocity.x # Reverse x velocity
        if self.position.y < 0:
            self.position.y = 0
            self.velocity.y = -self.velocity.y
        if self.position.y + self.height > SCREEN_HEIGHT:
            self.position.y = SCREEN_HEIGHT - self.height
            self.velocity.y = -self.velocity.y

    def apply_force(self, force, dt):
        # Calculate acceleration
        acceleration = force / self.mass

        # Update velocity based on acceleration and time delta
        self.velocity += acceleration * dt

        # Store net force for visualization
        self.net_force = force

    def collide(self, wall, restitution_coefficient):
       # Simple collision: Reverse the x-velocity
        self.velocity.x = -self.velocity.x * restitution_coefficient

        # Calculate impulse (simplified)
        impulse = self.mass * abs(self.velocity.x)  #Approximation
        return impulse
        

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.position.x, self.position.y, self.width, self.height))

class Wall:
    def __init__(self, position, height, width, color, strength):
        self.position = pygame.math.Vector2(position)
        self.height = height
        self.width = width
        self.color = color
        self.strength = strength

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.position.x, self.position.y, self.width, self.height))

    def apply_force(self, force):
        self.strength -= force

    def is_broken(self):
        return self.strength <= 0

class NewtonSimulation:
    def __init__(self):
        pygame.init()
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Initial values
        initial_mass = 1.0
        initial_velocity = 50.0
        initial_restitution = 0.8
        initial_friction = 0.1

        # Create Box, Wall, and UI elements
        self.box = Box(initial_mass, (initial_velocity, 0), (100, SCREEN_HEIGHT // 2 - 25), 50, 50, RED, initial_friction)
        self.wall = Wall((SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 - 50), 100, 20, BLUE, 100)

        # Sliders
        slider_y_offset = 50
        self.mass_slider = Slider((50, slider_y_offset), (200, 20), 0.5, 5.0, initial_mass, "Mass")
        self.velocity_slider = Slider((50, slider_y_offset + 50), (200, 20), -100.0, 100.0, initial_velocity, "Velocity")
        self.restitution_slider = Slider((50, slider_y_offset + 100), (200, 20), 0.0, 1.0, initial_restitution, "Restitution")
        self.friction_slider = Slider((50, slider_y_offset + 150), (200, 20), 0.0, 0.5, initial_friction, "Friction")

        # Text displays
        text_y_offset = 300
        self.force_display = TextDisplay((50, text_y_offset), 20, BLACK, "Force: 0")
        self.impulse_display = TextDisplay((50, text_y_offset + 30), 20, BLACK, "Impulse: 0")
        self.energy_loss_display = TextDisplay((50, text_y_offset + 60), 20, BLACK, "Energy Loss: 0")

        # Force Vector
        self.force_vector = ForceVector((0,0), (0,0), GREEN, 0.1) # Initialize with zero force

        self.running = True

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Time in seconds

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.mass_slider.handle_event(event)
                self.velocity_slider.handle_event(event)
                self.restitution_slider.handle_event(event)
                self.friction_slider.handle_event(event)

            # Update simulation state
            self.box.mass = self.mass_slider.get_value()
            self.box.velocity.x = self.velocity_slider.get_value()
            self.box.friction_coefficient = self.friction_slider.get_value()

            self.box.update(dt)

            # Collision detection
            if self.box.position.x + self.box.width >= self.wall.position.x and \
               self.box.position.x <= self.wall.position.x + self.wall.width and \
               self.box.position.y + self.box.height >= self.wall.position.y and \
               self.box.position.y <= self.wall.position.y + self.wall.height:
                   impulse = self.box.collide(self.wall, self.restitution_slider.get_value())
                   self.impulse_display.set_text(f"Impulse: {impulse:.2f}")
                   self.force_display.set_text(f"Force: {self.box.net_force.length():.2f}")
                   #Very simple energy loss calculation (change in KE after collision)
                   initial_ke = 0.5 * self.box.mass * self.box.velocity.length_squared()
                   self.box.velocity.x = -self.box.velocity.x * self.restitution_slider.get_value() #Reapply velocity after collision
                   final_ke = 0.5 * self.box.mass * self.box.velocity.length_squared()
                   energy_loss = initial_ke - final_ke
                   self.energy_loss_display.set_text(f"Energy Loss: {energy_loss:.2f}")

            # Update force vector
            self.force_vector.update(self.box.position + pygame.math.Vector2(self.box.width / 2, self.box.height/2), self.box.net_force)

            # Drawing
            self.screen.fill(WHITE)
            self.box.draw(self.screen)
            self.wall.draw(self.screen)
            self.force_vector.draw(self.screen)
            self.mass_slider.draw(self.screen)
            self.velocity_slider.draw(self.screen)
            self.restitution_slider.draw(self.screen)
            self.friction_slider.draw(self.screen)
            self.force_display.draw(self.screen)
            self.impulse_display.draw(self.screen)
            self.energy_loss_display.draw(self.screen)
            

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    simulation = NewtonSimulation()
    simulation.run()