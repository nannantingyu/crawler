var socket = new WebSocket("wss://realtime-prod.wallstreetcn.com/ws");

socket.onopen = function(evt) {
    console.log("Connection open ...");
    socket.send(JSON.stringify({
        "command":"ENTER_CHANNEL",
        "data": {
            "chann_name":"live",
            "cursor":"771109"
        }
    }));
};

socket.onmessage = function(event) {
    var data = event.data;
    window.callPhantom(data);
};