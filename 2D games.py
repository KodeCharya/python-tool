import pygame
import random

# Initialize pygame
pygame.init()

# Set up the display
width, height = 600, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Dodge the Falling Blocks')

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Game variables
player_width, player_height = 50, 50
player_x = width // 2 - player_width // 2
player_y = height - player_height - 10
player_speed = 5

block_width = 50
block_height = 50
block_speed = 5
blocks = []

score = 0
font = pygame.font.SysFont(None, 30)

# Function to display score
def display_score(score):
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

# Function to create a new block
def create_block():
    x = random.randint(0, width - block_width)
    return {'x': x, 'y': -block_height}

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)

    # Check for events (like closing the window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get key states for player movement
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < width - player_width:
        player_x += player_speed

    # Move blocks
    for block in blocks[:]:
        block['y'] += block_speed
        if block['y'] > height:
            blocks.remove(block)
            score += 1  # Increase score when block goes off screen
        if block['x'] < player_x + player_width and block['x'] + block_width > player_x and \
           block['y'] < player_y + player_height and block['y'] + block_height > player_y:
            running = False  # Game Over if collision happens

    # Create new block randomly
    if random.randint(1, 60) == 1:  # Chance to create a new block
        blocks.append(create_block())

    # Draw the player
    pygame.draw.rect(screen, GREEN, (player_x, player_y, player_width, player_height))

    # Draw blocks
    for block in blocks:
        pygame.draw.rect(screen, RED, (block['x'], block['y'], block_width, block_height))

    # Display the score
    display_score(score)

    # Update the display
    pygame.display.update()

    # Frame rate
    clock.tick(60)

# Game over screen
screen.fill(BLACK)
game_over_text = font.render(f"Game Over! Final Score: {score}", True, WHITE)
screen.blit(game_over_text, (width // 4, height // 2))
pygame.display.update()

# Wait for a few seconds before closing
pygame.time.wait(3000)

pygame.quit()
