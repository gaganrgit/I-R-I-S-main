from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

def AnswerModifier(Answer):
    Lines = Answer.split("\n")
    non_empty_lines = [Line for Line in Lines if Line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    
    if any(word in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1]
        else:
            pass
        new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1]
        else:
            pass
        new_query += "."
    
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data', "w", encoding='utf-8') as file:
        file.write(Text)

class MainScreen(QWidget):
    def _init_(self):
        super()._init_()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top bar
        top_bar = CustomTopBar(self)
        layout.addWidget(top_bar)

        # Main content area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Chat section (left side)
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(20, 20, 20, 20)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        font = QFont()
        font.setPointSize(11)
        self.chat_text_edit.setFont(font)
        
        chat_layout.addWidget(self.chat_text_edit)
        
        # Status label for typing/listening
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                color: #4A9EFF;
                font-size: 14px;
                margin-top: 10px;
            }
        """)
        chat_layout.addWidget(self.status_label)

        # Visualization section (right side)
        visual_widget = QWidget()
        visual_layout = QVBoxLayout(visual_widget)
        visual_layout.setContentsMargins(0, 0, 0, 0)
        visual_layout.setSpacing(0)
        
        # Create a container for the GIF with vertical centering
        gif_container = QWidget()
        gif_container_layout = QVBoxLayout(gif_container)
        gif_container_layout.setContentsMargins(0, 0, 0, 0)
        gif_container_layout.addStretch(1)  # Less space at top
        
        # Add the Jarvis GIF
        self.gif_label = QLabel()
        self.movie = QMovie(os.path.join(GraphicsDirPath, "Jarvis.gif"))
        self.movie.setScaledSize(QSize(600, 600))
        self.gif_label.setMovie(self.movie)
        self.movie.start()
        self.movie.setSpeed(50)  # Start with slower speed
        gif_container_layout.addWidget(self.gif_label, alignment=Qt.AlignCenter)
        gif_container_layout.addStretch(2)  # More space at bottom
        
        visual_layout.addWidget(gif_container)
        
        # Add the microphone button at the bottom
        mic_container = QWidget()
        mic_layout = QVBoxLayout(mic_container)
        mic_layout.setContentsMargins(0, 0, 0, 40)  # Increased bottom margin
        
        self.mic_button = QPushButton()
        self.mic_button.setFixedSize(60, 60)
        self.mic_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 30px;
            }
        """)
        self.toggled = True
        self.updateMicIcon()
        self.mic_button.clicked.connect(self.toggleMic)
        
        mic_layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)
        visual_layout.addWidget(mic_container)

        # Add sections to main content
        content_layout.addWidget(chat_widget, 60)
        content_layout.addWidget(visual_widget, 40)

        layout.addWidget(content_widget)
        
        # Set up timers for updates
        self.message_timer = QTimer(self)
        self.message_timer.timeout.connect(self.loadMessages)
        self.message_timer.start(100)

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.updateStatus)
        self.status_timer.start(100)

        self.setStyleSheet("background-color: #000000;")

    def updateMicIcon(self):
        icon_path = os.path.join(GraphicsDirPath, "Mic_on.png" if self.toggled else "Mic_off.png")
        self.mic_button.setIcon(QIcon(icon_path))
        self.mic_button.setIconSize(QSize(40, 40))
        # Update animation speed based on mic state
        if self.toggled:
            self.movie.setSpeed(50)  # Slower when mic is off
        else:
            self.movie.setSpeed(100)  # Normal speed when mic is on

    def toggleMic(self):
        self.toggled = not self.toggled
        self.updateMicIcon()
        SetMicrophoneStatus("False" if self.toggled else "True")

    def loadMessages(self):
        global old_chat_message
        try:
            with open(os.path.join(TempDirPath, 'Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()

            if messages and messages != old_chat_message:
                self.addMessage(messages, 'white')
                old_chat_message = messages
        except Exception as e:
            print(f"Error loading messages: {e}")

    def updateStatus(self):
        try:
            with open(os.path.join(TempDirPath, 'Status.data'), "r", encoding='utf-8') as file:
                status = file.read()
            self.status_label.setText(status)
        except Exception as e:
            print(f"Error updating status: {e}")

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        block_format = QTextBlockFormat()
        block_format.setTopMargin(10)
        block_format.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(block_format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)
        self.chat_text_edit.ensureCursorVisible()

class CustomTopBar(QWidget):
    def _init_(self, parent=None):
        super()._init_(parent)
        self.initUI()
        self.parent = parent

    def initUI(self):
        self.setFixedHeight(40)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)

        # Title with spaced letters
        title_text = " ".join("J A R V I S")
        title_label = QLabel(title_text)
        title_label.setStyleSheet("""
            QLabel {
                color: #4A9EFF;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 2px;
            }
        """)
        layout.addWidget(title_label)
        
        layout.addStretch()

        # Window controls
        for button_data in [
            ("minimize", self.minimizeWindow),
            ("maximize", self.maximizeWindow),
            ("close", self.closeWindow)
        ]:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(74, 158, 255, 0.2);
                    border-radius: 15px;
                }
            """)
            btn.setIcon(QIcon(os.path.join(GraphicsDirPath, f"{button_data[0]}.png")))
            btn.clicked.connect(button_data[1])
            layout.addWidget(btn)

        self.setStyleSheet("background-color: #000000;")
        
        self.draggable = True
        self.offset = None

    def minimizeWindow(self):
        self.window().showMinimized()

    def maximizeWindow(self):
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def closeWindow(self):
        self.window().close()

    def mousePressEvent(self, event):
        if self.draggable and event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            self.window().move(event.globalPos() - self.offset)

class MainWindow(QMainWindow):
    def _init_(self):
        super()._init_()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        self.central_widget = MainScreen()
        self.setCentralWidget(self.central_widget)
        
        # Set initial window size to 85% of screen size
        screen = QApplication.primaryScreen().size()
        self.resize(int(screen.width() * 0.85), int(screen.height() * 0.85))
        
        # Center the window
        self.center()
        
        # Set window background color
        self.setStyleSheet("background-color: #000000;")  # Pure black background

    def center(self):
        frame = self.frameGeometry()
        center = QApplication.primaryScreen().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "_main_":
    GraphicalUserInterface()