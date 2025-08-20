import pygame
import random
import math

# prompt : Create a simple simulation where, on clicking, a ball falls on the ground. Here, there will be parameters like the coefficient of restitution, based on which the rebound is decided, adjusting the speed of balls, no of balls, and the mass of balls.

# Initialize Pygame
pygame.init()

# --- Screen dimensions ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bouncing Ball Simulation")

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# --- Constants ---
GRAVITY = 981  # Acceleration due to gravity (pixels/second^2)
FPS = 60

# --- Helper Functions ---
def clamp(value, min_value, max_value):
    """Clamps a value between a minimum and maximum value."""
    return max(min_value, min(value, max_value))


# --- Classes ---
class Ball:
    def __init__(self, x, y, radius, mass, velocity_x, velocity_y, color, restitution):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color
        self.restitution = restitution

    def move(self, dt):
        """Updates the ball's position based on velocity and gravity."""
        self.velocity_y += GRAVITY * dt
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

    def draw(self, screen):
        """Draws the ball on the screen."""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))


class Ground:
    def __init__(self, y, color, bounciness, friction, angle):
        self.y = y
        self.color = color
        self.bounciness = bounciness
        self.friction = friction
        self.angle = angle

    def draw(self, screen):
        """Draws the ground on the screen, taking into account the angle."""
        # Calculate the points for the ground based on the angle
        ground_width = SCREEN_WIDTH * 2  # Extend beyond the screen edges
        x_offset = SCREEN_WIDTH / 2  # Center the ground

        p1 = (int(x_offset - ground_width / 2), int(self.y + math.tan(math.radians(self.angle)) * (-ground_width / 2)))
        p2 = (int(x_offset + ground_width / 2), int(self.y + math.tan(math.radians(self.angle)) * (ground_width / 2)))

        pygame.draw.line(screen, self.color, p1, p2, 5) # Draw the ground line


