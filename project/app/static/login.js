document.addEventListener("DOMContentLoaded", function() {
    const toggleLinkToSignup = document.getElementById("toggle-link-to-signup");
    const toggleLinkToLogin = document.getElementById("toggle-link-to-login");
    const signinForm = document.getElementById("signin");
    const signupForm = document.getElementById("signup");

    if (toggleLinkToSignup && toggleLinkToLogin) {
        toggleLinkToSignup.addEventListener("click", function(event) {
            event.preventDefault();
            signupForm.classList.remove('form-inactive');
            signupForm.classList.add('form-active');
            signinForm.classList.remove('form-active');
            signinForm.classList.add('form-inactive');
        });

        toggleLinkToLogin.addEventListener("click", function(event) {
            event.preventDefault();
            signinForm.classList.remove('form-inactive');
            signinForm.classList.add('form-active');
            signupForm.classList.remove('form-active');
            signupForm.classList.add('form-inactive');
        });
    }
});
