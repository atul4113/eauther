
function addFirstOrLastClass(list_element, i) {
	if (i % 5 == 0) {
		list_element.addClass('first');
	}
	if (i % 5 == 4) {
		list_element.addClass('last');
	}
}

function sortByRankDescending(allContents) {
	allContents = allContents.sort(function(a, b) {
		return b.rank - a.rank; // sort descending by rank
	});
}

function showLoadingScreen() {
	$('.search-in-progress').css('display', 'block');
}

function hideLoadingScreen() {
	$('.search-in-progress').css('display', 'none');
}

function filterRepeatingContents(contents, allContents, allContentsIDs) {
	for (var i = 0; i < contents.length; i++) {
		if (allContentsIDs.indexOf(contents[i].id) === -1) {
			allContents.push(contents[i]);
			allContentsIDs.push(contents[i].id);
		}
	}
}

function displayErrorMessage() {
	var message = 'There was an error. Not all results are shown.'
	var errorMessage = createErrorMessage(message);
	$('.error-message').html(errorMessage);
}