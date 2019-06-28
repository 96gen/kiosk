import sqlite3
from datetime import datetime
conn = sqlite3.connect("kiosk.db")
c = conn.cursor()
cursor = c.execute("select id from summary order by id desc limit 1")
ID = cursor.fetchone()
if(ID is None):
    ID = 1
else:
    ID = ID[0] + 1
TIME = str(datetime.utcnow())
MEAL = "1"
PRICE = 250
DISCOUNT = 0
PEOPLE_NUMBER = 1
TABLE_NUMBER = 1

c.execute("INSERT INTO SUMMARY (ID,TIME,MEAL,PRICE,DISCOUNT,PEOPLE_NUMBER,TABLE_NUMBER,BILL_CHECK,MEAL_SERVE) \
      VALUES (?,?,?,?,?,?,?,'0','0')",(ID, TIME, MEAL, PRICE, DISCOUNT, PEOPLE_NUMBER, TABLE_NUMBER))
conn.commit()


cursor = c.execute("select * from SUMMARY WHERE time LIKE ?",('2019-04-19%',))
for row in cursor:
   print(row)
conn.close()