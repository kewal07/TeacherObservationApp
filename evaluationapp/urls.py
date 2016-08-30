from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from evaluationapp import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
	# r'',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
	url(r'^$',login_required(views.IndexView.as_view()), name='index'),
	url(r'^gettoken/', views.gettoken, name='gettoken'),
	url(r'^test$',login_required(views.TestView.as_view()),name='test'),
	url(r'^create-form$',login_required(views.CreateFormView.as_view()),name='create-form'),
	url(r'^evaluation-form/(?P<pk>\d+)/(?P<form_slug>[\w\-]+)/preview$',login_required(views.FormPreviewView.as_view()),name='evaluation_form_preview'),
	url(r'^edit-evaluation-forms$',login_required(views.EvaluationEditableFormsView.as_view()),name='edit_evaluations'),
	url(r'^edit-evaluation-forms/(?P<pk>\d+)/(?P<form_slug>[\w\-]+)/edit$',login_required(views.EvaluationFormEditView.as_view()),name='edit_form'),
	url(r'^view-inactive-evaluation-forms$',login_required(views.EvaluationEditableFormsView.as_view()),name='view_inactive'),
	url(r'^view-active-evaluation-forms$',login_required(views.EvaluationEditableFormsView.as_view()),name='view_active'),
	url(r'^evaluation-form-state/(?P<pk>\d+)/(?P<form_slug>[\w\-]+)/state$',login_required(views.EvaluationFormsStateView.as_view()),name='form_state'),
	url(r'^evaluation-home$',login_required(views.EvauationHomeView.as_view()),name='evaluation_home'),
	url(r'^evaluation-home/assign-evaluation$',login_required(views.AssignEvaluationView.as_view()),name='evaluation_assign'),
	url(r'^evaluation-ongoing$',login_required(views.EvaluationListView.as_view()),name='evaluation_ongoing'),
	url(r'^evaluation-submitted$',login_required(views.EvaluationListView.as_view()),name='evaluation_submitted'),
	url(r'^evaluation-reviewed$',login_required(views.EvaluationListView.as_view()),name='evaluation_reviewed'),
	url(r'^evaluation-completed$',login_required(views.EvaluationListView.as_view()),name='evaluation_completed'),
	url(r'^evaluation-review$',login_required(views.EvaluationListView.as_view()),name='evaluation_review'),
	url(r'^evaluation-archive$',login_required(views.EvaluationListView.as_view()),name='evaluation_archive'),
	url(r'^send-mail$',login_required(views.SendMail.as_view()),name='send_evaluation_reminder'),
	url(r'^evaluation-form/(?P<pk>\d+)/(?P<form_slug>[\w\-]+)/(?P<evaluation_id>[\d+]+)$',login_required(views.EvaluationFormVoteView.as_view()),name='evaluation_form_vote'),
	url(r'^evaluation-under-me$',login_required(views.EvaluationListView.as_view()),name='evaluation_under_me'),
	url(r'^my-evaluations$',login_required(views.EvaluationListView.as_view()),name='my_evaluations'),
	url(r'^view-evaluation/(?P<pk>\d+)/(?P<form_slug>[\w\-]+)/(?P<evaluation_id>[\d+]+)$',login_required(views.EvaluationFormVoteView.as_view()),name='view_evaluation'),
	url(r'^accept-reject/(?P<pk>\d+)$',login_required(views.AcceptRejectView.as_view()),name='evaluation_form_vote'),
	url(r'^forms-home$',login_required(views.FormsHomeView.as_view()),name='view_forms_home'),
	url(r'^settings-home$',login_required(views.SettingsHomeView.as_view()),name='view_settings'),
	url(r'^school-home$',login_required(views.SubjectHomeView.as_view()),name='school_view'),
	url(r'^subjects-home$',login_required(views.SubjectHomeView.as_view()),name='subjects_view'),
	url(r'^classes-home$',login_required(views.SubjectHomeView.as_view()),name='classes_view'),
	url(r'^download-home$',login_required(views.DownloadHomeView.as_view()),name='view_download'),
	url(r'^exportexcel',views.excel_view,name="exportexcel"),
	url(r'^analytics',login_required(views.AnalyticsView.as_view()),name='analytics'),
	url(r'^detail_analytics',login_required(views.AnalyticsDetailView.as_view()),name='detail_analytics'),
	url(r'^comparative_analytics',login_required(views.TeacherAnalyticsDetailView.as_view()),name='teacher_analytics'),
	url(r'^detail_teacher',login_required(views.DetailTeacherView.as_view()),name='detail_teacher'),
	url(r'^termsofservice', TemplateView.as_view(template_name='termsofservice.html'), name='termsofservice'),
    url(r'^privacypolicy', TemplateView.as_view(template_name='privacypolicy.html'), name='privacypolicy'),
    url(r'^getteachersubjects_in_section$', login_required(views.getteachersubjects_in_section), name='getteachersubjectsection'),
    url(r'^assign-targets$', login_required(views.AssignTargets.as_view()), name='assigntargettoteachers'),
    url(r'^review-targets$', login_required(views.ReviewTargets.as_view()), name='target_review'),
    url(r'^dashboard/(?P<school_name>[\w\-]+)$', login_required(views.AdminDashboard.as_view()), name='dashboard')
]