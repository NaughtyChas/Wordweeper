import curses
import os
from board import Board
from user import User
from user_statistics import UserStatistics

class Menu:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_row = 0
        self.current_menu = "main"
        self.current_user = None
        self.users = self.load_users()
        self.menus = {
            "main": ["Start Game", "View Statistics", "Exit Game"],
            "start_game": [],
            "classic_mode": ["Easy", "Hard", "Expert", "Back"]
        }
        self.descriptions = {
            "Start Game": "* Play some Wordweeper!",
            "View Statistics": "* Check data and statistics",
            "Exit Game": "* Exit the game",
            "Classic Mode": "* Play the classic mode",
            "Timed Mode": "* Play the timed mode",
            "Back": "* Go back to the previous menu",
            "Easy": "* Easy difficulty",
            "Hard": "* Hard difficulty",
            "Expert": "* Expert difficulty",
            "New player? Click here to register!": "* Register a new player",
            "Click here or press 'Enter' to register!": "* Register a new player"
        }
        self.ascii_art = [
            "  __          __           _                                   ",
            "  \\ \\        / /          | |                                  ",
            "   \\ \\  /\\  / /__  _ __ __| |_      _____  ___ _ __   ___ _ __ ",
            "    \\ \\/  \\/ / _ \\| '__/ _` \\ \\ /\\ / / _ \\/ _ \\ '_ \\ / _ \\ '__|",
            "     \\  /\\  / (_) | | | (_| |\\ V  V /  __/  __/ |_) |  __/ |   ",
            "      \\/  \\/ \\___/|_|  \\__,_| \\_/\\_/ \\___|\\___| .__/ \\___|_|   ",
            "                                              | |                ",
            "                                              |_|                "
        ]

    def load_users(self):
        users = []
        if os.path.exists('./data/user.txt'):
            with open('./data/user.txt', 'r') as file:
                for line in file:
                    data = line.strip().split(',')
                    if len(data) == 11:  # Ensure the correct number of fields
                        user = User(data[0], int(data[1]), int(data[2]), int(data[3]), data[4], int(data[5]), int(data[6]), int(data[7]), float(data[8]), int(data[9]), int(data[10]))
                        users.append(user)
        return users

    def check_window_size(self):
        h, w = self.stdscr.getmaxyx()
        min_height = 25
        min_width = 142

        if h < min_height or w < min_width:
            size_prompt = curses.newwin(h, w, 0, 0)
            size_prompt.clear()
            message = "Terminal window is too small! Please increase the window size."
            y = h // 2
            x = (w - len(message)) // 2
            size_prompt.addstr(y, x, message, curses.A_BOLD)
            size_prompt.refresh()
            size_prompt.getch()  # Wait for user input
            return False
        return True

    def print_menu(self, menu):
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        menu_start_y = (h - len(self.ascii_art) - len([item for item in menu if item != ""])) // 2 + len(self.ascii_art)
        for idx, row in enumerate(self.ascii_art):
            self.stdscr.addstr(idx, (w - len(row)) // 2, row)
        for idx, row in enumerate(menu):
            if row == "":
                continue  # Skip empty lines for spacing
            x = 2  # Align menu items to the left
            y = menu_start_y + idx
            if idx == self.current_row:
                self.stdscr.attron(curses.color_pair(1))
                self.stdscr.addstr(y, x, row)
                self.stdscr.attroff(curses.color_pair(1))
            else:
                self.stdscr.addstr(y, x, row)
        self.stdscr.refresh()

    def handle_enter(self):
        menu = self.menus[self.current_menu]
        if self.current_menu == "main":
            if menu[self.current_row] == "Start Game":
                self.start_game()
            elif menu[self.current_row] == "View Statistics":
                self.view_statistics()
            elif menu[self.current_row] == "Exit Game":
                exit()
        elif self.current_menu == "start_game":
            if menu[self.current_row] == "New player? Click here to register!" or menu[self.current_row] == "Click here or press 'Enter' to register!":
                self.current_menu = "register"
                self.register()
            elif self.current_row < len(self.users):
                self.current_user = self.users[self.current_row]
                self.current_menu = "user_menu"
                self.current_row = 0
        elif self.current_menu == "register":
            self.register()

    def start_game(self):
        if not self.users:
            self.menus["start_game"] = ["Click here or press 'Enter' to register!"]
        else:
            self.menus["start_game"] = [user.user_id for user in self.users] + ["New player? Click here to register!"]
        self.current_menu = "start_game"
        self.current_row = 0

    def register(self):
        self.stdscr.addstr(0, 0, "Enter user ID: ")
        curses.echo()
        user_id = self.stdscr.getstr().decode('utf-8')
        curses.noecho()
        if User.load_from_file(user_id):
            self.stdscr.addstr(1, 0, "User ID already exists. Press any key to continue.")
            self.stdscr.getch()
        else:
            user = User(user_id)
            user.save_to_file()
            self.users.append(user)
            self.stdscr.addstr(1, 0, "Registration successful. Press any key to continue.")
            self.stdscr.getch()
        self.current_menu = "main"
        self.current_row = 0

    def view_statistics(self):
        stats = UserStatistics(self.stdscr)
        stats.display()
        self.current_menu = "main"
        self.current_row = 0

    def run(self):
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        while True:
            if not self.check_window_size():
                continue
            self.print_menu(self.menus[self.current_menu])
            key = self.stdscr.getch()
            if key == curses.KEY_UP and self.current_row > 0:
                self.current_row -= 1
            elif key == curses.KEY_DOWN and self.current_row < len(self.menus[self.current_menu]) - 1:
                self.current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                self.handle_enter()
            elif key == 27:  # ESC key
                if self.current_menu == "main":
                    exit()
                elif self.current_menu == "start_game" or self.current_menu == "register":
                    self.current_menu = "main"
                    self.current_row = 0
            elif key == curses.KEY_MOUSE:
                _, mx, my, _, _ = curses.getmouse()
                h, w = self.stdscr.getmaxyx()
                menu_start_y = (h - len(self.ascii_art) - len([item for item in self.menus[self.current_menu] if item != ""])) // 2 + len(self.ascii_art)
                for idx, row in enumerate(self.menus[self.current_menu]):
                    if row == "":
                        continue  # Skip empty lines for spacing
                    x = 2  # Align menu items to the left
                    y = menu_start_y + idx
                    if y == my:
                        self.current_row = idx
                        self.handle_enter()
                        break

if __name__ == "__main__":
    curses.wrapper(Menu)