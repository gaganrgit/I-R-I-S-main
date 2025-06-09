from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtGui import (QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, 
                        QTextBlockFormat, QLinearGradient, QPen, QBrush, QPainterPath, QRadialGradient)
from PyQt5.QtCore import (Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRect, 
                         QRectF, QPointF, pyqtProperty, QUrl)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import sys
import os
import math
import random
from dotenv import dotenv_values

# Environment setup
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "IRIS")
# Get the Frontend directory path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
old_chat_message = ""
TempDirPath = os.path.join(current_dir, "Files")
GraphicsDirPath = os.path.join(current_dir, "Graphics")

# Ensure directories exist
os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(GraphicsDirPath, exist_ok=True)

# Utility functions
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

# Custom button with glow effect
class NeonButton(QPushButton):
    def __init__(self, *args, **kwargs):
        self._glow_color = kwargs.pop('glow_color', QColor("#4A9EFF"))
        self._glow_radius = kwargs.pop('glow_radius', 20)
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 30px;
            }
        """)
        
        # Add glow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(self._glow_radius)
        self.shadow.setColor(self._glow_color)
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)
        
        # Animation for pulsating glow
        self.animation = QPropertyAnimation(self.shadow, b"blurRadius")
        self.animation.setDuration(1500)
        self.animation.setStartValue(self._glow_radius)
        self.animation.setEndValue(self._glow_radius * 2)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setLoopCount(-1)  # Infinite loop
        self.animation.start()

# Animated text display with typing effect and conversation history
class AnimatedTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #E0E0E0;
                border: none;
                border-radius: 15px;
                padding: 15px;
            }
            QScrollBar:vertical {
                border: none;
                background: #000000;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #4A9EFF;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        font = QFont("Consolas", 11)
        self.setFont(font)
        
        # For typing animation
        self.full_text = ""
        self.current_text = ""
        self.typing_index = 0
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self.type_text)
        self.typing_speed = 1  # ms between characters
        
        # For conversation history
        self.conversation_history = []
        
        # For background effects
        self.ripple_centers = []
        self.ripple_timer = QTimer(self)
        self.ripple_timer.timeout.connect(self.update_ripples)
        self.ripple_timer.start(50)
        
    def set_text(self, text):
        if text != self.full_text:
            # Store the previous conversation if it exists
            if self.full_text and self.full_text.strip():
                self.conversation_history.append(self.full_text)
            
            # Set the new text to be the full history with the new message
            history_text = ""
            for i, conv in enumerate(self.conversation_history):
                history_text += conv
                if i < len(self.conversation_history) - 1:
                    history_text += "\n\n\n\n"  # Add four line breaks between conversations
            
            if history_text:
                history_text += "\n\n\n\n"  # Add four line breaks before new text
                
            self.full_text = history_text + text
            self.current_text = ""
            self.typing_index = 0
            self.typing_timer.start(self.typing_speed)
            # Add a new ripple
            self.add_ripple()
    
    def type_text(self):
        if self.typing_index < len(self.full_text):
            self.current_text += self.full_text[self.typing_index]
            self.typing_index += 1
            self.setText(self.current_text)
            self.ensureCursorVisible()
        else:
            self.typing_timer.stop()
    
    def add_ripple(self):
        width = self.width()
        height = self.height()
        center_x = random.randint(0, width)
        center_y = random.randint(0, height)
        self.ripple_centers.append({
            'x': center_x,
            'y': center_y,
            'radius': 0,
            'max_radius': random.randint(100, 200),
            'color': QColor(74, 158, 255, 30)
        })
    
    def update_ripples(self):
        updated_ripples = []
        for ripple in self.ripple_centers:
            ripple['radius'] += 2
            if ripple['radius'] < ripple['max_radius']:
                updated_ripples.append(ripple)
        self.ripple_centers = updated_ripples
        self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw ripple effects
        for ripple in self.ripple_centers:
            painter.setPen(Qt.NoPen)
            gradient = QRadialGradient(ripple['x'], ripple['y'], ripple['radius'])
            gradient.setColorAt(0, QColor(74, 158, 255, 30))
            gradient.setColorAt(1, QColor(74, 158, 255, 0))
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(QPoint(ripple['x'], ripple['y']), ripple['radius'], ripple['radius'])

# Advanced IRIS visualization panel with circular audio waves
# Advanced IRIS visualization panel with high-tech style
class AdvancedVisualizationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")
        
        # Rings for visualization
        self.rings = []
        self.max_rings = 8  # Multiple rings for complex effect
        self.generate_rings()
        
        # Segments for arc visualization
        self.segments = []
        self.num_segments = 36  # Segments around the circle
        self.generate_segments()
        
        # Particles for holographic effect
        self.particles = []
        self.max_particles = 200
        self.generate_particles()
        
        # Scanning effect
        self.scan_angle = 0
        self.scan_active = False
        
        # Animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_visualization)
        self.animation_timer.start(16)  # ~60fps
        
        # Rotation angles
        self.rotation_angle = 0
        self.secondary_angle = 0
        
        # Active state
        self.active = False
        self.pulse_factor = 0
        self.pulse_direction = 1
        
        # Colors
        self.blue_color = QColor(0, 180, 255)
        self.cyan_color = QColor(0, 255, 255)
        self.highlight_color = QColor(255, 255, 255)
        
        # Animation phase
        self.animation_phase = 0
        self.phase_timer = 0
        
    def generate_rings(self):
        for i in range(self.max_rings):
            # Create rings with different properties
            self.rings.append({
                'radius': 40 + i * 25,  # Increasing radius for each ring
                'thickness': random.uniform(1, 3),
                'rotation_speed': 0.2 * (1 if i % 2 == 0 else -1) * random.uniform(0.5, 1.5),
                'rotation': random.uniform(0, 2 * math.pi),
                'opacity': random.uniform(0.5, 1.0),
                'dash_pattern': [random.randint(2, 15), random.randint(2, 15)] if i % 3 != 0 else [],
                'active': random.random() > 0.3,  # Some rings start inactive
                'activation_delay': random.uniform(0, 5),  # Delay before ring becomes active
                'pulse_offset': random.uniform(0, 2 * math.pi)  # Offset for pulsing effect
            })
    
    def generate_segments(self):
        for i in range(self.num_segments):
            angle = 2 * math.pi * i / self.num_segments
            self.segments.append({
                'start_angle': angle,
                'span': 2 * math.pi / self.num_segments * 0.8,  # Leave small gap between segments
                'inner_radius': random.uniform(100, 150),
                'outer_radius': random.uniform(180, 220),
                'active': random.random() > 0.5,
                'highlight': random.random() > 0.8,
                'opacity': random.uniform(0.3, 0.8),
                'pulse_speed': random.uniform(0.02, 0.05)
            })
            
    def generate_particles(self):
        for _ in range(self.max_particles):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.1, 0.9)  # Distance from center (0-1)
            self.particles.append({
                'x': 0.5 + math.cos(angle) * distance,
                'y': 0.5 + math.sin(angle) * distance,
                'size': random.uniform(0.5, 2.5),
                'speed': random.uniform(0.001, 0.004),
                'angle': angle,
                'distance': distance,
                'opacity': random.uniform(0.3, 0.9),
                'color': random.choice([self.blue_color, self.cyan_color, self.highlight_color]),
                'pulse_factor': random.uniform(0, 2 * math.pi)
            })
        
    def set_active(self, active):
        """Set the active state of the visualization panel."""
        self.active = active
        self.update()  # Trigger a repaint
        
    def update_visualization(self):
        # Update rotation angles
        self.rotation_angle += 0.005
        self.secondary_angle += 0.008
        if self.rotation_angle > 2 * math.pi:
            self.rotation_angle -= 2 * math.pi
        if self.secondary_angle > 2 * math.pi:
            self.secondary_angle -= 2 * math.pi
            
        # Update pulse effect
        self.pulse_factor += 0.02 * self.pulse_direction
        if self.pulse_factor > 1:
            self.pulse_factor = 1
            self.pulse_direction = -1
        elif self.pulse_factor < 0:
            self.pulse_factor = 0
            self.pulse_direction = 1
            
        # Update scan effect
        if self.scan_active:
            self.scan_angle += 0.1
            if self.scan_angle > 2 * math.pi:
                self.scan_active = False
                
        # Update animation phase
        self.phase_timer += 0.016  # ~16ms per frame
        if self.phase_timer > (2 if self.active else 5):  # Faster phase changes when active
            self.phase_timer = 0
            self.animation_phase = (self.animation_phase + 1) % 5
            
            # Randomly activate/deactivate segments
            for segment in self.segments:
                if random.random() > 0.7:
                    segment['active'] = random.random() > 0.3
                if random.random() > 0.9:
                    segment['highlight'] = random.random() > 0.7
            
            # Randomly activate/deactivate rings
            for ring in self.rings:
                if random.random() > 0.8:
                    ring['active'] = random.random() > 0.2
            
        # Update rings
        for ring in self.rings:
            if self.active and ring['activation_delay'] > 0:
                ring['activation_delay'] -= 0.016
                if ring['activation_delay'] <= 0:
                    ring['active'] = True
                    
            ring['rotation'] += ring['rotation_speed'] * (2 if self.active else 1)
            if ring['rotation'] > 2 * math.pi:
                ring['rotation'] -= 2 * math.pi
                
            # Pulse opacity based on phase
            pulse = 0.5 + 0.5 * math.sin(self.pulse_factor * 2 * math.pi + ring['pulse_offset'])
            ring['opacity'] = 0.5 + 0.5 * pulse if ring['active'] else 0.2
        
        # Update segments
        for segment in self.segments:
            # Pulse opacity based on activity
            if segment['active']:
                segment['opacity'] += segment['pulse_speed'] * (1 if random.random() > 0.5 else -1)
                segment['opacity'] = max(0.3, min(0.9, segment['opacity']))
            else:
                segment['opacity'] = max(0.1, segment['opacity'] - 0.01)
        
        # Update particles
        for particle in self.particles:
            # Update pulse factor
            particle['pulse_factor'] += 0.01
            if particle['pulse_factor'] > 2 * math.pi:
                particle['pulse_factor'] -= 2 * math.pi
                
            # Pulse size and opacity
            pulse = 0.5 + 0.5 * math.sin(particle['pulse_factor'])
            
            # Rotate particles around center with varying speeds
            particle['angle'] += particle['speed'] * (3 if self.active else 1)
            if particle['angle'] > 2 * math.pi:
                particle['angle'] -= 2 * math.pi
                
            # Update position based on angle and distance
            particle['x'] = 0.5 + math.cos(particle['angle']) * particle['distance']
            particle['y'] = 0.5 + math.sin(particle['angle']) * particle['distance']
            
            # Randomly change distance for some particles
            if random.random() < 0.005:
                particle['distance'] = random.uniform(0.1, 0.9)
                
            # Update opacity based on activity
            if self.active:
                particle['opacity'] = 0.3 + 0.7 * pulse
                particle['size'] = particle['size'] * 0.95 + random.uniform(0.5, 2.5) * 0.05
            else:
                particle['opacity'] = 0.1 + 0.3 * pulse
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw pure black background
        painter.fillRect(self.rect(), QColor("#000000"))
        
        # Get center coordinates
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        # Draw particles
        for particle in self.particles:
            x = particle['x'] * self.width()
            y = particle['y'] * self.height()
            
            # Size based on activity
            size = particle['size'] * (1.5 if self.active else 1)
            
            # Draw particle with glow
            color = QColor(particle['color'])
            color.setAlphaF(particle['opacity'])
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(x, y), size, size)
            
            # Add small glow for some particles
            if particle['size'] > 1.5 and random.random() > 0.7:
                glow_color = QColor(color)
                glow_color.setAlphaF(particle['opacity'] * 0.3)
                painter.setBrush(QBrush(glow_color))
                painter.drawEllipse(QPointF(x, y), size * 2, size * 2)
        
        # Draw segments (arc sections)
        for segment in self.segments:
            if segment['active'] or segment['opacity'] > 0.1:
                # Calculate angles with rotation
                start_angle = segment['start_angle'] + self.rotation_angle
                
                # Create gradient for segment
                if segment['highlight']:
                    color = QColor(255, 255, 255, int(segment['opacity'] * 255))
                else:
                    color = QColor(0, 180, 255, int(segment['opacity'] * 255))
                
                # Draw arc segment
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(color))
                
                # Create path for segment
                path = QPainterPath()
                
                # Convert to degrees for Qt
                start_degrees = math.degrees(start_angle)
                span_degrees = math.degrees(segment['span'])
                
                # Draw segment as pie slice
                inner_radius = segment['inner_radius'] * (1.1 if self.active else 1.0)
                outer_radius = segment['outer_radius'] * (1.1 if self.active else 1.0)
                
                # Create path for segment
                path.moveTo(center_x + math.cos(start_angle) * inner_radius, 
                           center_y + math.sin(start_angle) * inner_radius)
                path.arcTo(center_x - inner_radius, center_y - inner_radius, 
                          inner_radius * 2, inner_radius * 2, 
                          start_degrees, span_degrees)
                path.lineTo(center_x + math.cos(start_angle + segment['span']) * outer_radius, 
                           center_y + math.sin(start_angle + segment['span']) * outer_radius)
                path.arcTo(center_x - outer_radius, center_y - outer_radius, 
                          outer_radius * 2, outer_radius * 2, 
                          start_degrees + span_degrees, -span_degrees)
                path.closeSubpath()
                
                painter.drawPath(path)
        
        # Draw rings
        for ring in self.rings:
            if ring['active'] or ring['opacity'] > 0.1:
                pen = QPen(QColor(0, 180, 255, int(255 * ring['opacity'])))
                pen.setWidthF(ring['thickness'])
                if ring['dash_pattern']:
                    pen.setDashPattern(ring['dash_pattern'])
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                
                # Draw rotated ring
                painter.save()
                painter.translate(center_x, center_y)
                painter.rotate(math.degrees(ring['rotation']))
                painter.drawEllipse(QPoint(0, 0), ring['radius'], ring['radius'])
                painter.restore()
        
        # Draw scan line effect
        if self.scan_active:
            scan_pen = QPen(QColor(0, 255, 255, 150))
            scan_pen.setWidth(2)
            painter.setPen(scan_pen)
            
            # Draw scan line
            line_length = max(self.width(), self.height()) * 1.5
            scan_x = center_x + math.cos(self.scan_angle) * line_length
            scan_y = center_y + math.sin(self.scan_angle) * line_length
            painter.drawLine(center_x, center_y, scan_x, scan_y)
            
            # Draw scan glow
            glow_gradient = QRadialGradient(center_x, center_y, 50)
            glow_gradient.setColorAt(0, QColor(0, 255, 255, 100))
            glow_gradient.setColorAt(1, QColor(0, 255, 255, 0))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(glow_gradient))
            painter.drawEllipse(QPointF(center_x, center_y), 50, 50)
        
        # Draw center core
        core_radius = 40 * (1.2 if self.active else 1.0)
        
        # Draw outer glow
        glow_radius = core_radius + 20
        glow_gradient = QRadialGradient(center_x, center_y, glow_radius * 2)
        glow_gradient.setColorAt(0, QColor(0, 255, 255, 100))
        glow_gradient.setColorAt(0.5, QColor(0, 150, 255, 30))
        glow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow_gradient))
        painter.drawEllipse(QPointF(center_x, center_y), glow_radius, glow_radius)
        
        # Draw center core with gradient
        core_gradient = QRadialGradient(center_x, center_y, core_radius)
        core_gradient.setColorAt(0, QColor(255, 255, 255, 200))
        core_gradient.setColorAt(0.5, QColor(0, 255, 255, 150))
        core_gradient.setColorAt(1, QColor(0, 150, 255, 100))
        
        painter.setBrush(QBrush(core_gradient))
        painter.drawEllipse(QPointF(center_x, center_y), core_radius, core_radius)
        
        # Draw inner circles for tech effect
        for i in range(3):
            inner_radius = core_radius * (0.8 - i * 0.2)
            painter.setPen(QPen(QColor(255, 255, 255, 150 - i * 40), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(center_x, center_y), inner_radius, inner_radius)
        
        # Draw holographic elements that appear and disappear
        if self.animation_phase % 5 == 0:
            # Draw triangular markers
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(0, 255, 255, 150)))
            
            for i in range(4):
                angle = i * math.pi / 2 + self.secondary_angle
                marker_distance = 250
                
                # Create triangle path
                triangle = QPainterPath()
                p1 = QPointF(center_x + math.cos(angle) * marker_distance, 
                            center_y + math.sin(angle) * marker_distance)
                p2 = QPointF(center_x + math.cos(angle + 0.1) * (marker_distance - 10), 
                            center_y + math.sin(angle + 0.1) * (marker_distance - 10))
                p3 = QPointF(center_x + math.cos(angle - 0.1) * (marker_distance - 10), 
                            center_y + math.sin(angle - 0.1) * (marker_distance - 10))
                
                triangle.moveTo(p1)
                triangle.lineTo(p2)
                triangle.lineTo(p3)
                triangle.closeSubpath()
                
                painter.drawPath(triangle)
        
        # Draw pulsing rings during certain animation phases
        if self.animation_phase % 3 == 1:
            pulse_pen = QPen(QColor(0, 255, 255, 50 + int(50 * self.pulse_factor)))
            pulse_pen.setWidth(2)
            painter.setPen(pulse_pen)
            painter.setBrush(Qt.NoBrush)
            
            pulse_radius = 100 + 50 * self.pulse_factor
            painter.drawEllipse(QPointF(center_x, center_y), pulse_radius, pulse_radius)
            
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")
        
        # Colors
        self.blue_color = QColor(0, 150, 255)
        self.pink_color = QColor(255, 0, 255)
        self.cyan_color = QColor(0, 255, 255)
        
        # Circles for visualization
        self.circles = []
        self.max_circles = 5  # Concentric circles
        self.generate_circles()
        
        # Audio wave points
        self.wave_points = []
        self.num_wave_points = 180  # Points around the circle
        self.generate_wave_points()
        
        # Particles for additional effect
        self.particles = []
        self.max_particles = 150
        self.generate_particles()
        
        # Animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_visualization)
        self.animation_timer.start(16)  # ~60fps
        
        # Rotation angle
        self.rotation_angle = 0
        
        # Active state
        self.active = False
        self.pulse_factor = 0
        self.pulse_direction = 1
        
        # Audio player for visualization sync
        self.audio_player = QMediaPlayer()
        self.setup_audio()
        
    def setup_audio(self):
        # This would be replaced with actual audio processing in a real app
        # For now, we'll simulate audio levels
        self.audio_levels = [random.uniform(0.5, 1.0) for _ in range(self.num_wave_points)]
        self.audio_timer = QTimer(self)
        self.audio_timer.timeout.connect(self.update_audio_levels)
        self.audio_timer.start(50)
        
    def update_audio_levels(self):
        # Simulate changing audio levels
        for i in range(self.num_wave_points):
            # Create a wave-like pattern
            base = 0.5 + 0.3 * math.sin(i / 10 + self.rotation_angle / 10)
            variation = random.uniform(-0.1, 0.1)
            self.audio_levels[i] = min(1.0, max(0.2, base + variation))
            
            if self.active:
                # More dramatic changes when active
                if random.random() < 0.05:
                    self.audio_levels[i] = random.uniform(0.7, 1.0)
        
    def generate_circles(self):
        for i in range(self.max_circles):
            self.circles.append({
                'radius': (i + 1) * 40,  # Increasing radius for each circle
                'thickness': 2,
                'rotation_speed': 0.2 * (1 if i % 2 == 0 else -1),  # Alternate rotation direction
                'rotation': random.uniform(0, 2 * math.pi),
                'dash_pattern': [5, 5] if i % 2 == 0 else [10, 5]  # Alternate dash patterns
            })
    
    def generate_wave_points(self):
        for i in range(self.num_wave_points):
            angle = 2 * math.pi * i / self.num_wave_points
            self.wave_points.append({
                'angle': angle,
                'amplitude': random.uniform(0.8, 1.0),
                'phase': random.uniform(0, 2 * math.pi),
                'frequency': random.uniform(1, 3)
            })
            
    def generate_particles(self):
        for _ in range(self.max_particles):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, 0.8)  # Distance from center (0-1)
            self.particles.append({
                'x': 0.5 + math.cos(angle) * distance,
                'y': 0.5 + math.sin(angle) * distance,
                'size': random.uniform(1, 3),
                'speed': random.uniform(0.001, 0.003),
                'angle': angle,
                'distance': distance,
                'color': random.choice([self.blue_color, self.pink_color, self.cyan_color])
            })
        
    def set_active(self, active):
        self.active = active
        
    def update_visualization(self):
        # Update rotation angle
        self.rotation_angle += 0.01
        if self.rotation_angle > 2 * math.pi:
            self.rotation_angle -= 2 * math.pi
            
        # Update pulse effect
        self.pulse_factor += 0.02 * self.pulse_direction
        if self.pulse_factor > 1:
            self.pulse_factor = 1
            self.pulse_direction = -1
        elif self.pulse_factor < 0:
            self.pulse_factor = 0
            self.pulse_direction = 1
            
        # Update circles
        for circle in self.circles:
            circle['rotation'] += circle['rotation_speed'] * (2 if self.active else 1)
            if circle['rotation'] > 2 * math.pi:
                circle['rotation'] -= 2 * math.pi
        
        # Update particles
        for particle in self.particles:
            # Rotate particles around center
            particle['angle'] += particle['speed'] * (3 if self.active else 1)
            if particle['angle'] > 2 * math.pi:
                particle['angle'] -= 2 * math.pi
                
            # Update position based on angle and distance
            particle['x'] = 0.5 + math.cos(particle['angle']) * particle['distance']
            particle['y'] = 0.5 + math.sin(particle['angle']) * particle['distance']
            
            # Randomly change distance for some particles
            if random.random() < 0.01:
                particle['distance'] = random.uniform(0, 0.8)
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw pure black background
        painter.fillRect(self.rect(), QColor("#000000"))
        
        # Get center coordinates
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        # Draw particles
        for particle in self.particles:
            x = particle['x'] * self.width()
            y = particle['y'] * self.height()
            
            # Size based on activity
            size = particle['size'] * (1.5 if self.active else 1)
            
            # Draw particle
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(particle['color']))
            painter.drawEllipse(QPointF(x, y), size, size)
        
        # Draw concentric circles
        for circle in self.circles:
            pen = QPen(QColor(0, 150, 255, 100))
            pen.setWidth(circle['thickness'])
            pen.setDashPattern(circle['dash_pattern'])
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            
            # Draw rotated circle
            painter.save()
            painter.translate(center_x, center_y)
            painter.rotate(math.degrees(circle['rotation']))
            painter.drawEllipse(QPoint(0, 0), circle['radius'], circle['radius'])
            painter.restore()
        
        # Draw audio wave visualization
        if self.audio_levels:
            # Create path for the wave
            blue_path = QPainterPath()
            pink_path = QPainterPath()
            
            # Base radius for the wave
            base_radius = min(center_x, center_y) * 0.6
            
            # Start points
            first_blue_point = None
            first_pink_point = None
            
            # Draw the wave points
            for i in range(self.num_wave_points):
                angle = 2 * math.pi * i / self.num_wave_points + self.rotation_angle
                
                # Calculate amplitude based on audio level
                blue_amplitude = self.audio_levels[i] * 50 * (1.5 if self.active else 1)
                pink_amplitude = self.audio_levels[(i + self.num_wave_points // 2) % self.num_wave_points] * 50 * (1.5 if self.active else 1)
                
                # Calculate point positions
                blue_x = center_x + math.cos(angle) * (base_radius + blue_amplitude)
                blue_y = center_y + math.sin(angle) * (base_radius + blue_amplitude)
                
                pink_x = center_x + math.cos(angle) * (base_radius - pink_amplitude)
                pink_y = center_y + math.sin(angle) * (base_radius - pink_amplitude)
                
                # Add points to paths
                if i == 0:
                    blue_path.moveTo(blue_x, blue_y)
                    pink_path.moveTo(pink_x, pink_y)
                    first_blue_point = QPointF(blue_x, blue_y)
                    first_pink_point = QPointF(pink_x, pink_y)
                else:
                    blue_path.lineTo(blue_x, blue_y)
                    pink_path.lineTo(pink_x, pink_y)
                    
                # Draw small circles at wave points for additional effect
                if i % 10 == 0:  # Only draw some points to avoid clutter
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QBrush(self.blue_color))
                    painter.drawEllipse(QPointF(blue_x, blue_y), 2, 2)
                    
                    painter.setBrush(QBrush(self.pink_color))
                    painter.drawEllipse(QPointF(pink_x, pink_y), 2, 2)
            
            # Close the paths
            if first_blue_point:
                blue_path.lineTo(first_blue_point.x(), first_blue_point.y())
            if first_pink_point:
                pink_path.lineTo(first_pink_point.x(), first_pink_point.y())
            
            # Draw the blue wave with gradient
            blue_gradient = QRadialGradient(center_x, center_y, base_radius + 50)
            blue_gradient.setColorAt(0, QColor(0, 150, 255, 30))
            blue_gradient.setColorAt(1, QColor(0, 150, 255, 80))
            
            painter.setPen(QPen(self.blue_color, 2))
            painter.setBrush(QBrush(blue_gradient))
            painter.drawPath(blue_path)
            
            # Draw the pink wave with gradient
            pink_gradient = QRadialGradient(center_x, center_y, base_radius - 50)
            pink_gradient.setColorAt(0, QColor(255, 0, 255, 30))
            pink_gradient.setColorAt(1, QColor(255, 0, 255, 80))
            
            painter.setPen(QPen(self.pink_color, 2))
            painter.setBrush(QBrush(pink_gradient))
            painter.drawPath(pink_path)
        
        # Draw center circle with tech details
        center_radius = 50 * (1.2 if self.active else 1)
        
        # Draw outer glow
        glow_radius = center_radius + 20
        glow_gradient = QRadialGradient(center_x, center_y, glow_radius * 2)
        glow_gradient.setColorAt(0, QColor(0, 255, 255, 100))
        glow_gradient.setColorAt(0.5, QColor(0, 150, 255, 30))
        glow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow_gradient))
        painter.drawEllipse(QPointF(center_x, center_y), glow_radius, glow_radius)
        
        # Draw center circle
        center_gradient = QRadialGradient(center_x, center_y, center_radius)
        center_gradient.setColorAt(0, QColor(0, 255, 255, 200))
        center_gradient.setColorAt(1, QColor(0, 150, 255, 150))
        
        painter.setBrush(QBrush(center_gradient))
        painter.drawEllipse(QPointF(center_x, center_y), center_radius, center_radius)
        
        # Draw inner circles for tech effect
        for i in range(3):
            inner_radius = center_radius * (0.8 - i * 0.2)
            painter.setPen(QPen(QColor(0, 255, 255, 150), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(center_x, center_y), inner_radius, inner_radius)
        
        # Draw tech lines
        painter.setPen(QPen(QColor(0, 255, 255, 100), 1))
        for i in range(8):
            angle = i * math.pi / 4 + self.rotation_angle
            line_length = self.width() * 0.4
            start_point = QPointF(
                center_x + math.cos(angle) * center_radius,
                center_y + math.sin(angle) * center_radius
            )
            end_point = QPointF(
                center_x + math.cos(angle) * line_length,
                center_y + math.sin(angle) * line_length
            )
            painter.drawLine(start_point, end_point)
        
        # Draw "AUDIO LEVEL" text at bottom
        painter.setPen(QPen(QColor(0, 255, 255, 200), 1))
        painter.setFont(QFont("Consolas", 10))
        painter.drawText(
            QRect(int(center_x - 100), int(center_y + base_radius + 20), 200, 20),
            Qt.AlignCenter,
            "AUDIO LEVEL"
        )
        
        # Draw level indicators
        level_width = 10
        level_gap = 2
        level_count = 10
        total_width = level_count * (level_width + level_gap)
        start_x = center_x - total_width / 2
        
        for i in range(level_count):
            # Determine if this level indicator should be lit
            is_active = i < int(sum(self.audio_levels) / len(self.audio_levels) * level_count)
            
            if is_active:
                painter.setBrush(QBrush(QColor(0, 255, 255, 200)))
            else:
                painter.setBrush(QBrush(QColor(0, 255, 255, 50)))
                
            painter.drawRect(
                int(start_x + i * (level_width + level_gap)),
                int(center_y + base_radius + 40),
                level_width,
                5
            )

# Custom microphone button with 3D white circles
class MicrophoneButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)
        self.toggled = True
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 60px;
            }
        """)
        
        # Add glow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(30)
        self.shadow.setColor(QColor("#FFFFFF"))
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Center coordinates
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        # Draw outer circle - increased sizes
        painter.setPen(QPen(QColor("#FFFFFF"), 3))  # Increased from 2 to 3
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(center_x, center_y), 45, 45)  # Increased from 30 to 45
        
        # Draw inner circle - increased sizes
        if self.toggled:
            # Mic off - draw full inner circle
            painter.setPen(QPen(QColor("#FFFFFF"), 3))  # Increased from 2 to 3
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(center_x, center_y), 22, 22)  # Increased from 15 to 22
        else:
            # Mic on - draw inner circle with two cuts
            painter.setPen(QPen(QColor("#FFFFFF"), 3))  # Increased from 2 to 3
            painter.setBrush(Qt.NoBrush)
            
            # Draw two arcs instead of a full circle - increased sizes
            path = QPainterPath()
            path.arcMoveTo(center_x - 22, center_y - 22, 44, 44, 45)  # Increased from 15 to 22
            path.arcTo(center_x - 22, center_y - 22, 44, 44, 45, 135)
            
            path2 = QPainterPath()
            path2.arcMoveTo(center_x - 22, center_y - 22, 44, 44, 225)
            path2.arcTo(center_x - 22, center_y - 22, 44, 44, 225, 135)
            
            painter.drawPath(path)
            painter.drawPath(path2)
        
        # Draw microphone icon in the center - increased sizes
        if self.toggled:
            # Mic off - draw with a slash
            # Draw mic base
            painter.setPen(QPen(QColor("#FFFFFF"), 3))  # Increased from 2 to 3
            painter.drawRoundedRect(int(center_x - 7), int(center_y - 15), 14, 30, 7, 7)  # Increased proportionally
            
            # Draw slash
            painter.setPen(QPen(QColor("#FFFFFF"), 3))  # Increased from 2 to 3
            painter.drawLine(int(center_x - 22), int(center_y + 22), int(center_x + 22), int(center_y - 22))  # Increased from 15 to 22
        else:
            # Mic on - draw normal mic
            # Draw mic base
            painter.setPen(QPen(QColor("#FFFFFF"), 3))  # Increased from 2 to 3
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.drawRoundedRect(int(center_x - 7), int(center_y - 15), 14, 30, 7, 7)  # Increased proportionally
            
            # Draw mic stand
            painter.setPen(QPen(QColor("#FFFFFF"), 3))  # Increased from 2 to 3
            painter.drawLine(int(center_x), int(center_y + 15), int(center_x), int(center_y + 22))  # Increased proportionally
            painter.drawLine(int(center_x - 12), int(center_y + 22), int(center_x + 12), int(center_y + 22))  # Increased from 8 to 12

