
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from student import views

urlpatterns = [
    #管理员登陆
    path('admin/', admin.site.urls),
    #学生登陆
    url(r'^studentLogin/',views.studentLogin),
    #教师登陆
    url(r'^teacherLogin/',views.teacherLogin),
    #默认访问首页
    url(r'^$',views.index),
    url(r'^toIndex/$',views.toIndex),
    url('showGrade',views.showGrade),
    url('queryStudent',views.queryStudent),
    url(r'^startExam/$',views.startExam),
    url(r'^calGrade/$',views.calGrade),
    url(r'^logout/$',views.logOut),
]
