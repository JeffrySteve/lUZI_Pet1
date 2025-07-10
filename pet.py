import sys
import os

import random
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, QSize

class PopupLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)  # Use super() instead of direct init
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAlignment(Qt.AlignCenter)

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()

class VirtualCat(QWidget):
    def __init__(self):
        super().__init__()  # Use super() instead of direct init
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Initialize messages
        self.drag_messages = [
            "Meoooow! Put me down!",
            "Hey! I was napping there!",
            "Wheeeee!",
            "Not the tail, not the tail!",
            "I'm getting dizzy..."
        ]

        # Initialize all resources before use
        self.popup = None
        self.popup_timer = None
        self.popup_update_timer = None
        self.movie = None
        self.is_sleeping = False
        self.drag_start_position = None

        # Initialize state flags
        self.is_initialized = False
        self.is_moving = False

        try:
            # Load and validate all animations first
            self.load_animations()
            self.init_timers()
            self.setup_animations()
            self.is_initialized = True
        except Exception as e:
            print(f"Initialization failed: {e}")
            sys.exit(1)

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

    def load_animations(self):
        """Load all animation files"""
        self.idle_movie = self._load_movie("assets/cat_idle.gif")
        self.sleep_movie = self._load_movie("assets/sleepy_cat.gif")
        self.talk_movie = self._load_movie("assets/cat.gif")
        self.loading_movie = self._load_movie("assets/loading_cat.gif")
        
        # Initialize cat with idle animation
        self.movie = self.idle_movie
        self.cat_label = QLabel(self)
        self.cat_label.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.cat_label.setMovie(self.movie)
        self.movie.start()

    def init_timers(self):
        """Safely initialize all timers"""
        self.sleep_timer = QTimer(self)
        self.wake_timer = QTimer(self)
        self.movement_timer = QTimer(self)

        self.sleep_timer.timeout.connect(self.go_to_sleep)
        self.wake_timer.timeout.connect(self.wake_up)
        self.movement_timer.timeout.connect(self.random_move)

        self.sleep_timer.start(30 * 1000)
        self.movement_timer.start(15000)

    def _load_movie(self, path):
        """Safely load and validate movie file"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Animation file not found: {path}")
        movie = QMovie(path)
        if not movie.isValid():
            raise RuntimeError(f"Invalid animation file: {path}")
        movie.setCacheMode(QMovie.CacheAll)
        return movie

    def setup_animations(self):
        """Setup animation sizes and scaling"""
        pixmap = self.movie.currentPixmap()
        width = max(1, pixmap.width() // 2)
        height = max(1, pixmap.height() // 2)
        self.cat_size = QSize(width, height)
        
        # Scale all animations
        self.idle_movie.setScaledSize(self.cat_size)
        sleep_size = QSize(int(width * 0.5), int(height * 0.5))
        self.sleep_movie.setScaledSize(sleep_size)
        self.talk_movie.setScaledSize(self.cat_size)
        self.loading_movie.setScaledSize(self.cat_size)
        
        # Set widget sizes
        self.cat_label.setFixedSize(width, height)
        self.setFixedSize(width, height)

    def show_popup(self, message):
        """Thread-safe popup display"""
        try:
            self.cleanup_popup()  # Clean existing popup first
            if not self.is_sleeping:
                self._switch_animation(self.talk_movie)

            self.popup = PopupLabel()
            self.popup.setText(message)
            self.popup.setWordWrap(True)
            self.popup.setStyleSheet("""
                QLabel {
                    background-color: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #ffffff, stop: 1 #f0f0f0
                    );
                    color: #333333;
                    border: 2px solid #c0c0c0;
                    border-radius: 15px;
                    padding: 12px 18px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 200px;
                    max-width: 300px;
                }
            """)

            self.popup.adjustSize()
            self.update_popup_position()
            self.popup.show()

            self.popup_update_timer = QTimer(self)
            self.popup_update_timer.timeout.connect(self.update_popup_position)
            self.popup_update_timer.start(16)  # Update at ~60fps

            self.popup_timer = QTimer()
            self.popup_timer.setSingleShot(True)
            self.popup_timer.timeout.connect(self.cleanup_popup)
            self.popup_timer.start(3000)
        except Exception as e:
            print(f"Error showing popup: {e}")

    def _switch_animation(self, new_movie):
        """Safely switch between animations"""
        if self.movie != new_movie:
            self.movie = new_movie
            self.cat_label.setMovie(self.movie)
            self.movie.start()

    def cleanup_popup(self):
        try:
            if hasattr(self, 'popup_update_timer'):
                self.popup_update_timer.stop()
                self.popup_update_timer.deleteLater()
            if hasattr(self, 'popup_timer'):
                self.popup_timer.stop()
                self.popup_timer.deleteLater()
            if hasattr(self, 'popup'):
                self.popup.hide()
                self.popup.deleteLater()
                self.popup = None
        except Exception:
            pass
        finally:
            if not self.is_sleeping:
                self.movie = self.idle_movie
                self.cat_label.setMovie(self.movie)
                self.movie.start()

    def update_popup_position(self):
        if hasattr(self, 'popup') and self.popup and self.popup.isVisible():
            self.popup.adjustSize()
            cat_pos = self.mapToGlobal(QPoint(0, 0))
            popup_x = cat_pos.x() + (self.width() - self.popup.width()) // 2
            popup_y = cat_pos.y() - self.popup.height() - 10
            # Ensure popup stays within screen bounds
            screen = QApplication.primaryScreen().availableGeometry()
            popup_x = max(0, min(popup_x, screen.width() - self.popup.width()))
            popup_y = max(0, min(popup_y, screen.height() - self.popup.height()))
            self.popup.move(popup_x, popup_y)

    def random_move(self):
        if self.is_sleeping or self.is_moving or not self.is_initialized:
            return

        self.is_moving = True
        try:
            # Disconnect previous connections to avoid multiple calls
            try:
                self.animation.finished.disconnect()
            except:
                pass

            screen = QApplication.primaryScreen().availableGeometry()
            padding = 100

            # Get current position
            current_pos = self.pos()

            # Calculate new random position within visible screen
            new_x = random.randint(padding, screen.width() - self.width() - padding)
            new_y = random.randint(padding, screen.height() - self.height() - padding)

            # Ensure minimum movement distance
            while abs(new_x - current_pos.x()) < 100 and abs(new_y - current_pos.y()) < 100:
                new_x = random.randint(padding, screen.width() - self.width() - padding)
                new_y = random.randint(padding, screen.height() - self.height() - padding)

            self.animation.setEndValue(QPoint(new_x, new_y))
            self.animation.finished.connect(self.finish_move)
            self.animation.start()
        except Exception as e:
            print(f"Movement error: {e}")
            self.is_moving = False

    def finish_move(self):
        """Handle movement completion"""
        self.is_moving = False
        self.update_popup_position()

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

    def mousePressEvent(self, event):  # Fix method name
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos()
            self.animation.stop()
            if not self.is_sleeping:
                self.show_popup(random.choice(self.drag_messages))

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton) or self.drag_start_position is None:
            return
            
        # Calculate new position with proper error checking
        try:
            current_pos = event.globalPos()
            delta = current_pos - self.drag_start_position
            new_pos = self.pos() + delta
            self.drag_start_position = current_pos  # Update drag position
            
            # Keep within screen bounds
            screen = QApplication.primaryScreen().availableGeometry()
            new_x = max(0, min(new_pos.x(), screen.width() - self.width()))
            new_y = max(0, min(new_pos.y(), screen.height() - self.height()))
            
            self.move(new_x, new_y)
            self.update_popup_position()
            
            if hasattr(self, 'sleep_timer'):
                self.sleep_timer.start(30 * 1000)
        except Exception as e:
            print(f"Drag error: {e}")
            self.drag_start_position = None

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.drag_start_position is not None:
                distance = (event.pos() - self.drag_start_position).manhattanLength()
                if distance < 3:  # If barely moved, count as click
                    self.show_popup("Meow!")  # Replace water increment with simple meow
            self.drag_start_position = None

    def closeEvent(self, event):
        # Proper cleanup with error handling
        try:
            if hasattr(self, 'movement_timer'):
                self.movement_timer.stop()
            if hasattr(self, 'animation'):
                self.animation.stop()
            # ...existing cleanup code...
        except Exception as e:
            print(f"Cleanup error: {e}")
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    cat = VirtualCat()
    sys.exit(app.exec_())