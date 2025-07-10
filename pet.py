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

        self.cat_label.mousePressEvent = self.handle_mouse_press
        self.drag_start_position = None
        self.drag_messages = [
            "Meoooow! Put me down!",
            "Hey! I was napping there!",
            "Wheeeee!",
            "Not the tail, not the tail!",
            "I'm getting dizzy..."
        ]

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
        self.talk_movie = QMovie("assets/cat.gif")  # Add talking animation
        self.sleep_movie.setScaledSize(self.cat_size)  # Set sleep gif to same size
        self.talk_movie.setScaledSize(self.cat_size)
        
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(3000)  # 3 seconds movement duration for slower movement

        self.show()
        # Show welcome message after initialization
        welcome_messages = [
            "Hello hooman! I'm here to help you stay hydrated!",
            "Meow! Let's work together today!",
            "Hi friend! Don't forget to drink water!",
            "Purr~ I'll keep you company today!"
        ]
        self.show_popup(random.choice(welcome_messages))

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
        # Switch to talking animation
        if not self.is_sleeping:
            self.movie = self.talk_movie
            self.cat_label.setMovie(self.movie)
            self.movie.start()

        # Safely delete existing popup
        try:
            if hasattr(self, 'popup') and self.popup:
                self.popup.hide()
                self.popup.deleteLater()
        except:
            pass
            
        # Create new popup with proper parenting
        self.popup = QLabel(self)
        self.popup.setText(message)
        self.popup.setWordWrap(True)  # Enable word wrapping
        self.popup.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.95);
                color: #000000;
                border: 2px solid #808080;
                border-radius: 15px;
                padding: 12px 18px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
                max-width: 300px;
            }
        """)
        
        # Ensure proper sizing and positioning
        self.popup.adjustSize()
        popup_x = (self.width() - self.popup.width()) // 2
        popup_y = -self.popup.height() - 10
        self.popup.move(popup_x, popup_y)
        
        # Ensure visibility
        self.popup.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.popup.raise_()
        self.popup.show()
        
        # Single cleanup timer
        def cleanup():
            if hasattr(self, 'popup') and self.popup:
                self.popup.deleteLater()
                self.popup = None
            if not self.is_sleeping:
                self.movie = self.idle_movie
                self.cat_label.setMovie(self.movie)
                self.movie.start()
                
        QTimer.singleShot(3000, cleanup)  # Increased display time to 3 seconds

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

    def handle_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            # Store initial position relative to window
            self.drag_start_position = event.pos()
            self.animation.stop()
            if not self.is_sleeping:
                self.show_popup(random.choice(self.drag_messages))

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_start_position is not None:
            # Reset sleep timer when dragging
            self.sleep_timer.start(30 * 1000)
            
            # Calculate movement delta
            delta = event.pos() - self.drag_start_position
            new_pos = self.pos() + delta
            
            # Keep cat within screen bounds
            screen = QApplication.primaryScreen().availableGeometry()
            new_x = max(0, min(new_pos.x(), screen.width() - self.width()))
            new_y = max(0, min(new_pos.y(), screen.height() - self.height()))
            
            self.move(new_x, new_y)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if we actually dragged
            if self.drag_start_position is not None:
                distance = (event.pos() - self.drag_start_position).manhattanLength()
                if distance < 3:  # If barely moved, count as click
                    self.increment_water_intake(event)
            self.drag_start_position = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    cat = VirtualCat()
    sys.exit(app.exec_())