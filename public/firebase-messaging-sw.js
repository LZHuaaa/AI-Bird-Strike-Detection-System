importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging-compat.js');

firebase.initializeApp({
    apiKey: "AIzaSyC87UxBCfKu78jCrmHdGgx454uIFgoQ13A",
    authDomain: "birdstrikedetection.firebaseapp.com",
    projectId: "birdstrikedetection",
    storageBucket: "birdstrikedetection.firebasestorage.app",
    messagingSenderId: "185377277139",
    appId: "1:185377277139:web:fb8a40052daf071439c026",
    measurementId: "G-ZGBQ9BP7TY"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/firebase-logo.png'
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});