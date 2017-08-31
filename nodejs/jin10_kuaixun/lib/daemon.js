var spawn = require('child_process').spawn,
    server = null;

function startServer(){
    console.log('start server');
    server = spawn('node', ['socket_jin.js', '../config/config.js']);
    console.log('node js pid is ' + server.pid);
    server.on('close',function(code, signal){
        console.log('close', signal);
        console.log('close', code);

        if(signal) {
            server.kill(signal);
        }
        server = startServer();
    });
    server.on('error',function(code, signal){
        if(signal) {
            server.kill(signal);
        }

        server = startServer();
    });
    return server;
};

startServer();