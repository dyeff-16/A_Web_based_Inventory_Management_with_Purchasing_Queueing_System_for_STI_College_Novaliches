function signup() {
    const inputEmail = document.getElementById('inputEmail').value;
    const inputPassword = document.getElementById('inputPassword').value;
    const inputCode = document.getElementById('inputCode').value;
    const inputNumber = document.getElementById('inputNumber').value;


    fetch('/auth/signupPost', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inputEmail, inputPassword, inputCode, inputNumber })
    })
        .then(r => r.json())
        .then(data => {

            if (data.message) {
                alert(data.message);
            }
            if (data.success) {
                window.location.href = '/auth/login';
            }

        })
}