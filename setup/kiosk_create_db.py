import sqlite3
conn = sqlite3.connect("kiosk.db")
c = conn.cursor()
c.execute('''CREATE TABLE SUMMARY
          (ID           INT        PRIMARY KEY NOT NULL,
          TIME          CHAR(26)               NOT NULL,
          MEAL          CHAR(50)               NOT NULL,
          PRICE         INT                    NOT NULL,
          DISCOUNT      INT                    NOT NULL,
          PEOPLE_NUMBER INT                    NOT NULL,
          TABLE_NUMBER  INT                    NOT NULL,
          BILL_CHECK    CHAR(26)               NOT NULL,
          MEAL_SERVE    CHAR(26)               NOT NULL);''')
conn.commit()
conn.close()