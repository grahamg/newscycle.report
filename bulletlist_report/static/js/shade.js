const initShade = () => {
	const toggleShadeElements = document.querySelectorAll('.toggle-shade');
	
	toggleShadeElements.forEach(element => {
		element.addEventListener('click', function(event) {
			event.preventDefault();
			
			const target = event.target.closest('.item');

			if (target) {
				if (target.style.display === '') {
					// Hide selected feed bullet points and add to minimized feed list.
					target.style.display = 'none';
					addToMinimizedFeedList(target);
				} else {
					// Make selected feed bullet points visible again and remove from minimized feed list.
					target.style.display = '';
					removeFromMinimizedFeedList(target);
				}
			}
		});
	});
	
	document.addEventListener('keydown', function(event) {
		// Keypress: m
		if (event.key === 'm') {
			// Toggle minimize/maximize state of feed lists.
			let allShadeButtons = document.querySelectorAll('.toggle-shade');
			allShadeButtons.forEach(function(button) {
				button.click();
			});
		}
		
		// Keypress: Shift + M
		if (event.shiftKey) {
			if (event.key === 'M') {
				// Toggle minimize/maximize state of minimized feed list.
				let minimizedFeedListButtons = document.querySelectorAll('.toggle-minimized-feed-list');
				minimizedFeedListButtons.forEach(function(button) {
					button.click();
				});
			}
		}
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
	const feedTitle = target.querySelector('.feed-title').textContent.trim();
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
	const feedTitle = target.querySelector('.feed-title').textContent.trim();
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
	const originalFeeds = document.querySelectorAll('.item');
	originalFeeds.forEach(feed => {
		const titleElement = feed.querySelector('.feed-title');
		if (titleElement && titleElement.textContent.trim() === feedTitle) {
			const list = feed;
			if (list) {
				list.style.display = '';
				listItem.remove();
				updateMinimizedFeedListVisibility();
			}
		}
	});
}
