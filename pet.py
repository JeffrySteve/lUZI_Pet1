import sys
import os
import json
import random
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton
from PyQt5.QtGui import QMovie, QCursor
from PyQt5.QtCore import Qt, QTimer, QPoint, QDate, QPropertyAnimation, QEasingCurve, QSize

WATER_GOAL = 8  # glasses per day
REMINDER_INTERVAL_MINUTES = 30

class VirtualCat(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create and scale cat
        self.cat_label = QLabel(self)
        self.movie = QMovie("assets/cat_idle.gif")
        self.movie.start()  # Start movie first to get valid pixmap
        
        # Get size and scale it
        pixmap = self.movie.currentPixmap()
        width = max(1, pixmap.width() // 2)  # Ensure non-zero size
        height = max(1, pixmap.height() // 2)
        self.movie.setScaledSize(QSize(width, height))
        
        self.cat_label.setMovie(self.movie)
        self.cat_label.setFixedSize(width, height)
        self.setFixedSize(width, height)

        # Store size for sleep animation
        self.cat_size = QSize(width, height)

        self.load_water_log()

        self.cat_label.mousePressEvent = self.increment_water_intake

        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self.show_reminder)
        self.reminder_timer.start(REMINDER_INTERVAL_MINUTES * 60 * 1000)

        # Remove move_timer and only use sleep cycle
        self.sleep_timer = QTimer()
        self.sleep_timer.timeout.connect(self.go_to_sleep)
        self.sleep_timer.start(30 * 1000)  # 30 seconds awake time

        self.wake_timer = QTimer()
        self.wake_timer.timeout.connect(self.wake_up)
        
        self.is_sleeping = False
        self.idle_movie = self.movie
        self.sleep_movie = QMovie("assets/sleepy_cat.gif")
        self.sleep_movie.setScaledSize(self.cat_size)  # Set sleep gif to same size
        
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(3000)  # 3 seconds movement duration for slower movement

        self.show()

    def load_water_log(self):
        today = QDate.currentDate().toString(Qt.ISODate)
        if not os.path.exists('data'):
            os.makedirs('data')
        if not os.path.exists('data/water_log.json'):
            with open('data/water_log.json', 'w') as f:
                json.dump({}, f)
        with open('data/water_log.json', 'r') as f:
            self.water_log = json.load(f)
        if today not in self.water_log:
            self.water_log[today] = 0
        self.today = today

    def save_water_log(self):
        with open('data/water_log.json', 'w') as f:
            json.dump(self.water_log, f, indent=4)

    def increment_water_intake(self, event):
        self.water_log[self.today] += 1
        self.save_water_log()
        self.show_popup(f"🐱 Meow! Water intake: {self.water_log[self.today]}/{WATER_GOAL} glasses today!")

    def show_reminder(self):
        messages = [
            "🐱 Time to drink some water!",
            "🐱 Stretch and fix your posture!",
            "🐱 Blink and rest your eyes!",
            "🐱 Time to hydrate, hooman!"
        ]
        message = random.choice(messages)
        self.show_popup(message)

    def show_popup(self, message):
        self.popup = QLabel(message, self)
        self.popup.setStyleSheet("background-color: rgba(255, 255, 255, 200); color: black; border: 1px solid gray; padding: 5px;")
        self.popup.move(0, -30)
        self.popup.show()
        QTimer.singleShot(3000, self.popup.deleteLater)

    def random_move(self):
        screen = QApplication.primaryScreen().availableGeometry()
        # Add padding to keep cat more towards center
        padding = 100
        max_x = screen.width() - self.width() - padding
        max_y = screen.height() - self.height() - padding
        
        # Randomly choose which edge to move to (0: top, 1: right, 2: bottom, 3: left)
        edge = random.randint(0, 3)
        
        if edge == 0:  # Top edge
            new_x = random.randint(padding, max_x)
            new_y = padding
        elif edge == 1:  # Right edge
            new_x = max_x
            new_y = random.randint(padding, max_y)
        elif edge == 2:  # Bottom edge
            new_x = random.randint(padding, max_x)
            new_y = max_y
        else:  # Left edge
            new_x = padding
            new_y = random.randint(padding, max_y)
        
        self.animation.setEndValue(QPoint(new_x, new_y))
        self.animation.start()

    def go_to_sleep(self):
        if not self.is_sleeping:
            self.is_sleeping = True
            self.sleep_timer.stop()
            self.movie = self.sleep_movie
            self.cat_label.setMovie(self.movie)
            self.movie.start()
            self.wake_timer.start(30 * 1000)  # 30 seconds sleep time

    def wake_up(self):
        self.is_sleeping = False
        self.wake_timer.stop()
        self.movie = self.idle_movie
        self.cat_label.setMovie(self.movie)
        self.movie.start()
        # Move to new position after waking up
        self.random_move()
        # Restart sleep timer
        self.sleep_timer.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    cat = VirtualCat()
    sys.exit(app.exec_())