from django.shortcuts import render,redirect
from student import models
from django.http import HttpResponse
from django.contrib.auth import logout
# Create your views here.
def index(request):
    return render(request,'index.html')

def toIndex(request):
    return render(request,'index.html')


# 学生登陆 视图函数
def studentLogin(request):
    if request.method=='POST':
        # 获取表单信息
        stuId=request.POST.get('id')
        password=request.POST.get('password')
        print("id",stuId,"password",password)
        # 通过学号获取该学生实体
        student=models.Student.objects.get(id=stuId)
        print(student)
        if password==student.password:  #登录成功
            #查询考试信息
            paper=models.Paper.objects.filter(major=student.major)
            #查询成绩信息
            grade=models.Grade.objects.filter(sid=student.id)
            # 渲染index模板
            return render(request,'index.html',{'student':student,'paper':paper,'grade':grade})

        else:return render(request,'index.html',{'message':'密码不正确'})

# 教师登陆 视图函数
def teacherLogin(request):

    if request.method == 'POST':
        teaId = request.POST.get('id')
        password = request.POST.get('password')
        # print("id", teaId, "password", password)

        teacher=models.Teacher.objects.get(id=teaId)
        print(teacher)
        if password == teacher.password:  # 登录成功
            # 实现成绩统计功能
            #在试卷表 paper 找到该老师发布的试题
            paper=models.Paper.objects.filter(tid=teacher.id)

            data1=models.Grade.objects.filter(subject='软件工程',grade__lt=60).count()
            data2=models.Grade.objects.filter(subject='软件工程',grade__gte=60,grade__lt=70).count()
            data3 = models.Grade.objects.filter(subject='软件工程', grade__gte=70, grade__lt=80).count()
            data4 = models.Grade.objects.filter(subject='软件工程', grade__gte=80, grade__lt=90).count()
            data5 = models.Grade.objects.filter(subject='软件工程', grade__gte=90).count()

            data6 = models.Grade.objects.filter(subject='数据库原理', grade__lt=60).count()
            data7= models.Grade.objects.filter(subject='数据库原理', grade__gte=60, grade__lt=70).count()
            data8= models.Grade.objects.filter(subject='数据库原理', grade__gte=70, grade__lt=80).count()
            data9 = models.Grade.objects.filter(subject='数据库原理', grade__gte=80, grade__lt=90).count()
            data10= models.Grade.objects.filter(subject='数据库原理', grade__gte=90).count()


            data_1={'data1':data1,'data2':data2,'data3':data3,'data4':data4,'data5':data5}
            data_2 = {'data6': data6, 'data7': data7, 'data8': data8, 'data9': data9, 'data10': data10}


            print("数量：",data2)
            return render(request, 'teacher.html', {'teacher': teacher, 'paper':paper,'data_1':data_1,'data_2':data_2})

        else:
            return render(request, 'index.html', {'message': '密码不正确'})

#教师查看成绩
def showGrade(request):
    subject1=request.GET.get('subject')
    grade=models.Grade.objects.filter(subject=subject1)

    data1 = models.Grade.objects.filter(subject=subject1, grade__lt=60).count()
    data2 = models.Grade.objects.filter(subject=subject1, grade__gte=60, grade__lt=70).count()
    data3 = models.Grade.objects.filter(subject=subject1, grade__gte=70, grade__lt=80).count()
    data4 = models.Grade.objects.filter(subject=subject1, grade__gte=80, grade__lt=90).count()
    data5 = models.Grade.objects.filter(subject=subject1, grade__gte=90).count()

    data = {'data1': data1, 'data2': data2, 'data3': data3, 'data4': data4, 'data5': data5}

    return render(request,'showGrade.html',{'grade':grade,'data':data,'subject':subject1})

#教师按条件查询学生
def queryStudent(request):
    #获取教师查询的条件值
    sid=request.GET.get('id')
    sex=request.GET.get('sex')
    subject=request.GET.get('subject')

    #获取老师的id
    tid=request.GET.get('tid')
    teacher = models.Teacher.objects.get(id=tid)
    paper = models.Paper.objects.filter(tid=teacher.id)

    # print(sid,sex,subject)
    from django.db import connection,transaction
    cursor=connection.cursor()
    sql="select * from grade,student where student.id=grade.sid_id " \
        "and student.id like %s and grade.subject like %s and student.sex like %s and '1'='1'"
    val=('%'+sid+'%','%'+subject+'%','%'+sex+'%')
    cursor.execute(sql,val)
    result=dictfetchall(cursor)


    # print(result)
    return render(request,'teacher.html',{'teacher':teacher,'result':result,'paper':paper})

#将使用原生sql语句查到的结果由tuple类型转换为dictionary(字典)类型
def dictfetchall(cursor):
    "将游标返回的结果保存到一个字典对象中"
    desc = cursor.description
    return [
    dict(zip([col[0] for col in desc], row))
    for row in cursor.fetchall()
    ]


#学生考试 的视图函数
def startExam(request):
    sid = request.GET.get('sid')
    subject1=request.GET.get('subject')

    student=models.Student.objects.get(id=sid)
    paper=models.Paper.objects.filter(subject=subject1)
    # print('学号',sid,'考试科目',subject1)
    return render(request,'exam.html',{'student':student,'paper':paper,'subject':subject1})


#计算由exam.html模版传过来的数据计算成绩
def calGrade(request):

    if request.method=='POST':
        # 得到学号和科目
        sid=request.POST.get('sid')
        subject1 = request.POST.get('subject')

        # 重新生成Student实例，Paper实例，Grade实例，名字和index中for的一致，可重复渲染
        student= models.Student.objects.get(id=sid)
        paper = models.Paper.objects.filter(major=student.major)
        grade = models.Grade.objects.filter(sid=student.id)

        # 计算该门考试的学生成绩
        question= models.Paper.objects.filter(subject=subject1).values("pid").values('pid__id','pid__answer','pid__score')

        mygrade=0#初始化一个成绩为0
        for p in question:
            qId=str(p['pid__id'])#int 转 string,通过pid找到题号
            myans=request.POST.get(qId)#通过 qid 得到学生关于该题的作答
            # print(myans)
            okans=p['pid__answer']#得到正确答案
            # print(okans)
            if myans==okans:#判断学生作答与正确答案是否一致
                mygrade+=p['pid__score']#若一致,得到该题的分数,累加mygrade变量

        #向Grade表中插入数据
        models.Grade.objects.create(sid_id=sid,subject=subject1,grade=mygrade)
        # print(mygrade)
        # 重新渲染index.html模板
        return render(request,'index.html',{'student':student,'paper':paper,'grade':grade})

# 教师退出
def logOut(request):
    return redirect('/toIndex/')







