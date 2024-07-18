from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.views.generic import DetailView,ListView,DeleteView,UpdateView,CreateView,FormView
from .form import LessonForm,ComForm,RepForm,EvaluationForm, QuestionForm, ChoiceForm, StudentAnswerForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from utilisateurs.models import Profile




# Create your views here.

class NiveauListView(LoginRequiredMixin, ListView):
    context_object_name = 'niveaux'
    model = Niveaux
    template_name = 'cours/niveaulist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            user_profile = Profile.objects.get(user=self.request.user)
            context['user_niveau'] = user_profile.level
        except Profile.DoesNotExist:
            context['user_niveau'] = None
        return context
class MatiereListView(DetailView):
    model = Niveaux
    template_name = 'cours/matierelist.html'
    context_object_name = 'niveau'

    
    

class LessonListView(DetailView): 
    context_object_name='matieres' 
    model=Matiere
    template_name='cours/lessonlist.html'

class LessonListViewDetail(DetailView, FormView):
    context_object_name = 'lesson'
    model = Lesson
    template_name = 'cours/lessonlistdetail.html'
    form_class = ComForm              
    second_form_class = RepForm

    def get_object(self, queryset=None):
        lesson = super().get_object(queryset)
        lesson.view_count += 1
        lesson.save()
        return lesson

    def get_context_data(self, **kwargs):
        context = super(LessonListViewDetail, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class()
        if 'form2' not in context:
            context['form2'] = self.second_form_class()
        return context

    def form_valid(self, form):
        self.object = self.get_object()
        fd = form.save(commit=False) # on envoi pas encore
        fd.auteur = self.request.user
        fd.nom_lesson_id = self.object.id
        fd.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_valid2(self, form):
        self.object = self.get_object()
        fd = form.save(commit=False)
        fd.auteur = self.request.user
        fd.nom_comm_id = self.request.POST.get('comment_id')
        fd.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        self.object = self.get_object()
        niveau = self.object.niveau
        matiere = self.object.matiere
        return reverse_lazy('cours:lessonlistdetail', kwargs={'niveau': niveau.slug, 'matiere': matiere.slug, 'slug': self.object.slug})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'form' in request.POST:
            form_class = self.form_class
            form_name = 'form'
        else:
            form_class = self.second_form_class
            form_name = 'form2'
        form = self.get_form(form_class) # On prend soit form soit form2
        if form_name == 'form' and form.is_valid():
            return self.form_valid(form)
        if form_name == 'form2' and form.is_valid():
            return self.form_valid2(form)

def download_file(request, lesson_id, file_type):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if file_type == 'pdf' and lesson.pdf:
        file_url = lesson.pdf.url
    elif file_type == 'video' and lesson.video:
        file_url = lesson.video.url
    elif file_type == 'fp' and lesson.fp:
        file_url = lesson.fp.url
    else:
        return redirect('cours:lessonlistdetail', niveau=lesson.niveau.slug, matiere=lesson.matiere.slug, slug=lesson.slug)

    lesson.download_count += 1
    lesson.save()
    return HttpResponseRedirect(file_url)





class LessonCreateView(CreateView):
    form_class=LessonForm
    context_object_name='matieres'
    model=Matiere
    template_name='cours/lessoncreate.html'

    def get_success_url(self):
        self.object=self.get_object()
        niveau=self.object.niveau
      
        return reverse_lazy('cours:lessonlist',kwargs={'niveau':niveau,'slug':self.object.slug})

    def form_valid(self,form,*args,**kwargs):
        self.object=self.get_object()
        lsson=form.save(commit=False)
        lsson.creer_par=self.request.user # on prend le nom de user qui cree
        lsson.niveau=self.object.niveau
        lsson.matiere=self.object
        lsson.save()
        return HttpResponseRedirect(self.get_success_url()) #pour dire ou on part appres la creation
    
class LessonUpdateView(UpdateView):
    fields=('nom','position','pdf','fp')
    context_object_name='lesson'
    model=Lesson
    template_name='cours/lessonupdate.html'

class LessonDeleteView(DeleteView):
    model=Lesson
    context_object_name="lesson"
    template_name='cours/lessondelete.html'

    def get_success_url(self):
        niveau=self.object.niveau
        matiere=self.object.matiere
        return reverse_lazy("cours:lessonlist",kwargs={'niveau':niveau,'slug':matiere.slug})
    

#evaluation

@login_required
def create_evaluation(request, lesson_slug):
    lesson = get_object_or_404(Lesson, slug=lesson_slug)
    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.lesson = lesson
            evaluation.created_by = request.user
            evaluation.save()
            return redirect('evaluation_detail', slug=evaluation.slug)
    else:
        form = EvaluationForm()
    return render(request, 'create_evaluation.html', {'form': form, 'lesson': lesson})




@login_required
def evaluation_list(request):
    evaluations = Evaluation.objects.all()
    return render(request, 'evaluations/evaluation_list.html', {'evaluations': evaluations})

@login_required
def evaluation_detail(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    questions = Question.objects.filter(evaluation=evaluation)
    
    if request.method == 'POST':
        form = StudentAnswerForm(request.POST)
        if form.is_valid():
            student_answer = form.save(commit=False)
            student_answer.student = request.user  
            student_answer.evaluation = evaluation  
            student_answer.save()
            return redirect('cours:evaluation_list')  
    else:
        form = StudentAnswerForm()
    
    return render(request, 'evaluations/evaluation_detail.html', {
        'evaluation': evaluation,
        'questions': questions,
        'form': form
    })

#mark
@login_required


@login_required
def marquer_comme_complete(request, niveau, matiere, slug):
    lesson = get_object_or_404(Lesson, niveau__slug=niveau, matiere__slug=matiere, slug=slug)
    lesson.complet = True
    lesson.save()
    
    # Mettre à jour la progression de l'utilisateur
    user_progress, created = UserProgress.objects.get_or_create(user=request.user)
    user_progress.update_progress()
    
    # Ajouter des messages de débogage
    print(f"Leçon {lesson} marquée comme complétée pour l'utilisateur {request.user.username}")
    print(f"Progression mise à jour : {user_progress.lessons_completed} / {user_progress.total_lessons}")
    
    # Redirection vers une autre vue ou template
    return redirect('cours:lessonlistdetail', niveau=niveau, matiere=matiere, slug=slug)

def afficher_progression(request):
    #user_progress = UserProgress.objects.get(user=request.user) 
    user_progress, created = UserProgress.objects.get_or_create(user=request.user)
    context = {
        'user_progress': user_progress,
    }
    return render(request, 'progressions/progression.html', context)



