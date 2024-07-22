console.log('Loaded scroll.js');

const toggleScrollToTopBtn = () => {
	const scrollToTop = document.querySelector('.scroll-to-top');
	
	if (window.scrollY > 300) {
		scrollToTop.style.display = 'block';
	} else {
		scrollToTop.style.display = 'none';
	}
};

window.addEventListener('scroll', toggleScrollToTopBtn);