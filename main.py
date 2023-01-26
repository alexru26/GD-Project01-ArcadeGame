#Python tank shoot game PEW PEW!!!!
#1/26/23

__author__ = 'Alex Ru'

import arcade
import math
import random

"""
Projects used:
https://api.arcade.academy/en/latest/examples/sprite_move_keyboard_better.html#sprite-move-keyboard-better
https://api.arcade.academy/en/latest/examples/dual_stick_shooter.html#dual-stick-shooter
https://api.arcade.academy/en/latest/examples/sprite_follow_simple_2.html#sprite-follow-simple-2
https://api.arcade.academy/en/latest/examples/sprite_bullets_aimed.html#sprite-bullets-aimed
https://api.arcade.academy/en/latest/examples/sprite_bullets_random.html#sprite-bullets-random
"""

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "I'm tanking this grade for sure!!!"

MOVEMENT_SPEED = 4
ENEMY_SPEED = 2

ENEMY_SPAWN_INTERVAL = 1.2
ENEMY_BULLET_SPAWN_TICKS = 35
SPRITE_SCALING_ENEMY = 1

SPRITE_SCALING_LASER = 0.8
BULLET_SPEED = 7
BULLET_COOLDOWN_TICKS = 30

class Player(arcade.Sprite):
    # Player Object Class

    def update(self):
        # Updates every frame

        # Moving method by altering center
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Left right bounds
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        # Up down bounds
        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1

class Enemy(arcade.Sprite):
    # Enemy Object Class

    def follow_sprite(self, player_sprite):
        # Method for enemy to move towards another given sprite

        # Initial lock on
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Calculates angle to move at
        start_x = self.center_x
        start_y = self.center_y
        dest_x = player_sprite.center_x
        dest_y = player_sprite.center_y
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        self.angle = math.degrees(math.atan2(y_diff, x_diff)) + 90

        # Chance to lock onto player
        if random.randrange(50) == 0:
            start_x = self.center_x
            start_y = self.center_y

            # Get the destination location for the bullet
            dest_x = player_sprite.center_x
            dest_y = player_sprite.center_y

            # Do math to calculate how to get the bullet to the destination.
            # Calculation the angle in radians between the start points
            # and end points. This is the angle the bullet will travel.
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            # Taking into account the angle, calculate our change_x
            # and change_y. Velocity is how fast the bullet travels.
            self.change_x = math.cos(angle) * ENEMY_SPEED
            self.change_y = math.sin(angle) * ENEMY_SPEED

