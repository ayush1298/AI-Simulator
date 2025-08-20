import pygame
import math

# Initialize PyGame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Projectile Motion Simulation")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
grey = (128,128,128)

# Classes

class Projectile:
    def __init__(self, x, y, velocity, angle, mass, gravity, air_resistance, wind_speed):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.angle = angle
        self.mass = mass
        self.gravity = gravity
        self.air_resistance = air_resistance
        self.wind_speed = wind_speed
        self.velocity_x = velocity * math.cos(math.radians(angle))
        self.velocity_y = -velocity * math.sin(math.radians(angle)) #Negative for standard coordinate system
        self.radius = 10
        self.color = red
        self.time = 0
        self.launched = True
        self.trajectory = []


    def update(self, dt):
        # Physics equations here (integrate air resistance and wind)
        if self.launched:
            self.velocity_x -= self.air_resistance * self.velocity_x * dt
            self.velocity_x += self.wind_speed * dt
            self.velocity_y += self.gravity * dt - self.air_resistance * self.velocity_y * dt

            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            self.time += dt
            self.trajectory.append((int(self.x), int(self.y)))

    def draw(self, screen):
        if self.launched:
          pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.time = 0
        self.launched = False
        self.trajectory = []



class Cannon:
    def __init__(self, x, y, angle, length, color):
        self.x = x
        self.y = y
        self.angle = angle
        self.length = length
        self.color = color

    def draw(self, screen):
        end_x = self.x + self.length * math.cos(math.radians(self.angle))
        end_y = self.y - self.length * math.sin(math.radians(self.angle))  # Negative for standard coordinate system
        pygame.draw.line(screen, self.color, (self.x, self.y), (end_x, end_y), 5)

    def adjust_angle(self, mouse_position):
         dx = mouse_position[0] - self.x
         dy = self.y - mouse_position[1] # Correct for standard coordinate system
         self.angle = math.degrees(math.atan2(dy, dx))



class Target:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.dragging = False #to track if the target is being dragged

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def is_over(self, mouse_position):
        distance = math.sqrt((self.x - mouse_position[0])**2 + (self.y - mouse_position[1])**2)
        return distance <= self.radius

    def update_position(self, mouse_position):
        self.x = mouse_position[0]
        self.y = mouse_position[1]



