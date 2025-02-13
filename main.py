import random
import curses

MOVES = ['sword', 'shield', 'fire', 'dodge', 'heal', 'poison', 'cleanse']
CHOOSE_MESSAGE = f'Choose from: {" | ".join(map(lambda s: s.swapcase(), MOVES))}'


class Player:
    def __init__(self):
        self.health = 100
        self.energy = 10
        self.enemy = None
        self.move = 'None'
        self.effects = {}

    def take_turn(self, stdscr):
        stdscr.addstr(6, 0, CHOOSE_MESSAGE)
        stdscr.refresh()

        move = []
        cursor_x = 0  # Track cursor position

        while True:
            key = stdscr.getch(7, cursor_x)  # Read a single character

            if key in [curses.KEY_ENTER, 10, 13]:  # Enter key
                move_str = ''.join(move).lower()
                if move_str in MOVES:
                    if move_str == 'fire' and self.energy - 3 < 0 or move_str == 'poison' and self.energy - 1 < 0 \
                        or move_str == 'heal' and self.energy - 2 < 0:
                        stdscr.addstr(8, 0, 'Not enough energy! Try again.', curses.color_pair(2))
                        stdscr.refresh()
                        move.clear()
                        cursor_x = 0
                        stdscr.addstr(7, 0, " " * 20)  # Clear input line
                        stdscr.move(7, 0)
                        continue
                    break  # Valid move, exit loop
                else:
                    stdscr.addstr(8, 0, 'Invalid move! Try again.', curses.color_pair(2))
                    stdscr.refresh()
                    move.clear()
                    cursor_x = 0
                    stdscr.addstr(7, 0, " " * 20)  # Clear input line
                    stdscr.move(7, 0)
                    continue

            elif key in [curses.KEY_BACKSPACE, 127]:  # Handle backspace
                if move:
                    move.pop()
                    cursor_x -= 1
                    stdscr.addstr(7, cursor_x, " ")  # Clear the last character
                    stdscr.move(7, cursor_x)  # Move cursor back

            elif 32 <= key <= 126:  # Printable characters
                move.append(chr(key))
                stdscr.addstr(7, cursor_x, chr(key))  # Display character as typed
                cursor_x += 1  # Move cursor forward

            stdscr.refresh()

        self.move = ''.join(move)

    def check_effects(self):
        if self.move == 'cleanse':
            self.effects.clear()
        else:
            if 'fire' in self.effects.keys():
                self.effects['fire'] -= 1
                self.health -= 5
                if self.effects['fire'] == 0:
                    self.effects.pop('fire')
            if 'poison' in self.effects.keys():
                self.effects['poison'] -= 1
                self.health -= 2
                if self.effects['poison'] == 0:
                    self.effects.pop('poison')

    def play(self):
        if self.move == 'heal':
            self.health = min(self.health + 10, 100)
            self.energy -= 2
        if self.enemy.move == 'sword':
            if self.move != 'shield':
                if self.move == 'dodge':
                    self.health -= 5
                else:
                    self.health -= 10
        if self.move == 'fire':
            self.enemy.effects['fire'] = 3
            self.energy -= 3
        if self.move == 'poison':
            self.enemy.effects['poison'] = 5
            self.energy -= 1


class Enemy:
    def __init__(self):
        self.health = 100
        self.player = None
        self.move = 'None'
        self.effects = {}

    def take_turn(self):
        self.move = random.choice(MOVES)

    def check_effects(self):
        if self.move == 'cleanse':
            self.effects.clear()
        else:
            if 'fire' in self.effects.keys():
                self.effects['fire'] -= 1
                self.health -= 5
                if self.effects['fire'] == 0:
                    self.effects.pop('fire')
            if 'poison' in self.effects.keys():
                self.effects['poison'] -= 1
                self.health -= 2
                if self.effects['poison'] == 0:
                    self.effects.pop('poison')

    def play(self):
        if self.move == 'heal':
            self.health = min(self.health + 10, 100)
        if self.player.move == 'sword':
            if self.move != 'shield':
                if self.move == 'dodge':
                    self.health -= 5
                else:
                    self.health -= 10
        if self.move == 'fire':
            self.player.effects['fire'] = 3
        if self.move == 'poison':
            self.player.effects['poison'] = 5

def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)


    player = Player()
    enemy = Enemy()
    player.enemy = enemy
    enemy.player = player

    while True:
        stdscr.clear()
        if player.health <= 0 and enemy.health <= 0:
            stdscr.addstr(0, 0, 'The battle drained both of you.', curses.color_pair(4))
            player = Player()
            enemy = Enemy()
            player.enemy = enemy
            enemy.player = player
            stdscr.addstr(10, 0, 'Press any key to restart...')
        elif player.health <= 0:
            stdscr.addstr(0, 0, 'You died!', curses.color_pair(2))
            player = Player()
            enemy = Enemy()
            player.enemy = enemy
            enemy.player = player
            stdscr.addstr(10, 0, 'Press any key to restart...')
        elif enemy.health <= 0:
            stdscr.addstr(0, 0, 'You won!', curses.color_pair(3))
            player = Player()
            enemy = Enemy()
            player.enemy = enemy
            enemy.player = player
            stdscr.addstr(10, 0, 'Press any key to restart...')

        else:
            stdscr.addstr(0, 0, f'You: Health {player.health} | Energy {player.energy} |'
                                f' Effects {player.effects}', curses.color_pair(1))
            stdscr.addstr(1, 0, f'Enemy: Health {enemy.health} | Effects {enemy.effects}', curses.color_pair(1))

            player.take_turn(stdscr)
            enemy.take_turn()

            player.play()
            enemy.play()

            player.check_effects()
            enemy.check_effects()

            stdscr.addstr(9, 0, f'You played {player.move.swapcase()}! | Enemy played {enemy.move.swapcase()}!',
                          curses.color_pair(1))

            stdscr.addstr(10, 0, 'Press any key to continue...')

        stdscr.refresh()
        stdscr.getch()


if __name__ == '__main__':
    curses.wrapper(main)