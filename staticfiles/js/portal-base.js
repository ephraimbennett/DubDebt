document.addEventListener('DOMContentLoaded', function() {
    var userMenu = document.querySelector('.user-menu');
    var dropdown = userMenu.querySelector('.user-menu-dropdown');

    function closeDropdown(e) {
        userMenu.classList.remove('open');
        document.removeEventListener('click', outsideClickListener);
    }
    function outsideClickListener(e) {
        if (!userMenu.contains(e.target)) closeDropdown();
    }
    userMenu.addEventListener('click', function(e) {
        e.stopPropagation();
        userMenu.classList.toggle('open');
        if (userMenu.classList.contains('open')) {
            document.addEventListener('click', outsideClickListener);
        } else {
            document.removeEventListener('click', outsideClickListener);
        }
    });
    // Optional: close on Esc
    userMenu.addEventListener('keydown', function(e) {
        if (e.key === "Escape") closeDropdown();
    });
});
