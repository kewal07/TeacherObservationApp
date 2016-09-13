var UIAlertDialogApi = function () {

    var handleDialogs = function() {			
			$('.accept-reject').click(function(){
				var elemid = $(this)[0].id;
				var action = elemid.split("---")[0];
				var ev_id = elemid.split("---")[1];
				bootbox.prompt("Additional Feedback", function(result) {
                    if (result === null) {
                    } else {
						var arurl = "/accept-reject/"+ev_id+"?action="+action+"&add_comment="+result;
						$.ajax(
						{
							type: 'GET',
							url:arurl,
							processData: false,
							contentType: false,
							success:function(obj)
							{
								// console.log("Hello");
								// window.location = "{% url 'evaluationapp:my_evaluations' %}";
								window.location = "/my-evaluations";
							}
						});
                    }
                });
			});
    }

    var handleAlerts = function() {
        
        $('#alert_show').click(function(){

            Metronic.alert({
                container: $('#alert_container').val(), // alerts parent container(by default placed after the page breadcrumbs)
                place: $('#alert_place').val(), // append or prepent in container 
                type: $('#alert_type').val(),  // alert's type
                message: $('#alert_message').val(),  // alert's message
                close: $('#alert_close').is(":checked"), // make alert closable
                reset: $('#alert_reset').is(":checked"), // close all previouse alerts first
                focus: $('#alert_focus').is(":checked"), // auto scroll to the alert after shown
                closeInSeconds: $('#alert_close_in_seconds').val(), // auto close after defined seconds
                icon: $('#alert_icon').val() // put icon before the message
            });

        });

    }

    return {

        //main function to initiate the module
        init: function () {
            handleDialogs();
            handleAlerts();
        }
    };

}();