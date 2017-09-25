const argv = process.argv.slice(2),
    mysql = require('mysql'),
    moment = require("moment"),
    path = require('path'),
    root_path = process.cwd(),
    log4js = require('log4js'),
    request = require("request"),
    redis = require('redis'),
    url = require('url'),
    fs = require('fs'),
    config = require(path.join(root_path, "config")),
    forever = require('forever-monitor');

log4js.configure(config.log4js);
const logger = log4js.getLogger('wallstreet'),
    redis_client = redis.createClient(config.redis.port, config.redis.server);

mysqlconnection = mysql.createConnection(config.mysql);

//throw new Error("my error");

const dict_type = {
    "global-channel": "宏观",
    "a-stock-channel": "A股",
    "us-stock-channel": "美股",
    "forex-channel": "外汇",
    "commodity-channel": "商品"
};

let download = function(url, dir, filename){
    if(!fs.existsSync(dir)) {
        fs.mkdirSync(dir);
    }

    request.head(url, function(err, res, body){
        request(url).pipe(fs.createWriteStream(path.join(dir, filename)));
    });
};

var child = forever.start([ 'phantomjs', path.join(root_path, 'app/wallstreetcn/page.js') ], {
    max : 1,
    silent : true
});

child.on('stderr', function(data) {
    logger.error(`wallstreetcn 发生错误，时间${moment().format("YYYY-MM-DD HH:mm:ss")}, 错误：${data}`);
    process.kill(child.child.pid);
    child.stop();
    child.restart();
});

child.on('exit:code', function(code) {
    process.kill(child.child.pid);
    logger.error(`wallstreetcn 脚本退出，时间${moment().format("YYYY-MM-DD HH:mm:ss")}`);
});

child.on('restart', function() {
    process.kill(child.child.pid);
    logger.error(`wallstreetcn 重启脚本${argvs[0]}第${child.times}次，【错误发生】，时间：${moment().format("YYYY-MM-DD HH:mm:ss")}`);
});

child.on('stdout', function (content) {
    logger.info('[ori]', content.toString());
    content = content.toString().replace(/\\n/g, "")
        .replace(/\\\\\\"/g, "'")
        .replace(/\\"/g, '"')
        .replace(/\\"/g, '"')
        .replace(/\\\\u003c/g, '<')
        .replace(/\\\\u003e\\/g, '>')
        .replace(/\\\\u003e/g, '>')
        .replace(/\\/g, '')
        .trim();
    content = content.substr(1, content.length - 2);

    try{
        if(content.startsWith("{")){
            logger.info("[message] " + content);
            data = JSON.parse(content);
        }
        else{
            data = {};
        }
    }
    catch(err) {
        logger.error(err);
    }

    if(data && data.data && data.data.id) {
        info = {};
        redis_client.set('next_cursor', data.next_cursor);

        data = data.data;
        logger.info("[Data parse]", data.content);
        let now = moment().format("YYYY-MM-DD HH:mm:ss");
        info['created_time'] = now;
        info['updated_time'] = now;


        keys_format = ['t0', 'importance', 'publish_time', 'body', 'more_link', 't5', 'image', 't7', 't8', 'time_detail', 't10', 'dateid'];
        info['body'] = data.content;
        info['publish_time'] = moment(parseInt(data.display_time)*1000).format("YYYY-MM-DD HH:mm:ss");
        info['importance'] = data.score >= 2?0:1;

        //添加图片
        info['image'] = [];

        //下载图片
        if(data.image_uris && data.image_uris.length > 0) {
            for(let url of data.image_uris){
                let day_now = moment().format("YYYYMMDD");
                let filename = path.basename(url),
                    dirname = path.join(config.crawl.download_dir, day_now);
                download(url, dirname, filename);
                info['image'].push(path.join(day_now, filename));
            }
        }

        info['image'] = JSON.stringify(info['image']);

        info['dateid'] = data.id;
        info['calendar_id'] = data.op_id;

        let types = [];
        for(let t in data.channels){
            if(dict_type[data.channels[t]]){
                types.push(dict_type[data.channels[t]]);
            }
        }

        info['typename'] = types.join(",");

        let sql = "";
        if(data.op_name == 'update') {
            sql = `update crawl_wallstreetcn_kuaixun set body='${data.content}', updated_time='${now}', importance=${info['importance']} where dateid=${data.id};`;
        }
        else if (data.op_name == 'delete') {
            sql = `delete from crawl_wallstreetcn_kuaixun where dateid=${data.id};`;
        }
        else{
            sql = `insert into crawl_wallstreetcn_kuaixun(${Object.keys(info).join(',')}) values('${Object.values(info).join('\',\'')}');`;
        }

        logger.info(sql);
        mysqlconnection.query(sql, function(err, rows, fields) {
            if (err) {
                logger.error('error sql: ' + sql);
            }
            else{
                logger.info('插入数据成功, ' + sql);
            }
        });
    }
});