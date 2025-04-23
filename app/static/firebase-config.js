import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, 
         GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyArGd-Qxq7ykvP2zOIru5nHGAJPPEuCqzg",
  authDomain: "prjtest-53174.firebaseapp.com",
  projectId: "prjtest-53174",
  storageBucket: "prjtest-53174.firebasestorage.app",
  messagingSenderId: "814388118025",
  appId: "1:814388118025:web:9080114597e1d74b30eed8",
  measurementId: "G-XSTPPTKT70"
};

  // Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

const db = getFirestore(app);

export { auth, provider, db };