// static/js/bookmarks.js
console.log('Loaded bookmarks.js');

function removeAllEventListeners(element) {
    const newElement = element.cloneNode(true);
    element.parentNode.replaceChild(newElement, element);
}

const getBookmarks = () => {
    const url = `/api/v1/bookmark/`;
    const csrftoken = getCookie('csrftoken');
    const requestOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        }
    };

    fetch(url, requestOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok!');
            }
            return response.json();
        })
        .then(data => {
            for (const key in data.bookmark_feed_item_mapping) {
                if (data.bookmark_feed_item_mapping.hasOwnProperty(key)) {
					let id = data.bookmark_feed_item_mapping[key];
					let selectedBookmarkAnchor = document.getElementById(`rss-feed-item-id-${id}`);
					if (selectedBookmarkAnchor!= null) {
						selectedBookmarkAnchor.textContent = '✔';
						selectedBookmarkAnchor.removeAttribute('onclick');
						selectedBookmarkAnchor.onclick = function(event) {
							event.preventDefault();
						};
					}
                }
            }
        })
        .catch(error => {
            console.error('Error occurred when fetching bookmarks:', error);
        });
}

const userBookmark = (event, id, action) => {
	event.preventDefault();
	
	const postData = {
		id: id,
		action: action,
	};
	const url = `/api/v1/bookmark/`;
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
	        console.log('Modified user bookmark successfully:', data);
			if (data.action == 'add') {
				//console.log(id, action);
				const selectedBookmarkAnchor = document.getElementById(`rss-feed-item-id-${id}`);
				selectedBookmarkAnchor.textContent = 'Added!';
				selectedBookmarkAnchor.removeAttribute('onclick');
			} else if (data.action == 'remove') {
				//console.log(id, action);
				const selectedBookmarkAnchor = document.getElementById(`rss-feed-item-id-${id}`);
				selectedBookmarkAnchor.textContent = 'Removed!';
				selectedBookmarkAnchor.removeAttribute('onclick');
			}
	    })
	    .catch(error => {
	        console.error('Error occurred when modifying user bookmark:', error);
	    });
};