import pygame
import random
import sys
import pygame_gui

# Prompt: Create a simple simulation where, on clicking, a ball falls on the ground. Here, there will be parameters like the coefficient of restitution, based on which the rebound is decided, adjusting the speed of balls, no of balls, and the mass of balls.


# I. Project Setup and Core Classes:
# 1. Project Structure: See main.py

# 2. Import Libraries: Done

# 3. Ball Class:
class Ball:
    def __init__(self, x, y, radius, color, mass, velocity_x, velocity_y, restitution_coefficient):
        self.x = float(x)
        self.y = float(y)
        self.radius = int(radius)
        self.color = color
        self.mass = float(mass)
        self.velocity_x = float(velocity_x)
        self.velocity_y = float(velocity_y)
        self.restitution_coefficient = float(restitution_coefficient)
        self.original_color = color  # Store original color for highlighting
        self.highlight_start_time = 0
        self.highlight_duration = 100  # milliseconds

    def update(self, dt, gravity_x, gravity_y):
        self.velocity_x += gravity_x * dt
        self.velocity_y += gravity_y * dt
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        # Collision detection with the ground
        if self.y + self.radius > ground_level:
            self.y = ground_level - self.radius
            self.velocity_y = -self.velocity_y * self.restitution_coefficient
            # Collision highlighting
            self.original_color = self.color
            self.color = WHITE  # Highlight color
            self.highlight_start_time = pygame.time.get_ticks()

        # Simple Wall Collision (left and right)
        if self.x - self.radius < 0:
            self.x = self.radius
            self.velocity_x = -self.velocity_x * self.restitution_coefficient
        if self.x + self.radius > screen_width:
            self.x = screen_width - self.radius
            self.velocity_x = -self.velocity_x * self.restitution_coefficient


    def draw(self, screen):
        # Restore original color after highlight duration
        if self.highlight_start_time != 0 and pygame.time.get_ticks() - self.highlight_start_time > self.highlight_duration:
            self.color = self.original_color
            self.highlight_start_time = 0
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


# II. Simulation Environment and Parameters:
# 1. Screen Setup:
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bouncing Ball Simulation")

# 2. Color Definitions:
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0,255,0)

# 3. Simulation Parameters:
num_balls = 5
gravity_x = 0.0
gravity_y = 500.0
dt = 0.02
ground_level = screen_height - 50
ball_defaults = {
    'radius': 20,
    'mass': 1.0,
    'restitution_coefficient': 0.7,
}
force_scale = 1000.0

# 4. Ball List:
balls = []

# III. Initial Ball Creation and Management:
# 1. create_ball() Function:
def create_ball(x, y):
    radius = random.randint(15, 25)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    mass = random.uniform(0.5, 1.5)
    velocity_x = random.uniform(-100, 100)
    velocity_y = random.uniform(-300, -100)
    restitution_coefficient = random.uniform(0.3, 0.9)
    ball = Ball(x, y, radius, color, mass, velocity_x, velocity_y, restitution_coefficient)
    balls.append(ball)


# 2. Initial Ball Generation:
for _ in range(num_balls):
    create_ball(random.randint(50, screen_width - 50), random.randint(50, 150))

# IV. Main Game Loop:
clock = pygame.time.Clock()
running = True

# V. Interactive Features:

# VI. UI Elements:
manager = pygame_gui.UIManager((screen_width, screen_height))

# Create UI elements
num_balls_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 10), (150, 20)),
                                                text="Number of Balls:",
                                                manager=manager)
num_balls_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170, 10), (50, 20)),
                                                    manager=manager)
num_balls_entry.set_text(str(num_balls))

gravity_x_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 40), (100, 20)),
                                                text="Gravity X:",
                                                manager=manager)
gravity_x_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120, 40), (50, 20)),
                                                    manager=manager)
gravity_x_entry.set_text(str(gravity_x))

gravity_y_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 70), (100, 20)),
                                                text="Gravity Y:",
                                                manager=manager)
gravity_y_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120, 70), (50, 20)),
                                                    manager=manager)
gravity_y_entry.set_text(str(gravity_y))


force_scale_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 100), (100, 20)),
                                               text="Force Scale:",
                                               manager=manager)

force_scale_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((120, 100), (150, 20)),
                                                              start_value=force_scale, value_range=(0, 2000),
                                                              manager=manager)

restitution_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 130), (150, 20)),
                                               text="Restitution:",
                                               manager=manager)

restitution_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((120, 130), (150, 20)),
                                                              start_value=ball_defaults['restitution_coefficient'], value_range=(0, 1),
                                                              manager=manager)




def handle_input():
    global running, balls
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            create_ball(mouse_x, mouse_y)

        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == num_balls_entry:
                try:
                    global num_balls
                    num_balls = int(num_balls_entry.get_text())
                    # Regenerate balls based on the new number
                    balls = []  # Clear existing balls
                    for _ in range(num_balls):
                        create_ball(random.randint(50, screen_width - 50), random.randint(50, 150))
                except ValueError:
                    print("Invalid input for number of balls.  Using defaults.") #Basic Error Handling
                    num_balls_entry.set_text(str(num_balls)) #Reset Text

            elif event.ui_element == gravity_x_entry:
                try:
                    global gravity_x
                    gravity_x = float(gravity_x_entry.get_text())
                except ValueError:
                    print("Invalid input for gravity_x. Using defaults.")
                    gravity_x_entry.set_text(str(gravity_x))

            elif event.ui_element == gravity_y_entry:
                try:
                    global gravity_y
                    gravity_y = float(gravity_y_entry.get_text())
                except ValueError:
                    print("Invalid input for gravity_y. Using defaults.")
                    gravity_y_entry.set_text(str(gravity_y))


        manager.process_events(event)


def update_simulation(dt):
    global force_scale
    # Interactive Force Application:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()  # Returns a tuple (left, middle, right)

    for ball in balls:
        # Apply force if mouse button is held and mouse is near the ball.
        if mouse_buttons[0]:  # Left mouse button
            distance_x = mouse_x - ball.x
            distance_y = mouse_y - ball.y
            distance = (distance_x**2 + distance_y**2)**0.5
            if distance < 50: # Threshold distance
                # Apply force proportional to the distance vector
                ball.velocity_x += distance_x * force_scale * dt / ball.mass
                ball.velocity_y += distance_y * force_scale * dt / ball.mass

        ball.update(dt, gravity_x, gravity_y)

def draw_screen():
    screen.fill(BLACK)
    pygame.draw.rect(screen, GREEN, (0, ground_level, screen_width, screen_height - ground_level)) # Ground
    for ball in balls:
        ball.draw(screen)

    manager.draw_ui(screen)
    pygame.display.flip()


# Main Game Loop
while running:
    time_delta = clock.tick(60)/1000.0
    handle_input()
    update_simulation(dt)
    draw_screen()

    # Update UI elements
    force_scale = force_scale_slider.get_current_value()
    ball_defaults['restitution_coefficient'] = restitution_slider.get_current_value()
    manager.update(time_delta)



pygame.quit()
sys.exit()