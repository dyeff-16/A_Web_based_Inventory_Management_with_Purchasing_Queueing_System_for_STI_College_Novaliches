    function postLogin() {
        const inputEmail = document.getElementById('inputEmail').value;
        const inputPassword = document.getElementById('inputPassword').value;

        document.getElementById('btnLogin').disabled = true;

        fetch('/auth/postLogin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ inputEmail, inputPassword })
        })
            .then(response => response.json())
            .then(data => {

                if (data.change_force_password) {
                    window.location.href = '/auth/otp_force_change_password';
                }
                else if (data.login_pending) {
                    window.location.href = '/auth/login-mfa';

                } else {

                    if (!inputEmail) {
                        alert('Enter email first')
                        document.getElementById('btnLogin').disabled = false;
                    } else if (!inputPassword) {
                        alert('Enter a password first')
                        document.getElementById('btnLogin').disabled = false;

                    } else {
                        alert(data.message)
                        document.getElementById('btnLogin').disabled = false;
                        // const message = document.getElementById('message');
                        // message.innerText = data.message;
                        // message.style.display = 'block';
                    }
                }
            })

    }

   
    let time = 60; 
    window.onload = function() {
    const btn = document.getElementById('resendBtn');
    const text = document.getElementById('resendText');

    btn.disabled = true;
    text.textContent = `Resend in ${time}s`;

    const timer = setInterval(() => {
        time--;
        text.textContent = `Resend in ${time}s`;
        if (time <= 0) {
        clearInterval(timer);
        btn.disabled = false;
        text.textContent = 'Resend Code';
        }
    }, 1000);
    };

    function resendSMS(){
        const btn = document.getElementById('resendBtn');
        const text = document.getElementById('resendText');
        let time = 60;

        // 🔁 restart cooldown after resend
        btn.disabled = true;
        text.textContent = `Resend in ${time}s`;

        const timer = setInterval(() => {
            time--;
            text.textContent = `Resend in ${time}s`;
            if (time <= 0) {
            clearInterval(timer);
            btn.disabled = false;
            text.textContent = 'Resend Code';
            }
        }, 1000);

        fetch('/auth/resend_sms', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
        if (data.success) {
            alert('New OTP sent!');
        } else {
            alert('Failed to resend code.');
        }
        });
    }
    function resendEmail(){
        const btn = document.getElementById('resendBtn');
        const text = document.getElementById('resendText');
        let time = 60;

        // 🔁 restart cooldown after resend
        btn.disabled = true;
        text.textContent = `Resend in ${time}s`;

        const timer = setInterval(() => {
            time--;
            text.textContent = `Resend in ${time}s`;
            if (time <= 0) {
            clearInterval(timer);
            btn.disabled = false;
            text.textContent = 'Resend Code';
            }
        }, 1000);

        fetch('/auth/resend_email', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
        if (data.success) {
            alert('New OTP sent!');
        } else {
            alert('Failed to resend code.');
        }
        });
    }
    
    function moveNext(current, nextFieldID) {
        if (current.value.length === 1) {
            const nextField = document.getElementById(nextFieldID);
            if (nextField) nextField.focus();
        }
    }
    function moveBack(event, prevId) {
    if (event.key === "Backspace" && !event.target.value && prevId) {
        document.getElementById(prevId).focus();
    }
    }
    function emailOTP() {
        let inputOTP = document.getElementById("otp1").value +
            document.getElementById("otp2").value +
            document.getElementById("otp3").value +
            document.getElementById("otp4").value +
            document.getElementById("otp5").value +
            document.getElementById("otp6").value;

        document.getElementById('btnOTP').disabled = true;
        fetch('/auth/otpValidationLogin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ inputOTP })
        })
            .then(response => response.json())
            .then(data => {

                if (data.message) {
                    alert(data.message);
                    document.getElementById('btnOTP').disabled = false;

                }

                if (data.back_to_login) {
                    window.location.href = '/auth/login'
                }

                else {
                    const roles = data.roles;
                    if (data.success && roles == 'student') {
                        window.location.href = '/home';
                    }
                    else if (data.success && roles == 'admin') {
                        window.location.href = '/admin';
                    }
                    else if (data.success && roles == 'system_admin') {
                        window.location.href = '/system_admin';
                    }
                }
            })
    }

    function smsOTP() {
        let inputOTP = document.getElementById("otp1").value +
            document.getElementById("otp2").value +
            document.getElementById("otp3").value +
            document.getElementById("otp4").value +
            document.getElementById("otp5").value +
            document.getElementById("otp6").value;


        document.getElementById('btnOTP').disabled = true;
        fetch('/auth/sms_otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ inputOTP })
        })
            .then(response => response.json())
            .then(data => {

                if (data.message) {
                    alert(data.message);
                    document.getElementById('btnOTP').disabled = false;

                }

                if (data.back_to_login) {
                    window.location.href = '/auth/login'
                }

                else {
                    const roles = data.roles;
                    if (data.success && roles == 'student') {
                        window.location.href = '/home';
                    }
                    else if (data.success && roles == 'admin') {
                        window.location.href = '/admin';
                    }
                    else if (data.success && roles == 'system_admin') {
                        window.location.href = '/system_admin';
                    }
                }
            })
    }

    document.addEventListener('DOMContentLoaded', () => {
        const el = document.getElementById('otpTimer');
        const remaining = Number(el.dataset.remaining || 0);
        startOtpTimer(remaining);
    });

    function startOtpTimer(seconds) {
        const otpTimer = document.getElementById('otpTimer');
        let remain = Math.max(0, Number(seconds) || 0);

        function updateTimer() {
            const min = String(Math.floor(remain / 60)).padStart(2, '0');
            const sec = String(remain % 60).padStart(2, '0');
            otpTimer.innerText = `code expires in ${min}:${sec}`;
            if (remain <= 0) {
                clearInterval(interval);
                otpTimer.innerText = 'OTP expired. Please request a new one.';
                otpTimer.classList.remove('text-muted');
                otpTimer.classList.add('text-danger');
            } else {
                remain -= 1;
            }
        }

        updateTimer();
        const interval = setInterval(updateTimer, 1000);
    }


    function togglePassword() {
        const passwordInput = document.getElementById("inputPassword");
        const icon = document.getElementById("toggleIcon");

        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            icon.classList.remove("bi-eye-slash");
            icon.classList.add("bi-eye");
        } else {
            passwordInput.type = "password";
            icon.classList.remove("bi-eye");
            icon.classList.add("bi-eye-slash");
        }
    }
    // function validateTerms() {
    //     const termsCheckbox = document.getElementById("termscondition");
    //     if (!termsCheckbox.checked) {
    //         alert("You must read and agree to the Terms & Conditions before logging in.");
    //         return false;
    //         return true;
    //     }
    // }
    // document.addEventListener("DOMContentLoaded", function () {
    //     const termsCheckbox = document.getElementById("termscondition");
    //     const acceptBtn = document.getElementById("accept-terms");

    //     termsCheckbox.addEventListener("click", function (e) {
    //         if (termsCheckbox.disabled) {
    //             e.preventDefault();
    //         }
    //     });

    //     acceptBtn.addEventListener("click", function () {
    //         termsCheckbox.disabled = false;
    //         termsCheckbox.checked = true;
    //     });
    // });