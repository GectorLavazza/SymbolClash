import random
import curses

MOVES = ['sword', 'shield', 'fire', 'dodge', 'heal', 'poison', 'cleanse']
MOVES_COLORS = {0: 2,
                1: 1,
                2: 7,
                3: 1,
                4: 3,
                5: 7,
                6: 3}
CHOOSE_MESSAGE = f'Choose from: '


class Player:
    def __init__(self):
        self.health = 100
        self.energy = 10
        self.enemy = None
        self.move = 'None'
        self.effects = {}
        self.history = []

        self.sword_dmg = 8
        self.poison_dmg = 2
        self.fire_dmg = 5
        self.fire_time = 3
        self.poison_time = 5
        self.dodged_dmg = 2

    def take_turn(self, stdscr):
        stdscr.addstr(6, 0, CHOOSE_MESSAGE)
        offset = 0
        for i in range(len(MOVES)):
            move = MOVES[i]
            add = ' | ' if i < len(MOVES) - 1 else ''
            stdscr.addstr(6, len(CHOOSE_MESSAGE) + offset, move.swapcase(), curses.color_pair(MOVES_COLORS[1]))
            stdscr.addstr(6, len(CHOOSE_MESSAGE) + offset + len(move), add, curses.color_pair(MOVES_COLORS[1]))
            offset += len(move) + 3
        stdscr.refresh()

        move = []
        cursor_x = 0

        while True:
            key = stdscr.getch(7, cursor_x)

            if key in [curses.KEY_ENTER, 10, 13]:
                move_str = ''.join(move).lower()
                if move_str in MOVES:
                    if move_str == 'fire' and self.energy - 3 < 0 or move_str == 'poison' and self.energy - 1 < 0 \
                            or move_str == 'heal' and self.energy - 2 < 0:
                        stdscr.addstr(8, 0, 'Not enough energy! Try again.', curses.color_pair(2))
                        stdscr.refresh()
                        move.clear()
                        cursor_x = 0
                        stdscr.addstr(7, 0, " " * 20)
                        stdscr.move(7, 0)
                        continue
                    break
                else:
                    stdscr.addstr(8, 0, 'Invalid move! Try again.', curses.color_pair(2))
                    stdscr.refresh()
                    move.clear()
                    cursor_x = 0
                    stdscr.addstr(7, 0, " " * 20)
                    stdscr.move(7, 0)
                    continue

            elif key in [curses.KEY_BACKSPACE, 127]:
                if move:
                    move.pop()
                    cursor_x -= 1
                    stdscr.addstr(7, cursor_x, " ")
                    stdscr.move(7, cursor_x)

            elif 32 <= key <= 126:
                move.append(chr(key))
                stdscr.addstr(7, cursor_x, chr(key))
                cursor_x += 1

            stdscr.refresh()

        self.move = ''.join(move)
        self.history.append(self.move)
        if len(self.history) > 10:
            self.history = self.history[len(self.history) - 10:]

    def check_effects(self):
        if self.move == 'cleanse':
            self.effects.clear()
        else:
            if 'fire' in self.effects.keys():
                self.effects['fire'] -= 1
                self.health -= self.enemy.fire_dmg
                if self.effects['fire'] == 0:
                    self.effects.pop('fire')
            if 'poison' in self.effects.keys():
                self.effects['poison'] -= 1
                self.health -= self.enemy.poison_dmg
                if self.effects['poison'] == 0:
                    self.effects.pop('poison')

    def play(self):
        if self.enemy.move == 'sword':
            if self.move != 'shield':
                if self.move == 'dodge':
                    self.health -= self.enemy.sword_dmg // 2
                else:
                    self.health -= self.enemy.sword_dmg
        if self.move == 'fire':
            self.enemy.effects['fire'] = self.enemy.fire_time
            self.energy -= 3
        if self.move == 'poison':
            self.enemy.effects['poison'] = self.enemy.poison_time
            self.energy -= 1
        if self.move == 'heal':
            self.health = min(self.health + 10, 100)
            self.energy -= 2


