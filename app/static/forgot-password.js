import { auth } from './firebase-config.js';
import { sendPasswordResetEmail } from 'https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js';

document.querySelector('form').addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value.trim();

    sendPasswordResetEmail(auth, email)
        .then(() => {
            return fetch('/forgotPassword', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: 'success' })
            });
        })
        .catch((error) => {
            return fetch('/forgotPassword', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: 'error', message: error.message })
            });
        })
        .then(() => {
            // Reload lại trang để hiện flash message
            window.location.reload();
        });
});
