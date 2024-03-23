if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
        navigator.serviceWorker
            .register("https://eugeniosaintemarie.github.io/shop-publications/serviceWorker.js")
            .then(res => console.log("service worker registered"))
            .catch(err => console.log("service worker not registered", err))
    })
}

Notification.requestPermission().then(function (result) {
    console.log(result);
});

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
                applicationServerKey: urlBase64ToUint8Array(window.vapidPublicKey)
            }).then(function (subscription) {
                registration.pushManager.getSubscription().then(function (existingSubscription) {
                    if (existingSubscription) {
                        existingSubscription.unsubscribe().then(function (successful) {
                            registration.pushManager.subscribe(subscriptionOptions);
                        });
                    } else {
                        registration.pushManager.subscribe(subscriptionOptions);
                    }
                });

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

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('showSubscription').addEventListener('click', function () {
        navigator.serviceWorker.ready.then(function (registration) {
            registration.pushManager.getSubscription().then(function (subscription) {
                if (subscription) {
                    console.log('Información de suscripción:', subscription);
                    console.log('Endpoint:', subscription.endpoint);
                    console.log('P256DH Key:', subscription.keys.p256dh);
                    console.log('Auth Key:', subscription.keys.auth);
                } else {
                    console.log('No hay una suscripción activa.');
                }
            }).catch(function (error) {
                console.error('Error al obtener la suscripción:', error);
            });
        });
    });
});