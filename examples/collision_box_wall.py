import pygame
import sys

# prompt: Create a simple simulation of Newton's 3rd law of motion where a box is colliding with a wall and returning.  It should have options to change the mass of the box, the velocity of the box, and the friction of the ground, and it should show the force and impulse after changing things.

# --- Constants ---
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
GRAVITY = 9.81

# --- Helper Functions ---
def draw_slider(screen, x, y, width, height, value, label, color=BLUE):
    """Draws a slider and its label."""
    pygame.draw.rect(screen, color, (x, y, width, height))
    slider_pos = x + int(value * width) - 5
    pygame.draw.rect(screen, BLACK, (slider_pos, y - 5, 10, height + 10))  # Slider handle

    font = pygame.font.Font(None, 24)
    text_surface = font.render(f"{label}: {value:.2f}", True, BLACK)
    screen.blit(text_surface, (x, y - 30))

def check_slider_click(x, y, width, height, mouse_pos):
    """Checks if the mouse click is within the slider's area."""
    return x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height

def draw_button(screen, x, y, width, height, color, text, text_color, is_active):
    """Draws a button with text."""
    if is_active:
       pygame.draw.rect(screen, GREEN, (x, y, width, height))
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))

    font = pygame.font.Font(None, 24)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

def check_button_click(x, y, width, height, mouse_pos):
    """Checks if the mouse click is within the button's area."""
    return x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height

# --- Classes ---

class Box:
    def __init__(self, x, y, width, height, mass, velocity, color):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.mass = float(mass)
        self.velocity = float(velocity)
        self.color = color

    def update(self, dt, friction, applied_force):
        friction_force = friction * self.mass * GRAVITY
        net_force = applied_force - friction_force

        # Prevent the box from accelerating in the opposite direction due to applied force when friction is greater.
        if self.velocity > 0 and net_force < 0 and abs(net_force) < friction_force:
            net_force = 0
        if self.velocity < 0 and net_force > 0 and abs(net_force) < friction_force:
            net_force = 0

        acceleration = net_force / self.mass
        self.velocity += acceleration * dt
        self.x += self.velocity * dt

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Wall:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

# --- Main Function ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Newton's 3rd Law Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    # --- Initial Values ---
    box_x = 50
    box_y = HEIGHT - 50
    box_width = 50
    box_height = 50
    box_mass = 1.0
    box_velocity = 50.0

    wall_x = WIDTH - 20
    wall_y = 0
    wall_width = 20
    wall_height = HEIGHT

    friction = 0.1
    coefficient_of_restitution = 0.8
    elasticity_on = True
    applied_force = 0.0

    box = Box(box_x, box_y, box_width, box_height, box_mass, box_velocity, RED)
    wall = Wall(wall_x, wall_y, wall_width, wall_height, BLUE)

    # --- UI Elements ---
    slider_width = 200
    slider_height = 20
    mass_slider_x = 50
    mass_slider_y = 50
    velocity_slider_x = 50
    velocity_slider_y = 100
    friction_slider_x = 50
    friction_slider_y = 150
    restitution_slider_x = 50
    restitution_slider_y = 200

    # Button for toggling elasticity
    elasticity_button_x = 50
    elasticity_button_y = 250
    elasticity_button_width = 150
    elasticity_button_height = 30

    # --- Game Loop ---
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # --- Slider Click Handling ---
                if check_slider_click(mass_slider_x, mass_slider_y, slider_width, slider_height, mouse_pos):
                    box_mass = min(max((mouse_pos[0] - mass_slider_x) / slider_width * 5, 0.1), 5)
                    box.mass = box_mass
                if check_slider_click(velocity_slider_x, velocity_slider_y, slider_width, slider_height, mouse_pos):
                    box_velocity = min(max((mouse_pos[0] - velocity_slider_x) / slider_width * 200 - 100, -100), 100)
                    box.velocity = box_velocity
                if check_slider_click(friction_slider_x, friction_slider_y, slider_width, slider_height, mouse_pos):
                    friction = min(max((mouse_pos[0] - friction_slider_x) / slider_width, 0), 1)
                if check_slider_click(restitution_slider_x, restitution_slider_y, slider_width, slider_height, mouse_pos):
                    coefficient_of_restitution = min(max((mouse_pos[0] - restitution_slider_x) / slider_width, 0), 1)

                # --- Button Click Handling ---
                if check_button_click(elasticity_button_x, elasticity_button_y, elasticity_button_width, elasticity_button_height, mouse_pos):
                    elasticity_on = not elasticity_on  # Toggle elasticity state


        keys = pygame.key.get_pressed()
        applied_force = 0  # Reset applied force
        if keys[pygame.K_LEFT]:
            applied_force = -100
        if keys[pygame.K_RIGHT]:
            applied_force = 100

        # --- Update ---
        box.update(dt, friction, applied_force)

        # --- Collision Detection ---
        if box.x + box.width > wall.x:
            box.x = wall.x - box.width
            initial_velocity = box.velocity
            if elasticity_on:
                box.velocity *= -coefficient_of_restitution
            else:
                box.velocity = 0
            final_velocity = box.velocity
            impulse = box.mass * abs(final_velocity - initial_velocity)  # Simplified impulse calculation
            collision_time = 0.01  # Estimated collision time
            try:
                force = impulse / collision_time  # Simplified force calculation
            except ZeroDivisionError:
                force = 0

            collision_happened = True
        else:
            collision_happened = False
            impulse = 0
            force = 0

        # --- Draw ---
        screen.fill(WHITE)
        box.draw(screen)
        wall.draw(screen)

        # --- UI Elements ---
        draw_slider(screen, mass_slider_x, mass_slider_y, slider_width, slider_height, box_mass/5, "Mass")
        draw_slider(screen, velocity_slider_x, velocity_slider_y, slider_width, slider_height, (box_velocity+100)/200, "Velocity")
        draw_slider(screen, friction_slider_x, friction_slider_y, slider_width, slider_height, friction, "Friction")
        draw_slider(screen, restitution_slider_x, restitution_slider_y, slider_width, slider_height, coefficient_of_restitution, "Restitution")

        # --- Elasticity Button ---
        draw_button(screen, elasticity_button_x, elasticity_button_y, elasticity_button_width, elasticity_button_height, GRAY, "Elasticity", BLACK, elasticity_on)


        # --- Text Display ---
        text_color = BLACK
        font = pygame.font.Font(None, 24)

        text_surface = font.render(f"Impulse: {impulse:.2f}", True, text_color)
        screen.blit(text_surface, (50, 300))

        text_surface = font.render(f"Force: {force:.2f}", True, text_color)
        screen.blit(text_surface, (50, 330))

        text_surface = font.render(f"Applied Force: {applied_force:.2f}", True, text_color)
        screen.blit(text_surface, (50, 360))

        # --- Draw Force Vector --- (only if a collision happened)
        if collision_happened:
           force_vector_length = min(force / 10, 50)  # Scale down force for display
           force_vector_x = box.x + box.width
           force_vector_y = box.y + box.height / 2
           pygame.draw.line(screen, GREEN, (force_vector_x, force_vector_y), (force_vector_x - force_vector_length, force_vector_y), 3) # Draw a green line representing the force vector

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()