from evaluationapp.models import Grade,School,Subject,Form, Category, FormWithCategory, FormSection, FormQuestion, Question, Choice, FormVoted, Voted, VoteText, Vote, Evaluation, TeacherClassSubject, SchoolGradeSection, EvaluationTargets, GradeSchemes, GradesRange, Status

from django.http import HttpResponse

from wkhtmltopdf.views import PDFTemplateView

class PDFView(PDFTemplateView):
	template_name = 'form_wise_pdf_report.html'
	cmd_options = {
		'margin-top': 3,
	}