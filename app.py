
from flask import Flask, render_template, request, redirect, url_for, session    #pip install Flask
import cv2                                                              #pip install opencv-python
from flask_cors import CORS                                             #pip install Flask-Cors
import sqlite3
import random
import datetime


#Подключение Flask
app = Flask(__name__)
app.secret_key = '123456789'
cors = CORS(app, resources={r"/uploader": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

#Создание БД в SQLite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, login TEXT, score INTEGER, uc INTEGER)")
error = ''

soreva = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
score = 0
uc = 0

math_tasks = [
    {'task': 'Математика 1: Решить уравнение', 'answer': 'уравнение', 'sp': 2},
    {'task': 'Математика 2: Вычислить площадь круга', 'answer': 'площадь', 'sp': 1}
]

grammar_tasks = [
    {'task': 'Грамматика 1: Изучить правила пунктуации', 'answer': 'правила', 'sp': 3},
    {'task': 'Грамматика 2: Ознакомиться с временами глаголов', 'answer': 'времена', 'sp': 2}
]

riddle_tasks = [
    {'task': 'Загадка 1: Что это такое: всегда идет, но никогда не приходит?', 'answer': 'дождь', 'sp': 1},
    {'task': 'Загадка 2: Что можно увидеть с закрытыми глазами?', 'answer': 'сон', 'sp': 2}
]


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

        cursor.execute("INSERT INTO users (login, name, score, uc) VALUES (?, ?, ?, ?)", (login, name, score, uc,))
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
    session['login'] = login
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
    return render_template( 'success.html')
    

    
#Страница личного кабинета с камерой
@app.route('/profile/<login>', methods=['GET', 'POST'])
def profile(login):
    global soreva, score
    # current_time = datetime.datetime.now().time()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE Login=?", (login,))
    user = cursor.fetchone()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT uc FROM users WHERE login = ?", (login,))
    num_tasks = cursor.fetchone()
    num_tasks = list(num_tasks)
    num_tasks = num_tasks[0]

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
                cursor.execute("UPDATE users SET uc = uc + ? WHERE login = ?", (1, login))
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

        return render_template('user.html', oship=oship, soreva=soreva, user_data=user_data, login=login, num_tasks=num_tasks)
            
    else:
        error = 'Пользователь не найден'
        return render_template('success.html', error=error)

    
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    login = session.get('login', None)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT uc FROM users WHERE login = ?", (login,))
    num_tasks = cursor.fetchone()
    num_tasks = list(num_tasks)
    num_tasks = num_tasks[0]
    print(num_tasks)
    if num_tasks <= 0:
        print('OK')
        return render_template('bz_tasks.html', current_user=login)
    elif num_tasks > 0:
        print('No')
        return render_template('tasks.html')
    


@app.route('/math', methods=['GET', 'POST'])
def math():
    global math_tasks
    login = session.get('login', None)
    
    # Подключение к базе данных
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Получение количества доступных задач для пользователя
    cursor.execute("SELECT uc FROM users WHERE login = ?", (login,))
    num_tasks = cursor.fetchone()[0]
    
    if num_tasks <= 0:
        return render_template('bz_tasks.html', current_user=login)
    else:
        random_task = random.choice(math_tasks)
        task = random_task['task']
        sp = random_task['sp']
        print(sp)
    
        if request.method == 'POST':
            # user_answer = request.form['answer'].strip().lower()
            # print(request.form['answer'])
            # print(user_answer, random_task['answer'])

            if request.form['answer'].strip().lower() == random_task['answer']:
                # print(request.form['answer'])
                # print(user_answer, random_task['answer'])
                # Обновляем счет и количество доступных задач у пользователя
                cursor.execute("UPDATE users SET score = score + ?, uc = uc - ? WHERE login = ?", (sp, 1, login))
                conn.commit()
                conn.close()

        return render_template('tasks.html', math_task=task, active_tab='math', current_user=login)

@app.route('/grammar', methods=['GET', 'POST'])
def grammar():
    global grammar_tasks
    login = session.get('login', None)
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT uc FROM users WHERE login = ?", (login,))
    num_tasks = cursor.fetchone()[0]
    conn.close()
    
    if num_tasks <= 0:
        return render_template('bz_tasks.html', current_user=login)
    else:
        random_task = random.choice(grammar_tasks)
        task = random_task['task']
        sp = random_task['sp']
        print(sp)
    
        if request.method == 'POST':
            user_answer = request.form['answer'].strip().lower()
            for task in grammar_tasks:
                if user_answer == task['answer']:
                    conn = sqlite3.connect('database.db')
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET score = score + ?, uc = uc - ? WHERE login = ?", (sp, 1, login))
                    conn.commit()
                    conn.close()
                    break
        task  = random_task['task']
        return render_template('tasks.html', grammar_task=task, active_tab='grammar', current_user=login)

@app.route('/riddles', methods=['GET', 'POST'])
def riddles():
    global riddle_tasks
    login = session.get('login', None)
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT uc FROM users WHERE login = ?", (login,))
    num_tasks = cursor.fetchone()[0]
    conn.close()
    
    if num_tasks <= 0:
        return render_template('bz_tasks.html', current_user=login)
    else:
        random_task = random.choice(riddle_tasks)
        task = random_task['task']
        sp = random_task['sp']
        print(sp)
    
        if request.method == 'POST':
            user_answer = request.form['answer'].strip().lower()
            for task in riddle_tasks:
                if user_answer == task['answer']:
                    conn = sqlite3.connect('database.db')
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET score = score + ?, uc = uc - ? WHERE login = ?", (sp, 1, login))
                    conn.commit()
                    conn.close()
                    break
        task  = random_task['task']
        return render_template('tasks.html', riddle_task=task, active_tab='riddles', current_user=login)


# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    app.run(debug=True)











