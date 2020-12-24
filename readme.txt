Установка зависимостей
pip install -r requirements.txt

Сборка
pyinstaller --noconfirm --onefile --windowed --icon "D:/PythonProjects/TextHelper/icon.ico" --name "TextHelper" --add-data "D:/PythonProjects/TextHelper/icon.ico;." --add-data "D:/PythonProjects/TextHelper/data;data" --add-data "D:/Python37/Lib/site-packages/natasha/data;natasha/data" ./main.py