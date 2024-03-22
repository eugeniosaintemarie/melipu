const webpush = require('web-push');

console.log("Public Key:", process.env.PUBLIC_KEY);
console.log("Private Key:", process.env.PRIVATE_KEY);

const vapidKeys = {
    publicKey: process.env.PUBLIC_KEY,
    privateKey: process.env.PRIVATE_KEY
};

webpush.setVapidDetails(
    'mailto:e.saintemarie@outlook.com',
    vapidKeys.publicKey,
    vapidKeys.privateKey
);

console.log("Subscription Endpoint:", process.env.SUBSCRIPTION_ENDPOINT);
console.log("P256DH Key:", process.env.P256DH_KEY);
console.log("Auth Key:", process.env.AUTH_KEY);

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

console.log("Sending notification...");

webpush.sendNotification(pushSubscription, payload).then(response => {
    console.log("Notification sent successfully:", response);
}).catch(error => {
    console.error("Error sending notification:", error.stack);
});