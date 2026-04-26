import sys

from PySide6.QtWidgets import QApplication

from app.database import initialize_database
from app.seed_data import seed_demo_data_if_empty
from app.ui.main_window import MainWindow


def main() -> None:
    initialize_database()
    seed_demo_data_if_empty()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()