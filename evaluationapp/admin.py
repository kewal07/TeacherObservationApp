from django.contrib import admin
from evaluationapp.models import School,Grade,Subject,Form,Evaluation,Status,Category,FormWithCategory,Question,Choice,Vote,Voted,VoteText,FormQuestion,FormVoted, TeacherClassSubject, SchoolGradeSection, EvaluationTargets
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
admin.site.register(TeacherClassSubject)
admin.site.register(SchoolGradeSection)
admin.site.register(EvaluationTargets)
