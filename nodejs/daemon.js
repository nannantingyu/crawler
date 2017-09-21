const spawn = require('child_process').spawn,
    argvs = process.argv.slice(2),
    forever = require('forever-monitor'),
    moment = require('moment');

var child = new (forever.Monitor)(argvs[0], {
    max: 10,
    logFile: 'logs/daemon.log',
    outFile: 'logs/daemon-out.log',
    errFile: 'logs/daemon-out.log'
});

child.on('watch:restart', function(info) {
    console.error(`重启脚本${argvs[0]}，【脚本改变】，时间：${moment().format("YYYY-MM-DD HH:mm:ss")}`);
});

child.on('restart', function() {
    console.error(`重启脚本${argvs[0]}第${child.times}次，【错误发生】，时间：${moment().format("YYYY-MM-DD HH:mm:ss")}`);
});

child.on('exit:code', function(code) {
    console.error(`脚本退出，时间${moment().format("YYYY-MM-DD HH:mm:ss")}`);
});

child.start();