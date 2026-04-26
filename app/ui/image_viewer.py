from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class _ImageCanvas(QLabel):
    def __init__(self, viewer: "ImageViewerWidget") -> None:
        super().__init__()
        self._viewer = viewer

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._viewer.handle_canvas_mouse_press(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._viewer.handle_canvas_mouse_move(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._viewer.handle_canvas_mouse_release(event)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        self._viewer.paint_annotation(self)


class ImageViewerWidget(QWidget):
    """
    Minimal image display pane for V2-lite.
    Shows a generated placeholder until a local PNG/JPG path is loaded.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._source_pixmap: Optional[QPixmap] = None
        self._placeholder_pixmap = self._build_placeholder_pixmap()
        self._has_loaded_image = False
        self._is_drawing = False
        self._drag_start: Optional[QPoint] = None
        self._annotation_rect: Optional[QRect] = None
        self._annotation_source_rect: Optional[tuple[float, float, float, float]] = None

        self._build_ui()
        self.clear()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.header_label = QLabel("Image Viewer")
        self.header_label.setObjectName("sectionHeader")
        layout.addWidget(self.header_label)

        self.image_label = _ImageCanvas(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(320, 320)
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.image_label.setStyleSheet(
            """
            QLabel {
                background-color: #11151d;
                border: 1px solid #3a3f4b;
                border-radius: 6px;
                color: #aeb7c3;
            }
            """
        )
        layout.addWidget(self.image_label, stretch=1)

    def clear(self) -> None:
        self._source_pixmap = self._placeholder_pixmap
        self._has_loaded_image = False
        self._is_drawing = False
        self._drag_start = None
        self._annotation_rect = None
        self._annotation_source_rect = None
        self._refresh_pixmap()

    def load_image(self, image_path: Optional[str]) -> bool:
        if not image_path:
            self.clear()
            return False

        path = self._resolve_image_path(image_path)
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            self.clear()
            return False

        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            self.clear()
            return False

        self._source_pixmap = pixmap
        self._has_loaded_image = True
        self._is_drawing = False
        self._drag_start = None
        self._annotation_rect = None
        self._annotation_source_rect = None
        self._refresh_pixmap()
        return True

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh_pixmap()

    def _refresh_pixmap(self) -> None:
        if self._source_pixmap is None or self.image_label.width() <= 0:
            return

        scaled = self._source_pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)
        self._sync_canvas_rect_from_source_rect()
        self.image_label.update()

    def get_annotation_rect(self) -> Optional[tuple[float, float, float, float]]:
        return self._annotation_source_rect

    def set_annotation_rect(
        self,
        rect: Optional[tuple[float, float, float, float]],
    ) -> None:
        self._annotation_source_rect = rect
        if rect is None:
            self._annotation_rect = None
        self._sync_canvas_rect_from_source_rect()
        self.image_label.update()

    def handle_canvas_mouse_press(self, event: QMouseEvent) -> None:
        if not self._has_loaded_image or event.button() != Qt.MouseButton.LeftButton:
            return

        self._is_drawing = True
        self._drag_start = self._clamped_canvas_point(event.position().toPoint())
        self._annotation_rect = QRect(self._drag_start, self._drag_start)
        self._annotation_source_rect = None
        self.image_label.update()

    def handle_canvas_mouse_move(self, event: QMouseEvent) -> None:
        if not self._is_drawing or self._drag_start is None:
            return

        current_point = self._clamped_canvas_point(event.position().toPoint())
        self._annotation_rect = QRect(self._drag_start, current_point).normalized()
        self.image_label.update()

    def handle_canvas_mouse_release(self, event: QMouseEvent) -> None:
        if not self._is_drawing or self._drag_start is None:
            return

        current_point = self._clamped_canvas_point(event.position().toPoint())
        self._annotation_rect = QRect(self._drag_start, current_point).normalized()
        self._is_drawing = False
        self._drag_start = None
        self._annotation_source_rect = self._canvas_rect_to_source_rect(
            self._annotation_rect
        )
        self.image_label.update()

    def paint_annotation(self, canvas: QLabel) -> None:
        if not self._has_loaded_image or self._annotation_rect is None:
            return

        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#ffcc66"), 2)
        painter.setPen(pen)
        painter.drawRect(self._annotation_rect)
        painter.end()

    def _clamped_canvas_point(self, point: QPoint) -> QPoint:
        image_rect = self._displayed_image_rect()
        if image_rect.isNull():
            return point

        return QPoint(
            max(image_rect.left(), min(point.x(), image_rect.right())),
            max(image_rect.top(), min(point.y(), image_rect.bottom())),
        )

    def _displayed_image_rect(self) -> QRect:
        pixmap = self.image_label.pixmap()
        if pixmap is None or pixmap.isNull():
            return QRect()

        x = (self.image_label.width() - pixmap.width()) // 2
        y = (self.image_label.height() - pixmap.height()) // 2
        return QRect(x, y, pixmap.width(), pixmap.height())

    def _canvas_rect_to_source_rect(
        self,
        rect: QRect,
    ) -> Optional[tuple[float, float, float, float]]:
        image_rect = self._displayed_image_rect()
        if (
            self._source_pixmap is None
            or image_rect.isNull()
            or rect.width() <= 0
            or rect.height() <= 0
        ):
            return None

        x_scale = self._source_pixmap.width() / image_rect.width()
        y_scale = self._source_pixmap.height() / image_rect.height()

        return (
            (rect.x() - image_rect.x()) * x_scale,
            (rect.y() - image_rect.y()) * y_scale,
            rect.width() * x_scale,
            rect.height() * y_scale,
        )

    def _sync_canvas_rect_from_source_rect(self) -> None:
        if self._annotation_source_rect is None:
            return

        image_rect = self._displayed_image_rect()
        if self._source_pixmap is None or image_rect.isNull():
            return

        x, y, width, height = self._annotation_source_rect
        x_scale = image_rect.width() / self._source_pixmap.width()
        y_scale = image_rect.height() / self._source_pixmap.height()

        self._annotation_rect = QRect(
            int(image_rect.x() + x * x_scale),
            int(image_rect.y() + y * y_scale),
            int(width * x_scale),
            int(height * y_scale),
        )

    def _build_placeholder_pixmap(self) -> QPixmap:
        pixmap = QPixmap(800, 800)
        pixmap.fill(QColor("#11151d"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(QColor("#3a3f4b"))
        painter.drawRect(60, 60, 680, 680)
        painter.drawLine(60, 400, 740, 400)
        painter.drawLine(400, 60, 400, 740)

        painter.setPen(QColor("#aeb7c3"))
        painter.drawText(
            pixmap.rect(),
            Qt.AlignmentFlag.AlignCenter,
            "No image loaded",
        )
        painter.end()

        return pixmap

    def _resolve_image_path(self, image_path: str) -> Path:
        normalized_path = image_path.strip()

        if normalized_path.startswith("\\\\wsl$\\"):
            path_parts = normalized_path.split("\\")
            if len(path_parts) > 3:
                return Path("/") / Path(*path_parts[3:])

        path = Path(normalized_path)
        if path.exists() or path.is_absolute():
            return path

        project_root = Path(__file__).resolve().parents[2]
        return project_root / path
