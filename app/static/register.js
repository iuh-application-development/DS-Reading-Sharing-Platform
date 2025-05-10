import { auth } from "./firebase-config.js";
import { createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";

document.querySelector('form').addEventListener('submit', (e) => {
    e.preventDefault();  // Ngăn reload form

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const firstName = document.getElementById('first_name').value.trim();
    const lastName = document.getElementById('last_name').value.trim();

    createUserWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
        return userCredential.user.getIdToken();
    })
    .then((idToken) => {
        return fetch('/firebase-register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                status: 'success',
                message: 'Đăng ký thành công! Mời bạn đăng nhập.',
                idToken: idToken,
                first_name: firstName,
                last_name: lastName
            })
        });
    })
    .then(response => response.json())
    .then(data => {
        window.location.href = data.redirect;
    })
    .catch((error) => {
        fetch('/firebase-register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                status: 'error',
                message: 'Lỗi đăng ký: ' + error.message
            })
        })
        .then(response => response.json())
        .then(data => {
            window.location.href = data.redirect;
        });
    });
});
