if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
        navigator.serviceWorker
            .register("https://eugeniosaintemarie.github.io/shop-publications/serviceWorker.js")
            .then(res => console.log("service worker registered"))
            .catch(err => console.log("service worker not registered", err))
    })
}

function isIOS() {
    return [
        'iPad Simulator',
        'iPhone Simulator',
        'iPod Simulator',
        'iPad',
        'iPhone',
        'iPod'
    ].includes(navigator.platform)
        || (navigator.userAgent.includes("Mac") && "ontouchend" in document);
}

function isSafari() {
    return /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
}

function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + value + expires + "; path=/";
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

if (isIOS() && isSafari()) {
    var hasSeenPopup = getCookie('hasSeenPopup');
    if (!hasSeenPopup) {
        var popup = document.createElement("div");
        popup.style.position = "fixed";
        popup.style.bottom = "0";
        popup.style.width = "100%";
        popup.style.padding = "20px";
        popup.style.backgroundColor = "#ED1C24";
        popup.style.color = "white";
        popup.style.textAlign = "center";
        popup.innerHTML = "Para instalar HSBC Seguros Online, haz clic en el botón 'Compartir', y luego en 'Añadir a la pantalla de inicio' <button onclick='closePopup()'>Cerrar</button>";
        document.body.appendChild(popup);

        function closePopup() {
            document.body.removeChild(popup);
            setCookie('hasSeenPopup', true, 7);
        }
    }
}

Notification.requestPermission().then(function (result) {
    console.log(result);
});

const publicKey = 'BH6nVHnfduLF90IoVl-1-xAN_87d67IAn8QQ687b9dkXwXYX4HFdQzS-4hwNQ41y1yTxachsbHrFIqcJ7-AutOw';

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

Notification.requestPermission().then(function (result) {
    if (result === 'granted') {
        navigator.serviceWorker.ready.then(function (registration) {
            registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(publicKey)
            }).then(function (subscription) {
                console.log('User is subscribed:', subscription);
                console.log('Subscription Endpoint:', subscription.endpoint);
                console.log('P256DH Key:', subscription.keys.p256dh);
                console.log('Auth Key:', subscription.keys.auth);
            }).catch(function (error) {
                console.error('Failed to subscribe the user: ', error);
            });
        });
    }
});