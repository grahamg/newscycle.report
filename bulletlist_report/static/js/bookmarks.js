// static/js/bookmarks.js
console.log('Loaded bookmarks.js');

function removeAllEventListeners(element) {
    const newElement = element.cloneNode(true);
    element.parentNode.replaceChild(newElement, element);
}

function removeChildrenWithClass(parentElement, className) {
    // Select all child elements with the specified class within the parent element
    const childrenToRemove = parentElement.querySelectorAll(`.${className}`);
    
    // Loop through the selected elements and remove them from their parent
    childrenToRemove.forEach(child => {
        parentElement.removeChild(child);
    });
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

const userBookmark = (event, id, action, silent=false) => {
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
			
			if (silent) {
				return;
			}
			
			if (data.action == 'add') {
				const idName = `rss-feed-item-id-${id}`;
				const selectedBookmarkAnchor = document.getElementById(idName);
				selectedBookmarkAnchor.textContent = 'Added!';
				selectedBookmarkAnchor.removeAttribute('onclick');
				
				const newUndoAnchor = document.createElement('a');
				newUndoAnchor.href = '#';
				newUndoAnchor.textContent = ' Undo?';
				newUndoAnchor.id = `undo-action-${id}`;
				newUndoAnchor.onclick = function(event) {
					event.preventDefault();
					
					userBookmark(event, id, 'remove', true);
					const revertBookmarkAction = document.createElement('a');
					revertBookmarkAction.href = '#';
					revertBookmarkAction.textContent = '🔖';
					revertBookmarkAction.id = `rss-feed-item-id-${id}`;
					revertBookmarkAction.onclick = function(event) {
						event.preventDefault();
						userBookmark(event, id, 'add');
					}
					
					const undoAnchor = event.target;
					const addedAnchor = document.getElementById(idName);
					undoAnchor.parentElement.removeChild(undoAnchor);
					addedAnchor.insertAdjacentElement('afterend', revertBookmarkAction);
					addedAnchor.parentElement.removeChild(addedAnchor);
				};
				
				selectedBookmarkAnchor.insertAdjacentElement('afterend', newUndoAnchor);
			} else if (data.action == 'remove') {
				const idName = `rss-feed-item-id-${id}`;
				const selectedBookmarkAnchor = document.getElementById(idName);
				selectedBookmarkAnchor.textContent = 'Removed!';
				selectedBookmarkAnchor.removeAttribute('onclick');
				
				const newUndoAnchor = document.createElement('a');
				newUndoAnchor.href = '#';
				newUndoAnchor.textContent = ' Undo?';
				newUndoAnchor.id = `undo-action-${id}`;
				newUndoAnchor.onclick = function(event) {
					event.preventDefault();
					
					userBookmark(event, id, 'add', true);
					const revertBookmarkAction = document.createElement('a');
					revertBookmarkAction.href = '#';
					revertBookmarkAction.textContent = '❎';
					revertBookmarkAction.id = `rss-feed-item-id-${id}`;
					revertBookmarkAction.onclick = function(event) {
						event.preventDefault();
						userBookmark(event, id, 'remove');
					}
					
					const undoAnchor = event.target;
					const addedAnchor = document.getElementById(idName);
					undoAnchor.parentElement.removeChild(undoAnchor);
					addedAnchor.insertAdjacentElement('afterend', revertBookmarkAction);
					addedAnchor.parentElement.removeChild(addedAnchor);
				};
				
				selectedBookmarkAnchor.insertAdjacentElement('afterend', newUndoAnchor);
			}
	    })
	    .catch(error => {
	        console.error('Error occurred when modifying user bookmark:', error);
	    });
};