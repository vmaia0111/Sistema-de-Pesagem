# Sistema de Pesagem
Este projeto é um Sistema de Pesagem desenvolvido em Python usando PyQt5 para a interface gráfica e comunicação via porta COM com balanças industriais. Ele foi projetado para ser flexível, permitindo o uso tanto por operadores quanto por administradores, com diferentes níveis de acesso às funcionalidades.

## Funcionalidades Principais
Autenticação de Usuário: Diferencia dois tipos de usuários:

- Administrador: Com acesso completo, incluindo o cadastro de clientes, produtos e configurações do sistema.
- Operador: Com acesso restrito à pesagem e seleção de modelos de produto.
- Interface Gráfica: Desenvolvida com PyQt5 para proporcionar uma interface amigável e intuitiva.

1. Cadastro de Clientes e Produtos: (Somente para Administradores)

2. Cadastro de novos clientes e produtos.
3. Definição dos limites de peso mínimo e máximo para cada produto.
4. Pesagem: Integração com balanças via porta serial (COM), exibindo o peso em tempo real, com verificação de conformidade dentro dos limites estabelecidos.

Alertas Visuais e Sonoros:

- Visual: O sistema altera o status e as cores da interface para indicar se o peso está dentro ou fora do intervalo especificado.
- Sonoro: Um alerta sonoro é emitido quando o peso está fora dos limites.
--Seleção de Modelos: Permite que os operadores escolham o cliente e o produto para iniciar o processo de pesagem.

1. Tecnologias Utilizadas
Python 3.12: Linguagem principal de desenvolvimento.
PyQt5: Para a construção da interface gráfica.
SQLite: Banco de dados local para armazenamento de clientes e produtos.
Serial: Comunicação via porta COM com a balança.
Git: Controle de versão do projeto.
Instalação
Pré-requisitos
Python 3.12 ou superior.
Dependências do projeto (listadas em requirements.txt).
Passo a passo
Clone o repositório:

bash
Copiar código
git clone https://github.com/vmaia0111/Sistema-de-Pesagem.git
Crie um ambiente virtual (opcional, mas recomendado):

bash
Copiar código
python -m venv venv
Ative o ambiente virtual:

No Windows:
bash
Copiar código
venv\Scripts\activate
No macOS/Linux:
bash
Copiar código
source venv/bin/activate
Instale as dependências:

bash
Copiar código
pip install -r requirements.txt
Execute a aplicação:

bash
Copiar código
python app.py
Como Usar
Login:

Administrador:
Username: admin
Password: admin123
Operador:
Username: operador
Password: 1234
Pesagem:

Após o login, o usuário operador pode selecionar o modelo (cliente e produto) e realizar a pesagem.
O sistema exibirá o peso em tempo real e fornecerá alertas visuais e sonoros em caso de não conformidade com os limites de peso.
Cadastro:

Somente o administrador pode acessar a aba "Cadastro" para adicionar novos clientes e produtos, com a definição de intervalos de peso.
Estrutura do Projeto
plaintext
Copiar código
Sistema-de-Pesagem/
│
├── balanca_sistema/           # Diretório principal do código-fonte
│   ├── app.py                 # Arquivo principal da aplicação
│   ├── db.py                  # Módulo de gerenciamento do banco de dados
│   ├── path_to_icon.ico        # Ícone do sistema
│   ├── database.db             # Banco de dados SQLite
│   ├── requirements.txt        # Arquivo de dependências
│   └── ...                    # Outros arquivos
│
├── LICENSE                    # Licença MIT do projeto
└── README.md                  # Instruções e detalhes do projeto
Exemplos de Uso
Interface Gráfica
A interface foi projetada para facilitar o uso tanto por operadores quanto por administradores.


Pesagem
A interface de pesagem permite acompanhar o peso em tempo real. Quando o peso está fora do intervalo, o sistema muda a cor para amarelo/vermelho e emite um alerta sonoro.
Compilação para Executável
Para compilar o projeto em um executável (Windows):

Instale o PyInstaller:

bash
Copiar código
pip install pyinstaller
Compile a aplicação:

bash
Copiar código
pyinstaller --onefile --windowed --icon=path_to_icon.ico app.py
O executável será gerado na pasta dist.

Contribuições
Contribuições são bem-vindas! Se você tiver sugestões de melhorias, sinta-se à vontade para abrir uma issue ou enviar um pull request.

Licença
Este projeto está licenciado sob a MIT License.

Com essas instruções, o README fornece uma descrição mais detalhada do projeto e inclui seções importantes, como instalação, uso e estrutura do projeto.
