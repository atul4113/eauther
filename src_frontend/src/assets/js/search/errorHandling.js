function getErrorMessage(jqXHR, textStatus) {
	var message = '';
	if (jqXHR.status == 500) {
		message = 'Server response was 500.';
	} else if (jqXHR.status == 404) {
		message = 'Server response was 404.';
	} else if (textStatus == 'parseerror') {
		message = 'Parsing JSON request failed.';
	} else if (textStatus == 'timeout') {
		message = 'Request time out.';
	} else {
		message = 'Unknown error.';
	}
	return message;
}