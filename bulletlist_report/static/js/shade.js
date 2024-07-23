console.log('Loaded shade.js');

const initShade = () => {
	const toggleShadeElements = document.querySelectorAll('.toggle-shade');
	toggleShadeElements.forEach(element => {
	    element.addEventListener('click', function(event) {
			event.preventDefault();
	        const target = event.target.closest('.item'); // Find the closest item element
	        const closestListDisc = target.querySelector('ul');

	        if (closestListDisc) {
	            if (closestListDisc.style.display === '') {
					// Hide selected feed bullet points and add to minimized feed list.
	                closestListDisc.style.display = 'none';
	                addToMinimizedFeedList(target);
	            } else {
					// Make selected feed bullet points visible again and remove from minimized feed list.
	                closestListDisc.style.display = '';
	                removeFromMinimizedFeedList(target);
	            }
	        }
	    });
	});
	
	const toggleButton = document.querySelector('.toggle-minimized-feed-list');
    const minimizedFeedList = document.querySelector('.ul-minimized-feed-list');
    toggleButton.addEventListener('click', function(event) {
		event.preventDefault();
		
        if (minimizedFeedList.style.display === 'none' || minimizedFeedList.style.display === 'none') {
            minimizedFeedList.style.display = 'block';
        } else {
            minimizedFeedList.style.display = 'none';
        }
    });
}

const addToMinimizedFeedList = (target) => {
	const minimizedFeedList = document.querySelector('.minimized-feed-list ul');
	const feedTitle = target.querySelector('.feed-title').textContent.trim(); // Get the feed title from the h3 element
	if (!feedTitle) return; // Ensure there's text to add

	const listItem = document.createElement('li');
	listItem.textContent = feedTitle;
	listItem.classList.add('minimized');
	listItem.addEventListener('click', () => {
		restoreFeed(listItem);
	});
	minimizedFeedList.appendChild(listItem);
	updateMinimizedFeedListVisibility();
}

const removeFromMinimizedFeedList = (target) => {
	const minimizedFeedList = document.querySelector('.minimized-feed-list ul');
	const feedTitle = target.querySelector('.feed-title').textContent.trim(); // Get the feed title from the h3 element
	const feedItems = minimizedFeedList.querySelectorAll('li.minimized');
	feedItems.forEach(item => {
	    if (item.textContent.trim() === feedTitle) {
	        minimizedFeedList.removeChild(item);
	    }
	});
	updateMinimizedFeedListVisibility();
}

const updateMinimizedFeedListVisibility = () => {
	const minimizedFeedList = document.querySelector('.minimized-feed-list');
	const feedItems = minimizedFeedList.querySelectorAll('ul li.minimized');
	if (feedItems.length > 0) {
	    minimizedFeedList.style.display = 'block';
	} else {
	    minimizedFeedList.style.display = 'none';
	}
}

const restoreFeed = (listItem) => {
	const feedTitle = listItem.textContent.trim();
	const originalFeeds = document.querySelectorAll('.item'); // Adjust selector based on your HTML structure
	originalFeeds.forEach(feed => {
		const titleElement = feed.querySelector('.feed-title');
		if (titleElement && titleElement.textContent.trim() === feedTitle) {
			const list = feed.querySelector('ul');
			if (list) {
				list.style.display = ''; // Restore the original feed
				listItem.remove(); // Remove the <li> element from the minimized feed list
				updateMinimizedFeedListVisibility();
			}
		}
	});
}