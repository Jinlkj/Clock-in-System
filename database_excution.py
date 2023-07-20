import datetime
import pytz
import pymysql
db = None  # 全局变量用于保存数据库连接
def connect_db():
    global db
    db = pymysql.connect(
        host='localhost',    # 数据库主机地址
        user='root',         # 数据库用户名
        password='132900124xjxj',  # 数据库密码
        database='考勤系统'    # 数据库名称
    )
def query_for_plot1(Month):
    sql=f"SELECT COUNT(*) FROM ATTENDANCE WHERE MONTH(Time)={Month} and Type='work'"
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()  # 获取单行结果
    if result:
        row_count = result[0]  # 提取结果中的数字
        return row_count
    else:
        return 0
def query_for_plot2(Month):
    sql=f"SELECT COUNT(*) FROM ATTENDANCE WHERE MONTH(Time)={Month} and Type='work_off'"
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()  # 获取单行结果
    if result:
        row_count = result[0]  # 提取结果中的数字
        return row_count
    else:
        return 0
def query_for_static_early(date):
    sql=f"SELECT MIN(Time) AS EarliestTime FROM Attendance WHERE DAY(Time) = DAY(NOW())-{date} AND Type = 'work';"
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()  # 获取单行结果
    if result:
        row_count = result[0]  # 提取结果中的数字
        return row_count
    else:
        return None
def query_for_static_late(date):
    sql=f"SELECT MAX(Time) AS LatestTime FROM Attendance WHERE DAY(Time) = DAY(NOW())-{date} AND Type = 'work_off';"
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()  # 获取单行结果
    if result:
        row_count = result[0]  # 提取结果中的数字
        return row_count
    else:
        return None

def execute_query_num_current_month():
    sql = """SELECT count(*) as sum_num FROM Attendance WHERE MONTH(Attendance.Time) = MONTH(NOW());"""
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()  # 获取单行结果

    if result:
        row_count = result[0]  # 提取结果中的数字
        return row_count
    else:
        return 0
def execute_query_num_current_DAY():
    sql = "SELECT count(*) as sum_num FROM Attendance WHERE DAY(Attendance.Time) = DAY(NOW());"
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()  # 获取单行结果
    if result:
        row_count = result[0]  # 提取结果中的数字
        return row_count
    else:
        return None
def execute_query_num_current_DAY_work():
    sql = """SELECT count(*) as sum_num FROM Attendance WHERE DAY(Attendance.Time) = DAY(NOW()) and Attendance.type='work';"""
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()  # 获取单行结果

    if result:
        row_count = result[0]  # 提取结果中的数字
        return row_count
    else:
        return None
def execute_query_num():
    sql = """SELECT count(*) as sum_num FROM People;"""
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()  # 获取单行结果

    if result:
        row_count = result[0]  # 提取结果中的数字
        return row_count
    else:
        return None
def execute_query_num_all():
    sql = """SELECT count(*) as sum_num FROM Attendance;"""
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()  # 获取单行结果

    if result:
        row_count = result[0]  # 提取结果中的数字
        return row_count
    else:
        return 0
def execute_query(sql):
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()  # 获取所有记录
    datas=[]
    for row in results:
        name,time,type=row
        dic={"name":name,"time":time,"type":type}
        datas.append(dic)
    cursor.close()  # 关闭游标
    return datas
def insert_person(name):
    sql = "INSERT INTO People (Name) VALUES (%s)"
    cursor = db.cursor()
    cursor.execute(sql, name)
    db.commit()  # 提交事务
    cursor.close()  # 关闭游标
def delete_table(table):
    sql = f"DELETE FROM {table};"
    cursor = db.cursor()
    cursor.execute(sql)
    try:
        cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1;")
    except:
        print("没有自增长列")
    db.commit()  # 提交事务
    cursor.close()  # 关闭游标
def add_attendance_info(name,type):
    beijing_time = get_beijing_time()  # Assuming get_beijing_time() is defined elsewhere
    sql = f"INSERT INTO Attendance (Name, Time,Type) VALUES ('{name}', '{beijing_time}','{type}')"
    print(sql)
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()  # Commit the transaction
    cursor.close()  # Close the cursor

def get_beijing_time():
    # 获取当前的UTC时间
    utc_now = datetime.datetime.utcnow()

    # 创建时区对象
    beijing_tz = pytz.timezone('Asia/Shanghai')

    # 将UTC时间转换为北京时间
    beijing_now = utc_now.replace(tzinfo=pytz.utc).astimezone(beijing_tz)

    return beijing_now
