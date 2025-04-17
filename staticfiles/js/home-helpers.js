$(document).ready(function(){
	// click actions
	var buttons = $(".mpp-buttons").children();
	$.each(buttons, function() {
		$(this).on("click", function(event) {
			document.location = $(this).attr('click');
		})
	});
});