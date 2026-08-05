import json
from database import DatabaseManager

class CadastroBackend:
    def __init__(self):
        self.db = DatabaseManager()

    def parse_properties_to_json(self, text_input: str) -> str:
        """Converte o formato 'Chave: Valor' ou JSON direto para uma string JSON válida."""
        if not text_input or not text_input.strip():
            return "{}"

        text = text_input.strip()

        # Se já for um JSON válido
        try:
            parsed_json = json.loads(text)
            return json.dumps(parsed_json, ensure_ascii=False)
        except json.JSONDecodeError:
            pass

        # Interpretação do formato 'Chave: Valor'
        properties_dict = {}
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line or ":" not in line:
                continue

            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()

            if val.isdigit():
                val = int(val)
            else:
                try:
                    val = float(val)
                except ValueError:
                    if val.lower() == "true":
                        val = True
                    elif val.lower() == "false":
                        val = False

            properties_dict[key] = val

        return json.dumps(properties_dict, ensure_ascii=False)

    def cadastrar_item(self, form_data: dict) -> tuple[bool, str]:
        """Insere o item na tabela 'items' do banco de dados."""
        nome = form_data.get("name", "").strip()
        tipo = form_data.get("type", "").strip()

        if not nome:
            return False, "O campo 'Nome' é obrigatório!"
        if not tipo:
            return False, "O campo 'Tipo' é obrigatório!"

        try:
            weight = float(form_data.get("weight", 0.0) or 0.0)
            price = int(form_data.get("price", 0) or 0)
            stackable = 1 if form_data.get("stackable") else 0
            max_stack = int(form_data.get("max_stack", 1) or 1)
        except ValueError:
            return False, "Verifique se os campos Peso, Preço e Stack contêm números válidos."

        raw_properties = form_data.get("properties", "")
        properties_json = self.parse_properties_to_json(raw_properties)

        sql = """
            INSERT INTO items (name, type, weight, price, stackable, max_stack, properties)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        values = (nome, tipo, weight, price, stackable, max_stack, properties_json)

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, values)
                conn.commit()
            return True, f"Item '{nome}' cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro ao inserir no banco de dados:\n{str(e)}"