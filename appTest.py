import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import winsound  # Para o alerta sonoro

class TestApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(TestApp, self).__init__()
        self.initUI()
        self.min_weight = 0.155  # Defina o peso mínimo para o teste
        self.max_weight = 0.165  # Defina o peso máximo para o teste
        self.alert_timer = QtCore.QTimer(self)  # Timer para controlar o tempo do alerta
        self.alert_timer.timeout.connect(self.reset_status)  # Função que será chamada após o tempo do alerta

    def initUI(self):
        self.setWindowTitle('Sistema de Pesagem - Teste Manual')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QtGui.QIcon('C:/Users/vmaia/OneDrive/Área de Trabalho/Prix/path_to_icon.png'))  # Ícone do aplicativo

        # Configurando o layout principal
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        mainLayout = QtWidgets.QVBoxLayout(self.centralWidget)

        # Label para título
        self.title_label = QtWidgets.QLabel('Simulação de Pesagem', self)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50; margin-bottom: 20px;")
        mainLayout.addWidget(self.title_label)

        # Label para exibir o peso
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
        mainLayout.addWidget(self.label)

        # Label para status
        self.statusLabel = QtWidgets.QLabel('Status: AGUARDANDO PESAGEM', self)
        self.statusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.statusLabel.setStyleSheet("font-size: 20px; color: #2980B9;")
        mainLayout.addWidget(self.statusLabel)

        # Campo para inserção manual do peso
        self.weightInput = QtWidgets.QLineEdit(self)
        self.weightInput.setPlaceholderText('Insira o peso manualmente (Kg)')
        self.weightInput.setStyleSheet("padding: 10px; font-size: 16px;")
        mainLayout.addWidget(self.weightInput)

        # Botão para testar o peso
        self.testButton = QtWidgets.QPushButton('Testar Peso', self)
        self.testButton.setStyleSheet("background-color: #27AE60; color: white; padding: 10px; font-size: 16px;")
        self.testButton.clicked.connect(self.manual_weight_test)
        mainLayout.addWidget(self.testButton)

        self.show()

    def manual_weight_test(self):
        """Função que testa o peso inserido manualmente."""
        try:
            weight = float(self.weightInput.text())
            self.label.setText(f'Peso: {weight:.3f} Kg')

            # Verificação de peso e aviso visual e sonoro
            if weight < self.min_weight or weight > self.max_weight:
                self.statusLabel.setText("Status: PESO FORA DO INTERVALO!")
                self.statusLabel.setStyleSheet("color: red; font-size: 20px; background-color: yellow; border: 2px solid red;")
                self.label.setStyleSheet("color: red; font-size: 40px; background-color: yellow; border: 2px solid red;")
                self.play_warning_sound()

                # Iniciar o timer para que o alerta dure 3 segundos (3000 milissegundos)
                self.alert_timer.start(3000)
            else:
                self.statusLabel.setText("Status: PESO DENTRO DO INTERVALO")
                self.statusLabel.setStyleSheet("color: green; font-size: 20px; background-color: lightgreen; border: 2px solid green;")
                self.label.setStyleSheet("color: green; font-size: 40px; background-color: lightgreen; border: 2px solid green;")
                self.alert_timer.stop()  # Para o timer se o peso estiver correto
        except ValueError:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Por favor, insira um valor numérico válido para o peso.')

    def reset_status(self):
        """Função que reseta o status e cor da interface após o tempo do alerta."""
        self.statusLabel.setText("Status: AGUARDANDO PESAGEM")
        self.statusLabel.setStyleSheet("color: #2980B9; font-size: 20px; background-color: none; border: none;")
        self.label.setStyleSheet("""
            font-size: 40px; 
            color: #34495E; 
            font-weight: bold; 
            background-color: lightgray; 
            padding: 10px; 
            border: 3px solid #2980B9; 
            border-radius: 10px;
            """)

    def play_warning_sound(self):
        """Emite som de alerta quando o peso está fora do intervalo."""
        duration = 3000  # Durar 3 segundos
        interval = 500  # Intervalo entre sons

        end_time = QtCore.QTime.currentTime().addMSecs(duration)
        while QtCore.QTime.currentTime() < end_time:
            winsound.Beep(1000, 1000)  # Frequência de 1000 Hz por 1 segundo
            QtCore.QThread.msleep(interval)  # Pausa por 500ms entre os bipes

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = TestApp()
    sys.exit(app.exec_())
