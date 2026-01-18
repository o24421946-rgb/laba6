import pygame
import random
import sys
from logic import GameLogic

# Конфигурация игры
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
STARTING_BALLS = 10  # Стартовое количество шариков
SUCK_RADIUS = 50  # Радиус всасывания шариков мышью

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DELETE_ZONE_COLOR = (255, 200, 200, 150)  # Полупрозрачный красный
TEXT_COLOR = (50, 50, 50)

# Список начальных цветов для шариков
INITIAL_COLORS = [
    (255, 0, 0),    # Красный
    (0, 255, 0),    # Зелёный
    (0, 0, 255),    # Синий
    (255, 255, 0),  # Жёлтый
    (255, 0, 255),  # Пурпурный
    (0, 255, 255),  # Голубой
    (255, 165, 0),  # Оранжевый
    (128, 0, 128),  # Фиолетовый
]


class Game:
    """Класс для управления игровым окном и графикой."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Игра про шарики")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        # Создаём объект игровой логики
        self.game_logic = GameLogic(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Состояние мыши
        self.mouse_pressed = False
        self.mouse_x = 0
        self.mouse_y = 0
        
        # Инициализация стартовых шариков
        self._initialize_balls()
        
        # Создаём полупрозрачную поверхность для зоны удаления
        self.delete_zone_surface = pygame.Surface((self.game_logic.delete_zone_size, 
                                                   self.game_logic.delete_zone_size),
                                                  pygame.SRCALPHA)
        self.delete_zone_surface.fill(DELETE_ZONE_COLOR)
    
    def _initialize_balls(self):
        """Создаёт стартовое количество шариков со случайными позициями и цветами."""
        for _ in range(STARTING_BALLS):
            x = random.uniform(50, SCREEN_WIDTH - 50)
            y = random.uniform(50, SCREEN_HEIGHT - 50)
            
            # Случайная скорость
            vx = random.uniform(-100, 100)
            vy = random.uniform(-100, 100)
            
            # Случайный цвет из списка начальных цветов
            color = random.choice(INITIAL_COLORS)
            
            # Случайный радиус
            radius = random.uniform(10, 20)
            
            self.game_logic.add_ball(x, y, vx, vy, color, radius)
    
    def handle_events(self):
        """Обрабатывает события игры."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    self.mouse_pressed = True
                    self.mouse_x, self.mouse_y = event.pos
                    # Пытаемся всасывать шарик при нажатии
                    self.game_logic.suck_ball(self.mouse_x, self.mouse_y, SUCK_RADIUS)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Левая кнопка мыши
                    self.mouse_pressed = False
                    # Выплёвываем шарик при отпускании (с небольшой скоростью)
                    if self.game_logic.get_inventory_size() > 0:
                        # Направляем шарик в сторону движения мыши
                        self.game_logic.spit_ball(self.mouse_x, self.mouse_y, 0, 0)
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_x, self.mouse_y = event.pos
                # Продолжаем всасывать, если кнопка зажата
                if self.mouse_pressed:
                    self.game_logic.suck_ball(self.mouse_x, self.mouse_y, SUCK_RADIUS)
        
        return True
    
    def update(self, dt):
        """Обновляет состояние игры."""
        self.game_logic.update(dt)
    
    def draw(self):
        """Отрисовывает игровое поле."""
        # Заливаем экран белым
        self.screen.fill(WHITE)
        
        # Отрисовываем зону удаления (правый верхний угол)
        self.screen.blit(self.delete_zone_surface, 
                        (self.game_logic.delete_zone_x, self.game_logic.delete_zone_y))
        
        # Отрисовываем текст "Удалить" в зоне удаления
        delete_text = self.font.render("Удалить", True, BLACK)
        text_rect = delete_text.get_rect(center=(SCREEN_WIDTH - 50, 25))
        self.screen.blit(delete_text, text_rect)
        
        # Отрисовываем все шарики
        for ball in self.game_logic.get_balls():
            pygame.draw.circle(self.screen, ball.color, (int(ball.x), int(ball.y)), int(ball.radius))
            # Добавляем обводку для лучшей видимости
            pygame.draw.circle(self.screen, BLACK, (int(ball.x), int(ball.y)), int(ball.radius), 1)
        
        # Отрисовываем радиус всасывания, если мышь зажата
        if self.mouse_pressed:
            pygame.draw.circle(self.screen, (200, 200, 200), 
                             (self.mouse_x, self.mouse_y), SUCK_RADIUS, 2)
        
        # Отрисовываем информацию об инвентаре
        inventory_text = self.font.render(f"Инвентарь: {self.game_logic.get_inventory_size()}", 
                                         True, TEXT_COLOR)
        self.screen.blit(inventory_text, (10, 10))
        
        # Отрисовываем количество шариков на экране
        balls_count_text = self.font.render(f"Шариков на экране: {len(self.game_logic.get_balls())}", 
                                           True, TEXT_COLOR)
        self.screen.blit(balls_count_text, (10, 35))
        
        # Инструкции
        instruction_text = self.font.render("ЛКМ - всасывать/выпускать шарики", True, TEXT_COLOR)
        self.screen.blit(instruction_text, (10, SCREEN_HEIGHT - 25))
        
        pygame.display.flip()
    
    def run(self):
        """Основной игровой цикл."""
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Конвертируем миллисекунды в секунды
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