class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.percentage = (initial_val - min_val) / (max_val - min_val)
        self.thumb_pos = x + self.percentage * width
        self.dragging = False
        self.label = label
        self.font = pygame.font.Font(None, 20)

    def handle_event(self, event):
        """Handles mouse events for the slider."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x = event.pos[0]
                self.thumb_pos = clamp(mouse_x, self.rect.left, self.rect.right)
                self.percentage = (self.thumb_pos - self.rect.left) / self.rect.width
                self.val = self.min_val + self.percentage * (self.max_val - self.min_val)
                self.val = clamp(self.val, self.min_val, self.max_val) # Ensure value is within bounds

    def draw(self, screen):
        """Draws the slider and its label on the screen."""
        pygame.draw.rect(screen, GRAY, self.rect)
        thumb_rect = pygame.Rect(int(self.thumb_pos) - 5, self.rect.y - 5, 10, self.rect.height + 10)
        pygame.draw.rect(screen, RED, thumb_rect)

        # Render the label and current value
        text_surface = self.font.render(f"{self.label}: {self.val:.2f}", True, WHITE)
        screen.blit(text_surface, (self.rect.x, self.rect.y - 25))

    def get_value(self):
        """Returns the current value of the slider."""
        return self.val

class Button:
    def __init__(self, x, y, width, height, color, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.action = action
        self.font = pygame.font.Font(None, 24)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.action()  # Execute the button's action

# --- Main Program ---
def main():
    clock = pygame.time.Clock()

    # --- Ball list ---
    balls = []

    # --- Ground ---
    ground = Ground(SCREEN_HEIGHT - 100, GREEN, 0.8, 0.1, 0) # Initial ground

    # --- UI Elements ---
    ball_restitution_slider = Slider(20, 20, 200, 20, 0.0, 1.0, 0.7, "Ball Restitution")
    ball_mass_slider = Slider(20, 60, 200, 20, 0.1, 10.0, 1.0, "Ball Mass")
    num_balls_slider = Slider(20, 100, 200, 20, 1, 10, 1, "Balls per Click")
    ground_bounciness_slider = Slider(20, 140, 200, 20, 0.0, 1.0, 0.8, "Ground Bounciness")
    ground_friction_slider = Slider(20, 180, 200, 20, 0.0, 1.0, 0.1, "Ground Friction")
    ground_angle_slider = Slider(20, 220, 200, 20, -45, 45, 0, "Ground Angle")
    horizontal_velocity_slider = Slider(20, 260, 200, 20, -200, 200, 0, "Horizontal Velocity")
    ball_radius_slider = Slider(20, 300, 200, 20, 10, 50, 20, "Ball Radius")
    ball_elasticity_slider = Slider(20, 340, 200, 20, 0.0, 1.0, 0.9, "Ball Elasticity")

    def reset_balls():
        """Clears all balls from the screen."""
        balls.clear()

    reset_button = Button(20, 380, 100, 30, BLUE, "Reset", reset_balls)


    # --- Game loop ---
    running = True
    while running:
        dt = clock.tick(FPS) / 1000  # Delta time in seconds

        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Create new balls at the mouse position
                    x, y = event.pos
                    num_balls = int(num_balls_slider.get_value())
                    for _ in range(num_balls):
                        radius = ball_radius_slider.get_value()
                        mass = ball_mass_slider.get_value()
                        velocity_x = horizontal_velocity_slider.get_value()
                        velocity_y = -200  # Initial upward velocity
                        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                        restitution = ball_restitution_slider.get_value()
                        ball = Ball(x, y, radius, mass, velocity_x, velocity_y, color, restitution)
                        balls.append(ball)

            ball_restitution_slider.handle_event(event)
            ball_mass_slider.handle_event(event)
            num_balls_slider.handle_event(event)
            ground_bounciness_slider.handle_event(event)
            ground_friction_slider.handle_event(event)
            ground_angle_slider.handle_event(event)
            horizontal_velocity_slider.handle_event(event)
            ball_radius_slider.handle_event(event)
            ball_elasticity_slider.handle_event(event)
            reset_button.handle_event(event)

        # --- Update game logic ---
        ground.bounciness = ground_bounciness_slider.get_value()
        ground.friction = ground_friction_slider.get_value()
        ground.angle = ground_angle_slider.get_value()

        for i, ball in enumerate(balls):
            ball.move(dt)

            # --- Ground collision detection ---
            # Calculate the ground line equation (y = mx + b)
            angle_rad = math.radians(ground.angle)
            m = math.tan(angle_rad) # Slope
            b = ground.y - m * (SCREEN_WIDTH / 2) # Intercept

            # Calculate the expected y position of the ground at the ball's x position.
            ground_y = m * ball.x + b

            if ball.y + ball.radius >= ground_y:
                # Calculate the component of the velocity normal to the ground
                normal_x = -math.sin(angle_rad)
                normal_y = math.cos(angle_rad)
                
                # Calculate the dot product of the ball's velocity and the normal vector
                v_dot_n = ball.velocity_x * normal_x + ball.velocity_y * normal_y

                # Reverse the normal component of the velocity and apply restitution
                ball.velocity_x -= (1 + ball.restitution * ground.bounciness) * v_dot_n * normal_x
                ball.velocity_y -= (1 + ball.restitution * ground.bounciness) * v_dot_n * normal_y

                # Apply friction to the tangential component of the velocity
                tangent_x = math.cos(angle_rad)
                tangent_y = math.sin(angle_rad)
                v_dot_t = ball.velocity_x * tangent_x + ball.velocity_y * tangent_y
                ball.velocity_x -= v_dot_t * tangent_x * ground.friction
                ball.velocity_y -= v_dot_t * tangent_y * ground.friction

                # Prevent ball from sinking into the ground
                ball.y = ground_y - ball.radius

            # --- Ball-Ball collision detection ---
            for j in range(i + 1, len(balls)):  # Check collisions with other balls
                ball2 = balls[j]
                dx = ball2.x - ball.x
                dy = ball2.y - ball.y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance < ball.radius + ball2.radius:
                    # Collision detected

                    # Calculate the collision normal vector
                    normal_x = dx / distance
                    normal_y = dy / distance

                    # Calculate the relative velocity along the normal
                    relative_velocity_x = ball.velocity_x - ball2.velocity_x
                    relative_velocity_y = ball.velocity_y - ball2.velocity_y
                    v_dot_n = relative_velocity_x * normal_x + relative_velocity_y * normal_y

                    if v_dot_n < 0:  # Only apply impulse if balls are approaching
                        # Calculate the impulse magnitude
                        elasticity = ball_elasticity_slider.get_value()
                        j = -(1 + elasticity) * v_dot_n / (1 / ball.mass + 1 / ball2.mass)

                        # Apply the impulse to update velocities
                        ball.velocity_x += j * normal_x / ball.mass
                        ball.velocity_y += j * normal_y / ball.mass
                        ball2.velocity_x -= j * normal_x / ball2.mass
                        ball2.velocity_y -= j * normal_y / ball2.mass


            # --- Screen boundary collision detection ---
            if ball.x - ball.radius < 0:
                ball.x = ball.radius
                ball.velocity_x *= -ball.restitution
            elif ball.x + ball.radius > SCREEN_WIDTH:
                ball.x = SCREEN_WIDTH - ball.radius
                ball.velocity_x *= -ball.restitution
            if ball.y - ball.radius < 0:
                ball.y = ball.radius
                ball.velocity_y *= -ball.restitution

        # --- Draw everything ---
        screen.fill(BLACK)  # Clear the screen

        ground.draw(screen)

        for ball in balls:
            ball.draw(screen)

        ball_restitution_slider.draw(screen)
        ball_mass_slider.draw(screen)
        num_balls_slider.draw(screen)
        ground_bounciness_slider.draw(screen)
        ground_friction_slider.draw(screen)
        ground_angle_slider.draw(screen)
        horizontal_velocity_slider.draw(screen)
        ball_radius_slider.draw(screen)
        ball_elasticity_slider.draw(screen)
        reset_button.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()