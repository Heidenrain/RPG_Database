import sqlite3
import re
from database import DatabaseManager


class LeituraBackend:
    """
    Backend responsável exclusivamente por consultas, filtros dinâmicos e
    interpretação inteligente de comandos na aba de Consulta/Grid.
    """
    def __init__(self):
        self.db = DatabaseManager()

    def obter_sugestoes_nomes(self, tabela: str) -> list[str]:
        """Busca os nomes existentes em uma tabela para alimentar o autocomplete dinâmico."""
        # Tabelas relacionais (monster_drops e npc_shops) usam IDs, não possuem a coluna 'name'
        if tabela in ["monster_drops", "npc_shops"]:
            return []

        sql = f"SELECT DISTINCT name FROM {tabela} WHERE name IS NOT NULL"
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]
        except Exception:
            return []

    def buscar_por_filtros(
        self, 
        tabela: str, 
        nome: str = "", 
        ordenar_por: str = "id", 
        direcao: str = "ASC", 
        filtro_extra: str = ""
    ) -> tuple[list[tuple], list[str]]:
        """Aplica busca com wildcards (*), ordenação e cláusulas extra seguras."""
        where_conditions = []
        params = []

        if nome:
            # Transforma '*' digitado pelo usuário no coringa SQL '%'
            nome_pattern = nome.replace("*", "%")
            if "%" not in nome_pattern:
                nome_pattern = f"%{nome_pattern}%"
            
            # Se a tabela tiver a coluna 'name', faz a busca por ela
            if tabela not in ["monster_drops", "npc_shops"]:
                where_conditions.append("name LIKE ?")
                params.append(nome_pattern)

        if filtro_extra.strip():
            where_conditions.append(filtro_extra.strip())

        where_clause = f" WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
        sql = f"SELECT * FROM {tabela}{where_clause} ORDER BY {ordenar_por} {direcao}"

        return self.executar_raw_sql(sql, tuple(params))

    def parse_e_executar_consulta_livre(self, comando: str) -> tuple[list[tuple], list[str]]:
        """
        Interpreta entradas de texto livre ou SQL puro.
        Exemplos suportados:
        - "items price between 100 and 120" -> traduz para "SELECT * FROM items WHERE price between 100 and 120"
        - "monsters hp > 500" -> traduz para "SELECT * FROM monsters WHERE hp > 500"
        - "SELECT * FROM items JOIN monster_drops ON items.id = monster_drops.item_id"
        """
        cmd = comando.strip()
        if not cmd:
            return [], []

        # 1. Se já for uma query SQL iniciada com SELECT ou WITH
        if re.match(r"^(SELECT|WITH)\b", cmd, re.IGNORECASE):
            return self.executar_raw_sql(cmd)

        # 2. Expressão Regular para pegar: <tabela> <condição/cláusula>
        match = re.match(r"^(\w+)\s+(.*)$", cmd, re.IGNORECASE | re.DOTALL)
        if match:
            tabela = match.group(1)
            resto = match.group(2).strip()

            # Se não começar explicitamente com WHERE ou JOIN, adiciona WHERE
            if not resto.upper().startswith("WHERE") and not resto.upper().startswith("JOIN"):
                resto = f"WHERE {resto}"

            sql = f"SELECT * FROM {tabela} {resto}"
            return self.executar_raw_sql(sql)

        # 3. Fallback: Se digitou apenas o nome de uma tabela (ex: "items")
        return self.executar_raw_sql(f"SELECT * FROM {cmd}")

    def executar_raw_sql(self, sql: str, params: tuple = ()) -> tuple[list[tuple], list[str]]:
        """Executa a query SQLite final e extrai colunas + dados."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                colunas = [desc[0] for desc in cursor.description] if cursor.description else []
                resultados = cursor.fetchall()
                return resultados, colunas
        except sqlite3.Error as e:
            raise RuntimeError(f"Erro na Consulta SQL: {e}")