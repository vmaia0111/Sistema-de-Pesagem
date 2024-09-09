import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from db import DatabaseManager  # Certifique-se de que o arquivo db.py contém a classe DatabaseManager
import serial
import serial.tools.list_ports
import winsound  # Para o alerta sonoro

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
        
        # Verificação simples de exemplo (substitua com a lógica real de autenticação)
        if username == 'admin' and password == 'admin123':
            self.user_role = 'admin'
            self.accept()
        elif username == 'operador' and password == '1234':
            self.user_role = 'operador'
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Credenciais inválidas!')

class MainApp(QtWidgets.QMainWindow):
    def __init__(self, user_role):
        super(MainApp, self).__init__()
        self.db = DatabaseManager()  # Inicialize a conexão com o banco de dados
        self.user_role = user_role  # Definir o papel do usuário
        self.initUI()
        self.serialPort = None
        self.selected_client = None
        self.selected_product = None
        self.min_weight = 0.0
        self.max_weight = 0.0

    def initUI(self):
        self.setWindowTitle('Sistema de Pesagem')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QtGui.QIcon('C:/Users/vmaia/OneDrive/Área de Trabalho/Prix/path_to_icon.png'))  # Ícone do aplicativo

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

        # Layout Horizontal para a conexão com a porta COM
        portLayout = QtWidgets.QHBoxLayout()

        self.portComboBox = QtWidgets.QComboBox(self)
        self.portComboBox.addItems(self.get_available_ports())
        self.portComboBox.setStyleSheet("padding: 10px; font-size: 16px;")
        portLayout.addWidget(self.portComboBox)

        self.connectButton = QtWidgets.QPushButton('Conectar Porta', self)
        self.connectButton.setStyleSheet("background-color: #E67E22; color: white; padding: 10px; font-size: 16px;")
        self.connectButton.clicked.connect(self.start_serial_communication)
        portLayout.addWidget(self.connectButton)

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

        self.tabs.addTab(self.modelsTab, "Modelos")

        self.show()

        self.update_client_list()  # Atualiza a lista de clientes no início
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_weight)
        self.timer.start(500)  # Tempo reduzido para melhorar a resposta

    def get_available_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def start_serial_communication(self):
        try:
            selected_port = self.portComboBox.currentText()
            self.serialPort = serial.Serial(
                port=selected_port,
                baudrate=4800,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1  # Timeout reduzido para melhorar a resposta
            )
            QtWidgets.QMessageBox.information(self, 'Conexão', f"Conectado à {selected_port} com sucesso.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Erro', f"Erro ao conectar na balança: {e}")

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
        """Atualiza a lista de clientes no ComboBox da aba de modelos e cadastro de produto"""
        self.clientComboBox.clear()
        if hasattr(self, 'clientComboBoxProduct'):
            self.clientComboBoxProduct.clear()
        clientes = self.db.get_clientes()
        for cliente in clientes:
            self.clientComboBox.addItem(cliente[1], cliente[0])  # Adiciona o nome e ID do cliente
            if hasattr(self, 'clientComboBoxProduct'):
                self.clientComboBoxProduct.addItem(cliente[1], cliente[0])

    def update_product_list(self):
        """Atualiza a lista de produtos com base no cliente selecionado"""
        self.productComboBox.clear()
        selected_client_id = self.clientComboBox.currentData()  # Pega o ID do cliente selecionado
        produtos = self.db.get_produtos_by_cliente(selected_client_id)
        for produto in produtos:
            self.productComboBox.addItem(produto[1], produto[0])  # Adiciona o nome e ID do produto

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

    def read_weight_from_serial(self):
        try:
            if self.serialPort is not None and self.serialPort.is_open:
                raw_data = self.serialPort.readline()
                cleaned_data = raw_data.decode('utf-8').strip().replace('\x02', '').split('\r')[0]
                if cleaned_data:  # Verifica se os dados não estão vazios
                    return float(cleaned_data)
                else:
                    return 0.0  # Retorna 0 quando o peso é removido (dados vazios)
        except Exception as e:
            print(f"Erro ao ler peso: {e}")
            return 0.0  # Retorna 0 em caso de erro

    def update_weight(self):
        weight = self.read_weight_from_serial()
        if weight is not None:
            self.label.setText(f'Peso: {weight:.3f} Kg')

            # Verificação de peso e aviso visual e sonoro
            if weight < self.min_weight or weight > self.max_weight:
                self.statusLabel.setText("Status: PESO FORA DO INTERVALO!")
                self.statusLabel.setStyleSheet("color: red; font-size: 20px; background-color: yellow; border: 2px solid red;")
                self.label.setStyleSheet("color: red; font-size: 40px; background-color: yellow; border: 2px solid red;")
                self.play_warning_sound()
            elif weight == 0.0:  # Quando o peso é removido (zera)
                self.label.setText('Peso: 0.000 Kg')
                self.statusLabel.setText("Status: AGUARDANDO PESAGEM")
                self.statusLabel.setStyleSheet("color: blue; font-size: 20px; background-color: lightgray; border: none;")
                self.label.setStyleSheet("color: blue; font-size: 40px; background-color: lightgray; border: none;")
            else:
                self.statusLabel.setText("Status: PESO DENTRO DO INTERVALO")
                self.statusLabel.setStyleSheet("color: green; font-size: 20px; background-color: lightgreen; border: 2px solid green;")
                self.label.setStyleSheet("color: green; font-size: 40px; background-color: lightgreen; border: 2px solid green;")

    def play_warning_sound(self):
        """Emite som de alerta quando o peso está fora do intervalo."""
        winsound.Beep(1000, 2000)  # Frequência de 1000 Hz por 2 segundos

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    login = LoginDialog()
    if login.exec_() == QtWidgets.QDialog.Accepted:
        mainWindow = MainApp(login.user_role)
        sys.exit(app.exec_())
