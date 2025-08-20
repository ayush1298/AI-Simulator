import pygame
import math
import pygame_gui

# Constants
WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class Pendulum:
    def __init__(self, x, y, length, angle, angular_velocity, mass, gravity, air_resistance, bob_radius, color, trace_length):
        """
        Initializes the Pendulum object.

        Args:
            x (int): X-coordinate of the pivot point.
            y (int): Y-coordinate of the pivot point.
            length (float): Length of the pendulum string.
            angle (float): Initial angle of the pendulum from the vertical (in radians).
            angular_velocity (float): Initial angular velocity (in radians per second).
            mass (float): Mass of the pendulum bob.
            gravity (float): Acceleration due to gravity.
            air_resistance (float): Air resistance coefficient.
            bob_radius (int): Radius of the pendulum bob.
            color (tuple): Color of the pendulum bob (RGB).
            trace_length (int): Maximum length of the trace.
        """
        self.x = x
        self.y = y
        self.length = length
        self.angle = angle
        self.angular_velocity = angular_velocity
        self.mass = mass
        self.gravity = gravity
        self.air_resistance = air_resistance
        self.bob_radius = bob_radius
        self.color = color
        self.trace = []
        self.trace_length = trace_length
        self.kinetic_energy = 0
        self.potential_energy = 0

    def update(self, dt):
        """
        Updates the pendulum's state based on physics equations.

        Args:
            dt (float): Time step (delta time).
        """
        # Calculate angular acceleration
        angular_acceleration = (-self.gravity / self.length) * math.sin(self.angle) - self.air_resistance * self.angular_velocity

        # Update angular velocity and angle
        self.angular_velocity += angular_acceleration * dt
        self.angle += self.angular_velocity * dt

        # Calculate bob position
        bob_x = self.x + self.length * math.sin(self.angle)
        bob_y = self.y + self.length * math.cos(self.angle)

        # Add current bob position to trace
        self.trace.append((bob_x, bob_y))
        if len(self.trace) > self.trace_length:
            self.trace.pop(0)

        # Calculate Kinetic and potential energy
        self.kinetic_energy = 0.5 * self.mass * (self.length * self.angular_velocity)**2
        self.potential_energy = self.mass * self.gravity * self.length * (1 - math.cos(self.angle))


    def draw(self, screen):
        """
        Draws the pendulum on the screen.

        Args:
            screen (pygame.Surface): The PyGame screen to draw on.
        """
        # Calculate bob position
        bob_x = self.x + self.length * math.sin(self.angle)
        bob_y = self.y + self.length * math.cos(self.angle)

        # Draw trace
        for i in range(len(self.trace) - 1):
            pygame.draw.line(screen, BLUE, self.trace[i], self.trace[i+1], 2)

        # Draw string
        pygame.draw.line(screen, BLACK, (self.x, self.y), (bob_x, bob_y), 2)

        # Draw bob
        pygame.draw.circle(screen, self.color, (int(bob_x), int(bob_y)), self.bob_radius)

