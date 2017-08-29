const io = require('socket.io-client');
const argv = process.argv.slice(2);
const mysql = require('mysql');
const moment = require("moment");
const fs = require('fs');
const config = JSON.parse(fs.readFileSync(argv[0], 'utf-8'));
const log4js = require('log4js');
log4js.configure(config.log4js);
const logger = log4js.getLogger('log_file');
const path = require('path');
const request = require("request");
const mysqlconnection = mysql.createConnection(config.mysql);
mysqlconnection.connect();
const redis = require('redis');
const redis_client = redis.createClient(config.redis.port, config.redis.server);

var url = 'http://js.fx678.com:8000';
var socket = io.connect(url, {
    'reconnection': true,
    'reconnectionDelay': 200,
    'reconnectionDelayMax' : 1000,
    'force new connection' : true,
    'transportOptions': {
        polling: {
            extraHeaders: {
                'x-clientid': 'abc',
                'Origin': 'http://kx.fx678.com'
            }
        }
    }
});

var socket = io.connect(url);
socket.on('news', function (message) {
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
socket.on('reconnecting', function () {
    console.log("reconnecting");
});
socket.on('reconnect_failed', function () {
    console.log("reconnect_failed");
});
socket.on('reconnect_error',function(){
    console.log("reconnect_error");
});