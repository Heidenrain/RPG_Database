import sys
from PyQt6.QtWidgets import QApplication
from database import DatabaseManager
from gui import MainWindow

def main():
    # Garantimos que a estrutura e tabelas do banco existam
    db = DatabaseManager()

    # Inicializamos a aplicação PyQt6
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Instanciamos e exibimos a interface gráfica principal
    window = MainWindow()
    window.show()

    # Inicia o loop da aplicação
    sys.exit(app.exec())

if __name__ == "__main__":
    main()