def main():
    """
    Main function to run the pendulum simulation.
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Interactive Pendulum Simulation")

    # Pygame GUI Manager
    try:
        manager = pygame_gui.UIManager((WIDTH, HEIGHT), 'theme.json')
    except FileNotFoundError:
        print("Warning: 'theme.json' not found. Using default theme.")
        manager = pygame_gui.UIManager((WIDTH, HEIGHT))


    # --- Pendulum Parameters ---
    pivot_x = WIDTH // 2
    pivot_y = HEIGHT // 4
    initial_length = 200
    initial_angle = math.radians(30)
    initial_angular_velocity = 0
    initial_mass = 1
    initial_gravity = 9.81
    initial_air_resistance = 0.1
    bob_radius = 20
    trace_length = 100

    # Initialize Pendulum object
    pendulum = Pendulum(pivot_x, pivot_y, initial_length, initial_angle, initial_angular_velocity, initial_mass, initial_gravity, initial_air_resistance, bob_radius, RED, trace_length)

    # --- GUI Elements ---
    # Initial Angle Slider
    angle_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((10, 10), (200, 20)),
        start_value=math.degrees(initial_angle),
        value_range=(-90, 90),
        manager=manager
    )
    angle_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((220, 10), (50, 20)),
        text="Angle:",
        manager=manager
    )

    # Angular Velocity Slider
    velocity_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((10, 40), (200, 20)),
        start_value=initial_angular_velocity,
        value_range=(-5, 5),
        manager=manager
    )
    velocity_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((220, 40), (80, 20)),
        text="Velocity:",
        manager=manager
    )

    # Mass Slider
    mass_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((10, 70), (200, 20)),
        start_value=initial_mass,
        value_range=(0.1, 5),
        manager=manager
    )
    mass_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((220, 70), (50, 20)),
        text="Mass:",
        manager=manager
    )

    # Gravity Slider
    gravity_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((10, 100), (200, 20)),
        start_value=initial_gravity,
        value_range=(0, 20),
        manager=manager
    )
    gravity_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((220, 100), (60, 20)),
        text="Gravity:",
        manager=manager
    )

    # Air Resistance Slider
    air_resistance_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((10, 130), (200, 20)),
        start_value=initial_air_resistance,
        value_range=(0, 1),
        manager=manager
    )
    air_resistance_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((220, 130), (100, 20)),
        text="Air Resist:",
        manager=manager
    )

    # String Length Slider
    length_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((10, 160), (200, 20)),
        start_value=initial_length,
        value_range=(50, 300),
        manager=manager
    )
    length_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((220, 160), (60, 20)),
        text="Length:",
        manager=manager
    )

     # Trace Length Slider
    trace_length_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((10, 190), (200, 20)),
        start_value=trace_length,
        value_range=(0, 500),
        manager=manager
    )
    trace_length_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((220, 190), (100, 20)),
        text="Trace Length:",
        manager=manager
    )


    # Reset Button
    reset_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((10, 220), (100, 30)),
        text="Reset",
        manager=manager
    )

    # Pause/Resume Button
    pause_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((120, 220), (100, 30)),
        text="Pause",
        manager=manager
    )

    # Display Boxes
    angle_display = pygame_gui.elements.UITextBox(
        relative_rect=pygame.Rect((600, 10), (180, 50)),
        html_text="Angle: ",
        manager=manager
    )

    velocity_display = pygame_gui.elements.UITextBox(
        relative_rect=pygame.Rect((600, 70), (180, 50)),
        html_text="Velocity: ",
        manager=manager
    )

    kinetic_energy_display = pygame_gui.elements.UITextBox(
        relative_rect=pygame.Rect((600, 130), (180, 50)),
        html_text="Kinetic Energy: ",
        manager=manager
    )

    potential_energy_display = pygame_gui.elements.UITextBox(
        relative_rect=pygame.Rect((600, 190), (180, 50)),
        html_text="Potential Energy: ",
        manager=manager
    )

    total_energy_display = pygame_gui.elements.UITextBox(
        relative_rect=pygame.Rect((600, 250), (180, 50)),
        html_text="Total Energy: ",
        manager=manager
    )

    clock = pygame.time.Clock()
    is_running = True
    paused = False

    while is_running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == reset_button:
                        pendulum.angle = math.radians(angle_slider.get_current_value())
                        pendulum.angular_velocity = velocity_slider.get_current_value()
                        pendulum.trace = []  # Clear the trace
                    elif event.ui_element == pause_button:
                        paused = not paused
                        if paused:
                            pause_button.set_text("Resume")
                        else:
                            pause_button.set_text("Pause")
                elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED: #Corrected line
                    if event.ui_element == angle_slider:
                        pendulum.angle = math.radians(angle_slider.get_current_value())
                    elif event.ui_element == velocity_slider:
                        pendulum.angular_velocity = velocity_slider.get_current_value()
                    elif event.ui_element == mass_slider:
                        pendulum.mass = mass_slider.get_current_value()
                    elif event.ui_element == gravity_slider:
                        pendulum.gravity = gravity_slider.get_current_value()
                    elif event.ui_element == air_resistance_slider:
                        pendulum.air_resistance = air_resistance_slider.get_current_value()
                    elif event.ui_element == length_slider:
                        pendulum.length = length_slider.get_current_value()
                    elif event.ui_element == trace_length_slider:
                        pendulum.trace_length = int(trace_length_slider.get_current_value())
                        pendulum.trace = pendulum.trace[-pendulum.trace_length:]


            # Handle GUI events
            manager.process_events(event)

        # Update game state
        if not paused:
            pendulum.update(time_delta)

        # Draw everything
        screen.fill(WHITE)
        pendulum.draw(screen)

        # Update Display Boxes
        angle_display.html_text = f"Angle: {math.degrees(pendulum.angle):.2f} degrees"
        angle_display.rebuild()

        velocity_display.html_text = f"Velocity: {pendulum.angular_velocity:.2f} rad/s"
        velocity_display.rebuild()

        kinetic_energy_display.html_text = f"Kinetic Energy: {pendulum.kinetic_energy:.2f} J"
        kinetic_energy_display.rebuild()

        potential_energy_display.html_text = f"Potential Energy: {pendulum.potential_energy:.2f} J"
        potential_energy_display.rebuild()

        total_energy_display.html_text = f"Total Energy: {pendulum.kinetic_energy + pendulum.potential_energy:.2f} J"
        total_energy_display.rebuild()

        # Update GUI
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()