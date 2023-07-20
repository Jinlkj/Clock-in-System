from django.shortcuts import render
from database_excution import *
from datetime import datetime
def index(request):
    return render(request,'index.html')
def index_v5(request):
    connect_db()
    dic_list = execute_query("select * from Attendance WHERE DAY(Time)=DAY(Now())")
    time_static=[]
    tongji1=[]
    for i in range(1,int(datetime.now().month)+1):
        tongji1.append(query_for_plot1(i))
    tongji2 = []
    for i in range(1, int(datetime.now().month) + 1):
        tongji2.append(query_for_plot2(i))
    for i in range(3):
        time_early=query_for_static_early(i)
        time_late=query_for_static_late(i)
        if time_early and time_late:
            time_static.append((f"{datetime.now().year}.{datetime.now().month}.{datetime.now().day-i}",f"{time_early.hour}:{time_early.minute}:{time_early.second}",f"{time_late.hour}:{time_late.minute}:{time_late.second}"))
        else:
            time_static.append((f"{datetime.now().year}.{datetime.now().month}.{datetime.now().day-i}",time_early,time_late))
    sum_num_month=execute_query_num_current_month()
    sum_day=execute_query_num_current_DAY()
    sum_day_work=execute_query_num_current_DAY_work()
    sum_day_work_off=sum_day-sum_day_work
    sum_people=execute_query_num()
    date=f"{datetime.now().year}.{datetime.now().month}"
    sum_all=execute_query_num_all()
    try:
        percent1=round(sum_day_work/sum_people*100,2)
        percent2=round(sum_day_work_off/sum_people*100,2)
        percent_work = round(sum_day_work / sum_people * 100,2)
        percent_off = round(sum_day_work_off / sum_people * 100,2)
    except:
        percent1=0
        percent2=0
        percent_work=0
        percent_off=0
    return render(request,
                  'index_v5.html',
                  {"checkin_dict":dic_list,
                   "sum":sum_num_month,
                   "sum_all":sum_all,
                   "sum_day":sum_day,
                   'sum_day_work':sum_day_work,
                   'sum_day_work_off':sum_day_work_off,
                   "percent_work":percent_work,
                   'percent_off':percent_off,
                   "sum_people":sum_people,
                   "date":date,
                   "behavior_list":time_static,
                   "tongji1":tongji1,
                   "tongji2":tongji2,
                   "percent1":percent1,
                   "percenr2":percent2
                   }
                  )