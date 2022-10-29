import pygame
import random
import logging
import os
import sys
import enum
import pickle

pygame.init()

logging.basicConfig(level=logging.DEBUG)

Position = tuple[int, int]
Velocity = tuple[int, int]
Color = tuple[int, int, int]

GREEN: Color = (0, 255, 0)
RED: Color = (255, 0, 0)
BLACK: Color = (0, 0, 0)

STOP: Velocity = (0, 0)
UP: Velocity = (0, -1)
RIGHT: Velocity = (1, 0)
DOWN: Velocity = (0, 1)
LEFT: Velocity = (-1, 0)

grid_size_pixels: int = 600
window_size_pixels: tuple[int, int] = (grid_size_pixels, grid_size_pixels + 50)
window_width_center: int = window_size_pixels[0] // 2

font_path: str = 'fixedsys.ttf'
if hasattr(sys, '_MEIPASS'):
    # noinspection PyProtectedMember
    font_path = os.path.join(sys._MEIPASS, font_path)

class Speed(enum.Enum):
    slow = 5
    medium = 10
    fast = 15

class Size(enum.Enum):
    small = 10
    medium = 20
    large = 30

def get_font(size: int) -> pygame.font.Font:
    return pygame.font.Font(font_path, size)

def make_text_surface(text: str, font_size: int, color: Color) -> pygame.Surface:
    return get_font(font_size).render(text, True, color)

def make_text_rect(surface: pygame.Surface, **kwargs) -> pygame.Rect:
    return surface.get_rect(**kwargs)

def make_text(text: str, font_size: int, color: Color, **kwargs) -> tuple[pygame.Surface, pygame.Rect]:
    surface = make_text_surface(text, font_size, color)
    rect = make_text_rect(surface, **kwargs)
    return surface, rect

