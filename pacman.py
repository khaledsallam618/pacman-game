import pygame
import random
import os

TILE_SIZE = 40 
OFFSET_Y = 60   
SCREEN_WIDTH = 26 * TILE_SIZE  
SCREEN_HEIGHT = 17 * TILE_SIZE + OFFSET_Y  
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
VIOLET = (148, 0, 211)

class Player:
    def __init__(self, x, y, img=None):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.image = img
        self.lives = 3
        self.power_timer = 0

    def move(self, dx, dy, bricks):
        test_rect = self.rect.move(dx * TILE_SIZE, dy * TILE_SIZE)
        if not any(test_rect.colliderect(b.rect) for b in bricks):
            self.rect = test_rect

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, YELLOW, self.rect)


class Brick:
    def __init__(self, x, y, img=None):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.image = img

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, BLUE, self.rect)


class Apple:
    def __init__(self, x, y, img=None, is_golden=False):
        self.rect = pygame.Rect(x, y, 12, 12)
        self.image = img
        self.is_golden = is_golden

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            color = GOLD if self.is_golden else RED
            pygame.draw.ellipse(screen, color, self.rect)


class Enemy:
    def __init__(self, x, y, img=None):
        self.start_pos = (x, y)
        self.rect = pygame.Rect(x, y, 32, 32)
        self.image = img
        self.speed = 2  
        self.dir_x = 0
        self.dir_y = 0

    def reset_position(self):
        self.rect.topleft = self.start_pos
        self.dir_x = 0
        self.dir_y = 0

    def move(self, bricks, player_rect, is_frightened=False):
        rel_x = (self.rect.x - 4) % TILE_SIZE
        rel_y = (self.rect.y - 4 - OFFSET_Y) % TILE_SIZE
        at_center = (rel_x == 0 and rel_y == 0)

        if at_center or (self.dir_x == 0 and self.dir_y == 0):
            all_directions = [
                (self.speed, 0),
                (-self.speed, 0),
                (0, self.speed),
                (0, -self.speed)
            ]

            valid_dirs = []
            for dx, dy in all_directions:
                if (dx == -self.dir_x and dy == 0 and self.dir_x != 0) or \
                   (dy == -self.dir_y and dx == 0 and self.dir_y != 0):
                    continue

                step_x = (dx // abs(dx)) * TILE_SIZE if dx != 0 else 0
                step_y = (dy // abs(dy)) * TILE_SIZE if dy != 0 else 0
                test_rect = self.rect.move(step_x, step_y)

                if not any(test_rect.colliderect(b.rect) for b in bricks):
                    valid_dirs.append((dx, dy))

            if not valid_dirs:
                for dx, dy in all_directions:
                    step_x = (dx // abs(dx)) * TILE_SIZE if dx != 0 else 0
                    step_y = (dy // abs(dy)) * TILE_SIZE if dy != 0 else 0
                    test_rect = self.rect.move(step_x, step_y)
                    if not any(test_rect.colliderect(b.rect) for b in bricks):
                        valid_dirs.append((dx, dy))

            if valid_dirs:
                def dist_to_target(d):
                    projected_x = self.rect.x + (d[0] * 20)
                    projected_y = self.rect.y + (d[1] * 20)
                    return (projected_x - player_rect.x) ** 2 + (projected_y - player_rect.y) ** 2

                if is_frightened:
                    self.dir_x, self.dir_y = max(valid_dirs, key=dist_to_target)
                else:
                    if random.random() < 0.75:
                        self.dir_x, self.dir_y = min(valid_dirs, key=dist_to_target)
                    else:
                        self.dir_x, self.dir_y = random.choice(valid_dirs)

        self.rect.x += self.dir_x
        self.rect.y += self.dir_y

    def draw(self, screen, is_frightened):
        if is_frightened:
            pygame.draw.rect(screen, VIOLET, self.rect)
        else:
            if self.image:
                screen.blit(self.image, self.rect)
            else:
                pygame.draw.rect(screen, GREEN, self.rect)


def manage_highscore(score=0, save=False):
    filename = "highscore.txt"
    if save:
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(str(score))
        except OSError:
            pass
        return score
    else:
        if not os.path.exists(filename):
            return 0
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return int(content) if content.isdigit() else 0
        except (OSError, ValueError):
            return 0


game_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]


def spawn_single_apple(player, apples, img, is_golden=False):
    valid_positions = []
    for r_idx, row in enumerate(game_map):
        for c_idx, cell in enumerate(row):
            if cell == 0:
                x = c_idx * TILE_SIZE + 14
                y = r_idx * TILE_SIZE + OFFSET_Y + 14
                test_rect = pygame.Rect(x, y, 12, 12)

                if not test_rect.colliderect(player.rect) and not any(test_rect.colliderect(a.rect) for a in apples):
                    valid_positions.append((x, y))

    if valid_positions:
        rx, ry = random.choice(valid_positions)
        return Apple(rx, ry, img, is_golden)
    return None


def generate_level(images):
    bricks, apples, enemies = [], [], []

    player = Player(1 * TILE_SIZE + 4, 1 * TILE_SIZE + OFFSET_Y + 4, images.get('player'))

    for r_idx, row in enumerate(game_map):
        for c_idx, cell in enumerate(row):
            x, y = c_idx * TILE_SIZE, r_idx * TILE_SIZE + OFFSET_Y
            if cell == 1:
                bricks.append(Brick(x, y, images.get('wall')))

    for _ in range(3):
        new_apple = spawn_single_apple(player, apples, images.get('apple'), is_golden=False)
        if new_apple:
            apples.append(new_apple)

    gold_apple = spawn_single_apple(player, apples, images.get('gold_apple'), is_golden=True)
    if gold_apple:
        apples.append(gold_apple)

    enemy_positions = [
        (9 * TILE_SIZE + 4, 5 * TILE_SIZE + OFFSET_Y + 4),
        (4 * TILE_SIZE + 4, 11 * TILE_SIZE + OFFSET_Y + 4),
        (15 * TILE_SIZE + 4, 3 * TILE_SIZE + OFFSET_Y + 4),
        (21 * TILE_SIZE + 4, 8 * TILE_SIZE + OFFSET_Y + 4),
        (12 * TILE_SIZE + 4, 14 * TILE_SIZE + OFFSET_Y + 4)
    ]
    for pos in enemy_positions:
        enemies.append(Enemy(pos[0], pos[1], images.get('enemy')))

    return player, bricks, apples, enemies


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pacman - Endless Mode")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 22, bold=True)

    images = {}
    try:
        images['player'] = pygame.transform.scale(pygame.image.load("player2.png"), (32, 32))
        images['wall'] = pygame.transform.scale(pygame.image.load("wall.jpg"), (40, 40))
        images['apple'] = pygame.transform.scale(pygame.image.load("apple4.png"), (22, 22))
        images['enemy'] = pygame.transform.scale(pygame.image.load("enemy.png"), (30, 30))
        images['gold_apple'] = pygame.transform.scale(pygame.image.load("golden apple.png"), (22, 22))
    except Exception:
        images.setdefault('player', None)
        images.setdefault('wall', None)
        images.setdefault('apple', None)
        images.setdefault('enemy', None)
        images.setdefault('gold_apple', None)

    highscore = manage_highscore(save=False)
    score = 0

    player, bricks, apples, enemies = generate_level(images)
    running, game_over = True, False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        main()
                        return
                else:
                    if event.key == pygame.K_LEFT:
                        player.move(-1, 0, bricks)
                    elif event.key == pygame.K_RIGHT:
                        player.move(1, 0, bricks)
                    elif event.key == pygame.K_UP:
                        player.move(0, -1, bricks)
                    elif event.key == pygame.K_DOWN:
                        player.move(0, 1, bricks)

        if not game_over:
            if player.power_timer > 0:
                player.power_timer -= 1

            is_player_super = player.power_timer > 0

            for enemy in enemies:
                enemy.move(bricks, player.rect, is_frightened=is_player_super)

            for apple in apples[:]:
                if player.rect.colliderect(apple.rect):
                    apples.remove(apple)

                    if apple.is_golden:
                        score += 25
                        player.power_timer = 10 * FPS
                        new_apple = spawn_single_apple(player, apples, images.get('gold_apple'), is_golden=True)
                    else:
                        score += 10
                        new_apple = spawn_single_apple(player, apples, images.get('apple'), is_golden=False)

                    if new_apple:
                        apples.append(new_apple)

                    if score > highscore:
                        highscore = score
                        manage_highscore(highscore, save=True)

            for enemy in enemies:
                if player.rect.colliderect(enemy.rect):
                    if is_player_super:
                        score += 50
                        if score > highscore:
                            highscore = score
                            manage_highscore(highscore, save=True)
                        enemy.reset_position()
                    else:
                        player.lives -= 1
                        player.rect.topleft = (1 * TILE_SIZE + 4, 1 * TILE_SIZE + OFFSET_Y + 4)
                        pygame.time.delay(400)

                        if player.lives <= 0:
                            game_over = True
                        break

        screen.fill(BLACK)

        for obj in bricks + apples:
            obj.draw(screen)

        for enemy in enemies:
            enemy.draw(screen, is_frightened=(player.power_timer > 0))

        player.draw(screen)

        screen.blit(font.render(f"Score: {score}", True, WHITE), (30, 15))
        screen.blit(font.render(f"High Score: {highscore}", True, WHITE), (SCREEN_WIDTH // 2 - 60, 15))
        screen.blit(font.render(f"Lives: {player.lives}", True, WHITE), (SCREEN_WIDTH - 120, 15))

        if player.power_timer > 0:
            seconds_left = (player.power_timer // FPS) + 1
            screen.blit(font.render(f"POWER: {seconds_left}s", True, GOLD), (SCREEN_WIDTH // 2 - 200, 15))

        pygame.draw.line(screen, WHITE, (0, 50), (SCREEN_WIDTH, 50), 2)

        if game_over:
            screen.blit(font.render("GAME OVER - Press 'R' to Restart", True, RED),
                        (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
