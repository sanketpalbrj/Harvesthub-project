
function openNoupeChat(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    const chatBtn = document.querySelector('.noupe-chat-button');
    if (chatBtn) {
        chatBtn.click();
    } else {
        console.warn("Noupe chat button is still loading.");
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const isLoggedIn = "{{ request.session.custid|yesno:'true,false' }}" === "true";

    if (!isLoggedIn) {
        const loginModal = new bootstrap.Modal(document.getElementById('login'));
        // Inside if (!isLoggedIn) { ... }
        if (new URLSearchParams(window.location.search).get('show_login') === '1') {
            loginModal.show();
}

        document.querySelectorAll('.auth-required').forEach(el => {
            // 1. Deactivated visual appearance
           if (el.classList.contains('nav-link') && !el.classList.contains('no-dim')) {
                el.classList.add('opacity-50');
            }
            el.title = "Login required";
        
            // 2. Prevent offcanvas/other Bootstrap toggles from firing
            el.removeAttribute('data-bs-toggle');

            // 3. Intercept click (capture phase runs BEFORE inline onclick="showSection(...)")
            el.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopImmediatePropagation();
                loginModal.show();
            }, true);
        });
    }
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('emailInput');
    const clearEmailBtn = document.getElementById('clearEmail');
    const emailError = document.getElementById('email-error');
    const emailErrorText = document.getElementById('email-error-text');

    const passwordInput = document.getElementById('passwordInput');
    const passwordError = document.getElementById('password-error');
    const passwordErrorText = document.getElementById('password-error-text');

    function clearAllErrors() {
        emailInput.classList.remove('input-invalid');
        passwordInput.classList.remove('input-invalid');
        emailError.classList.add('d-none');
        passwordError.classList.add('d-none');
    }

    emailInput.addEventListener('input', function () {
        clearEmailBtn.classList.toggle('d-none', emailInput.value.length === 0);
        clearAllErrors();
    });

    clearEmailBtn.addEventListener('click', function () {
        emailInput.value = '';
        clearEmailBtn.classList.add('d-none');
        clearAllErrors();
        emailInput.focus();
    });

    passwordInput.addEventListener('input', clearAllErrors);

    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();
        clearAllErrors();

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        // 1. Check email format first
        if (!emailInput.value.trim() || !emailRegex.test(emailInput.value.trim())) {
            emailInput.classList.add('input-invalid');
            clearEmailBtn.classList.toggle('d-none', emailInput.value.length === 0);
            emailErrorText.textContent = "Invalid email address!";
            emailError.classList.remove('d-none');
            return;
        }

        // 2. Check password is not blank
        if (!passwordInput.value.trim()) {
            passwordInput.classList.add('input-invalid');
            passwordErrorText.textContent = "Enter your password";
            passwordError.classList.remove('d-none');
            return;
        }

        // 3. Check credentials against Django logincust view
        fetch(loginForm.action, {
            method: 'POST',
            body: new FormData(loginForm)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                window.location.href = window.location.pathname;
            } else {
                // Highlight both inputs in red & show "Invalid email or password"
                emailInput.classList.add('input-invalid');
                passwordInput.classList.add('input-invalid');
                clearEmailBtn.classList.remove('d-none');
                passwordErrorText.textContent = "Invalid password!";
                passwordError.classList.remove('d-none');
            }
        });
    });
const regForm = document.getElementById('regForm');
    if (regForm) {
        // Use querySelector inside regForm so duplicate IDs on the page can't break it
        const regEmail = regForm.querySelector('[name="custemail"]');
        const regEmailErr = document.getElementById('reg-email-error');
        const regEmailErrText = document.getElementById('reg-email-error-text');

        const regPhone = regForm.querySelector('[name="custphone"]');
        const regPhoneErr = document.getElementById('reg-phone-error');
        const regPhoneErrText = document.getElementById('reg-phone-error-text');
        const pincodeInput = regForm.querySelector('[name="custpincode"]');
        const cityInput = regForm.querySelector('[name="custcity"]');
        const stateInput = regForm.querySelector('[name="custstate"]');
        const pincodeStatus = document.getElementById('pincode-status');

if (pincodeInput) {
    pincodeInput.addEventListener('input', function () {
        // Strip non-digits
        this.value = this.value.replace(/\D/g, '');
        pincodeInput.classList.remove('is-invalid');
        pincodeStatus.classList.add('d-none');

        if (this.value.length === 6) {
            pincodeStatus.textContent = "Fetching location...";
            pincodeStatus.className = "small mt-1 text-muted";

            fetch(`https://api.postalpincode.in/pincode/${this.value}`)
                .then(res => res.json())
                .then(data => {
                    if (data[0].Status === "Success" && data[0].PostOffice.length > 0) {
                        const po = data[0].PostOffice[0];
                        cityInput.value = po.District;
                        stateInput.value = po.State;
                        pincodeStatus.classList.add('d-none');
                    } else {
                        cityInput.value = "";
                        stateInput.value = "";
                        pincodeInput.classList.add('is-invalid');
                        pincodeStatus.innerHTML = '<i class="bi bi-exclamation-circle-fill"></i> Invalid Indian pincode';
                        pincodeStatus.className = "small mt-1 text-danger d-flex align-items-center gap-1";
                    }
                })
                .catch(() => {
                    // If offline or API unreachable, let user type City & State manually
                    pincodeStatus.classList.add('d-none');
                });
        }
    });
}

        function clearRegErrors() {
            if (regEmail) regEmail.classList.remove('is-invalid');
            if (regPhone) regPhone.classList.remove('is-invalid');
            if (regEmailErr) {
                regEmailErr.classList.add('d-none');
                regEmailErr.classList.remove('d-flex');
            }
            if (regPhoneErr) {
                regPhoneErr.classList.add('d-none');
                regPhoneErr.classList.remove('d-flex');
            }
        }

        if (regEmail) regEmail.addEventListener('input', clearRegErrors);
        if (regPhone) regPhone.addEventListener('input', clearRegErrors);

        regForm.addEventListener('submit', function (e) {
            e.preventDefault();
            clearRegErrors();

            // Trigger native required checks for blank fields first
            if (!regForm.checkValidity()) {
                regForm.reportValidity();
                return;
            }

            fetch(regForm.action, {
                method: 'POST',
                body: new FormData(regForm)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.href = window.location.pathname;
                } else if (data.field === 'email') {
                    regEmail.classList.add('is-invalid');
                    regEmailErrText.textContent = data.error;
                    regEmailErr.classList.remove('d-none');
                    regEmailErr.classList.add('d-flex');
                    regEmail.focus();
                } else if (data.field === 'phone') {
                    regPhone.classList.add('is-invalid');
                    regPhoneErrText.textContent = data.error;
                    regPhoneErr.classList.remove('d-none');
                    regPhoneErr.classList.add('d-flex');
                    regPhone.focus();
                }
            });
        });
    }
});
