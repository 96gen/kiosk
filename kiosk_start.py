# coding=utf-8
import sqlite3, os, uuid, hashlib
from flask_uploads import UploadSet, IMAGES, configure_uploads, ALL
from flask import Flask,render_template,request,jsonify, redirect, url_for
from datetime import datetime

DATABASE = 'kiosk.db'
MENU_DATABASE = 'menu.db'
app = Flask(__name__)
#上傳圖片的設定
app.config['UPLOADED_PHOTO_DEST'] = os.path.dirname(os.path.abspath(__file__)) + '/static/'
app.config['UPLOADED_PHOTO_ALLOW'] = IMAGES
photos = UploadSet('PHOTO')
configure_uploads(app, photos)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/menu')
def menu():
    try:
        #uListStr用來存放要顯示在網頁上的內容
        uListStr = ""
        sqliteDB = sqlite3.connect(MENU_DATABASE)
        cur = sqliteDB.execute("select KIND from MENU order by KIND asc")
        pre = ""
        i = 0
        #產生側邊欄
        for row in cur.fetchall():
            #如果有新的種類出現，在側邊欄加上它
            if(pre != row):
                uListStr += "<a href=\"#scroll" + str(i) + '\" class="list-group-item list-group-item-action bg-light">' + str(row)[2:len(row)-4] + '</a>'
                i += 1
            pre = row
        uListStr += '</div></div><div id="page-content-wrapper">'
        #從資料庫抓取菜單上要顯示的內容
        cur = sqliteDB.execute("select ID,MEAL_NAME,PRICE,KIND from MENU order by KIND asc")
        pre = ""
        i = 0
        uListStr += "點餐請按圖片，點幾個就按幾次"
        #菜單顯示
        for row in cur.fetchall():
            #如果有新的種類出現，在菜單上標示出來
            if(pre != row[3]):
                if(i != 0):
                    uListStr += "</div>"
                uListStr += "<div id=\"scroll" + str(i) + "\">" + str(row[3]) + '</div><br />'
                uListStr += "<div class=\"row\">"
                i += 1
            pre = row[3]
            #顯示餐點名稱和價格
            uListStr += "<div class=\"col-md-4\" id=\" "+ str(row[0]) +"\"><img src=\"/static/" + str(row[0]) + ".jpg\" style=\"height: 90%;width: 90%;\"><br />"
            uListStr += str(row[1])
            uListStr += "<br />價格:" + str(row[2]) + "<br /></div>"
            
        uListStr += "</div></div>"
        sqliteDB.close()
    except:
        return "error"
    return render_template('form.html') + uListStr + render_template("menu.html") + render_template("home.html") + "</div></div></body></html>"
@app.route('/bill')
def bill():
    return render_template('bill.html') + render_template("home.html")
@app.route('/kitchen')
def getUsers():
    try:
        uListStr = ""
        sqliteDB = sqlite3.connect(DATABASE)
        #從資料庫取得還沒出菜的餐點
        cur = sqliteDB.execute("select TABLE_NUMBER,MEAL,MEAL_SERVE,ID from SUMMARY where MEAL_SERVE = 0")
        for row in cur.fetchall():
            uListStr += "<div class=\"divTableRow\">"
            i = 0
            for cell in row:
                #因為只需要顯示桌號、餐點名稱、出菜的時間共3個
                if(i == 3):
                    i = 0
                    break
                else:
                    i += 1
                uListStr += "<div class=\"divTableCell\">"
                uListStr += str(cell)
                uListStr += "</div>"
            #用ID作為修改資料庫MEAL_SERVE的依據
            uListStr += "<button id=\""+str(row[3])+"\" class=\"done\">Done</button>"
            uListStr += "</div>" 
        sqliteDB.close()
        return render_template("home.html") + render_template('kitchen.html') + uListStr + "</div></div>"
    except Exception as err:
        return err
#處理MEAL_SERVE並將結果存到資料庫
@app.route('/background_process_test', methods=['POST'])
def background_process_test():
    try:
        data = request.get_json(force=True)
        data_id =data['id']
        print(data_id)
        sqliteDB = sqlite3.connect(DATABASE)
        sqliteDB.execute("update summary set MEAL_SERVE = ? where id = ?",(str(datetime.utcnow()),data_id))
        sqliteDB.commit()
        sqliteDB.close()
    except Exception as err:
        print(err)
        return "" 
    return ""
#根據輸入的桌號，顯示該桌的帳單
@app.route('/bill_show', methods=['POST'])
def bill_show():
    try:
        total = 0
        uListStr = ""
        data = request.get_json(force=True)
        data_id =data['table_number']
        sqliteDB = sqlite3.connect(DATABASE)
        cur = sqliteDB.execute("select MEAL,PRICE,DISCOUNT from SUMMARY where TABLE_NUMBER = ? and BILL_CHECK = ?",(data_id,str(0)))
        #顯示該桌點的餐點、價格及折扣
        for row in cur.fetchall():
            uListStr += "<div class=\"divTableRow\">"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(row[0])
            uListStr += "</div>"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(row[1]-row[2])
            total += row[1]-row[2]
            uListStr += "</div>"
            uListStr += "</div>"
        uListStr += "總共:" + str(total) + "元"
        total = 0
        sqliteDB.close()
        return jsonify(uListStr)
    except:
        print("error")
        return "error"
