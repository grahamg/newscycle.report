const isMobileDevice = () => {
    return /Mobi|Android/i.test(navigator.userAgent) || window.innerWidth <= 800;
}