var server = require('http').createServer();
var io = require('socket.io')(server);
io.on('connection', function(client){
    client.on('event', function(data){});
    client.on('disconnect', function(){});
    io.emit("hello", "world");
});
server.listen(3000);