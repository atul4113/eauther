/**
 * Handles ENTER key in forms without submit button.
 */
$(function() {
    $('form').each(function() {
        $('input').keypress(function(e, callback) {
            // Enter pressed?
            if(e.which == 10 || e.which == 13) {
            	e.preventDefault();
            	if (this.form) {
            		this.form.submit();
            	}
            }
            return true
        });

        $('input[type=submit]').hide();
    });
});


/**
 * Disable link after first click
 */
$(document).ready(function() {
	$("a.dblclick").click(function(e) {
		e.preventDefault();
		if (!$(this).hasClass('disabled')) {
			$(this).addClass('disabled');
			window.location.href = $(this).attr('href')
		}
	});
});