import sqlite3

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        self.create_tables()  # Garante que as tabelas serão criadas ao inicializar o banco

    def create_tables(self):
        try:
            # Cria a tabela de clientes
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    nome TEXT NOT NULL
                                )''')

            # Cria a tabela de produtos
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    cliente_id INTEGER,
                                    nome TEXT NOT NULL,
                                    min_peso REAL,
                                    max_peso REAL,
                                    FOREIGN KEY (cliente_id) REFERENCES clientes (id)
                                )''')

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar tabelas: {e}")

    def get_cliente_by_name(self, client_name):
        try:
            query = "SELECT * FROM clientes WHERE nome = ?"
            self.cursor.execute(query, (client_name,))
            cliente = self.cursor.fetchone()
            return cliente
        except sqlite3.Error as e:
            print(f"Erro ao buscar cliente: {e}")
            return None

    def get_produto_by_name(self, product_name):
        try:
            query = "SELECT * FROM produtos WHERE nome = ?"
            self.cursor.execute(query, (product_name,))
            produto = self.cursor.fetchone()
            return produto
        except sqlite3.Error as e:
            print(f"Erro ao buscar produto: {e}")
            return None

    def get_clientes(self):
        try:
            query = "SELECT id, nome FROM clientes"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar clientes: {e}")
            return []

    def add_cliente(self, nome_cliente):
        try:
            query = "INSERT INTO clientes (nome) VALUES (?)"
            self.cursor.execute(query, (nome_cliente,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao adicionar cliente: {e}")

    def get_produtos_by_cliente(self, cliente_id):
        try:
            query = "SELECT id, nome, min_peso, max_peso FROM produtos WHERE cliente_id = ?"
            self.cursor.execute(query, (cliente_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar produtos: {e}")
            return []

    def add_produto(self, cliente_id, nome_produto, min_peso, max_peso):
        try:
            query = "INSERT INTO produtos (cliente_id, nome, min_peso, max_peso) VALUES (?, ?, ?, ?)"
            self.cursor.execute(query, (cliente_id, nome_produto, min_peso, max_peso))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao adicionar produto: {e}")
