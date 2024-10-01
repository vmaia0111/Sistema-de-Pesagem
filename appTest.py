import json
import os
import re
import sys
import threading
from PyQt5 import QtWidgets, QtCore, QtGui
from db import DatabaseManager
import serial
import serial.tools.list_ports
import time

def resource_path(relative_path):
    """Obter o caminho absoluto para o recurso, considerando se é executável ou não."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

config_path = resource_path('config.json')

# Classe LoginDialog para autenticação
class LoginDialog(QtWidgets.QDialog):
    def __init__(self, auto_login_operator=False):
        super(LoginDialog, self).__init__()
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 300, 100)

        if auto_login_operator:
            self.user_role = 'operador'
            self.accept()
            return

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

        if username == 'operador':
            self.user_role = 'operador'
            self.accept()
        elif username == 'admin' and password == 'admin123':
            self.user_role = 'admin'
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Credenciais inválidas!')

class MainApp(QtWidgets.QMainWindow):
    def __init__(self, user_role):
        super(MainApp, self).__init__()
        self.db = DatabaseManager()
        self.user_role = user_role
        self.config = self.load_config()
        self.min_weight = 0.0  # Defina um valor padrão
        self.max_weight = 1000.0  # Defina um valor padrão alto
        self.initUI()
        self.serialPort = None
        self.arduinoPort = None
        self.reading_thread = threading.Thread(target=self.read_weight_continuously)
        self.reading_thread.daemon = True  # Permite que o thread seja fechado ao encerrar o programa
        self.reading_thread.start()  # Inicia o thread de leitura contínua da balança

    def load_config(self):
        """Carrega as configurações do arquivo JSON."""
        config_path = 'config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Arquivo de configuração não encontrado.')
            sys.exit()

    def initUI(self):
        self.setWindowTitle('Sistema de Pesagem')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QtGui.QIcon('C:/Users/vmaia/OneDrive/Área de Trabalho/Prix/path_to_icon.png'))

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

        self.tabs.addTab(self.weightTab, "Peso")

        # Adicionar as outras abas (Cadastro de produtos e clientes)
        # ...

        self.show()

        # Iniciar a conexão com a balança e o Arduino
        self.start_serial_communication()

    def start_serial_communication(self):
        try:
            # Conexão com a balança usando os parâmetros do arquivo JSON
            balanca_config = self.config.get('balanca', {})
            self.serialPort = serial.Serial(
                port=balanca_config.get('port', 'COM'),
                baudrate=balanca_config.get('baudrate', 4800),
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE if balanca_config.get('parity') == 'N' else serial.PARITY_ODD,
                stopbits=serial.STOPBITS_ONE if balanca_config.get('stopbits') == 1 else serial.STOPBITS_TWO,
                timeout=balanca_config.get('timeout', 1)
            )
            QtWidgets.QMessageBox.information(self, 'Conexão', "Conectado à balança com sucesso.")
            
            # Conexão com o Arduino usando os parâmetros do arquivo JSON
            arduino_config = self.config.get('arduino', {})
            self.arduinoPort = serial.Serial(
                port=arduino_config.get('port', 'COM6'),
                baudrate=arduino_config.get('baudrate', 9600),
                timeout=arduino_config.get('timeout', 1)
            )
            QtWidgets.QMessageBox.information(self, 'Conexão', "Conectado ao Arduino com sucesso.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Erro', f"Erro ao conectar: {e}")

    def read_weight_continuously(self):
        """Leitura contínua do peso da balança, rodando em um thread separado."""
        while True:
            self.update_weight()  # Atualiza o peso na interface
            time.sleep(0.5)  # Espera 0.5 segundos antes da próxima leitura

    def read_weight_from_serial(self):
        try:
            if self.serialPort is not None and self.serialPort.is_open:
                raw_data = self.serialPort.readline()
                print(f"Dados brutos recebidos: {raw_data}")

                # Função para processar e decodificar os dados recebidos com latin1
                weight = self.process_data(raw_data)
                return weight
        except Exception as e:
            print(f"Erro ao ler peso: {e}")
            return 0.0

    def process_data(self, raw_data):
        try:
            # Decodificar os dados brutos
            decoded_data = raw_data.decode('latin1', errors='ignore').strip()
            print(f"Dados decodificados: {decoded_data}")

            # Substituição de caracteres especiais como '²' por números
            decoded_data = decoded_data.replace('²', '2').replace('³', '3')

            # Extrair apenas números e pontos, ignorando letras e outros caracteres
            numeric_pattern = re.findall(r'[0-9]+(?:\.[0-9]+)?', decoded_data)

            # Mostrar os números encontrados
            if numeric_pattern:
                print(f"Números capturados: {numeric_pattern}")

                # Verifica se o número capturado tem parte decimal (ponto)
                final_number = None
                for num in numeric_pattern:
                    if '.' in num:
                        final_number = num
                        break

                # Se não encontrou número decimal, pega o maior número como peso
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
        if weight is not None:
            self.label.setText(f'Peso: {weight:.3f} Kg')
    
            if weight == 0.0:
                self.label.setText('Peso: 0.000 Kg')
                self.statusLabel.setText("Status: AGUARDANDO PESAGEM")
                self.statusLabel.setStyleSheet("color: blue; font-size: 20px; background-color: lightgray; border: none;")
                self.label.setStyleSheet("color: blue; font-size: 40px; background-color: lightgray; border: none;")
            elif weight < self.min_weight or weight > self.max_weight:
                self.statusLabel.setText("Status: PESO FORA DO INTERVALO!")
                self.statusLabel.setStyleSheet("color: red; font-size: 20px; background-color: yellow; border: 2px solid red;")
                self.label.setStyleSheet("color: red; font-size: 40px; background-color: yellow; border: 2px solid red;")
            else:
                self.statusLabel.setText("Status: PESO DENTRO DO INTERVALO")
                self.statusLabel.setStyleSheet("color: green; font-size: 20px; background-color: lightgreen; border: 2px solid green;")
                self.label.setStyleSheet("color: green; font-size: 40px; background-color: lightgreen; border: 2px solid green;")

# Código para cadastro de clientes e produtos, conforme o código original
# ...

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    login = LoginDialog()
    if login.exec_() == QtWidgets.QDialog.Accepted:
        mainWindow = MainApp(login.user_role)

        sys.exit(app.exec_())