class MyGame(arcade.Window):
    # Main game

    def __init__(self, width, height, title):
        # Initialize variables

        super().__init__(width, height, title)

        self.player_list = None
        self.player_sprite = None

        self.bullet_list = None
        self.bullet_cooldown = 0

        self.enemy_list = None
        self.enemy_sprite = None
        self.enemy_bullet_list = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.game_over = False

        # Set the background color
        arcade.set_background_color(arcade.color.ASH_GREY)

    def setup(self):
        # Setup all variables

        self.player_list = arcade.SpriteList()
        self.player_sprite = Player(":resources:images/topdown_tanks/tank_blue.png")
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_sprite.angle = 0
        self.player_list.append(self.player_sprite)

        self.bullet_list = arcade.SpriteList()

        self.enemy_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()

        # Schedule spawning enemy
        arcade.window_commands.schedule(self.spawn_enemy, ENEMY_SPAWN_INTERVAL)

    def spawn_enemy(self, _elapsed):
        # Spawns enemy

        if self.game_over:
            return

        # Spawns enemy and makes sure it is not spawning on top of player
        self.enemy_sprite = Enemy(":resources:images/topdown_tanks/tank_red.png", SPRITE_SCALING_ENEMY)
        while True:
            x = random.randrange(SCREEN_WIDTH)
            y = random.randrange(SCREEN_HEIGHT)
            if math.hypot(x - self.player_sprite.center_x, y - self.player_sprite.center_y) > 150:
                break

        # Moves towards player
        self.enemy_sprite.center_x = x
        self.enemy_sprite.center_y = y
        start_x = self.enemy_sprite.center_x
        start_y = self.enemy_sprite.center_y
        dest_x = self.player_sprite.center_x
        dest_y = self.player_sprite.center_y
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)
        self.enemy_sprite.change_x = math.cos(angle) * ENEMY_SPEED
        self.enemy_sprite.change_y = math.sin(angle) * ENEMY_SPEED
        self.enemy_list.append(self.enemy_sprite)

    def on_draw(self):
        # Clear the screen
        self.clear()

        self.player_list.draw()
        self.enemy_list.draw()

        if not self.game_over:
            # Draw all the sprites.
            self.bullet_list.draw()
            self.enemy_bullet_list.draw()

    def update_player_speed(self):
        # Calculate speed based on the keys pressed

        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = MOVEMENT_SPEED

        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -MOVEMENT_SPEED

        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -MOVEMENT_SPEED

        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        # Aligns player angle to mouse location
        if not self.game_over:
            angle = math.atan2((y - self.player_sprite.center_y),
                               (x - self.player_sprite.center_x)) * 180 / math.pi + 90
            self.player_sprite.angle = angle

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        # Checks if mouse pressed

        # Check cooldown
        if self.bullet_cooldown < BULLET_COOLDOWN_TICKS:
            return
        self.bullet_cooldown = 0

        # Spawns laser towards enemy
        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_LASER)
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y
        dest_x = x
        dest_y = y
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)
        bullet.angle = math.degrees(angle)
        bullet.change_x = math.cos(angle) * BULLET_SPEED
        bullet.change_y = math.sin(angle) * BULLET_SPEED
        self.bullet_list.append(bullet)

    def on_update(self, delta_time):
        """ Movement and game logic """

        if self.game_over:
            return

        self.bullet_cooldown += 1

        # Call update to move the sprite
        # If using a physics engine, call update player to rely on physics engine
        # for movement, and call physics engine here.
        self.player_list.update()

        # Call update on all sprites
        self.bullet_list.update()

        self.enemy_bullet_list.update()

        # Loop through each bullet
        for bullet in self.bullet_list:

            # If the bullet flies off-screen, remove it.
            if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                bullet.remove_from_sprite_lists()

            enemy_hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            if len(enemy_hit_list) > 0:
                bullet.remove_from_sprite_lists()
                enemy_hit_list[0].remove_from_sprite_lists()

        for bullet in self.enemy_bullet_list:

            # If the bullet flies off-screen, remove it.
            if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                bullet.remove_from_sprite_lists()

        for enemy in self.enemy_list:
            enemy.follow_sprite(self.player_sprite)
            if random.randrange(50) == 0:
                self.spawn_bullet(enemy, self.player_sprite)

        # Checks collision
        player_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)
        player_bullet_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_bullet_list)
        if len(player_hit_list) > 0:
            self.game_over = True
        if len(player_bullet_hit_list) > 0:
            self.game_over = True

    def on_key_press(self, key, modifiers):
        # Called whenever a key is pressed.

        if key == arcade.key.W:
            self.up_pressed = True
            self.update_player_speed()

        elif key == arcade.key.S:
            self.down_pressed = True
            self.update_player_speed()

        elif key == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()

        elif key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()

    def on_key_release(self, key, modifiers):
        # Called when the user releases a key.

        if key == arcade.key.W:
            self.up_pressed = False
            self.update_player_speed()

        elif key == arcade.key.S:
            self.down_pressed = False
            self.update_player_speed()

        elif key == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()

        elif key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()

    def spawn_bullet(self, enemy_sprite, player_sprite):
        # Spawns bullet
        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_LASER)
        start_x = enemy_sprite.center_x
        start_y = enemy_sprite.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y
        dest_x = player_sprite.center_x
        dest_y = player_sprite.center_y
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)
        bullet.angle = math.degrees(angle)
        bullet.change_x = math.cos(angle) * BULLET_SPEED
        bullet.change_y = math.sin(angle) * BULLET_SPEED
        self.enemy_bullet_list.append(bullet)

def main():
    # Main function
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    # Entry point!
    main()