#結帳把結果存到資料庫
@app.route('/paid', methods=['POST'])
def paid():
    try:
        data = request.get_json(force=True)
        data_id =data['table_number']
        sqliteDB = sqlite3.connect(DATABASE)
        sqliteDB.execute("update summary set BILL_CHECK = ? where TABLE_NUMBER = ?",(str(datetime.utcnow()),data_id))
        sqliteDB.commit()
        sqliteDB.close()
        return "付款成功" + render_template('home.html')
    except:
        print("error")
        return "error" + render_template('home.html')
@app.route('/order', methods=['POST'])
def order():
    try:
        uListStr = "<link href=\"/static/table.css\" rel=\"stylesheet\" type=\"text/css\" /><div class=\"divTable\"><div class=\"divTableBody\"><div class=\"divTableRow\"><div class=\"divTableCell\">菜名</div><div class=\"divTableCell\">價格</div><div class=\"divTableCell\">人數</div><div class=\"divTableCell\">桌號</div></div>"        
        #從menu的form獲得資料
        data_id = request.form['order_list']
        PEOPLE_NUMBER = request.form['people_number']
        TABLE_NUMBER = request.form['table_number']
        BUTTON_TYPE = request.form['order']
        #判斷點的是點餐完畢還是預覽點餐結果
        if(BUTTON_TYPE == 'preview'):
            return preview_order()
        #因為點餐那邊用;分隔餐點，;前面就是菜的ID
        order_list = data_id.split(';')
        sqliteDB = sqlite3.connect(DATABASE)
        sqlite_menuDB = sqlite3.connect(MENU_DATABASE)
        sqliteDB_c = sqliteDB.cursor()
        sqlite_menuDB_c = sqlite_menuDB.cursor()
        total = 0
        for i in range(0,len(order_list) - 1):
            sqliteDB_cursor = sqliteDB_c.execute("select id from summary order by id desc limit 1")
            ID = sqliteDB_cursor.fetchone()
            sqlite_menuDB_cursor = sqlite_menuDB_c.execute("select MEAL_NAME,PRICE from menu where id = ?",(order_list[i],))
            #如果sqliteDB沒有任何紀錄，這次點菜就是第一筆
            if(ID is None):
                ID = 1
            #如果有紀錄，就是第 最後一筆加一 筆
            else:
                ID = ID[0] + 1
            TIME = str(datetime.utcnow())
            #取得餐點名稱和價格
            for row in sqlite_menuDB_cursor:
                MEAL = row[0]
                PRICE = row[1]
            DISCOUNT = 0
            #顯示點的餐點、折扣後的價格、用餐人數和桌號
            uListStr += "<div class=\"divTableRow\">"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(MEAL)
            uListStr += "</div>"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(PRICE-DISCOUNT)
            total += PRICE-DISCOUNT
            uListStr += "</div>"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(PEOPLE_NUMBER)
            uListStr += "</div>"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(TABLE_NUMBER)
            uListStr += "</div>"
            uListStr += "</div>"
            #將點餐資訊存到資料庫
            sqliteDB.execute("INSERT INTO SUMMARY (ID,TIME,MEAL,PRICE,DISCOUNT,PEOPLE_NUMBER,TABLE_NUMBER,BILL_CHECK,MEAL_SERVE) \
                        VALUES (?,?,?,?,?,?,?,'0','0')",(ID, TIME, MEAL, PRICE, DISCOUNT, PEOPLE_NUMBER, TABLE_NUMBER,))
            sqliteDB.commit()
        sqlite_menuDB.close()
        sqliteDB.close()
        return uListStr + "<br />總價:" + str(total) + render_template('home.html') + "</div></div>"
    except Exception as err:
        print(err)
        return "error"
