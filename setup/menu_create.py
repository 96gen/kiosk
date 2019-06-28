import sqlite3
conn = sqlite3.connect("menu.db")
c = conn.cursor()
c.execute('''CREATE TABLE MENU
          (ID           INT        PRIMARY KEY NOT NULL,
          MEAL_NAME     CHAR(26)               NOT NULL,
          PRICE         INT                    NOT NULL,
          KIND          CHAR(10)               NOT NULL);''')
conn.commit()
conn.close()