from evaluationapp.models import Status

ev_status = {
	"ongoing" : 1,
	"submitted" : 2,
	"reviewed" : 3,
	"completed" : 4,
	"accepted" : 5,
	"rejected" : 6
}

def getEvStatus(status_str):
	return Status.objects.get(status_id=ev_status.get(status_str))
