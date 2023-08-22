import datetime

current_time = datetime.datetime.now().time()

if (current_time >= datetime.time(9, 45) and current_time < datetime.time(10, 0)) or \
   (current_time >= datetime.time(10, 45) and current_time < datetime.time(11, 0)) or \
   (current_time >= datetime.time(11, 45) and current_time < datetime.time(12, 0)):
    print("ок")
else:
    print("не ок")
