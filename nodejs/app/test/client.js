const io = require('socket.io-client');
const socket = io('http://localhost:3000');

socket.on('hello', function (message) {
    console.log(message);
});
socket.on('connect', function () {
    console.log("connect");
    state='connect';
});
socket.on('disconnect', function () {
    console.log("disconnect");
});
socket.on('reconnect', function () {
    console.log("reconnect");
});