@app.route('/preview_order', methods=['POST'])
def preview_order():
    try:
        uListStr = "<link href=\"/static/table.css\" rel=\"stylesheet\" type=\"text/css\" /><div class=\"divTable\"><div class=\"divTableBody\"><div class=\"divTableRow\"><div class=\"divTableCell\">菜名</div><div class=\"divTableCell\">價格</div><div class=\"divTableCell\">人數</div><div class=\"divTableCell\">桌號</div></div>"        
        #從menu的form獲得資料
        data_id = request.form['order_list']
        PEOPLE_NUMBER = request.form['people_number']
        TABLE_NUMBER = request.form['table_number']
        #因為點餐那邊用;分隔餐點，;前面就是菜的ID
        order_list = data_id.split(';')
        sqlite_menuDB = sqlite3.connect(MENU_DATABASE)
        sqlite_menuDB_c = sqlite_menuDB.cursor()
        total = 0
        for i in range(0,len(order_list) - 1):
            sqlite_menuDB_cursor = sqlite_menuDB_c.execute("select MEAL_NAME,PRICE from menu where id = ?",(order_list[i],))
            #取得餐點名稱和價格
            for row in sqlite_menuDB_cursor:
                MEAL = row[0]
                PRICE = row[1]
            DISCOUNT = 0
            #顯示點的餐點、折扣後的價格、用餐人數和桌號
            uListStr += "<div class=\"divTableRow\">"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(MEAL)
            uListStr += "</div>"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(PRICE-DISCOUNT)
            total += PRICE-DISCOUNT
            uListStr += "</div>"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(PEOPLE_NUMBER)
            uListStr += "</div>"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(TABLE_NUMBER)
            uListStr += "</div>"
            uListStr += "</div>"
        sqlite_menuDB.close()
        return uListStr + "<br />預覽總價:" + str(total) +"</div></div><button onclick=\"history.back();\">回上一頁</button>"
    except Exception as err:
        print(err)
        return "error"
#新增餐點資訊和圖片
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        try:
            #從upload的form取得資料
            meal_name = str(request.form['meal_name'])
            price = int(request.form['price'])
            kind = str(request.form['kind'])
            
            conn = sqlite3.connect(MENU_DATABASE)
            c = conn.cursor()
            cursor = c.execute("select id from menu order by id desc limit 1")
            ID = cursor.fetchone()
            if(ID is None):
                ID = 1
            else:
                ID = ID[0] + 1
            #將餐點圖片存到設定好的資料夾
            photos.save(request.files['photo'], name=str(ID)+".jpg")
            #將餐點資料存到負責餐點的資料庫
            c.execute("INSERT INTO MENU (ID,MEAL_NAME,PRICE,KIND) \
                VALUES (?,?,?,?)",(ID, meal_name, price, kind))
            conn.commit()
            return render_template('upload.html') + render_template('home.html') + '上傳成功'
        except:
            return render_template('upload.html') + render_template('home.html') + '失敗'
    return render_template('upload.html') + render_template('home.html')
#顯示所有的訂單，並且可以刪除訂單
@app.route('/manage')
def manage():
    try:
        uListStr = ""
        sqliteDB = sqlite3.connect(DATABASE)
        cur = sqliteDB.execute("select * from SUMMARY")
        for row in cur.fetchall():
            uListStr += "<div class=\"divTableRow\">"
            for cell in row:
                uListStr += "<div class=\"divTableCell\">"
                uListStr += str(cell)
                uListStr += "</div>"
            uListStr += "<button id=\""+str(row[0])+"\" class=\"delete\">Delete</button>"
            uListStr += "</div>" 
        sqliteDB.close()
        return render_template('manage.html') + uListStr + render_template('home.html') + "</div></div>"
    except Exception as err:
        return err
#從資料庫刪除訂單
@app.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.get_json(force=True)
        data_id =data['id']
        sqliteDB = sqlite3.connect(DATABASE)
        sqliteDB.execute("delete from summary where id = ?",(data_id))
        sqliteDB.commit()
        sqliteDB.close()
    except:
        return "error" 
    return ""
#顯示每天的營業額、折扣金額、來客數和客單價
@app.route('/summary') 
def summary():
    try:
        dates = []
        uListStr = ""
        sqliteDB = sqlite3.connect(DATABASE)
        cur = sqliteDB.execute("select TIME from SUMMARY order by time desc")
        for row in cur.fetchall():
            #因為0:10是年月日，10之後是時間所以不需要
            if(row[0][0:10] not in dates):
                dates.append(row[0][0:10])
        total_profit = 0
        total_people = 0
        total_discount = 0
        while(len(dates) > 0):
            date = str(dates.pop())
            cur = sqliteDB.execute("select PRICE,DISCOUNT,PEOPLE_NUMBER from SUMMARY WHERE time LIKE ?",(date+'%',))
            daily_revenue = 0
            daily_discount = 0
            daily_people = 0
            for row in cur.fetchall():
                daily_revenue += row[0]
                daily_discount += row[1]
                daily_people += row[2]
            total_profit += (daily_revenue - daily_discount)
            total_people += daily_people
            total_discount += daily_discount
            #顯示營業額、折扣金額、來客數和客單價
            uListStr += "<div class=\"divTableRow\">"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += date
            uListStr += "</div>"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(daily_revenue)
            uListStr += "</div>"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(daily_discount)
            uListStr += "</div>"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(daily_people)
            uListStr += "</div>"
            uListStr += "<div class=\"divTableCell\">"
            uListStr += str(int((daily_revenue - daily_discount)/daily_people))
            uListStr += "</div>"
            uListStr += "</div>"
        sqliteDB.close()
        return  render_template('summary.html') + render_template('home.html') + uListStr + "</div></div>"
    except Exception as err:
        return err


if(__name__ == "__main__"):
    app.run(host='0.0.0.0',debug=True)
