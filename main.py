from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.database import initialize_database
from app.seed_data import seed_demo_data_if_needed
from app.ui.main_window import MainWindow


def main() -> int:
    initialize_database()
    seed_demo_data_if_needed()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())