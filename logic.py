import math
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass


@dataclass
class Ball:
    """Класс, представляющий шарик в игре."""
    x: float
    y: float
    vx: float = 0.0  # Скорость по оси X
    vy: float = 0.0  # Скорость по оси Y
    radius: float = 15.0
    color: Tuple[int, int, int] = (255, 0, 0)  # RGB цвет
    id: int = 0
    
    def update_position(self, dt: float, screen_width: float, screen_height: float):
        """Обновляет позицию шарика с учётом границ экрана."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Отражение от границ экрана
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx = -self.vx
        elif self.x + self.radius >= screen_width:
            self.x = screen_width - self.radius
            self.vx = -self.vx
            
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy = -self.vy
        elif self.y + self.radius >= screen_height:
            self.y = screen_height - self.radius
            self.vy = -self.vy


class GameLogic:
    """Основной класс, управляющий игровой логикой."""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.balls: List[Ball] = []
        self.inventory: List[Ball] = []  # Инвентарь для "всасывания" шариков
        self.next_ball_id = 0
        
        # Зона удаления (правый верхний угол)
        self.delete_zone_size = 100
        self.delete_zone_x = screen_width - self.delete_zone_size
        self.delete_zone_y = 0
        
        # Множество пар шариков, которые уже столкнулись (чтобы избежать множественных смешиваний)
        self.collided_pairs: Set[Tuple[int, int]] = set()
        
    def add_ball(self, x: float, y: float, vx: float = 0.0, vy: float = 0.0, 
                 color: Optional[Tuple[int, int, int]] = None, radius: float = 15.0) -> Ball:
        """Добавляет новый шарик в игру."""
        if color is None:
            color = (255, 0, 0)  # Красный по умолчанию
            
        ball = Ball(x, y, vx, vy, radius, color, self.next_ball_id)
        self.next_ball_id += 1
        self.balls.append(ball)
        return ball
    
    def update(self, dt: float):
        """Обновляет состояние игры за время dt."""
        # Очищаем множество столкновений для нового кадра
        self.collided_pairs.clear()
        
        # Обновляем позиции шариков
        for ball in self.balls:
            ball.update_position(dt, self.screen_width, self.screen_height)
            
            # Проверка попадания в зону удаления
            if self._is_in_delete_zone(ball):
                self.remove_ball(ball)
                continue
        
        # Проверяем столкновения между шариками
        self._check_collisions()
    
    def _is_in_delete_zone(self, ball: Ball) -> bool:
        """Проверяет, находится ли шарик в зоне удаления."""
        return (ball.x >= self.delete_zone_x and 
                ball.y <= self.delete_zone_size and
                ball.x <= self.screen_width and
                ball.y >= 0)
    
    def _check_collisions(self):
        """Проверяет столкновения между шариками и смешивает их цвета."""
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                ball1 = self.balls[i]
                ball2 = self.balls[j]
                
                # Пропускаем, если эта пара уже обрабатывалась
                pair_id = (min(ball1.id, ball2.id), max(ball1.id, ball2.id))
                if pair_id in self.collided_pairs:
                    continue
                
                # Вычисляем расстояние между центрами
                dx = ball2.x - ball1.x
                dy = ball2.y - ball1.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Проверяем столкновение
                if distance < (ball1.radius + ball2.radius):
                    # Шарики столкнулись - смешиваем цвета
                    self._mix_colors(ball1, ball2)
                    self.collided_pairs.add(pair_id)
    
    def _mix_colors(self, ball1: Ball, ball2: Ball):
        """
        Смешивает цвета двух шариков при столкновении.
        Использует математическое усреднение RGB-значений для точного результата.
        """
        r1, g1, b1 = ball1.color
        r2, g2, b2 = ball2.color
        
        # Математическое усреднение RGB-компонентов
        new_r = (r1 + r2) // 2
        new_g = (g1 + g2) // 2
        new_b = (b1 + b2) // 2
        
        # Применяем новый цвет к обоим шарикам
        new_color = (new_r, new_g, new_b)
        ball1.color = new_color
        ball2.color = new_color
    
    def suck_ball(self, mouse_x: float, mouse_y: float, suck_radius: float = 50.0) -> Optional[Ball]:
        """
        "Всасывает" ближайший шарик в инвентарь при наведении мыши.
        Возвращает шарик, если он был добавлен в инвентарь.
        """
        closest_ball = None
        min_distance = suck_radius
        
        for ball in self.balls[:]:  # Копируем список для безопасной итерации
            dx = ball.x - mouse_x
            dy = ball.y - mouse_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < min_distance:
                min_distance = distance
                closest_ball = ball
        
        if closest_ball is not None:
            self.balls.remove(closest_ball)
            self.inventory.append(closest_ball)
            return closest_ball
        
        return None
    
    def spit_ball(self, mouse_x: float, mouse_y: float, vx: float = 0.0, vy: float = 0.0) -> Optional[Ball]:
        """
        "Выплёвывает" шарик из инвентаря обратно на экран.
        Возвращает шарик, если он был выплюнут.
        """
        if not self.inventory:
            return None
        
        ball = self.inventory.pop(0)  # Берем первый шарик из инвентаря
        ball.x = mouse_x
        ball.y = mouse_y
        ball.vx = vx
        ball.vy = vy
        self.balls.append(ball)
        return ball
    
    def remove_ball(self, ball: Ball):
        """Удаляет шарик из игры."""
        if ball in self.balls:
            self.balls.remove(ball)
    
    def get_balls(self) -> List[Ball]:
        """Возвращает список всех шариков на экране."""
        return self.balls.copy()
    
    def get_inventory(self) -> List[Ball]:
        """Возвращает список шариков в инвентаре."""
        return self.inventory.copy()
    
    def get_inventory_size(self) -> int:
        """Возвращает количество шариков в инвентаре."""
        return len(self.inventory)
    
    def is_in_delete_zone(self, x: float, y: float) -> bool:
        """Проверяет, находится ли точка в зоне удаления."""
        return (x >= self.delete_zone_x and 
                y <= self.delete_zone_size and
                x <= self.screen_width and
                y >= 0)
    
    def set_screen_size(self, width: int, height: int):
        """Устанавливает размер экрана."""
        self.screen_width = width
        self.screen_height = height
        self.delete_zone_x = width - self.delete_zone_size

