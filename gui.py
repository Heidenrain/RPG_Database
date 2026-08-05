import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QTextEdit, QCheckBox,
    QPushButton, QTabWidget, QScrollArea, QFrame,
    QFormLayout, QMessageBox, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QCompleter
)
from PyQt6.QtCore import Qt
from backend_cadastro import CadastroBackend
from backend_leitura import LeituraBackend


class JSONPreviewDialog(QFrame):
    """
    Popup flutuante para exibir o JSON completo com scroll e botão de fechar (❌).
    """
    def __init__(self, text, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 2px solid #1976D2;
                border-radius: 6px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #f44336;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        header_layout = QHBoxLayout()
        lbl_title = QLabel("<b>📦 Conteúdo Completo (JSON / Texto)</b>")
        lbl_title.setStyleSheet("border: none; font-size: 11px;")
        
        btn_close = QPushButton("❌")
        btn_close.setFixedSize(22, 22)
        btn_close.clicked.connect(self.close)

        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        layout.addLayout(header_layout)

        self.txt_display = QTextEdit()
        self.txt_display.setReadOnly(True)
        self.txt_display.setPlainText(text)
        self.txt_display.setStyleSheet("border: 1px solid #444; background-color: #1e1e1e; font-family: monospace;")
        layout.addWidget(self.txt_display)


class CadastroWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backend = CadastroBackend()
        self.categories = [
            "items", "monsters", "characters",
            "spells", "maps", "npcs", "monster_drops", "npc_shops"
        ]
        self.inputs = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        top_frame = QFrame()
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(0, 0, 0, 0)

        lbl_select = QLabel("<b>O que deseja cadastrar?</b>")
        lbl_select.setStyleSheet("font-size: 14px;")

        self.combo_tables = QComboBox()
        self.combo_tables.setStyleSheet("font-size: 14px; padding: 5px;")
        self.combo_tables.addItems(self.categories)
        self.combo_tables.currentTextChanged.connect(self.on_category_changed)

        top_layout.addWidget(lbl_select)
        top_layout.addWidget(self.combo_tables, stretch=1)
        layout.addWidget(top_frame)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.StyledPanel)

        self.form_container = QWidget()
        self.form_layout = QFormLayout(self.form_container)
        self.form_layout.setSpacing(12)
        self.scroll_area.setWidget(self.form_container)

        layout.addWidget(self.scroll_area, stretch=1)

        bottom_layout = QHBoxLayout()

        self.btn_clear = QPushButton("🧹 Limpar Campos")
        self.btn_clear.setMinimumHeight(40)
        self.btn_clear.clicked.connect(self.clear_form)

        self.btn_save = QPushButton("💾 Salvar Registro")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        self.btn_save.clicked.connect(self.save_data)

        bottom_layout.addWidget(self.btn_clear)
        bottom_layout.addWidget(self.btn_save)
        layout.addLayout(bottom_layout)

        self.on_category_changed(self.combo_tables.currentText())

    def build_items_form(self):
        txt_name = QLineEdit()
        txt_name.setPlaceholderText("Ex: Espada de Aço, Poção de Vida")
        self.form_layout.addRow("Nome do Item:", txt_name)
        self.inputs["name"] = txt_name

        txt_type = QLineEdit()
        txt_type.setPlaceholderText("Ex: Arma, Consumível, Equipamento")
        self.form_layout.addRow("Tipo:", txt_type)
        self.inputs["type"] = txt_type

        txt_weight = QLineEdit("0.0")
        self.form_layout.addRow("Peso (Kg):", txt_weight)
        self.inputs["weight"] = txt_weight

        txt_price = QLineEdit("0")
        self.form_layout.addRow("Preço Base:", txt_price)
        self.inputs["price"] = txt_price

        chk_stackable = QCheckBox("Sim (Permite juntar no mesmo slot)")
        self.form_layout.addRow("Acumulável:", chk_stackable)
        self.inputs["stackable"] = chk_stackable

        txt_max_stack = QLineEdit("1")
        self.form_layout.addRow("Stack Máximo:", txt_max_stack)
        self.inputs["max_stack"] = txt_max_stack

        txt_properties = QTextEdit()
        txt_properties.setPlaceholderText(
            "Digite em formato Chave: Valor\nExemplo:\n"
            "Ataque: 10\n"
            "Raridade: Raro\n"
            "Descrição: Espada de aço forjada por elfos"
        )
        txt_properties.setMaximumHeight(120)
        self.form_layout.addRow("Propriedades (JSON):", txt_properties)
        self.inputs["properties"] = txt_properties

    def on_category_changed(self, category_name):
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.inputs.clear()

        if category_name == "items":
            self.build_items_form()
        else:
            placeholder = QLabel(f"<i>[Aguardando implementação dos campos para '{category_name}']</i>")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.form_layout.addRow(placeholder)

    def clear_form(self):
        self.on_category_changed(self.combo_tables.currentText())

    def save_data(self):
        category = self.combo_tables.currentText()

        if category != "items":
            QMessageBox.warning(self, "Aviso", f"O cadastro da categoria '{category}' será implementado nos próximos passos.")
            return

        raw_data = {}
        for field_name, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                raw_data[field_name] = widget.text()
            elif isinstance(widget, QTextEdit):
                raw_data[field_name] = widget.toPlainText()
            elif isinstance(widget, QCheckBox):
                raw_data[field_name] = widget.isChecked()

        success, message = self.backend.cadastrar_item(raw_data)

        if success:
            QMessageBox.information(self, "Sucesso", message)
            self.clear_form()
        else:
            QMessageBox.warning(self, "Atenção", message)


class ConsultaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backend = LeituraBackend()
        self.active_popup = None
        self.categories = [
            "items", "monsters", "characters",
            "spells", "maps", "npcs", "monster_drops", "npc_shops"
        ]
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        group_filtros = QGroupBox("🔍 Filtros & Busca em Tempo Real")
        grid_filtros_layout = QVBoxLayout(group_filtros)

        line1 = QHBoxLayout()
        line1.addWidget(QLabel("Tabela:"))
        self.combo_tabela = QComboBox()
        self.combo_tabela.addItems(self.categories)
        self.combo_tabela.currentTextChanged.connect(self.on_tabela_changed)
        line1.addWidget(self.combo_tabela)

        line1.addWidget(QLabel("Nome / Termo (* para coringa):"))
        self.txt_busca_nome = QLineEdit()
        self.txt_busca_nome.setPlaceholderText("Ex: *Espada* ou *C*...")
        self.txt_busca_nome.textChanged.connect(self.executar_busca_filtros)
        line1.addWidget(self.txt_busca_nome, stretch=1)

        grid_filtros_layout.addLayout(line1)

        line2 = QHBoxLayout()
        line2.addWidget(QLabel("Ordenar Por:"))
        self.combo_ordenacao = QComboBox()
        self.combo_ordenacao.addItems(["id", "name", "type", "price"])
        self.combo_ordenacao.currentTextChanged.connect(self.executar_busca_filtros)
        line2.addWidget(self.combo_ordenacao)

        self.combo_direcao = QComboBox()
        self.combo_direcao.addItems(["ASC", "DESC"])
        self.combo_direcao.currentTextChanged.connect(self.executar_busca_filtros)
        line2.addWidget(self.combo_direcao)

        line2.addWidget(QLabel("Filtro Extra:"))
        self.txt_filtro_extra = QLineEdit()
        self.txt_filtro_extra.setPlaceholderText("Ex: price > 50")
        self.txt_filtro_extra.textChanged.connect(self.executar_busca_filtros)
        line2.addWidget(self.txt_filtro_extra, stretch=1)

        grid_filtros_layout.addLayout(line2)
        layout.addWidget(group_filtros)

        group_sql = QGroupBox("⚡ Consulta Livre / Interpretação de SQL")
        sql_layout = QHBoxLayout(group_sql)

        self.txt_prompt_sql = QLineEdit()
        self.txt_prompt_sql.setPlaceholderText("Ex: item price between 100 and 120  OU  SELECT * FROM items JOIN monster_drops...")
        self.txt_prompt_sql.returnPressed.connect(self.executar_busca_livre)
        sql_layout.addWidget(self.txt_prompt_sql, stretch=1)

        self.btn_exec_sql = QPushButton("🚀 Interpretar & Buscar")
        self.btn_exec_sql.setStyleSheet("background-color: #1976D2; color: white; font-weight: bold;")
        self.btn_exec_sql.clicked.connect(self.executar_busca_livre)
        sql_layout.addWidget(self.btn_exec_sql)

        layout.addWidget(group_sql)

        self.table_grid = QTableWidget()
        self.table_grid.setAlternatingRowColors(True)
        self.table_grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.table_grid.cellClicked.connect(self.on_cell_clicked)
        self.table_grid.currentCellChanged.connect(self.fechar_popup_ativo)

        layout.addWidget(self.table_grid, stretch=1)

        self.configurar_autocomplete()
        self.executar_busca_filtros()

    def fechar_popup_ativo(self):
        if self.active_popup:
            self.active_popup.close()
            self.active_popup = None

    def configurar_autocomplete(self):
        tabela = self.combo_tabela.currentText()
        sugestoes = self.backend.obter_sugestoes_nomes(tabela)

        completer = QCompleter(sugestoes, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.txt_busca_nome.setCompleter(completer)

    def on_tabela_changed(self):
        self.fechar_popup_ativo()
        tabela = self.combo_tabela.currentText()
        
        self.combo_ordenacao.blockSignals(True)
        self.combo_ordenacao.clear()
        if tabela == "items":
            self.combo_ordenacao.addItems(["id", "name", "type", "price", "weight"])
        elif tabela == "monsters":
            self.combo_ordenacao.addItems(["id", "name", "type", "exp", "def"])
        elif tabela == "spells":
            self.combo_ordenacao.addItems(["id", "name", "type", "mana"])
        else:
            self.combo_ordenacao.addItems(["id", "name", "type"])
        self.combo_ordenacao.blockSignals(False)

        self.configurar_autocomplete()
        self.executar_busca_filtros()

    def preencher_grid(self, registros: list[tuple], colunas: list[str]):
        self.fechar_popup_ativo()
        self.table_grid.clear()
        self.table_grid.setRowCount(len(registros))
        self.table_grid.setColumnCount(len(colunas))
        self.table_grid.setHorizontalHeaderLabels(colunas)

        for row_idx, row_data in enumerate(registros):
            for col_idx, value in enumerate(row_data):
                val_str = str(value) if value is not None else ""
                item = QTableWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, val_str)

                if len(val_str) > 25 or val_str.startswith("{") or val_str.startswith("["):
                    preview = val_str.replace("\n", " ")
                    if len(preview) > 22:
                        preview = preview[:22] + "..."
                    item.setText(f"🔍 {preview}")
                    item.setToolTip("Clique para expandir o conteúdo completo")
                else:
                    item.setText(val_str)

                self.table_grid.setItem(row_idx, col_idx, item)

    def on_cell_clicked(self, row: int, col: int):
        self.fechar_popup_ativo()

        item = self.table_grid.item(row, col)
        if not item:
            return

        full_text = item.data(Qt.ItemDataRole.UserRole)
        
        if len(full_text) > 25 or full_text.startswith("{") or full_text.startswith("["):
            popup = JSONPreviewDialog(full_text, self)
            cell_rect = self.table_grid.visualItemRect(item)
            global_pos = self.table_grid.viewport().mapToGlobal(cell_rect.bottomLeft())
            popup.setGeometry(global_pos.x(), global_pos.y(), 320, 180)
            popup.show()
            self.active_popup = popup

    def executar_busca_filtros(self):
        tabela = self.combo_tabela.currentText()
        nome = self.txt_busca_nome.text()
        ordenar = self.combo_ordenacao.currentText() or "id"
        direcao = self.combo_direcao.currentText()
        filtro_extra = self.txt_filtro_extra.text()

        try:
            dados, colunas = self.backend.buscar_por_filtros(tabela, nome, ordenar, direcao, filtro_extra)
            self.preencher_grid(dados, colunas)
        except Exception:
            pass

    def executar_busca_livre(self):
        prompt = self.txt_prompt_sql.text()
        if not prompt.strip():
            return

        try:
            dados, colunas = self.backend.parse_e_executar_consulta_livre(prompt)
            self.preencher_grid(dados, colunas)
        except Exception as e:
            QMessageBox.warning(self, "Erro na Interpretação SQL", f"Não foi possível processar a consulta:\n{str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RPG Engine Editor - Core Dashboard")
        self.setMinimumSize(850, 650)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)

        self.tabs = QTabWidget()

        self.tab_cadastro = CadastroWidget()
        self.tab_consulta = ConsultaWidget()

        self.tabs.addTab(self.tab_cadastro, "📝 Cadastro Dinâmico")
        self.tabs.addTab(self.tab_consulta, "🔍 Consulta & Data Grid")

        main_layout.addWidget(self.tabs)