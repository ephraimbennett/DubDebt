document.addEventListener('DOMContentLoaded', function() {
    function setupToggle(pwId, btnId, eyeOpenId, eyeClosedId) {
        const passwordInput = document.getElementById(pwId);
        const toggleBtn = document.getElementById(btnId);
        const eyeOpen = document.getElementById(eyeOpenId);
        const eyeClosed = document.getElementById(eyeClosedId);
        toggleBtn.addEventListener('click', function() {
            const isPassword = passwordInput.type === "password";
            passwordInput.type = isPassword ? "text" : "password";
            toggleBtn.setAttribute('aria-label', isPassword ? "Hide password" : "Show password");
            eyeOpen.style.display = isPassword ? "none" : "inline";
            eyeClosed.style.display = isPassword ? "inline" : "none";
        });
    }
    setupToggle('password1', 'toggle-password', 'eye-open', 'eye-closed');
    setupToggle('password2', 'toggle-confirm-password', 'eye2-open', 'eye2-closed');
});