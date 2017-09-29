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

log4js.configure(config.log4js);
const logger = log4js.getLogger('fx678'),
    redis_client = redis.createClient(config.redis.port, config.redis.server);

mysqlconnection = mysql.createConnection(config.mysql);

var child = forever.start([ 'phantomjs', path.join(root_path, 'app/fx678/page.js') ], {
    max : 1,
    silent : true
});

child.on('exit:code', function(code) {
    process.kill(child.child.pid);
    logger.error(`fx678脚本退出，时间${moment().format("YYYY-MM-DD HH:mm:ss")}`);
});

child.on('restart', function() {
    process.kill(child.child.pid);
    logger.error(`fx678重启脚本${argvs[0]}第${child.times}次，【错误发生】，时间：${moment().format("YYYY-MM-DD HH:mm:ss")}`);
});

child.on('stderr', function(data) {
    logger.error(`fx678 发生错误，时间${moment().format("YYYY-MM-DD HH:mm:ss")}, 错误：${data}`);
    process.kill(child.child.pid);
    child.stop();
    child.restart();
});

child.on('stdout', function (data) {
    logger.info("Data fetch", data.toString());
    try{
        data = JSON.parse(data);
    }
    catch(err) {
        logger.log(err);
        data = null;
    }

    if(data && data.type == 'data') {
        info = {};
        data = data.data;

        let now = moment().format("YYYY-MM-DD HH:mm:ss");
        info['created_time'] = now;
        info['updated_time'] = now;

        if(isNaN(data.newsType)) {
            return;
        }


        let newsType = parseInt(data.newsType);
        if(newsType == 118) {
            info['former_value'] = data.previousValue;
            info['predicted_value'] = data.forecaseValue;
            info['published_value'] = data.currentValue;

            info['body'] = data.newsTitle;
            info['publish_time'] = moment(parseInt(data.publishtime)*1000).format("YYYY-MM-DD HH:mm:ss");
            info['importance'] = data.importantLevel == 3?0:1;

            info['influnce'] = '';
            analysis = data.newsAnalysis.split("|");
            if(analysis[0]) {
                info['influnce'] += '利多 ' + analysis[0];
            }
            if(analysis[1]) {
                if(!info['influnce']) {
                    info['influnce'] += ",";
                }

                info['influnce'] += '利空 ' + analysis[0];
            }

            if(analysis[2]) {
                if(!info['influnce']) {
                    info['influnce'] += ",";
                }

                info['influnce'] += '中性';
            }

            info['star'] = data.importantLevel == 3?5: data.importantLevel == 2?3: 1;
            info['dateid'] = data.newsId;
            info['calendar_id'] = data.idxId;
            info['country'] = data.country;

            mysqlconnection.query(`select * from crawl_fx678_kuaixun where dateid = '${info['dateid']}';`, function(err, rows, fields) {
                let sql = "";
                if(data.actionType == 1) {
                    if(rows.length > 0) {
                        sql = `update crawl_fx678_kuaixun set body='${data.newsTitle}', updated_time='${now}', importance=${info['importance']}, former_value='${info['former_value']}', predicted_value='${info['predicted_value']}', published_value='${info['published_value']}' where dateid=${data.newsId};`;
                    }
                    else {
                        sql = `insert into crawl_fx678_kuaixun(${Object.keys(info).join(',')}) values('${Object.values(info).join('\',\'')}');`;
                    }
                }
                else if (data.actionType == 3) {
                    sql = `delete from crawl_fx678_kuaixun where dateid=${data.newsId};`;
                }
                else{
                    sql = `update crawl_fx678_kuaixun set body='${data.newsTitle}', updated_time='${now}', importance=${info['importance']}, former_value='${info['former_value']}', predicted_value='${info['predicted_value']}', published_value='${info['published_value']}' where dateid=${data.newsId};`;
                }

                logger.info(sql);
                mysqlconnection.query(sql, function(err, rows, fields) {
                    if (err) {
                        logger.error('error sql: ' + sql);
                        console.log(err);
                    }
                    else{
                        logger.info('插入数据成功, ' + sql);
                    }
                });
            });
        }
        else {
            keys_format = ['t0', 'importance', 'publish_time', 'body', 'more_link', 't5', 'image', 't7', 't8', 'time_detail', 't10', 'dateid'];
            info['body'] = data.newsTitle;
            info['publish_time'] = moment(parseInt(data.publishtime)*1000).format("YYYY-MM-DD HH:mm:ss");
            info['importance'] = data.importantLevel == 3?0:1;

            if(newsType != 116 && newsType != 119 && newsType != 802){
                //添加更多，抓取详情页
                redis_client.sadd("fx678_detail_pages", "http://news.fx678.com/" + data.newsId + ".shtml");
            }

            //添加图片
            if(newsType == 116 || newsType == 117 || newsType == 119) {
                if(data.newsimage != null && data.newsimage.length > 1){
                    info['image'] = data.newsimage;
                }
            }

            info['dateid'] = data.newsId;

            mysqlconnection.query(`select * from crawl_fx678_kuaixun where dateid = '${info['dateid']}';`, function(err, rows, fields) {
                let sql = '';
                if (data.actionType == 1){
                    if(rows.length > 0) {
                        sql = `update crawl_fx678_kuaixun set body='${data.newsTitle}', updated_time='${now}', importance=${info['importance']}, body='${info['body']}' where dateid=${data.newsId};`;
                    }
                    else {
                        sql = `insert into crawl_fx678_kuaixun(${Object.keys(info).join(',')}) values('${Object.values(info).join('\',\'')}');`;
                    }
                }
                else if (data.actionType == 3) {
                    sql = `delete from crawl_fx678_kuaixun where dateid=${data.newsId};`;
                }
                else{
                    sql = `update crawl_fx678_kuaixun set body='${data.newsTitle}', updated_time='${now}', importance=${info['importance']}, body='${info['body']}' where dateid=${data.newsId};`;
                }

                logger.info(sql);
                mysqlconnection.query(sql, function(err, rows, fields) {
                    if (err) {
                        logger.error('error sql: ' + sql);
                        console.log(err);
                    }
                    else{
                        logger.info('插入数据成功, ' + sql);
                    }
                });
            });
        }
    }
});

//child.stderr.on('data', function (data) {
//    console.log('stderr: ' + data);
//});
//
//child.on('exit', function (code) {
//    console.log('child process exited with code ' + code);
//});