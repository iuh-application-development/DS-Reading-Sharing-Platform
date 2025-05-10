import { auth } from "./firebase-config.js";
import { signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";

document.querySelector('form').addEventListener('submit', (e) => {
    e.preventDefault();  // Ngăn reload form

    const email = document.getElementById('login_id').value.trim();
    const password = document.getElementById('password').value.trim();

    signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            const user = userCredential.user;
            return user.getIdToken();  // Lấy ID token từ Firebase
        })
        .then((idToken) => {
            return fetch('/firebase-login', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + idToken
                 },
                body: JSON.stringify({
                    status: 'success',
                })
            });
        })
        .then(response => response.json())
        .then(data => {
            window.location.href = data.redirect;
        })
        .catch((error) => {
            // alert('Firebase login error:', error.code, error.message);
            fetch('/firebase-login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    status: 'error',
                    message: 'Lỗi đăng nhập: ' + error.message
                })
            })
            .then(response => response.json())
            .then(data => {
                window.location.href = data.redirect;
            });
        });
});