class Enemy(Player):
    def __init__(self):
        super().__init__()
        self.energy = 10000
        self.effects = {}
        self.sword_dmg = 10

    def take_turn(self):
        sw, sh, f, d, h, p, c = [5] * len(MOVES)
        amounts = [self.enemy.history.count(m) for m in MOVES]

        if self.enemy.history.count('sword') == max(amounts):
            sw, sh, f, d, h, p, c = 9, 10, 5, 6, 8, 5, 3
        elif self.enemy.history.count('shield') == max(amounts):
            sw, sh, f, d, h, p, c = 3, 3, 8, 4, 4, 8, 4
        elif self.enemy.history.count('fire') == max(amounts):
            sw, sh, f, d, h, p, c = 8, 5, 7, 4, 8, 5, 10
        elif self.enemy.history.count('dodge') == max(amounts):
            sw, sh, f, d, h, p, c = 8, 4, 8, 3, 7, 8, 4
        elif self.enemy.history.count('heal') == max(amounts):
            sw, sh, f, d, h, p, c = 6, 5, 8, 4, 7, 7, 4
        elif self.enemy.history.count('poison') == max(amounts):
            sw, sh, f, d, h, p, c = 8, 5, 7, 4, 8, 7, 10
        elif self.enemy.history.count('cleanse') == max(amounts):
            sw, sh, f, d, h, p, c = 10, 5, 5, 6, 7, 5, 5

        if 'fire' in self.enemy.effects.keys():
            f = max(1, f - 2)
        if 'poison' in self.enemy.effects.keys():
            p = max(1, p - 2)

        if 'fire' in self.enemy.history[-2:] or 'poison' in self.enemy.history[-2:]:
            c = min(10, c + 2)
            h = min(10, c + 1)

        if self.enemy.energy < 3:
            sw = min(10, sw + 2)

        if self.health < self.health // 2:
            h = min(10, c + 2)
        if self.health < self.health // 4:
            c = min(10, c + 1)
            h = min(10, c + 4)
            d = min(10, c + 1)
            sh = min(10, c + 2)

        if self.enemy.history.count('sword') > 10:
            sh = min(10, c + 2)

        if self.health < 15:
            sh = 9
            h = 10
            c = 8
            d = f = p = sw = 4

        if self.enemy.health < 10:
            sw = 10

        if not self.effects.keys():
            c = 0

        weights = (sw, sh, f, d, h, p, c)

        self.move = random.choices(MOVES, k=1, weights=weights)[0]
        self.energy = 10000


def main(stdscr):
    curses.start_color()

    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    player = Player()
    enemy = Enemy()
    player.enemy = enemy
    enemy.enemy = player

    while True:
        stdscr.clear()
        restart = False
        if player.health <= 0 and enemy.health <= 0:
            stdscr.addstr(0, 0, 'The battle drained both of you.', curses.color_pair(4))
            restart = True
        elif player.health <= 0:
            stdscr.addstr(0, 0, 'You died!', curses.color_pair(2))
            restart = True
        elif enemy.health <= 0:
            stdscr.addstr(0, 0, 'You won!', curses.color_pair(3))
            restart = True

        if restart:
            player = Player()
            enemy = Enemy()
            player.enemy = enemy
            enemy.enemy = player
            stdscr.addstr(10, 0, 'Press any key to restart...')
        else:
            player_fx = ' | '.join([f'{i[0].capitalize()}: {i[1]}' for i in player.effects.items()])
            enemy_fx = ' | '.join([f'{i[0].capitalize()}: {i[1]}' for i in enemy.effects.items()])
            stdscr.addstr(0, 0, f'You: Health {player.health} | Energy {player.energy} | '
                                f'{player_fx}', curses.color_pair(1))
            stdscr.addstr(1, 0, f'Enemy: Health {enemy.health} | {enemy_fx}', curses.color_pair(4))

            player.take_turn(stdscr)
            enemy.take_turn()

            enemy.play()
            player.play()

            player.check_effects()
            enemy.check_effects()

            player_msg = f'You played {player.move.swapcase()}!'
            enemy_msg = f'Enemy played {enemy.move.swapcase()}!'

            stdscr.addstr(9, 0, player_msg, curses.color_pair(1))
            stdscr.addstr(9, len(player_msg), ' | ')
            stdscr.addstr(9, len(player_msg) + 3, enemy_msg, curses.color_pair(4))

            stdscr.addstr(10, 0, 'Press any key to continue...')

        stdscr.refresh()
        stdscr.getch()


if __name__ == '__main__':
    curses.wrapper(main)
