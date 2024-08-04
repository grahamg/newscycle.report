const enqueueRSSFeedItemSummary = async (event, id) => {
	event.preventDefault();
	
	const postData = {
		'id': id
	};
	const url = `/api/v1/summary/`;
	const csrftoken = getCookie('csrftoken');
	const requestOptions = {
	    method: 'POST',
	    headers: {
	        'Content-Type': 'application/json',
	        'X-CSRFToken': csrftoken,
	    },
	    body: JSON.stringify(postData)
	};
	
	fetch(url, requestOptions)
	    .then(response => {
	        if (!response.ok) {
	            throw new Error('Network response was not ok!');
	        }
	        return response.json();
	    })
	    .then(data => {
	    	console.log(`This is the then block.`);
	    }).catch(error => {
	        console.error('Error occurred when attempting to enqueue an rss feed item: ', error);
	    });
};