var url = 'http://js.fx678.com:8000';
var socket = io.connect(url,{
    'reconnection': true,
    'reconnectionDelay': 200,
    'reconnectionDelayMax' : 1000,
    'force new connection' : true
});

socket.on('news', function (message) {
    if (typeof window.callPhantom === 'function') {
        var status = window.callPhantom({
            message: message
        });
    }
});