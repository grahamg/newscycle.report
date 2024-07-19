console.log('Loaded feed_tab_select.js');

function* iterateObject(obj) {
    const keys = Object.keys(obj);
    let index = 0;
    while (true) {
        yield [keys[index], obj[keys[index]]];
        index = (index + 1) % keys.length; // Loop back to the beginning if end is reached
    }
}

const getFeedsById = () => {
	const feedTitles = document.querySelectorAll('.feed-title');
	const h3Mapping = {};
	
	feedTitles.forEach(feedTitle => {
		const h3 = feedTitle.closest('h3');
		
		if (h3 && h3.id) {
			h3Mapping[h3.id] = h3.textContent.trim();
		}
	});
	
	return h3Mapping;
}

const initFeedTabSelect = (event) => {
	window.feedIdMapping = iterateObject(getFeedsById());
	
	let mobileLastTouchTime = 0;
	let mobileTouchDelay = 300;
	
	document.addEventListener('dblclick', function(event) {
		event.preventDefault();
		
	    const currentFeed = window.feedIdMapping.next();
	    if (!currentFeed.done) {
	        const [key, value] = currentFeed.value;
	        // Perform processing here for each feed key-value
			// pair that's iterated through presseing <tab>.
			document.querySelectorAll('.glow').forEach(e => {
				e.classList.remove('glow');
			});
			
			let currentElement = document.querySelector(`#${key}`);
			if (currentElement) {
			    currentElement.scrollIntoView({
			        behavior: 'smooth',
			        block: 'start'
			    });
			}
			currentElement.classList.add('glow');
	    } else {
	        // Restart the iteration by resetting the iterator
	        iterator.return(); // Optional: Clean up if needed
	        iterator = iterateObject(h3Mapping); // Reset iterator
	        processNext(); // Start iterating again from the beginning
	    }
	});
	
	document.addEventListener('touchend', function(event) {
		let currentTime = new Date().getTime();
		let timeDiff = currentTime - mobileLastTouchTime;
		
		if (timeDiff < mobileTouchDelay && timeDiff > 0) {
			// Double tap detected on mobile device
			event.preventDefault();
			
		    const currentFeed = window.feedIdMapping.next();
		    if (!currentFeed.done) {
		        const [key, value] = currentFeed.value;
		        // Perform processing here for each feed key-value
				// pair that's iterated through presseing <tab>.
				document.querySelectorAll('.glow').forEach(e => {
					e.classList.remove('glow');
				});
				
				let currentElement = document.querySelector(`#${key}`);
				if (currentElement) {
				    currentElement.scrollIntoView({
				        behavior: 'smooth',
				        block: 'start'
				    });
				}
				currentElement.classList.add('glow');
		    } else {
		        // Restart the iteration by resetting the iterator
		        iterator.return(); // Optional: Clean up if needed
		        iterator = iterateObject(h3Mapping); // Reset iterator
		        processNext(); // Start iterating again from the beginning
		    }
			
			mobileLastTouchTime = 0;
		} else {
			// Single tap detected on mobile device
			document.querySelectorAll('.glow').forEach(e => {
				e.classList.remove('glow');
			});
			
			mobileLastTouchTime = currentTime;
		}
	});
	
	document.addEventListener('click', function(event) {
		document.querySelectorAll('.glow').forEach(e => {
			e.classList.remove('glow');
		});
	});
	
	document.addEventListener('keydown', function(event) {
		if (!isMobileDevice()) {
			if (event.key === 'Tab' || event.keyCode === 9) {
				event.preventDefault();				
			    const currentFeed = window.feedIdMapping.next();
			    if (!currentFeed.done) {
			        const [key, value] = currentFeed.value;
			        // Perform processing here for each feed key-value
					// pair that's iterated through presseing <tab>.
					document.querySelectorAll('.glow').forEach(e => {
						e.classList.remove('glow');
					});
					
					let currentElement = document.querySelector(`#${key}`);
					if (currentElement) {
					    currentElement.scrollIntoView({
					        behavior: 'smooth',
					        block: 'start'
					    });
					}
					currentElement.classList.add('glow');
			    } else {
			        // Restart the iteration by resetting the iterator
			        iterator.return(); // Optional: Clean up if needed
			        iterator = iterateObject(h3Mapping); // Reset iterator
			        processNext(); // Start iterating again from the beginning
			    }
			}
		}
	});
}