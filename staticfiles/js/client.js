document.addEventListener('DOMContentLoaded', function() {
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobile-menu');
  const closeMenu = document.querySelector('.close-mobile-menu');
  const mobileLinks = document.querySelectorAll('.mobile-link, .mobile-btn');

  function openMenu() {
    mobileMenu.classList.add('active');
    hamburger.setAttribute('aria-expanded', 'true');
    mobileMenu.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden'; // Prevent background scroll
  }
  function closeMenuFn() {
    mobileMenu.classList.remove('active');
    hamburger.setAttribute('aria-expanded', 'false');
    mobileMenu.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  hamburger.addEventListener('click', openMenu);
  closeMenu.addEventListener('click', closeMenuFn);
  mobileMenu.addEventListener('click', function(e) {
    if (e.target === mobileMenu) closeMenuFn();
  });
  // Auto-close on nav link click
  mobileLinks.forEach(link => link.addEventListener('click', closeMenuFn));
  // ESC to close
  document.addEventListener('keydown', function(e) {
    if (e.key === "Escape") closeMenuFn();
  });
});
