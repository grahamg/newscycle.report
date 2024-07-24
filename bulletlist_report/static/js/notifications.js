const notificationSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/notifications/'
);

notificationSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const message = data['message'];

    // Handle the incoming message (e.g., display notification)
    alert(message);
};

notificationSocket.onclose = function(e) {
    console.error('Notification socket closed unexpectedly');
};

// Function to send a message to the WebSocket
function sendNotification(message) {
    notificationSocket.send(JSON.stringify({
        'message': message
    }));
}