import pygame
import sys


class Slider:
    def __init__(self, x, y, length, min_value, max_value, default_value):
        self.x = x
        self.y = y
        self.length = length
        self.min_value = min_value
        self.max_value = max_value
        self.value = default_value  # Initial value
        self.handle_radius = 10
        self.grabbed = False

    def draw(self, screen):
        # Draw slider bar
        pygame.draw.line(screen, (255, 255, 255), (self.x, self.y), (self.x + self.length, self.y), 5)

        # Draw handle
        handle_pos = (int(self.x + (self.value - self.min_value) / (self.max_value - self.min_value) * self.length), self.y)
        pygame.draw.circle(screen, (255, 255, 255), handle_pos, self.handle_radius)

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            handle_pos = (int(self.x + (self.value - self.min_value) / (self.max_value - self.min_value) * self.length), self.y)
            if pygame.Rect(handle_pos[0] - self.handle_radius, handle_pos[1] - self.handle_radius,
                           self.handle_radius * 2, self.handle_radius * 2).collidepoint(mouse_x, mouse_y):
                self.grabbed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.grabbed = False

        elif event.type == pygame.MOUSEMOTION and self.grabbed:
            mouse_x, _ = pygame.mouse.get_pos()
            self.value = self.min_value + (mouse_x - self.x) / self.length * (self.max_value - self.min_value)
            self.value = max(self.min_value, min(self.max_value, self.value))  # Clamp value between min and max

    def get_value(self):
        return self.value
