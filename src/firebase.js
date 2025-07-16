import { initializeApp } from "firebase/app";
import { getMessaging } from "firebase/messaging";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyC87UxBCfKu78jCrmHdGgx454uIFgoQ13A",
  authDomain: "birdstrikedetection.firebaseapp.com",
  projectId: "birdstrikedetection",
  storageBucket: "birdstrikedetection.appspot.com", // <-- fixed typo here!
  messagingSenderId: "185377277139",
  appId: "1:185377277139:web:fb8a40052daf071439c026",
  measurementId: "G-ZGBQ9BP7TY"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

export { messaging };