import { auth } from './firebase-config.js';
import { sendPasswordResetEmail } from 'https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js';

document.querySelector('form').addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value.trim();

    sendPasswordResetEmail(auth, email)
        .then(() => {
            fetch('/forgotPassword', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: 'success' })
            })
            .then(response => response.json())
            .then(data => {
                window.location.href = data.redirect;
            });
        })
        .catch((error) => {
            fetch('/forgotPassword', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: 'error', message: error.message })
            })
            .then(response => response.json())
            .then(data => {
                window.location.href = data.redirect;
            });
        });
});
