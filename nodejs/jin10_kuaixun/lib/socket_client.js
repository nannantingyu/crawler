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

select_sql = "select * from crawl_jin10_article where body "
mysqlconnection.query(insert_sql, function(err, rows, fields) {
    if (err) logger.error('error sql: ' + insert_sql);;
    console.log("add one");

    //将详情页填到redis中
    if(keys_format.includes('more_link') && data['more_link']) {
        if(data['more_link'].includes('news.jin10'))
        {
            redis_client.zadd("detail_pages", 0, data['more_link']);
            yaml_data['img'] = data['image'];
        }
    }

    logger.info('插入数据成功, ' + insert_sql);
});