class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, color, handle_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = initial_val
        self.color = color
        self.handle_color = handle_color
        self.handle_pos = self.x + (self.current_val - self.min_val) / (self.max_val - self.min_val) * self.width
        self.is_dragging = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(screen, self.handle_color, (int(self.handle_pos), int(self.y + self.height // 2)), self.height // 2)

    def update(self, mouse_position):
        if self.is_dragging:
            self.handle_pos = mouse_position[0]
            if self.handle_pos < self.x:
                self.handle_pos = self.x
            elif self.handle_pos > self.x + self.width:
                self.handle_pos = self.x + self.width
            self.current_val = self.min_val + (self.handle_pos - self.x) / self.width * (self.max_val - self.min_val)

    def is_over(self, mouse_position):
        return self.x <= mouse_position[0] <= self.x + self.width and self.y <= mouse_position[1] <= self.y + self.height


class Button:
    def __init__(self, x, y, width, height, color, text, text_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font(None, 24)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)

    def is_over(self, mouse_position):
        return self.x <= mouse_position[0] <= self.x + self.width and self.y <= mouse_position[1] <= self.y + self.height


# Game objects
cannon = Cannon(50, screen_height - 50, 45, 50, green)
projectile = None  # Initially no projectile
target = Target(600, screen_height - 50, 20, blue)

# Sliders
velocity_slider = Slider(100, 50, 200, 10, 0, 100, 50, white, blue)
angle_slider = Slider(100, 80, 200, 10, 0, 90, 45, white, blue)
mass_slider = Slider(100, 110, 200, 10, 0.1, 10, 1, white, blue)
gravity_slider = Slider(100, 140, 200, 10, 0, 20, 9.81, white, blue)
air_resistance_slider = Slider(100, 170, 200, 10, 0, 1, 0.1, white, blue)
wind_speed_slider = Slider(100, 200, 200, 10, -10, 10, 0, white, blue)


# Buttons
launch_button = Button(100, 230, 80, 30, green, "Launch", white)
reset_button = Button(200, 230, 80, 30, red, "Reset", white)

# Font
font = pygame.font.Font(None, 24)


# Function to calculate predicted trajectory
def calculate_trajectory(velocity, angle, gravity, air_resistance, wind_speed, cannon_x, cannon_y):
    trajectory = []
    x = cannon_x
    y = cannon_y
    velocity_x = velocity * math.cos(math.radians(angle))
    velocity_y = -velocity * math.sin(math.radians(angle))
    t = 0
    dt = 0.1

    while y < screen_height:
        velocity_x -= air_resistance * velocity_x * dt
        velocity_x += wind_speed * dt
        velocity_y += gravity * dt - air_resistance * velocity_y * dt

        x += velocity_x * dt
        y += velocity_y * dt
        trajectory.append((x, y))
        t += dt
        if x < 0 or x > screen_width:
            break

    return trajectory


# Game loop
running = True
clock = pygame.time.Clock()
collision = False #to track collision with the target
ground_collision = False # to track collision with the ground

while running:
    dt = clock.tick(60) / 1000  # Time in seconds

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if launch_button.is_over(mouse_pos):
                # Launch projectile
                if projectile is None or not projectile.launched:  # Only launch if no projectile exists or the old one is not launched
                    initial_velocity = velocity_slider.current_val
                    launch_angle = angle_slider.current_val
                    mass = mass_slider.current_val
                    gravity = gravity_slider.current_val
                    air_resistance = air_resistance_slider.current_val
                    wind_speed = wind_speed_slider.current_val

                    projectile = Projectile(cannon.x + cannon.length * math.cos(math.radians(cannon.angle)),
                                            cannon.y - cannon.length * math.sin(math.radians(cannon.angle)),
                                            initial_velocity, launch_angle, mass, gravity, air_resistance, wind_speed)
            elif reset_button.is_over(mouse_pos):
                # Reset projectile
                if projectile:
                   projectile.reset(cannon.x + cannon.length * math.cos(math.radians(cannon.angle)),
                                            cannon.y - cannon.length * math.sin(math.radians(cannon.angle)))
                collision = False
                ground_collision = False
            elif velocity_slider.is_over(mouse_pos):
                velocity_slider.is_dragging = True
            elif angle_slider.is_over(mouse_pos):
                angle_slider.is_dragging = True
            elif mass_slider.is_over(mouse_pos):
                mass_slider.is_dragging = True
            elif gravity_slider.is_over(mouse_pos):
                gravity_slider.is_dragging = True
            elif air_resistance_slider.is_over(mouse_pos):
                air_resistance_slider.is_dragging = True
            elif wind_speed_slider.is_over(mouse_pos):
                wind_speed_slider.is_dragging = True
            elif target.is_over(mouse_pos):
                target.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            velocity_slider.is_dragging = False
            angle_slider.is_dragging = False
            mass_slider.is_dragging = False
            gravity_slider.is_dragging = False
            air_resistance_slider.is_dragging = False
            wind_speed_slider.is_dragging = False
            target.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            cannon.adjust_angle(mouse_pos)
            if velocity_slider.is_dragging:
                velocity_slider.update(mouse_pos)
            if angle_slider.is_dragging:
                angle_slider.update(mouse_pos)
            if mass_slider.is_dragging:
                mass_slider.update(mouse_pos)
            if gravity_slider.is_dragging:
                gravity_slider.update(mouse_pos)
            if air_resistance_slider.is_dragging:
                air_resistance_slider.update(mouse_pos)
            if wind_speed_slider.is_dragging:
                wind_speed_slider.update(mouse_pos)
            if target.dragging:
                target.update_position(mouse_pos)


    # Update game objects
    if projectile and projectile.launched:
        projectile.update(dt)

        # Collision detection
        distance = math.sqrt((projectile.x - target.x)**2 + (projectile.y - target.y)**2)
        if distance <= projectile.radius + target.radius:
            collision = True
            projectile.launched = False #stop the projectile
        if projectile.y >= screen_height - projectile.radius:
            ground_collision = True
            projectile.launched = False #stop the projectile


    # Drawing
    screen.fill(black)

    # Draw predicted trajectory
    predicted_trajectory = calculate_trajectory(velocity_slider.current_val, angle_slider.current_val,
                                              gravity_slider.current_val, air_resistance_slider.current_val,
                                              wind_speed_slider.current_val,
                                              cannon.x + cannon.length * math.cos(math.radians(cannon.angle)),
                                              cannon.y - cannon.length * math.sin(math.radians(cannon.angle))) # cannon.x, cannon.y) # corrected parameters
    for point in predicted_trajectory:
        pygame.draw.circle(screen, grey, (int(point[0]), int(point[1])), 2) #draw small dots

    # Draw actual trajectory
    if projectile:
        for point in projectile.trajectory:
            pygame.draw.circle(screen, red, point, 2)

    cannon.draw(screen)
    if projectile:
        projectile.draw(screen)
    target.draw(screen)

    velocity_slider.draw(screen)
    angle_slider.draw(screen)
    mass_slider.draw(screen)
    gravity_slider.draw(screen)
    air_resistance_slider.draw(screen)
    wind_speed_slider.draw(screen)

    launch_button.draw(screen)
    reset_button.draw(screen)


    # Display real-time data
    if projectile and projectile.launched:
        x_pos_text = font.render(f"X: {projectile.x:.2f}", True, white)
        y_pos_text = font.render(f"Y: {projectile.y:.2f}", True, white)
        x_vel_text = font.render(f"Vx: {projectile.velocity_x:.2f}", True, white)
        y_vel_text = font.render(f"Vy: {projectile.velocity_y:.2f}", True, white)
        time_text = font.render(f"Time: {projectile.time:.2f}", True, white)
        potential_energy = projectile.mass * projectile.gravity * (screen_height - projectile.y) if projectile.y < screen_height else 0
        kinetic_energy = 0.5 * projectile.mass * (projectile.velocity_x**2 + projectile.velocity_y**2)
        pe_text = font.render(f"PE: {potential_energy:.2f}", True, white)
        ke_text = font.render(f"KE: {kinetic_energy:.2f}", True, white)

        screen.blit(x_pos_text, (400, 50))
        screen.blit(y_pos_text, (400, 80))
        screen.blit(x_vel_text, (400, 110))
        screen.blit(y_vel_text, (400, 140))
        screen.blit(time_text, (400, 170))
        screen.blit(pe_text, (400, 200))
        screen.blit(ke_text, (400, 230))


    if collision:
        collision_text = font.render("Target Hit!", True, green)
        screen.blit(collision_text, (400, 260))

    if ground_collision:
        ground_collision_text = font.render("Ground Hit!", True, red)
        screen.blit(ground_collision_text, (400, 290))

    pygame.display.flip()

pygame.quit()