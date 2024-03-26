if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
        navigator.serviceWorker
            .register("https://eugeniosaintemarie.github.io/melipu/serviceWorker.js")
            .then(res => console.log("service worker registered"))
            .catch(err => console.log("service worker not registered", err))
    })
}

Notification.requestPermission().then(function (result) {
    console.log(result);
});

firebase.firestore().settings({
    timestampsInSnapshots: true
});

var firebaseConfig = {
    apiKey: "AIzaSyDpEOWIwaO1Ce0zRdOlIcNep5BXRJ1oO_Q",
    authDomain: "melipu-9a9ae.firebaseapp.com",
    projectId: "melipu-9a9ae",
    storageBucket: "melipu-9a9ae.appspot.com",
    messagingSenderId: "628006825968",
    appId: "1:628006825968:web:15b2c6ff577d0843007735"
};
firebase.initializeApp(firebaseConfig);

firebase.messaging().getToken({ vapidKey: 'BBZWqDE__B3Y8ApoiALHUXuvQAxMejyJQWF09sKN20auDT1ojrOTt82QLCALgh645j9lZ6ReVokHfkiUyLZVqDw' }).then((currentToken) => {
    if (currentToken) {
        console.log('Token de dispositivo:', currentToken);
        firebase.firestore().collection('tokens').add({ token: currentToken })
            .then(() => console.log('Token guardado exitosamente'))
            .catch((error) => console.error('Error al guardar el token:', error));
    } else {
        console.log('No se pudo obtener el token de dispositivo.');
    }
}).catch((err) => {
    console.log('Error al obtener el token de dispositivo:', err);
});