import sqlite3
from datetime import datetime
conn = sqlite3.connect("menu.db")
c = conn.cursor()
cursor = c.execute("select id from menu order by id desc limit 1")
ID = cursor.fetchone()
if(ID is None):
    ID = 1
else:
    ID = ID[0] + 1
MEAL_NAME = "三倍安格斯漢堡"
PRICE = 100
KIND = "漢堡"

#c.execute("INSERT INTO MENU (ID,MEAL_NAME,PRICE,KIND) \
      #VALUES (?,?,?,?)",(ID, MEAL_NAME, PRICE, KIND))
#conn.commit()

cursor = c.execute("SELECT ID,MEAL_NAME,PRICE,KIND from MENU order by KIND asc")
for row in cursor:
   print(row)

conn.close()