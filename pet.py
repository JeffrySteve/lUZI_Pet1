import sys
import os
import random
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGraphicsDropShadowEffect
from PyQt5.QtGui import QMovie, QColor
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, QSize, QTime

class PopupLabel(QLabel):
    def __init__(self, parent=None):
        QLabel.__init__(self, parent)  # Changed to direct init
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAlignment(Qt.AlignCenter)

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()

class VirtualCat(QWidget):
    def __init__(self):
        QWidget.__init__(self)  # Changed to direct init
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Initialize messages
        self.drag_messages = {
            'start': ["Meoooow! Put me down!", "Hey, what are you doing?"],
            'sleep_interrupt': ["Hey! I was napping there!", "Five more minutes please..."],
            'moving': ["Wheeeee!", "I can fly!", "Higher, higher!"],
            'fast_moving': ["Not the tail, not the tail!", "I'm getting dizzy...", "Too fast!"],
            'drop': ["Thanks for the ride!", "That was fun!", "Phew, solid ground!"]
        }

        # Initialize all resources before use
        self.popup = None
        self.popup_timer = QTimer()  # Initialize timer in constructor
        self.popup_update_timer = QTimer()
        self.movie = None
        self.is_sleeping = False
        self.drag_start_position = None
        self.last_move_pos = None
        self.last_move_time = 0

        # Initialize state flags
        self.is_initialized = False
        self.is_moving = False
        self.popup_message_queue = []  # Add message queue to prevent spam

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
        self.animation.setDuration(3500)  # Changed to 3.5 seconds for moderate movement

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
        self.movement_timer.start(20000)  # Changed to 20 seconds between moves

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
        if hasattr(self, 'popup') and self.popup:
            self.popup_message_queue.append(message)
            return
            
        try:
            self.cleanup_popup()

            if not self.is_sleeping:
                self._switch_animation(self.talk_movie)

            self.popup = PopupLabel()
            self.popup.setText(message)
            self.popup.setWordWrap(True)
            
            # Simpler, more reliable styling
            self.popup.setStyleSheet("""
                QLabel {
                    background-color: #ffefef;
                    color: #333333;
                    border: 2px solid #ff7777;
                    border-radius: 15px;
                    padding: 12px 16px;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            
            # Add drop shadow
            shadow = QGraphicsDropShadowEffect(self.popup)
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(2, 2)
            self.popup.setGraphicsEffect(shadow)

            self.popup.adjustSize()
            self.popup.show()
            self.update_popup_position()

            # Properly handle timers
            if self.popup_timer and self.popup_timer.isActive():
                self.popup_timer.stop()
            
            self.popup_timer = QTimer(self)
            self.popup_timer.setSingleShot(True)
            self.popup_timer.timeout.connect(self.cleanup_and_next_message)
            self.popup_timer.start(2000)

            if self.popup_update_timer and self.popup_update_timer.isActive():
                self.popup_update_timer.stop()
                
            self.popup_update_timer = QTimer(self)
            self.popup_update_timer.timeout.connect(self.update_popup_position)
            self.popup_update_timer.start(16)

        except Exception as e:
            print(f"Error showing popup: {e}")
            self.cleanup_popup()  # Ensure cleanup on error

    def cleanup_and_next_message(self):
        """Handle cleanup and show next message if any"""
        try:
            # Cleanup current popup
            if hasattr(self, 'popup'):
                self.popup.hide()
                self.popup.deleteLater()
                self.popup = None

            # Show next message after a short delay
            if self.popup_message_queue:
                next_message = self.popup_message_queue.pop(0)
                QTimer.singleShot(200, lambda: self.show_popup(next_message))
            else:
                if not self.is_sleeping:
                    self._switch_animation(self.idle_movie)
        except Exception as e:
            print(f"Error in cleanup: {e}")

    def show_next_message(self):
        """Show next message in queue or cleanup if none"""
        try:
            if self.popup_message_queue:
                next_message = self.popup_message_queue.pop(0)
                self.cleanup_popup()
                self.show_popup(next_message)
            else:
                self.cleanup_popup()
        except Exception as e:
            print(f"Error showing next message: {e}")
            self.cleanup_popup()

    def _switch_animation(self, new_movie):
        """Safely switch between animations"""
        if self.movie == new_movie:
            return
            
        try:
            old_movie = self.movie
            self.movie = new_movie
            self.cat_label.setMovie(new_movie)
            new_movie.start()
            
            if old_movie and old_movie != new_movie:
                old_movie.stop()
        except Exception as e:
            print(f"Animation switch error: {e}")
            if self.idle_movie and self.idle_movie.isValid():
                self.movie = self.idle_movie
                self.cat_label.setMovie(self.idle_movie)
                self.idle_movie.start()

    def cleanup_popup(self):
        try:
            if self.popup_update_timer and self.popup_update_timer.isActive():
                self.popup_update_timer.stop()
            if self.popup_timer and self.popup_timer.isActive():
                self.popup_timer.stop()
            if self.popup:
                self.popup.hide()
                self.popup.deleteLater()
                self.popup = None
        except Exception as e:
            print(f"Cleanup error: {e}")
        finally:
            if not self.is_sleeping:
                self._switch_animation(self.idle_movie)

    def update_popup_position(self):
        if hasattr(self, 'popup') and self.popup and self.popup.isVisible():
            self.popup.adjustSize()
            cat_pos = self.mapToGlobal(QPoint(0, 0))
            
            # Add padding for shadow in position calculation
            popup_x = cat_pos.x() + (self.width() - self.popup.width()) // 2 + 5
            popup_y = cat_pos.y() - self.popup.height() - 15
            
            # Ensure popup stays within screen bounds
            screen = QApplication.primaryScreen().availableGeometry()
            popup_x = max(5, min(popup_x, screen.width() - self.popup.width() - 5))
            popup_y = max(5, min(popup_y, screen.height() - self.popup.height() - 5))
            
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Store initial click position and window position
            self.drag_start_position = QPoint(event.globalPos() - self.frameGeometry().topLeft())
            self.animation.stop()
            if not self.is_sleeping:
                self.show_popup(random.choice(self.drag_messages['start']))
            else:
                self.is_sleeping = False
                self.wake_timer.stop()
                self.show_popup(random.choice(self.drag_messages['sleep_interrupt']))
                self.movie = self.idle_movie
                self.cat_label.setMovie(self.movie)
                self.movie.start()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton) or self.drag_start_position is None:
            return
            
        try:
            # Move window to new position
            new_pos = event.globalPos() - self.drag_start_position
            
            # Keep within screen bounds
            screen = QApplication.primaryScreen().availableGeometry()
            new_x = max(0, min(new_pos.x(), screen.width() - self.width()))
            new_y = max(0, min(new_pos.y(), screen.height() - self.height()))
            
            self.move(new_x, new_y)
            self.update_popup_position()

            # Limit popup frequency during drag
            current_time = QTime.currentTime().msecsSinceStartOfDay()
            if self.last_move_time and current_time - self.last_move_time > 500:
                if self.last_move_pos:
                    speed = (event.globalPos() - self.last_move_pos).manhattanLength()
                    if speed > 100 and not self.popup:
                        self.show_popup(random.choice(self.drag_messages['fast_moving']))
                    elif speed > 50 and not self.popup:
                        self.show_popup(random.choice(self.drag_messages['moving']))
                        
            self.last_move_pos = event.globalPos()
            self.last_move_time = current_time
            
            if hasattr(self, 'sleep_timer'):
                self.sleep_timer.start(30 * 1000)
                
        except Exception as e:
            print(f"Drag error: {e}")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.drag_start_position is not None:
                distance = (event.pos() - self.drag_start_position).manhattanLength()
                if distance > 3:  # If actually dragged
                    self.show_popup(random.choice(self.drag_messages['drop']))
                else:  # If just clicked
                    self.show_popup("Meow!")
            self.drag_start_position = None
            self.last_move_pos = None
            self.last_move_time = 0

    def closeEvent(self, event):
        """Ensure proper cleanup of all resources"""
        try:
            # Stop all timers
            for timer in [self.sleep_timer, self.wake_timer, 
                         self.movement_timer, self.popup_timer, 
                         self.popup_update_timer]:
                if hasattr(self, timer.__name__):
                    timer.stop()
                    timer.deleteLater()

            # Stop animation
            if hasattr(self, 'animation'):
                self.animation.stop()

            # Stop all movies
            for movie in [self.idle_movie, self.sleep_movie, 
                         self.talk_movie, self.loading_movie]:
                if movie:
                    movie.stop()

            # Clear labels
            if hasattr(self, 'cat_label'):
                self.cat_label.clear()
                self.cat_label.deleteLater()
            
            self.cleanup_popup()

        except Exception as e:
            print(f"Cleanup error: {e}")
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    cat = VirtualCat()
    sys.exit(app.exec_())