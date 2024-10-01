import re
import sys
import json  # Importar o módulo json
from PyQt5 import QtWidgets, QtCore, QtGui
from db import DatabaseManager  # Certifique-se de que o arquivo db.py contém a classe DatabaseManager
import serial

# Classe LoginDialog para autenticação
class LoginDialog(QtWidgets.QDialog):
    def __init__(self):
        super(LoginDialog, self).__init__()
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 300, 100)

        self.username_label = QtWidgets.QLabel("Username:")
        self.password_label = QtWidgets.QLabel("Password:")
        self.username_input = QtWidgets.QLineEdit(self)
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.login_button = QtWidgets.QPushButton("Login", self)
        self.login_button.clicked.connect(self.check_credentials)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

        self.user_role = None

    def check_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == 'admin' and password == 'admin123':
            self.user_role = 'admin'
            self.accept()
        elif username == '' and password == '':
            self.user_role = 'operador'
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Credenciais inválidas!')

class MainApp(QtWidgets.QMainWindow):
    def __init__(self, user_role):
        super(MainApp, self).__init__()
        self.db = DatabaseManager()  # Inicialize a conexão com o banco de dados
        self.user_role = user_role  # Definir o papel do usuário
        self.load_config()  # Carrega as configurações do arquivo JSON
        self.initUI()
        self.serialPort = None
        self.arduinoPort = None
        self.selected_client = None
        self.selected_product = None
        self.min_weight = 0.0
        self.max_weight = 0.0

    def load_config(self):
        # Lê o arquivo config.json e carrega as portas configuradas
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                self.balanca_port = config.get('balanca_port', '')
                self.arduino_port = config.get('arduino_port', '')
        except FileNotFoundError:
            print("Arquivo de configuração não encontrado.")
            self.balanca_port = ''
            self.arduino_port = ''

    def initUI(self):
        self.setWindowTitle('Sistema de Pesagem')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QtGui.QIcon('C:/Users/vmaia/OneDrive/Área de Trabalho/Prix/path_to_icon.png'))

        # Configurando o layout principal
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        mainLayout = QtWidgets.QVBoxLayout(self.centralWidget)

        # Tabs para a interface
        self.tabs = QtWidgets.QTabWidget(self)
        mainLayout.addWidget(self.tabs)

        # Tab para exibir o peso
        self.weightTab = QtWidgets.QWidget()
        self.weightTabLayout = QtWidgets.QVBoxLayout(self.weightTab)
        self.weightTabLayout.setContentsMargins(20, 20, 20, 20)

        self.title_label = QtWidgets.QLabel('Sistema de Pesagem', self)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50; margin-bottom: 20px;")
        self.weightTabLayout.addWidget(self.title_label)

        self.label = QtWidgets.QLabel('Peso: 0.000 Kg', self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("""
            font-size: 40px; 
            color: #34495E; 
            font-weight: bold; 
            background-color: lightgray; 
            padding: 10px; 
            border: 3px solid #2980B9; 
            border-radius: 10px;
            """)
        self.weightTabLayout.addWidget(self.label)

        self.statusLabel = QtWidgets.QLabel('Status: AGUARDANDO PESAGEM', self)
        self.statusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.statusLabel.setStyleSheet("font-size: 20px; color: #2980B9;")
        self.weightTabLayout.addWidget(self.statusLabel)

        self.selectedInfoLabel = QtWidgets.QLabel('Cliente: - | Produto: - | Intervalo de Peso: -', self)
        self.selectedInfoLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.selectedInfoLabel.setStyleSheet("font-size: 18px; color: #8E44AD; margin-top: 20px;")
        self.weightTabLayout.addWidget(self.selectedInfoLabel)

        # Layout Horizontal para os botões de conexão
        portLayout = QtWidgets.QHBoxLayout()

        self.connectButton = QtWidgets.QPushButton('Conectar Balança', self)
        self.connectButton.setStyleSheet("background-color: #E67E22; color: white; padding: 10px; font-size: 16px;")
        self.connectButton.clicked.connect(self.start_serial_communication)
        portLayout.addWidget(self.connectButton)

        self.arduinoConnectButton = QtWidgets.QPushButton('Conectar Arduino', self)
        self.arduinoConnectButton.setStyleSheet("background-color: #27AE60; color: white; padding: 10px; font-size: 16px;")
        self.arduinoConnectButton.clicked.connect(self.connect_to_arduino)
        portLayout.addWidget(self.arduinoConnectButton)

        self.weightTabLayout.addLayout(portLayout)

        self.tabs.addTab(self.weightTab, "Peso")

        # Tab de Cadastro (com subabas) - Apenas para administradores
        if self.user_role == 'admin':
            self.registerTab = QtWidgets.QWidget()
            self.registerTabLayout = QtWidgets.QVBoxLayout(self.registerTab)
            self.tabs.addTab(self.registerTab, "Cadastro")

            # Subabas para Cadastro de Cliente e Cadastro de Produto
            self.subTabs = QtWidgets.QTabWidget(self)
            self.registerTabLayout.addWidget(self.subTabs)

            # Subaba para cadastrar clientes
            self.clientRegisterTab = QtWidgets.QWidget()
            self.clientRegisterLayout = QtWidgets.QVBoxLayout(self.clientRegisterTab)

            self.clientFormLayout = QtWidgets.QFormLayout()
            self.clientNameInput = QtWidgets.QLineEdit(self)
            self.clientNameInput.setPlaceholderText('Nome do Cliente')
            self.clientNameInput.setStyleSheet("padding: 10px; font-size: 16px;")
            self.clientFormLayout.addRow("Cliente:", self.clientNameInput)

            self.addClientButton = QtWidgets.QPushButton('Cadastrar Cliente', self)
            self.addClientButton.setStyleSheet("background-color: #3498DB; color: white; padding: 10px; font-size: 16px;")
            self.addClientButton.clicked.connect(self.add_client)

            self.clientRegisterLayout.addLayout(self.clientFormLayout)
            self.clientRegisterLayout.addWidget(self.addClientButton)

            self.subTabs.addTab(self.clientRegisterTab, "Cadastrar Cliente")

            # Subaba para cadastrar produtos
            self.productRegisterTab = QtWidgets.QWidget()
            self.productRegisterLayout = QtWidgets.QVBoxLayout(self.productRegisterTab)

            self.productFormLayout = QtWidgets.QFormLayout()

            self.clientComboBoxProduct = QtWidgets.QComboBox(self)
            self.clientComboBoxProduct.setStyleSheet("padding: 10px; font-size: 16px;")
            self.productFormLayout.addRow("Cliente:", self.clientComboBoxProduct)

            self.productInput = QtWidgets.QLineEdit(self)
            self.productInput.setPlaceholderText('Nome do Produto')
            self.productInput.setStyleSheet("padding: 10px; font-size: 16px;")
            self.productFormLayout.addRow("Produto:", self.productInput)

            self.minWeightInput = QtWidgets.QLineEdit(self)
            self.minWeightInput.setPlaceholderText('Peso Mínimo (Kg)')
            self.minWeightInput.setStyleSheet("padding: 10px; font-size: 16px;")
            self.productFormLayout.addRow("Peso Mínimo:", self.minWeightInput)

            self.maxWeightInput = QtWidgets.QLineEdit(self)
            self.maxWeightInput.setPlaceholderText('Peso Máximo (Kg)')
            self.maxWeightInput.setStyleSheet("padding: 10px; font-size: 16px;")
            self.productFormLayout.addRow("Peso Máximo:", self.maxWeightInput)

            self.addProductButton = QtWidgets.QPushButton('Cadastrar Produto', self)
            self.addProductButton.setStyleSheet("background-color: #3498DB; color: white; padding: 10px; font-size: 16px;")
            self.addProductButton.clicked.connect(self.add_product)

            self.productRegisterLayout.addLayout(self.productFormLayout)
            self.productRegisterLayout.addWidget(self.addProductButton)

            self.subTabs.addTab(self.productRegisterTab, "Cadastrar Produto")

        # Adicionar aba de Modelos (para selecionar clientes e produtos do banco)
        self.modelsTab = QtWidgets.QWidget()
        self.modelsTabLayout = QtWidgets.QVBoxLayout(self.modelsTab)
        self.modelsTabLayout.setContentsMargins(20, 20, 20, 20)

        self.modelsTitle = QtWidgets.QLabel('Selecionar Modelo', self)
        self.modelsTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.modelsTitle.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50; margin-bottom: 20px;")
        self.modelsTabLayout.addWidget(self.modelsTitle)

        self.clientComboBox = QtWidgets.QComboBox(self)
        self.clientComboBox.setStyleSheet("padding: 10px; font-size: 16px;")
        self.clientComboBox.currentIndexChanged.connect(self.update_product_list)
        self.modelsTabLayout.addWidget(self.clientComboBox)

        self.productComboBox = QtWidgets.QComboBox(self)
        self.productComboBox.setStyleSheet("padding: 10px; font-size: 16px;")
        self.modelsTabLayout.addWidget(self.productComboBox)

        self.selectButton = QtWidgets.QPushButton('Selecionar Modelo', self)
        self.selectButton.setStyleSheet("background-color: #27AE60; color: white; padding: 10px; font-size: 16px;")
        self.selectButton.clicked.connect(self.select_product)
        self.modelsTabLayout.addWidget(self.selectButton)

        # Mostrar botões "Editar" e "Excluir" apenas para administradores
        if self.user_role == 'admin':
            self.editButton = QtWidgets.QPushButton('Editar Produto', self)
            self.editButton.setStyleSheet("background-color: #3498DB; color: white; padding: 10px; font-size: 16px;")
            self.editButton.clicked.connect(self.edit_product)
            self.modelsTabLayout.addWidget(self.editButton)

            self.deleteButton = QtWidgets.QPushButton('Excluir Produto', self)
            self.deleteButton.setStyleSheet("background-color: #E74C3C; color: white; padding: 10px; font-size: 16px;")
            self.deleteButton.clicked.connect(self.delete_product)
            self.modelsTabLayout.addWidget(self.deleteButton)

        self.tabs.addTab(self.modelsTab, "Modelos")

        self.show()

        self.update_client_list()  # Atualiza a lista de clientes no início
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_weight)
        self.timer.start(500)  # Tempo reduzido para melhorar a resposta

    def start_serial_communication(self):
        try:
            selected_port = self.balanca_port  # Usa a porta definida no arquivo JSON
            self.serialPort = serial.Serial(
                port=selected_port,
                baudrate=4800,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1  # Timeout reduzido para melhorar a resposta
            )
            QtWidgets.QMessageBox.information(self, 'Conexão', f"Conectado à balança na {selected_port} com sucesso.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Erro', f"Erro ao conectar na balança: {e}")

    def connect_to_arduino(self):
        arduino_port = self.arduino_port  # Usa a porta definida no arquivo JSON
        try:
            self.arduinoPort = serial.Serial(
                port=arduino_port,
                baudrate=9600,  # Taxa de transmissão comum para Arduino
                timeout=1
            )
            QtWidgets.QMessageBox.information(self, 'Conexão', f"Conectado ao Arduino na {arduino_port}.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Erro', f"Erro ao conectar no Arduino: {e}")

    def send_command_to_arduino(self, command):
        if self.arduinoPort is not None and self.arduinoPort.is_open:
            self.arduinoPort.write(f"{command}\n".encode())  # Enviar string simples com quebra de linha
            print(f"Comando enviado ao Arduino: {command}")

    def add_client(self):
        client_name = self.clientNameInput.text()
        if client_name:
            cliente_existe = self.db.get_cliente_by_name(client_name)
            if not cliente_existe:
                self.db.add_cliente(client_name)
                QtWidgets.QMessageBox.information(self, 'Cadastro', 'Cliente cadastrado com sucesso!')
            else:
                QtWidgets.QMessageBox.information(self, 'Cadastro', 'Cliente já cadastrado.')
            self.update_client_list()  # Atualiza a lista de clientes na aba de cadastro de produtos
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Preencha o nome do cliente.')

    def add_product(self):
        client_name = self.clientComboBoxProduct.currentText()
        product_name = self.productInput.text()
        min_weight = self.minWeightInput.text()
        max_weight = self.maxWeightInput.text()

        if client_name and product_name and min_weight and max_weight:
            cliente_id = self.db.get_cliente_by_name(client_name)[0]
            self.db.add_produto(cliente_id, product_name, float(min_weight), float(max_weight))
            QtWidgets.QMessageBox.information(self, 'Cadastro', 'Produto cadastrado com sucesso!')
            self.update_client_list()  # Atualiza a lista de clientes
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Preencha todos os campos.')

    def update_client_list(self):
        self.clientComboBox.clear()
        if hasattr(self, 'clientComboBoxProduct'):
            self.clientComboBoxProduct.clear()
        clientes = self.db.get_clientes()
        for cliente in clientes:
            self.clientComboBox.addItem(cliente[1], cliente[0])
            if hasattr(self, 'clientComboBoxProduct'):
                self.clientComboBoxProduct.addItem(cliente[1], cliente[0])

    def update_product_list(self):
        self.productComboBox.clear()
        selected_client_id = self.clientComboBox.currentData()
        produtos = self.db.get_produtos_by_cliente(selected_client_id)
        for produto in produtos:
            self.productComboBox.addItem(produto[1], produto[0])

    def select_product(self):
        self.selected_client = self.clientComboBox.currentText()
        self.selected_product = self.productComboBox.currentText()

        if self.selected_client and self.selected_product:
            produto = self.db.get_produto_by_name(self.selected_product)
            if produto:
                self.min_weight = produto[3]
                self.max_weight = produto[4]
                self.selectedInfoLabel.setText(f'Cliente: {self.selected_client} | Produto: {self.selected_product} | Intervalo de Peso: {self.min_weight} - {self.max_weight} Kg')
            QtWidgets.QMessageBox.information(self, 'Seleção', f"Modelo {self.selected_product} selecionado!")
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Selecione um cliente e produto.')

    def edit_product(self):
        # Obtém os dados do produto selecionado
        selected_client_id = self.clientComboBox.currentData()
        selected_product_name = self.productComboBox.currentText()

        # Janela de diálogo para editar produto
        if selected_client_id and selected_product_name:
            produto = self.db.get_produto_by_name(selected_product_name)
            if produto:
                novo_nome, ok = QtWidgets.QInputDialog.getText(self, "Editar Produto", "Novo Nome do Produto:", QtWidgets.QLineEdit.Normal, produto[2])
                novo_peso_min, ok_min = QtWidgets.QInputDialog.getDouble(self, "Editar Produto", "Novo Peso Mínimo:", produto[3], 0, 10000, 3)
                novo_peso_max, ok_max = QtWidgets.QInputDialog.getDouble(self, "Editar Produto", "Novo Peso Máximo:", produto[4], 0, 10000, 3)

                if ok and ok_min and ok_max:
                    self.db.update_produto(produto[0], novo_nome, novo_peso_min, novo_peso_max)
                    QtWidgets.QMessageBox.information(self, "Sucesso", "Produto atualizado com sucesso!")
                    self.update_product_list()
                else:
                    QtWidgets.QMessageBox.warning(self, "Erro", "Edição cancelada ou dados inválidos.")
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Selecione um produto para editar.')

    def delete_product(self):
        selected_client_id = self.clientComboBox.currentData()
        selected_product_name = self.productComboBox.currentText()

        if selected_client_id and selected_product_name:
            confirmation = QtWidgets.QMessageBox.question(self, 'Confirmação', f'Tem certeza de que deseja excluir o produto "{selected_product_name}"?',
                                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if confirmation == QtWidgets.QMessageBox.Yes:
                self.db.delete_produto(selected_client_id, selected_product_name)
                QtWidgets.QMessageBox.information(self, "Sucesso", "Produto excluído com sucesso!")
                self.update_product_list()
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Selecione um produto para excluir.')

    def read_weight_from_serial(self):
        try:
            if self.serialPort is not None and self.serialPort.is_open:
                raw_data = self.serialPort.read(60)  # Ler até 60 bytes
                print(f"Dados brutos recebidos: {raw_data}")
                if raw_data:  # Verifica se algum dado foi recebido
                    if len(raw_data) > 15:
                        raw_data = raw_data[15:]  # Ignora os primeiros 15 bytes
                    return self.process_data(raw_data)
                else:
                    print("Nenhum dado recebido da balança.")
                    return None
        except Exception as e:
            print(f"Erro ao ler peso: {e}")
        return None

    def process_data(self, raw_data):
        try:
            decoded_data = raw_data.decode('latin1', errors='ignore').strip()
            print(f"Dados decodificados: {decoded_data}")

            decoded_data = (decoded_data.replace('±', '1')
                                        .replace('·', '7')
                                        .replace('²', '2')
                                        .replace('³', '3')
                                        .replace('´', '4')
                                        .replace('¸', '8'))
                                        
            print(f"Dados corrigidos: {decoded_data}")

            cleaned_data = re.sub(r'[^0-9.-]', '', decoded_data)
            print(f"Dados limpos: {cleaned_data}")

            numeric_pattern = re.findall(r'[0-9]+(?:\.[0-9]+)?', cleaned_data)

            if numeric_pattern:
                print(f"Números capturados: {numeric_pattern}")

                final_number = None
                for num in numeric_pattern:
                    if '.' in num:
                        final_number = num
                        break

                if not final_number:
                    final_number = max(numeric_pattern, key=len)

                print(f"Peso capturado: {final_number} Kg")
                return float(final_number)
            else:
                print("Nenhum número válido encontrado.")
                return 0.0
        except Exception as e:
            print(f"Erro no processamento dos dados: {e}")
            return 0.0

    def update_weight(self):
        weight = self.read_weight_from_serial()

        if weight is not None and weight > 0:
            # Formata o peso para ter sempre três dígitos após o ponto
            formatted_weight = f'{weight:.3f}'
            self.label.setText(f'Peso: {formatted_weight} Kg')

            if weight < self.min_weight or weight > self.max_weight:
                self.statusLabel.setText("Status: PESO FORA DO INTERVALO!")
                self.statusLabel.setStyleSheet("color: red; font-size: 20px; background-color: yellow; border: 2px solid red;")
                self.label.setStyleSheet("color: red; font-size: 40px; background-color: yellow; border: 2px solid red;")

                self.send_command_to_arduino("LIGAR")
            else:
                self.statusLabel.setText("Status: PESO DENTRO DO INTERVALO")
                self.statusLabel.setStyleSheet("color: green; font-size: 20px; background-color: lightgreen; border: 2px solid green;")
                self.label.setStyleSheet("color: green; font-size: 40px; background-color: lightgreen; border: 2px solid green;")

                self.send_command_to_arduino("DESLIGAR")
        else:
            self.label.setText('Peso: 0.000 Kg')  # Exibe sempre com 3 dígitos após o ponto
            self.statusLabel.setText("Status: AGUARDANDO PESAGEM")
            self.statusLabel.setStyleSheet("color: blue; font-size: 20px; background-color: lightgray; border: none;")
            self.label.setStyleSheet("color: blue; font-size: 40px; background-color: lightgray; border: none;")
            self.send_command_to_arduino("DESLIGAR")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    login = LoginDialog()
    if login.exec_() == QtWidgets.QDialog.Accepted:
        mainWindow = MainApp(login.user_role)
        sys.exit(app.exec_())
