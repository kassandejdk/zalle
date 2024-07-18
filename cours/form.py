from django import forms
from .models import Lesson,Commentaire,Reponse,Evaluation, Question, Choice, StudentAnswer


class LessonForm(forms.ModelForm):
    class Meta():
        model=Lesson
        #fields=('__all__') # prendre tous les champs
        fields=('lesson_id','nom','video','fp','pdf','position') 

class ComForm(forms.ModelForm):
    class Meta:
        model=Commentaire
        fields={'corps'}
        labels={'corps':'Commentaires'}
        widgets={
            'corps':forms.Textarea(attrs={
                'class':'form-control',     # une class de bootstrap
                'rows':4,
                'cols':70,
                'placeholder':'Entrez votre commentaire'
            })
        }

class RepForm(forms.ModelForm):
    class Meta:
        model=Reponse
        fields={'corps'}
        labels={'corps':'Reponses'}
        widgets={
            'corps':forms.Textarea(attrs={
                'class':'form-control',     # une class de bootstrap
                'rows':2,
                'cols':10,
                'placeholder':'Repondez'
            })
        }



# forms.py

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['title', 'description']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'correct_answer']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct']

class StudentAnswerForm(forms.ModelForm):
    class Meta:
        model = StudentAnswer
        fields = ['answer_text', 'selected_choice','question']
 
    