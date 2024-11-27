from machine import Pin, I2C, freq
from ssd1306 import SSD1306_I2C
from utime import sleep, ticks_ms
import random

# Overclock the Pi Pico to 120MHz
freq(120000000)  # 120MHz

# Define I2C connection (SDA to GP16, SCL to GP17)
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=900000)
oled = SSD1306_I2C(128, 64, i2c)

# Define pins for buttons
jump_button = Pin(0, Pin.IN, Pin.PULL_UP)
duck_button = Pin(11, Pin.IN, Pin.PULL_UP)

# Bitmap graphics for dino
dino_bitmap = [
    0b00111000,
    0b01111100,
    0b11111110,
    0b11111111,
    0b11011011,
    0b11000011
]

dino_ducking_bitmap = [
    0b11111100,
    0b11111110,
    0b11111111,
    0b11011011
]

# Bitmap graphics for obstacles
small_cactus_bitmap = [
    0b001100,
    0b001100,
    0b001100,
    0b111111,
    0b111111,
    0b001100
]

medium_cactus_bitmap = [
    0b001100,
    0b001100,
    0b001100,
    0b001100,
    0b001100,
    0b001100,
    0b111111,
    0b111111,
    0b001100
]

large_cactus_bitmap = [
    0b001100,
    0b011110,
    0b111111,
    0b111111,
    0b001100,
    0b001100,
    0b001100,
    0b001100,
    0b001100,
    0b001100,
    0b001100,
    0b001100,
    0b111111,
    0b111111
]

bird_bitmap = [
    0b000011,
    0b011111,
    0b110000
]

obstacle_bitmaps = [small_cactus_bitmap, medium_cactus_bitmap, large_cactus_bitmap, bird_bitmap]

class Dino:
    def __init__(self):
        self.x = 10
        self.y = 0
        self.ground_y = 55
        self.jumping = False
        self.ducking = False
        self.jump_velocity = 0
        self.gravity = -1
        self.jump_force = 8
        self.graphics = dino_bitmap
        self.ducking_graphics = dino_ducking_bitmap

    def start_jump(self):
        if not self.jumping and not self.ducking:
            self.jumping = True
            self.jump_velocity = self.jump_force

    def update(self):
        if self.jumping:
            self.y += self.jump_velocity
            self.jump_velocity += self.gravity
            if self.y < 0:
                self.y = 0
                self.jumping = False
                self.jump_velocity = 0

    def draw(self, oled):
        graphics = self.ducking_graphics if self.ducking else self.graphics
        for i, line in enumerate(graphics):
            for j in range(8):
                if line & (1 << (7 - j)):
                    oled.pixel(self.x + j, self.ground_y - self.y - (i * 2) if not self.ducking else self.ground_y - 3 + i, 1)

class Obstacle:
    def __init__(self, x, speed):
        self.x = x
        self.speed = int(speed)
        self.graphics = random.choice(self.select_obstacle())
        if self.graphics == bird_bitmap:
            self.y = random.choice([35, 45])  # Birds should be higher up
        else:
            self.y = 55 - len(self.graphics)  # Adjust y position based on obstacle height

    def select_obstacle(self):
        global obstacle_bitmaps
        if Game.dispScore >= 100:  # Birds only appear after 100 points
            return obstacle_bitmaps
        return obstacle_bitmaps[:3]

    def update(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = 128 + random.randint(50, 100)
            self.graphics = random.choice(self.select_obstacle())
            if self.graphics == bird_bitmap:
                self.y = random.choice([35, 45])  # Birds should be higher up
            else:
                self.y = 55 - len(self.graphics)  # Adjust y position based on new obstacle height

    def draw(self, oled):
        for i, line in enumerate(self.graphics):
            for j in range(6 if len(self.graphics) == 6 else 8):
                if line & (1 << (5 - j if len(self.graphics) == 6 else 7 - j)):
                    oled.pixel(self.x + j, self.y + i, 1)

class Game:
    dispScore = 0

    def __init__(self, oled):
        self.oled = oled
        self.dino = Dino()
        self.obstacles = [Obstacle(128, 2)]
        self.score = 0
        self.game_running = True
        self.timeWindow = 10000

    def check_collision(self):
        dino_top = self.dino.ground_y - self.dino.y - 20 if not self.dino.ducking else self.dino.ground_y - len(self.dino.ducking_graphics) - 5
        dino_bottom = self.dino.ground_y - self.dino.y
        dino_left = self.dino.x
        dino_right = self.dino.x + 10

        for obstacle in self.obstacles:
            obstacle_top = obstacle.y
            obstacle_bottom = obstacle.y + (len(obstacle.graphics))
            obstacle_left = obstacle.x
            obstacle_right = obstacle.x + (6 if len(obstacle.graphics) == 6 else 8)

            if dino_right > obstacle_left and dino_left < obstacle_right and dino_bottom > obstacle_top and dino_top < obstacle_bottom:
                self.game_running = False

    def update(self):
        self.dino.update()
        for obstacle in self.obstacles:
            obstacle.update()
        self.check_collision()

    def draw(self):
        self.oled.fill(0)
        self.dino.draw(self.oled)
        for obstacle in self.obstacles:
            obstacle.draw(self.oled)
        self.oled.text(f'Score: {Game.dispScore}', 0, 0)
        self.oled.show()

    def run(self):
        global obstacle_bitmaps
        start_time = ticks_ms()
        while self.game_running:
            if not jump_button.value():
                self.dino.start_jump()
            if not duck_button.value():
                self.dino.ducking = True
            else:
                self.dino.ducking = False

            self.update()
            self.draw()
            sleep(0.01)
            
            if ticks_ms() - start_time > self.timeWindow:  # Increase speed every timeWindow
                for obstacle in self.obstacles:
                    obstacle.speed = int(obstacle.speed + 1)
                start_time = ticks_ms()
                print(f"Obstacle speed: {obstacle.speed}")
                print(f"Display score: {Game.dispScore}")
                self.timeWindow += 1000
            
            for obstacle in self.obstacles:
                speed = obstacle.speed
            self.score += int((speed-1))  # Increment score
            Game.dispScore = round((self.score / 10))
            
            # Debugging
            print(f"Raw Score: {self.score}")
            print(f"Display Score: {Game.dispScore}\n")
            

        # Display Game Over
        self.oled.fill(0)
        self.oled.text("Game Over", 22, 25)
        self.oled.text(f'Score: {Game.dispScore}', 22, 35)
        self.oled.show()

if __name__ == "__main__":
    try:
        # Create Game instance and run the game
        game = Game(oled)
        game.run()
    except KeyboardInterrupt:
        oled.fill(0)
        oled.show()
