const io = require('socket.io-client'),
    mysql = require('mysql'),
    moment = require("moment"),
    fs = require('fs'),
    path = require('path'),
    root_path = process.cwd(),
    log4js = require('log4js'),
    request = require("request"),
    redis = require('redis'),
    url = require('url'),
    querystring = require("querystring");

const config = require(path.join(root_path, "config"));
serverArr = config.jin10_rili_addr,
    mysqlconnection = mysql.createConnection(config.mysql),
    redis_client = redis.createClient(config.redis.port, config.redis.server);

log4js.configure(config.log4js);
const logger = log4js.getLogger('jin10rili');

mysqlconnection.connect();
const i = Math.floor(Math.random() * serverArr.length + 1) - 1, n = serverArr[i];
let socket = io(n), timeout = 3e4;

socket.on('connect', function (){
    console.log('socket connect');
    socket.emit('reg', 'ok');
    socket.emit('reqvote', 'ok');
});

let reGetServer = function() {
    logger.info('reGetServer');
    throw new Error("重新连接");
}

socket.on('error', function (reason) {
    logger.info('error');
    reGetServer();
});
socket.on('connect_error', function (reason) {
    logger.info('connect_error');
    reGetServer();
});

socket.on('repair', function (reason) {
    logger.info('repair');
    reGetServer();
});
socket.on('reconnecting', function (nextRetry) {
    logger.info('reconnecting');
});
socket.on('disconnect', function () {
    logger.info('socket disconnect');
    reGetServer();
});

socket.on('user message', function(msg){
    console.log('user message', msg);
    logger.info(msg);
    if(msg) {
        msg = msg.split("#");
        msg_dt = {
            pub_time: moment().format("YYYY-MM-DD " + msg[1] + ":00"),
            quota_name: msg[2],
            former_value: msg[3],
            predicted_value: msg[4],
            published_value: msg[5],
            influence: msg[7],
            country: msg[9],
            source_id: msg[11],
            updated_time: moment().format("YYYY-MM-DD HH:mm:ss")
        }

        sql = `update crawl_economic_calendar set quota_name="${msg_dt['quota_name']}", former_value="${msg_dt['former_value']}", predicted_value="${msg_dt['predicted_value']}", published_value="${msg_dt['published_value']}", influence="${msg_dt['influence']}", country="${msg_dt['country']}", updated_time="${msg_dt['updated_time']}" where source_id=${msg_dt['source_id']};`;
        //for(let o in msg_dt) {
        //    sql += o + '="' + msg_dt[o] + '",';
        //}
        //
        //sql = sql.substring(0, sql.length-1) + ' where source_id=' + msg[11] + ';';
        mysqlconnection.query(sql, function(err, row, fields) {
            if (err) {
                logger.error('error sql: ' + sql);
                logger.error(err);
            }
            else{
                logger.info('更新数据成功, ' + sql);
            }
        });
    }
});

socket.on('today', function(msg){
    let now = moment().format("YYYY-MM-DD HH:mm:ss");
    if(msg) {
        var sql = "", index = 0;
        for(let message of msg) {
            redis_client.sismember('rili:jin10', message['id'], function(err, data){
                quota_name = message['country']+message['datename']+message['dataname'];
                if(data) {
                    sql += `update crawl_economic_calendar set quota_name='${quota_name}', country='${message["country"]}', unit='${message["unit"]}', dataname='${message["dataname"]}', datename='${message["datename"]}', importance=${message["star"]}, former_value='${message["previous"]}', predicted_value='${message["consensus"]}', published_value='${message["actual"]}', updated_time='${now}' where source_id=${message["id"]};`;
                }
                else {
                    sql += `insert into crawl_economic_calendar(country, unit, dataname, datename, pub_time, importance, former_value, predicted_value, published_value, source_id, created_time, updated_time, quota_name) values ("${message['country']}", "${message['unit']}", "${message['dataname']}", "${message['datename']}", "${moment(message['timestr']).format('YYYY-MM-DD HH:mm:ss')}", ${message["star"]}, "${message['previous']}", "${message['consensus']}", "${message['actual']}", ${message["id"]}, "${now}", "${now}", "${quota_name}");`;
                }

                redis_client.sadd('rili:jin10', message['id']);

                if(index == msg.length-1 && sql){
                    mysqlconnection.query(sql, function(err, rows, fields) {
                        if (err) {
                            logger.error('error sql: ' + sql);
                            logger.error(err);
                        }
                        else{
                            logger.info('插入数据成功, ' + sql);
                        }
                    });
                }

                index ++;
            });
        }
    }
});