# Main screen widget
class MainScreen(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize movie object
        self.movie = QMovie(os.path.join(GraphicsDirPath, "Jarvis.gif"))
        self.movie.setScaledSize(QSize(500, 500))
        self.movie.start()
        self.movie.setSpeed(50)
        self.initUI()
        self.last_status = ""
        self.is_responding = False
        self.toggled = True
        self.current_image = None

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top bar
        top_bar = CustomTopBar(self)
        layout.addWidget(top_bar)

        # Main content area - pure black
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_widget.setStyleSheet("""
            #contentWidget {
                background-color: #000000;
                margin: 10px;
            }
        """)
        
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)

        # Chat section (left side)
        chat_widget = QWidget()
        chat_widget.setObjectName("chatWidget")
        chat_widget.setStyleSheet("""
            #chatWidget {
                background-color: #000000;
                border-radius: 15px;
            }
        """)
        
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(15, 15, 15, 15)

        # Enhanced text display with animations
        self.chat_text_edit = AnimatedTextEdit()
        chat_layout.addWidget(self.chat_text_edit)
        
        # Status label with neon glow
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                color: #4A9EFF;
                font-size: 14px;
                font-family: 'Consolas';
                margin-top: 10px;
                padding: 5px;
                border-radius: 10px;
                background-color: rgba(0, 0, 0, 0);
            }
        """)
        
        # Add glow effect to status label
        status_glow = QGraphicsDropShadowEffect()
        status_glow.setBlurRadius(15)
        status_glow.setColor(QColor("#4A9EFF"))
        status_glow.setOffset(0, 0)
        self.status_label.setGraphicsEffect(status_glow)
        
        chat_layout.addWidget(self.status_label)

        # Visualization section (right side)
        visual_widget = QWidget()
        visual_widget.setObjectName("visualWidget")
        visual_widget.setStyleSheet("""
            #visualWidget {
                background-color: #000000;
                border-radius: 15px;
            }
        """)
        
        visual_layout = QVBoxLayout(visual_widget)
        visual_layout.setContentsMargins(10, 10, 10, 0)
        visual_layout.setSpacing(0)
        
        # Add advanced visualization panel
        self.visualization = AdvancedVisualizationPanel()
        visual_layout.addWidget(self.visualization)

        # Add image display label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        visual_layout.addWidget(self.image_label)

        # Add the microphone button at the bottom with enhanced styling
        mic_container = QWidget()
        mic_container.setStyleSheet("background-color: transparent;")
        mic_layout = QVBoxLayout(mic_container)
        mic_layout.setContentsMargins(0, 0, 0, 20)
        
        # Add status label above mic button
        self.mic_status_label = QLabel("Listening")
        self.mic_status_label.setAlignment(Qt.AlignCenter)
        self.mic_status_label.setStyleSheet("""
            QLabel {
                color: #4A9EFF;
                font-size: 16px;
                font-family: 'Consolas';
                margin-bottom: 10px;
            }
        """)
        
        # Add glow effect to mic status label
        mic_status_glow = QGraphicsDropShadowEffect()
        mic_status_glow.setBlurRadius(15)
        mic_status_glow.setColor(QColor("#4A9EFF"))
        mic_status_glow.setOffset(0, 0)
        self.mic_status_label.setGraphicsEffect(mic_status_glow)
        
        mic_layout.addWidget(self.mic_status_label)
        
        # Use custom microphone button with 3D white circles
        self.mic_button = MicrophoneButton()
        self.toggled = True
        self.mic_button.toggled = self.toggled
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

        # Set background
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
        """)

    def toggleMic(self):
        self.toggled = not self.toggled
        self.mic_button.toggled = self.toggled
        self.mic_button.update()  # Force repaint of the button
        SetMicrophoneStatus("False" if self.toggled else "True")
        
        # Update visualization based on mic state
        if self.toggled:
            self.movie.setSpeed(50)  # Slower when mic is off
            self.visualization.set_active(False)
            self.mic_status_label.setText("")  # Remove text when mic is off
        else:
            self.movie.setSpeed(100)  # Normal speed when mic is on
            self.visualization.set_active(True)
            self.mic_status_label.setText("Listening")
        
        # Add ripple effect to text area when toggling mic
        self.chat_text_edit.add_ripple()

    def loadMessages(self):
        global old_chat_message
        try:
            with open(os.path.join(TempDirPath, 'Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()

            if messages and messages != old_chat_message:
                self.chat_text_edit.set_text(messages)
                old_chat_message = messages
                # Set to responding when new message is detected
                self.is_responding = True
                self.mic_status_label.setText("Responding")
            elif self.is_responding and self.chat_text_edit.typing_timer.isActive() == False:
                # When typing animation is complete, go back to listening/idle
                self.is_responding = False
                if not self.toggled:
                    self.mic_status_label.setText("Listening")
                else:
                    self.mic_status_label.setText("")  # Remove text when mic is off

            # Check for generated image
            image_path = os.path.join(TempDirPath, "generated_image.png")
            if os.path.exists(image_path):
                try:
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        # Scale the image to fit the visualization panel while maintaining aspect ratio
                        scaled_pixmap = pixmap.scaled(
                            self.visualization.width(),
                            self.visualization.height(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.image_label.setPixmap(scaled_pixmap)
                        self.current_image = scaled_pixmap
                    else:
                        print("Failed to load image")
                except Exception as e:
                    print(f"Error loading image: {e}")
                    
        except Exception as e:
            print(f"Error loading messages: {e}")

    def updateStatus(self):
        try:
            with open(os.path.join(TempDirPath, 'Status.data'), "r", encoding='utf-8') as file:
                status = file.read()
            
            # Only update if status has changed
            if status != self.last_status:
                self.status_label.setText(status)
                self.last_status = status
                
                # Update mic status based on assistant status
                if "processing" in status.lower() or "thinking" in status.lower():
                    self.mic_status_label.setText("Responding")
                    self.is_responding = True
                elif self.toggled:
                    self.mic_status_label.setText("")  # Remove text when mic is off
                
                # Handle image generation status
                if "generating image" in status.lower():
                    self.image_label.clear()  # Clear previous image
                    self.visualization.set_active(True)  # Activate visualization
                elif "image generation completed" in status.lower():
                    self.visualization.set_active(False)  # Deactivate visualization
                
        except Exception as e:
            print(f"Error updating status: {e}")

# Enhanced top bar with pure black background
class CustomTopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.parent = parent

    def initUI(self):
        self.setFixedHeight(60)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)

        # Title with spaced letters and enhanced styling
        title_text = "J A R V I S"
        title_label = QLabel(title_text)
        title_label.setStyleSheet("""
            QLabel {
                color: #4A9EFF;
                font-size: 22px;
                font-weight: bold;
                letter-spacing: 3px;
                font-family: 'Consolas';
            }
        """)

        layout.addWidget(title_label)
        layout.addStretch()

        # Window controls with enhanced styling
        for button_data in [
            ("minimize", self.minimizeWindow),
            ("maximize", self.maximizeWindow),
            ("close", self.closeWindow)
        ]:
            btn = NeonButton(glow_color=QColor("#4A9EFF"), glow_radius=10)
            btn.setFixedSize(45, 45)
            btn.setIcon(QIcon(os.path.join(GraphicsDirPath, f"{button_data[0]}.png")))
            btn.setIconSize(QSize(22, 22))
            btn.clicked.connect(button_data[1])
            layout.addWidget(btn)

        self.setStyleSheet("""
            background-color: #000000;
        """)

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

# Main window with pure black styling
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.initUI()

    def initUI(self):
        self.central_widget = MainScreen()
        self.setCentralWidget(self.central_widget)
        
        # Set initial window size to 85% of screen size
        screen = QApplication.primaryScreen().size()
        self.resize(int(screen.width() * 0.85), int(screen.height() * 0.85))
        
        # Center the window
        self.center()

    def center(self):
        frame = self.frameGeometry()
        center = QApplication.primaryScreen().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create rounded rectangle for window
        path = QPainterPath()
        path.addRoundedRect(QRectF(0.0, 0.0, float(self.width()), float(self.height())), 20.0, 20.0)
        
        # Draw shadow
        painter.setPen(Qt.NoPen)
        for i in range(10):
            opacity = 10 - i
            painter.setBrush(QColor(0, 0, 20, opacity))
            rect = QRectF(float(10-i), float(10-i), float(self.width()+(i*2)), float(self.height()+(i*2)))
            painter.drawRoundedRect(rect, 20.0, 20.0)
        
        # Draw window background - pure black with no border
        painter.setBrush(QColor("#000000"))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Consolas")
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()