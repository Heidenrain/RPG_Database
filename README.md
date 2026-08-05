# ⚔️ RPG Engine Editor (v0.1)

Um gerenciador e editor de dados para jogos de RPG desenvolvido em **Python 3** e **PyQt6**, integrado a um banco relacional **SQLite3**. O projeto foi construído para facilitar a criação, consulta e manutenção de itens, monstros, NPCs, magias e tabelas de drop de um jogo de RPG de forma flexível.

---

## 🚀 Funcionalidades Principais

### 📝 Aba de Cadastro Dinâmico
- **Formulário de Itens:** Interface intuitiva para cadastro de nome, tipo, peso, preço base, regras de agrupamento (stackable) e limites por slot.
- **Parser de Propriedades/JSON:** Aceita entrada tanto em JSON bruto quanto no formato intuitivo `Chave: Valor` (ex: `Ataque: 15`), convertendo automaticamente os tipos (inteiros, floats, booleanos e strings) para um payload JSON válido no banco.

### 🔍 Aba de Consulta & Data Grid
- **Busca em Tempo Real com Wildcards:** Suporte a buscas parciais com caractere coringa `*` em tempo real (ex: `*Espada*`).
- **Autocomplete Inteligente:** Sugestão dinâmica baseada nos registros existentes da tabela selecionada via `QCompleter`.
- **Filtros Flexíveis & Ordenação:** Seleção rápida de coluna de ordenação (`ASC`/`DESC`) e cláusulas condicionais adicionais (ex: `price > 50`).
- **Interpreter de SQL Livre:** Campo de prompt inteligente que aceita:
  - Nomes de tabelas simples (ex: `items`).
  - Condições curtas sem necessidade de sintaxe pesada (ex: `items price between 100 and 120` vira `SELECT * FROM items WHERE price between 100 and 120`).
  - Queries SQL complexas completas com `JOIN`, `WHERE`, `GROUP BY`, etc.
- **Visualizador Flutuante de JSON (Pop-up Preview):** Campos com dados muito longos ou estruturas JSON são resumidos no grid principal. Um clique na célula abre uma janela pop-up flutuante com barra de rolagem e botão de fechar para inspecionar todo o conteúdo.

---

## 🗄️ Estrutura do Banco de Dados (Schema SQLite)

O sistema conta com integridade referencial ativa (`PRAGMA foreign_keys = ON`) e gerencia as seguintes tabelas:

1. **`items`**: Registro de armas, equipamentos, consumíveis e itens genéricos.
2. **`monsters`**: Monstros, atributos base de defesa, experiência e lista de habilidades (JSON).
3. **`characters`**: Fichas de personagens, atributos, inventário e magias conhecidas.
4. **`spells`**: Magias, tipo, custo de mana e propriedades específicas.
5. **`maps`**: Locais e ambientes do jogo.
6. **`npcs`**: Personagens não-jogáveis do mundo.
7. **`monster_drops`**: Tabela relacional (Muitos-para-Muitos) vinculando monstros a itens com taxas de drop (`drop_chance`) e quantidades.
8. **`npc_shops`**: Tabela relacional vinculando lojas de NPCs a itens com suporte a alteração de preços (`price_override`).

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Interface Gráfica:** PyQt6 (Estilo Fusion)
- **Banco de Dados:** SQLite3

---

## 📁 Arquitetura do Projeto

```text
sistema_rpg/
│
├── main.py                # Ponto de entrada da aplicação e loop do PyQt6
├── database.py            # Conexão SQLite3 e criação automática do Schema
├── backend_cadastro.py    # Validação de formulários e parser de propriedades para JSON
├── backend_leitura.py     # Lógica de consultas SQL, filtros, autocomplete e SQL livre
├── gui.py                 # Interface gráfica PyQt6 (Abas de Cadastro, Grid e Popup JSON)
├── .gitignore             # Filtros de arquivos ignorados pelo Git
└── README.md              # Documentação oficial do repositório
