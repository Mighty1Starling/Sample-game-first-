import pygame
import random
import json
import os

# Инициализация pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60
GAME_TIME = 60

# Цвета
WHITE = (255, 255, 255)
BLUE = (135, 206, 235)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)

# Загрузка шрифтов
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Файл для рекорда
RECORD_FILE = "fish_record.json"

class Fish:
    def __init__(self, x, special=False):
        self.x = x
        self.y = random.randint(120, SCREEN_HEIGHT - 120)
        self.speed = random.randint(2, 5)
        self.special = special

        # Размеры
        self.body_width = 140 if special else 100
        self.body_height = 80 if special else 60

        # Цвета: особые рыбы зелёные, обычные красные
        if self.special:
            self.body_color = (0, 200, 0)      # зелёное тело
        else:
            self.body_color = (200, 50, 50)    # обычные красные

        self.fin_color = (0, 200, 0)          # плавники и хвост зелёные
        self.eye_outer_color = (255, 215, 0)
        self.eye_inner_color = BLACK

        # Прямоугольник для попадания мышью
        self.rect = pygame.Rect(self.x,
                                self.y - self.body_height // 2,
                                self.body_width + 40,
                                self.body_height)

    def update(self):
        self.x += self.speed
        self.rect.x = self.x

    def draw(self, screen):
        cy = self.y
        # Тело
        body_rect = pygame.Rect(self.x, cy - self.body_height // 2,
                                self.body_width, self.body_height)
        pygame.draw.ellipse(screen, self.body_color, body_rect)

        # Хвост (треугольник слева)
        tail_w = self.body_width // 3
        tail_h = self.body_height
        tail_points = [
            (self.x, cy),
            (self.x - tail_w, cy - tail_h // 2),
            (self.x - tail_w, cy + tail_h // 2)
        ]
        pygame.draw.polygon(screen, self.fin_color, tail_points

        # Верхний плавник (треугольник сверху)
        fin_h = self.body_height
        fin_points = [
            (self.x + self.body_width // 3, cy - self.body_height // 2),
            (self.x + self.body_width // 3 + fin_h // 2, cy - self.body_height),
            (self.x + self.body_width // 3 + fin_h, cy - self.body_height // 2)
        ]
        pygame.draw.polygon(screen, self.fin_color, fin_points)

        # Глаз
        eye_cx = self.x + int(self.body_width * 0.8)
        eye_cy = cy
        eye_outer_r = self.body_height // 4
        eye_inner_r = self.body_height // 7
        pygame.draw.circle(screen, self.eye_outer_color, (eye_cx, eye_cy), eye_outer_r)
        pygame.draw.circle(screen, self.eye_inner_color, (eye_cx, eye_cy), eye_inner_r)

    def off_screen(self):
        return self.x > SCREEN_WIDTH + 200


def load_record():
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, 'r') as f:
            return json.load(f).get('record', 0)
    return 0

def save_record(record):
    with open(RECORD_FILE, 'w') as f:
        json.dump({'record': record}, f)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Лови особых рыбок!")
    clock = pygame.time.Clock()

    # Переменные игры
    score = 0
    record = load_record()
    fishes = []
    time_left = GAME_TIME
    game_active = True
    game_over = False
    start_time = pygame.time.get_ticks()

    running = True
    while running:
        screen.fill(BLUE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and game_active:
                mouse_pos = pygame.mouse.get_pos()
                for fish in fishes[:]:
                    if fish.rect.collidepoint(mouse_pos) and fish.special:
                        score += 10
                        fishes.remove(fish)

        if game_active:
            current_time = pygame.time.get_ticks()
            time_left = max(0, GAME_TIME - (current_time - start_time) // 1000)

            # Спавн рыб
            if random.randint(1, 20) == 1:
                special = random.randint(1, 10) == 1  # 10% особых рыб
                fishes.append(Fish(-50, special))

            # Обновление рыб
            for fish in fishes[:]:
                fish.update()
                if fish.off_screen():
                    fishes.remove(fish)

            # Отрисовка
            for fish in fishes:
                fish.draw(screen)

            # UI
            score_text = font.render(f"Очки: {score}", True, BLACK)
            time_text = font.render(f"Время: {time_left}", True, BLACK)
            record_text = small_font.render(f"Рекорд: {record}", True, BLACK)
            screen.blit(score_text, (20, 20))
            screen.blit(time_text, (20, 60))
            screen.blit(record_text, (20, 100))

            if time_left == 0:
                game_active = False
                game_over = True
                if score > record:
                    record = score
                    save_record(record)

        if game_over:
            over_text = font.render("Время вышло!", True, BLACK)
            final_score = font.render(f"Финальный счёт: {score}", True, BLACK)
            new_record = small_font.render("Новый рекорд!" if score > load_record() else "", True, GOLD)
            restart_text = small_font.render("Нажми R для рестарта или ESC для выхода", True, BLACK)
            
            screen.blit(over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
            screen.blit(final_score, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2))
            screen.blit(new_record, (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 + 40))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 + 80))

            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                main()  # Рестарт
                return
            if keys[pygame.K_ESCAPE]:
                running = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
