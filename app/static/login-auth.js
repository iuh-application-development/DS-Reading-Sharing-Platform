import { auth, provider } from "./firebase-config.js";

import { 
         
         signInWithPopup
         } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";


const signInWithGoogleButtonEl = document.getElementById("google_login");

if (signInWithGoogleButtonEl) {
    signInWithGoogleButtonEl.addEventListener("click", authWithGoogle);
}
async function authWithGoogle(){
    // provider la dich vu google
    // auth la dich vu xac thuc
    try {
        const result = await signInWithPopup(auth, provider); // 
        if (!result) {
            throw new Error("Không có kết quả từ Google Sign-In.");
        }
        const user = result.user;
        const email = user.email;
        console.log("User:", user);
        // console.log("ID Token:", idToken);

        // console.log("Email từ Google Sign-In:", email);
        if (!email) {
            throw new Error("Không có email từ Google Sign-In.");
        }
        const idToken = await user.getIdToken(); // Lấy idToken từ credential
        console.log("Token gửi lên Flask:", idToken);

        loginUser(user, idToken);
      } catch (error) {
        console.error("Lỗi khi đăng nhập với Google:", error.message);
      }
    

}
function loginUser(user, idToken) {
    fetch('/auth', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + idToken
      },
      body: JSON.stringify({
        email: user.email,
        full_name: user.displayName,
        phone: user.phoneNumber,
        photo: user.photoURL
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === "success") {
        window.location.href = '/';
      } else {
        console.error("Xác thực thất bại:", data.message);
      }
    })
    .catch(error => {
      console.error("Lỗi khi gửi yêu cầu đăng nhập:", error);
    });
  }
  