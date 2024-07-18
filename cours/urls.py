from django.urls import path
from cours.views import *
app_name="cours"

urlpatterns=[
    path('',NiveauListView.as_view(),name="niveaulist"),
    path('evaluations/', evaluation_list, name='evaluation_list'),

    path('evaluations/<int:evaluation_id>/', evaluation_detail, name='evaluation_detail'),

    
 
    path('<slug:slug>',MatiereListView.as_view(),name="matierelist"),
    path('<str:niveau>/<slug:slug>/',LessonListView.as_view(),name="lessonlist"),
    path('<str:niveau>/<str:slug>/create/',LessonCreateView.as_view(),name="lessoncreate"),
    path('<str:niveau>/<str:matiere>/<slug:slug>/',LessonListViewDetail.as_view(),name="lessonlistdetail"),
    path('<str:niveau>/<str:matiere>/<slug:slug>/update/',LessonUpdateView.as_view(),name="lessonupdate"),
    path('<str:niveau>/<str:matiere>/<slug:slug>/delete/',LessonDeleteView.as_view(),name="lessondelete"),
   
    path('marquer-complete/<slug:niveau>/<slug:matiere>/<slug:slug>/',marquer_comme_complete, name='mark_completed'),
    path('progression/', afficher_progression, name='afficher_progression'),
   
    path('lesson/<int:lesson_id>/download/<str:file_type>/', download_file, name='download_file'),

    
   
    

]