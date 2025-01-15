No prompt após baixar o python seguir essa ordem de comandos
pip install pyinstaller
pip install -r requirements.txt
pyinstaller --onefile --icon=appico.ico AppIA.py

--Pasta Utils tem as funções adicionais de atualizar o executavel e controlar o uso dos usuarios
--Pasta Router tem as funções que geram as rotas http para comunicar com o frontend
--Pasta OpenAIConfig tem as funções para se comuunicar e conectar com a API do OpenAI