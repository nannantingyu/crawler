const argv = process.argv.slice(2),
    mysql = require('mysql'),
    moment = require("moment"),
    path = require('path'),
    root_path = process.cwd(),
    log4js = require('log4js'),
    request = require("request"),
    redis = require('redis'),
    url = require('url'),
    config = require(path.join(root_path, "config")),
    forever = require('forever-monitor');

var server = require('http').createServer();
var io = require('socket.io')(server);
io.on('connection', function(client){
    io.emit("hello", "world");
});
server.listen(3000);

io.on('connection', (socket) => {
    socket.emit('ferret', 'tobi', (data) => {
        console.log(data); // data will be 'woot'
    });
});

log4js.configure(config.log4js);
const logger = log4js.getLogger('btctrade'),
    redis_client = redis.createClient(config.redis.port, config.redis.server);

mysqlconnection = mysql.createConnection(config.mysql);

var child = forever.start([ 'phantomjs', path.join(root_path, 'app/btctrade/page.js') ], {
    max : 1,
    silent : true
});

child.on('stdout', function (data) {
    console.log("Data fetch", data.toString());
    io.emit("hq", data.toString());
});



child.on('exit:code', function(code) {
    process.kill(child.child.pid);
    logger.error(`btctrade 脚本退出，时间${moment().format("YYYY-MM-DD HH:mm:ss")}`);
});

child.on('restart', function() {
    process.kill(child.child.pid);
    logger.error(`btctrade 重启脚本${argvs[0]}第${child.times}次，【错误发生】，时间：${moment().format("YYYY-MM-DD HH:mm:ss")}`);
});

child.on('stderr', function(data) {
    logger.error(`btctrade 发生错误，时间${moment().format("YYYY-MM-DD HH:mm:ss")}, 错误：${data}`);
    process.kill(child.child.pid);
    child.stop();
    child.restart();
});