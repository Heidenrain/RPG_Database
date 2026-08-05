import sqlite3

class DatabaseManager:
    def __init__(self, db_name="game_database.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        """Abre a conexão com suporte a Foreign Keys ativado."""
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON;")  # Garante a integridade relacional
        return conn

    def init_db(self):
        """Cria toda a estrutura inicial do jogo."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Personagens do Jogador
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    class TEXT NOT NULL,
                    attributes TEXT DEFAULT '{}',  -- JSON
                    inventory TEXT DEFAULT '[]',   -- JSON
                    spells TEXT DEFAULT '[]'       -- JSON
                )
            """)

            # 2. Itens
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    weight REAL DEFAULT 0.0,
                    price INTEGER DEFAULT 0,
                    stackable INTEGER DEFAULT 0,  -- Boolean (0 ou 1)
                    max_stack INTEGER DEFAULT 1,
                    properties TEXT DEFAULT '{}'  -- JSON
                )
            """)

            # 3. Monstros
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monsters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    element TEXT,
                    abilities TEXT DEFAULT '[]',  -- JSON
                    def INTEGER DEFAULT 0,
                    mdef INTEGER DEFAULT 0,
                    exp INTEGER DEFAULT 0
                )
            """)

            # 4. Tabela Intermediária: Drops de Monstros (Muitos-para-Muitos)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monster_drops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    monster_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    drop_chance REAL NOT NULL, -- Ex: 0.05 para 5%
                    min_quantity INTEGER DEFAULT 1,
                    max_quantity INTEGER DEFAULT 1,
                    FOREIGN KEY (monster_id) REFERENCES monsters (id) ON DELETE CASCADE,
                    FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
                )
            """)

            # 5. Mapas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    properties TEXT DEFAULT '{}'  -- JSON
                )
            """)

            # 6. NPCs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS npcs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL
                )
            """)

            # 7. Tabela Intermediária: Lojas de NPCs (Muitos-para-Muitos)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS npc_shops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    npc_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    price_override INTEGER, -- Caso o NPC venda mais caro/barato que o preço base
                    FOREIGN KEY (npc_id) REFERENCES npcs (id) ON DELETE CASCADE,
                    FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
                )
            """)

            # 8. Magias / Spells
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spells (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    mana INTEGER NOT NULL,
                    class TEXT,
                    properties TEXT DEFAULT '{}'  -- JSON
                )
            """)

            conn.commit()

    def list_tables(self):
        """Retorna uma lista com o nome das tabelas principais (ignorando internas do sqlite)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            return [row[0] for row in cursor.fetchall()]

    def get_table_schema(self, table_name):
        """Lê os metadados de qualquer tabela selecionada."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info('{table_name}');")
            columns = cursor.fetchall()

            schema = []
            for col in columns:
                schema.append({
                    "cid": col[0],
                    "name": col[1],
                    "type": col[2],
                    "notnull": bool(col[3]),
                    "default_value": col[4],
                    "primary_key": bool(col[5])
                })
            return schema