def underline(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(
        surface,
        GREEN,
        (rect.left, rect.bottom + 5, rect.width, 5)
    )

def get_total_width(*surfaces: pygame.Surface, width_between: int = 0):
    return sum(map(lambda s: s.get_width(), surfaces)) + width_between * (len(surfaces) - 1)

def make_row(*surfaces: pygame.Surface, width_between: int = 0, top: int = 0) -> tuple[pygame.Rect]:
    total_width = get_total_width(*surfaces, width_between=width_between)
    prev = make_text_rect(surfaces[0], left=window_width_center - total_width // 2, top=top)
    tup = prev,
    for surface in surfaces[1:]:
        next_rect = make_text_rect(surface, left=prev.right + width_between, top=top)
        tup = tup + (next_rect,)
        prev = next_rect
    return tup

def main():
    pygame.display.set_caption('Snake')
    screen: pygame.Surface = pygame.display.set_mode(window_size_pixels)
    wrap: bool = False
    cheats: bool = False
    speed: Speed = Speed.medium
    size: Size = Size.medium
    settings_font_size = 30

    high_score: int = 0
    try:
        with open('high-score', 'rb') as f:
            high_score = pickle.load(f)
    except FileNotFoundError:
        pass

    title_surface, title_rect = make_text('Snake', 90, GREEN, centerx=window_width_center, top=20)
    play_surface, play_rect = make_text(
        'Play',
        40,
        GREEN,
        centerx=window_width_center,
        top=title_rect.bottom + 20
    )

    wrap_surface = make_text_surface('Wrap:', settings_font_size, GREEN)
    wrap_on_surface = make_text_surface('on', settings_font_size, GREEN)
    wrap_off_surface = make_text_surface('off', settings_font_size, GREEN)
    # noinspection PyTupleAssignmentBalance
    wrap_rect, wrap_on_rect, wrap_off_rect = make_row(
        wrap_surface,
        wrap_on_surface,
        wrap_off_surface,
        width_between=20,
        top=play_rect.bottom + 20
    )

    speed_surface = make_text_surface('Speed:', settings_font_size, GREEN)
    speed_slow_surface = make_text_surface('slow', settings_font_size, GREEN)
    speed_medium_surface = make_text_surface('medium', settings_font_size, GREEN)
    speed_fast_surface = make_text_surface('fast', settings_font_size, GREEN)
    # noinspection PyTupleAssignmentBalance
    speed_rect, speed_slow_rect, speed_medium_rect, speed_fast_rect = make_row(
        speed_surface,
        speed_slow_surface,
        speed_medium_surface,
        speed_fast_surface,
        width_between=20,
        top=wrap_rect.bottom + 20
    )

    size_surface = make_text_surface('Size:', settings_font_size, GREEN)
    size_small_surface = make_text_surface('small', settings_font_size, GREEN)
    size_medium_surface = make_text_surface('medium', settings_font_size, GREEN)
    size_large_surface = make_text_surface('large', settings_font_size, GREEN)
    # noinspection PyTupleAssignmentBalance
    size_rect, size_small_rect, size_medium_rect, size_large_rect = make_row(
        size_surface,
        size_small_surface,
        size_medium_surface,
        size_large_surface,
        width_between=20,
        top=speed_rect.bottom + 20
    )

    cheats_surface = make_text_surface('Cheats:', settings_font_size, GREEN)
    cheats_on_surface = make_text_surface('on', settings_font_size, GREEN)
    cheats_off_surface = make_text_surface('off', settings_font_size, GREEN)
    # noinspection PyTupleAssignmentBalance
    cheats_rect, cheats_on_rect, cheats_off_rect = make_row(
        cheats_surface,
        cheats_on_surface,
        cheats_off_surface,
        width_between=20,
        top=size_rect.bottom + 20
    )

    quit_surface, quit_rect = make_text(
        'Quit',
        40,
        GREEN,
        centerx=window_width_center,
        top=cheats_rect.bottom + 20
    )

    while True:
        for event in pygame.event.get():
            mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                with open('high-score', 'wb') as f:
                    pickle.dump(high_score, file=f)
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_rect.collidepoint(mouse_pos):
                    # noinspection PyTypeChecker
                    score = run_game(
                        screen,
                        grid_size_tiles=size.value,
                        speed=speed.value,
                        wrap=wrap,
                        cheats=cheats
                    )
                    if score > high_score:
                        high_score = score
                elif quit_rect.collidepoint(mouse_pos):
                    with open('high-score', 'wb') as f:
                        pickle.dump(high_score, file=f)
                    sys.exit()
                elif wrap_on_rect.collidepoint(mouse_pos):
                    wrap = True
                elif wrap_off_rect.collidepoint(mouse_pos):
                    wrap = False
                elif cheats_on_rect.collidepoint(mouse_pos):
                    cheats = True
                elif cheats_off_rect.collidepoint(mouse_pos):
                    cheats = False
                elif speed_slow_rect.collidepoint(mouse_pos):
                    speed = Speed.slow
                elif speed_medium_rect.collidepoint(mouse_pos):
                    speed = Speed.medium
                elif speed_fast_rect.collidepoint(mouse_pos):
                    speed = Speed.fast
                elif size_small_rect.collidepoint(mouse_pos):
                    size = Size.small
                elif size_medium_rect.collidepoint(mouse_pos):
                    size = Size.medium
                elif size_large_rect.collidepoint(mouse_pos):
                    size = Size.large

        screen.fill(BLACK)

        high_score_surface, high_score_rect = make_text(
            f'High score: {high_score}',
            40,
            GREEN,
            centerx=window_width_center,
            top=quit_rect.bottom + 20
        )

        screen.blits((
            (title_surface, title_rect),
            (play_surface, play_rect),
            (wrap_surface, wrap_rect),
            (wrap_on_surface, wrap_on_rect),
            (wrap_off_surface, wrap_off_rect),
            (speed_surface, speed_rect),
            (speed_slow_surface, speed_slow_rect),
            (speed_medium_surface, speed_medium_rect),
            (speed_fast_surface, speed_fast_rect),
            (size_surface, size_rect),
            (size_small_surface, size_small_rect),
            (size_medium_surface, size_medium_rect),
            (size_large_surface, size_large_rect),
            (cheats_surface, cheats_rect),
            (cheats_on_surface, cheats_on_rect),
            (cheats_off_surface, cheats_off_rect),
            (quit_surface, quit_rect),
            (high_score_surface, high_score_rect)
        ))

        underline(screen, wrap_on_rect) if wrap else underline(screen, wrap_off_rect)
        underline(screen, cheats_on_rect) if cheats else underline(screen, cheats_off_rect)
        if speed == Speed.slow:
            underline(screen, speed_slow_rect)
        elif speed == Speed.medium:
            underline(screen, speed_medium_rect)
        elif speed == Speed.fast:
            underline(screen, speed_fast_rect)
        if size == Size.small:
            underline(screen, size_small_rect)
        elif size == Size.medium:
            underline(screen, size_medium_rect)
        elif size == Size.large:
            underline(screen, size_large_rect)

        pygame.display.flip()

def get_food_position(grid_size: int, trail: list[Position]):
    return random.choice([(x, y) for y in range(grid_size) for x in range(grid_size) if (x, y) not in trail])

def run_game(
        screen,
        starting_length: int = 1,
        grid_size_tiles: int = 20,
        speed: int = 10,
        wrap: bool = False,
        cheats: bool = False
) -> int:
    x_vel: int
    y_vel: int
    x_vel, y_vel = STOP

    player_x: int
    player_y: int
    player_x, player_y = random.randrange(grid_size_tiles), random.randrange(grid_size_tiles)
    trail: list[Position] = [(player_x, player_y)]

    food_x: int
    food_y: int
    food_x, food_y = get_food_position(grid_size_tiles, trail)

    tile_size_pixels: int = grid_size_pixels // grid_size_tiles
    framerate: int = speed
    length: int = starting_length
    score: int = 0
    clock = pygame.time.Clock()

    while True:
        clock.tick(framerate)

        while (event := pygame.event.poll()).type != pygame.NOEVENT:
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and (x_vel, y_vel) not in (UP, DOWN):
                    x_vel, y_vel = UP
                    break
                elif event.key == pygame.K_RIGHT and (x_vel, y_vel) not in (RIGHT, LEFT):
                    x_vel, y_vel = RIGHT
                    break
                elif event.key == pygame.K_DOWN and (x_vel, y_vel) not in (UP, DOWN):
                    x_vel, y_vel = DOWN
                    break
                elif event.key == pygame.K_LEFT and (x_vel, y_vel) not in (RIGHT, LEFT):
                    x_vel, y_vel = LEFT
                    break
                if cheats:
                    if event.key == pygame.K_SLASH:
                        x_vel, y_vel = STOP
                    elif event.key == pygame.K_COMMA:
                        framerate -= 1
                    elif event.key == pygame.K_PERIOD:
                        framerate += 1
                    elif event.key == pygame.K_SEMICOLON:
                        length -= 1
                        score -= 1
                    elif event.key == pygame.K_QUOTE:
                        length += 1
                        score += 1

        player_x += x_vel
        player_y += y_vel
        if player_x < 0:
            if wrap:
                player_x = grid_size_tiles - 1
            else:
                break
        elif player_x > grid_size_tiles - 1:
            if wrap:
                player_x = 0
            else:
                break
        if player_y < 0:
            if wrap:
                player_y = grid_size_tiles - 1
            else:
                break
        elif player_y > grid_size_tiles - 1:
            if wrap:
                player_y = 0
            else:
                break

        if (x_vel, y_vel) != STOP:
            if (player_x, player_y) in trail[1:]:
                break

        trail.append((player_x, player_y))
        while len(trail) > length:
            trail.pop(0)

        if player_x == food_x and player_y == food_y:
            length += 1
            score += 1
            food_x, food_y = get_food_position(grid_size_tiles, trail)

        screen.fill(BLACK)
        for pos in trail:
            pygame.draw.rect(
                screen,
                GREEN,
                (
                    pos[0] * tile_size_pixels + 1,
                    pos[1] * tile_size_pixels + 1,
                    tile_size_pixels - 2,
                    tile_size_pixels - 2
                )
            )
        pygame.draw.rect(
            screen,
            RED,
            (
                food_x * tile_size_pixels + 1,
                food_y * tile_size_pixels + 1,
                tile_size_pixels - 2,
                tile_size_pixels - 2
            )
        )
        seperator_rect = pygame.draw.rect(
            screen,
            GREEN,
            (0, grid_size_pixels, grid_size_pixels, 1)
        )
        info_font = get_font(20)
        score_label = info_font.render(f'Score: {score}', True, GREEN)
        speed_label = info_font.render(f'Speed: {framerate}', True, GREEN)
        wrap_label = info_font.render(f'Wrap: {"on" if wrap else "off"}', True, GREEN)
        score_rect = screen.blit(score_label, (0, seperator_rect.bottom))
        speed_rect = screen.blit(speed_label, (0, score_rect.bottom))
        screen.blit(wrap_label, (max(speed_rect.right, score_rect.right) + 20, seperator_rect.bottom))
        pygame.display.flip()
    return score

if __name__ == '__main__':
    main()