import sqlite3

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.connection = sqlite3.connect('balanca_sistema.db')  # Nome do banco de dados
            self.cursor = self.connection.cursor()
            print("Conectado ao banco de dados com sucesso!")
            self.create_tables()
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def create_tables(self):
        """Cria as tabelas de clientes e produtos, se não existirem."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER,
                    nome TEXT NOT NULL,
                    peso_min REAL,
                    peso_max REAL,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                )
            ''')
            self.connection.commit()
            print("Tabelas criadas ou já existem.")
        except sqlite3.Error as e:
            print(f"Erro ao criar tabelas: {e}")

    def add_cliente(self, nome):
        """Adiciona um cliente no banco de dados."""
        try:
            query = "INSERT INTO clientes (nome) VALUES (?)"
            self.cursor.execute(query, (nome,))
            self.connection.commit()
            print("Cliente adicionado com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao adicionar cliente: {e}")

    def get_clientes(self):
        """Retorna todos os clientes cadastrados."""
        try:
            query = "SELECT id, nome FROM clientes"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print(f"Erro ao buscar clientes: {e}")
            return []

    def get_cliente_by_name(self, nome):
        """Busca um cliente pelo nome."""
        try:
            query = "SELECT * FROM clientes WHERE nome = ?"
            self.cursor.execute(query, (nome,))
            result = self.cursor.fetchone()
            return result
        except sqlite3.Error as e:
            print(f"Erro ao buscar cliente: {e}")
            return None

    def add_produto(self, cliente_id, nome, peso_min, peso_max):
        """Adiciona um produto no banco de dados."""
        try:
            query = "INSERT INTO produtos (cliente_id, nome, peso_min, peso_max) VALUES (?, ?, ?, ?)"
            self.cursor.execute(query, (cliente_id, nome, peso_min, peso_max))
            self.connection.commit()
            print("Produto adicionado com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao adicionar produto: {e}")

    def get_produtos_by_cliente(self, cliente_id):
        """Retorna os produtos de um cliente específico, incluindo o intervalo de peso."""
        try:
            query = "SELECT id, nome, peso_min, peso_max FROM produtos WHERE cliente_id = ?"
            self.cursor.execute(query, (cliente_id,))
            result = self.cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print(f"Erro ao buscar produtos: {e}")
            return []


    def get_produto_by_name(self, nome):
        """Busca um produto pelo nome."""
        try:
            query = "SELECT * FROM produtos WHERE nome = ?"
            self.cursor.execute(query, (nome,))
            result = self.cursor.fetchone()
            return result
        except sqlite3.Error as e:
            print(f"Erro ao buscar produto: {e}")
            return None

    def update_produto(self, produto_id, novo_nome, novo_peso_min, novo_peso_max):
        """Atualiza os dados de um produto existente."""
        try:
            query = '''UPDATE produtos 
                       SET nome = ?, peso_min = ?, peso_max = ?
                       WHERE id = ?'''
            self.cursor.execute(query, (novo_nome, novo_peso_min, novo_peso_max, produto_id))
            self.connection.commit()
            print("Produto atualizado com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao atualizar produto: {e}")

    def delete_produto(self, cliente_id, produto_nome):
        """Deleta um produto baseado no cliente_id e nome do produto"""
        try:
            query = "DELETE FROM produtos WHERE cliente_id = ? AND nome = ?"
            self.cursor.execute(query, (cliente_id, produto_nome))
            self.connection.commit()
            print("Produto deletado com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao deletar produto: {e}")


    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.connection:
            self.connection.close()
            print("Conexão com o banco de dados encerrada.")
