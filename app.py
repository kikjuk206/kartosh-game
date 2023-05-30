from flask import Flask, render_template, request, redirect, url_for    #pip install Flask
import cv2                                                              #pip install opencv-python
from flask_cors import CORS                                             #pip install Flask-Cors
import sqlite3



#Подключение Flask
app = Flask(__name__)
cors = CORS(app, resources={r"/uploader": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

#Создание БД в SQLite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, login TEXT, score INTEGER)")

error = ''

soreva = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
score = 0


#Страница рейтинга
@app.route('/')
def test():
    
#Подключаемся к БД
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    users.sort(key=lambda x: x[2], reverse=True)

    conn.close()
    return render_template('index.html', users=users)



#Стараница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    global score
    if request.method == 'POST':
        login = request.form['login']
        name = request.form['name']
#Подключаемся к БД
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (login, name, score) VALUES (?, ?, ?)", (login, name, score))
        conn.commit()
        conn.close()

        return render_template('success.html')
    else:
        return render_template('register.html')


#Страница входа
@app.route('/success', methods=['GET', 'POST'])
def success():

#Принимаем значения,которые ввел пользователь
    login = request.form.get('login')
    name = request.form.get('name')

    print('##########################################', login, name)

#Подключаемся к БД
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE Login=?", (login,))
    user = cursor.fetchone()
    
#Проверка введенных данных пользователя с данными из БД
    if user is not None:
        if user[0] == name:
            print('Ok!')
            conn.close()
            return redirect(url_for('profile', login=login))
        else:
            print('error')
            error = 'Неверное имя пользователя или пароль'
            conn.close()
            return render_template('success.html', error=error)

    conn.close()
    
#Страница личного кабинета с камерой
@app.route('/profile/<login>', methods=['GET', 'POST'])
def profile(login):
    global soreva, score

#Подключаемся к БД
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE Login=?", (login,))
    user = cursor.fetchone()

#Проверка введенных данных пользователя с данными из БД
    if user is not None:
        oship = ""
        if request.method == 'POST':
            user_data = login

#Принимаем изборажение с камеры и отрпавляем его на сервер
            file = request.files.get('file')
            print(f'Got file: {request.files}')
            file.save('./photo/original.png')

#Обрабатываем его при помощи OpenCV
            img = cv2.imread('photo/original.png')
            detector = cv2.QRCodeDetector()
            data, bbox, temp = detector.detectAndDecode(img)
            a = int(float(data))

            print('Have ',a)

#Проверем нашли ли картошку и если ее до этого не нашли то удаляем его и даем балл пользователю
            if a in soreva:
                soreva.remove(a)
                score += 1

#Записываем балл пользователю если он нашел картошку
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET score = score + ? WHERE login = ?", (1, login))
                conn.commit()
                conn.close()

#Если картошка уже найдена то говорим это пользователю
            else:
                oship = 'Эту картошку уже нашли!'
                    
#Если список собранных картошек оказался пуст, то создаем новый
            if not soreva:
                soreva = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            print("Soreva: ", soreva)

        user_data = {'login': login}

        return render_template('user.html', oship=oship, soreva=soreva, user_data=user_data, login=login)
        
    else:
        error = 'Пользователь не найден'
        return render_template('success.html', error=error)
    



# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    app.run(debug=True)
