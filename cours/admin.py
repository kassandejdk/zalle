from django.contrib import admin
from .models import Niveaux, Matiere, Lesson, Commentaire, Reponse, Evaluation, Question,Choice, StudentAnswer, UserProfile

# Register your models here.
class AdminMatiere(admin.ModelAdmin):
    list_display = ('nom', 'niveau', 'description')
    prepopulated_fields = {"slug": ("nom",)}

class AdminLesson(admin.ModelAdmin):
    list_display = ('nom', 'position', 'matiere', 'niveau', 'creer_par')
    prepopulated_fields = {"slug": ("nom",)}

class AdminEvaluation(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at', 'lesson', 'created_by')

class AdminQuestion(admin.ModelAdmin):
    list_display = ('question_text', 'question_type', 'evaluation')
    list_filter = ('question_type',)

class AdminChoice(admin.ModelAdmin):
    list_display = ('question', 'choice_text', 'is_correct')
    list_filter = ('is_correct',)

class AdminStudentAnswer(admin.ModelAdmin):
    list_display = ('student', 'question', 'answer_text', 'selected_choice')
    list_filter = ('question', 'student')

class AdminUserProfile(admin.ModelAdmin):
    list_display = ('user', 'is_teacher')

admin.site.register(Niveaux)
admin.site.register(Matiere, AdminMatiere)
admin.site.register(Lesson, AdminLesson)
admin.site.register(Commentaire)
admin.site.register(Reponse)
admin.site.register(Evaluation, AdminEvaluation)
admin.site.register(Question, AdminQuestion)
admin.site.register(Choice, AdminChoice)
admin.site.register(StudentAnswer, AdminStudentAnswer)
admin.site.register(UserProfile, AdminUserProfile)
