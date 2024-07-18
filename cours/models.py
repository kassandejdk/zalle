from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

from django.urls import reverse

# Table des niveaux
class Niveaux(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


# Table des matières
class Matiere(models.Model):
    matiere_id = models.CharField(unique=True, max_length=50)
    nom = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)
    niveau = models.ForeignKey(Niveaux, on_delete=models.CASCADE, related_name='matiere')
    image = models.ImageField(upload_to='matiere', blank=True)
    description = models.TextField(max_length=500)

    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

# Table des leçons
class Lesson(models.Model):
    lesson_id = models.CharField(unique=True, max_length=50)
    niveau = models.ForeignKey(Niveaux, on_delete=models.CASCADE)
    creer_par = models.ForeignKey(User, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='lesson')
    nom = models.CharField(max_length=100)
    position = models.PositiveSmallIntegerField(verbose_name='chapitre no')
    video = models.FileField(upload_to='Video', null=True, blank=True, verbose_name='Cours en video')
    fp = models.FileField(upload_to='FP', null=True, blank=True, verbose_name='Fiche de présentation')
    pdf = models.FileField(upload_to='PDF', null=True, blank=True, verbose_name='Cours en pdf')
    slug = models.SlugField(blank=True, null=True)
    complet = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)



    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("cours:lessonlist", kwargs={"slug": self.matiere.slug, "niveau": self.niveau.slug})

# Table des commentaires
class Commentaire(models.Model):
    nom_comm = models.CharField(max_length=100, blank=True)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    corps = models.TextField(max_length=500)
    date_ajou = models.DateTimeField(auto_now_add=True)
    nom_lesson = models.ForeignKey(Lesson, null=True, on_delete=models.CASCADE, related_name='comments')

    def save(self, *args, **kwargs):
        self.nom_comm = slugify(f"commenté par {self.auteur} à {self.date_ajou}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom_comm
    
    class Meta:
        ordering = ['-date_ajou']

# Table des réponses aux commentaires
class Reponse(models.Model):
    nom_comm = models.ForeignKey(Commentaire, on_delete=models.CASCADE, related_name='reponses')
    corps = models.TextField(max_length=500)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_ajou = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réponse à {self.nom_comm.nom_comm}"

# Table des évaluations
class Evaluation(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='evaluations')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_evaluations')

    def __str__(self):
        return self.title

# Table des questions
class Question(models.Model):
    TEXT = 'TEXT'
    MULTIPLE_CHOICE = 'MC'
    CALCULATION = 'CALC'

    QUESTION_TYPES = [
        (TEXT, 'Question textuelle'),
        (MULTIPLE_CHOICE, 'QCM'),
        (CALCULATION, 'Calcul'),
    ]

    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=5, choices=QUESTION_TYPES)
    correct_answer = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.question_text

# Table des choix pour les QCM
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text

# Table des réponses des élèves
class StudentAnswer(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    answer_text = models.CharField(max_length=255, blank=True, null=True)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, blank=True, null=True, related_name='student_answers')

    def __str__(self):
        return f"Réponse de {self.student} à {self.question}"

# Profil utilisateur pour ajouter un champ indiquant si l'utilisateur est un enseignant
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class UserProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_lessons = models.IntegerField(default=0)
    lessons_completed = models.IntegerField(default=0)

    def update_progress(self):
        self.total_lessons = Lesson.objects.count()
        self.lessons_completed = self.user.lesson_set.filter(complet=True).count()
        self.save()

    def __str__(self):
        return f"Progression de {self.user.username}"


