const webpush = require('web-push');

const vapidKeys = {
    publicKey: process.env.PUBLIC_KEY,
    privateKey: process.env.PRIVATE_KEY
};

webpush.setVapidDetails(
    'mailto:e.saintemarie@outlook.com',
    vapidKeys.publicKey,
    vapidKeys.privateKey
);

const pushSubscription = {
    endpoint: process.env.SUBSCRIPTION_ENDPOINT,
    keys: {
        p256dh: process.env.P256DH_KEY,
        auth: process.env.AUTH_KEY
    }
};

const payload = JSON.stringify({
    title: 'Nuevo precio',
    body: 'El precio de una publicación cambio',
    icon: 'https://eugeniosaintemarie.github.io/shop-publications/image/icon/icon-72x72.png',
    badge: 'https://eugeniosaintemarie.github.io/shop-publications/image/icon/icon-72x72.png'
});

webpush.sendNotification(pushSubscription, payload).catch(error => {
    console.error(error.stack);
});