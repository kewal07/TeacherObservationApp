from django.contrib import admin
from evaluationapp.models import School,Grade,Subject,Form,Evaluation,Status,EvaluationStatus,Category,FormWithCategory,Question,Choice,Vote,Voted,VoteText,FormQuestion,FormVoted, TeacherSubject, TeacherClass

# Register your models here.

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 10

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

admin.site.register(Grade)
admin.site.register(Subject)
admin.site.register(Form)
admin.site.register(Evaluation)
admin.site.register(Status)
admin.site.register(EvaluationStatus)
admin.site.register(Category)
admin.site.register(FormWithCategory)
admin.site.register(Question,QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Vote)
admin.site.register(Voted)
admin.site.register(VoteText)
admin.site.register(FormQuestion)
admin.site.register(FormVoted)
admin.site.register(School)
admin.site.register(TeacherSubject)
admin.site.register(TeacherClass)
