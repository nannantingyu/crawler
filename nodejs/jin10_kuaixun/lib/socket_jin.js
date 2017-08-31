const io = require('socket.io-client'),
    argv = process.argv.slice(2),
    mysql = require('mysql'),
    moment = require("moment"),
    fs = require('fs'),
    path = require('path'),
    root_path = path.dirname(__dirname),
    log4js = require('log4js'),
    request = require("request"),
    redis = require('redis'),
    url = require('url');

const config = require(path.join(root_path, "config/config")),
    serverArr = config.server_addr,
    mysqlconnection = mysql.createConnection(config.mysql),
    redis_client = redis.createClient(config.redis.port, config.redis.server);


log4js.configure(config.log4js);
const logger = log4js.getLogger(), msg_logger = log4js.getLogger("message");
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
    setTimeout(function(){
        socket.disconnect();
        let rand = Math.floor(Math.random() * serverArr.length + 1) - 1, server_addr = serverArr[rand];
        socket = io(server_addr)
    }, timeout)
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

let download = function(url, dir, filename){
    console.log(url);
    if(!fs.existsSync(dir)) {
        fs.mkdirSync(dir);
    }

    request.head(url, function(err, res, body){
        request(url).pipe(fs.createWriteStream(path.join(dir, filename)));
    });
};

socket.on('user message', function (msg) {
    msg_logger.info(msg);
    msg_0 = msg.charAt(0);
    let now = moment().format("YYYY-MM-DD HH:mm:ss");

    if (msg_0 == 1 || msg_0 == 0) {
        let yaml_dir = path.join(config.crawl.yaml_dir, config.crawl.yaml_root), detail_dir = config.crawl.detail_dir;
        fs.readFile(yaml_dir, function(err, file_data){
            if(err) {
                console.log("Read old json file err, ", err);
            }
            else {
                let old_data = [];
                try{
                    old_data = file_data.toString() ? Array.from(JSON.parse(file_data.toString())) : [];
                }
                catch(err) {
                    mysqlconnection.query("select * from crawl_jin10_kuaixun where date(publish_time)='"+moment().format("YYYY-MM-DD")+"' order by publish_time asc", function(err, rows, fields) {
                        old_data = JSON.parse(JSON.stringify(rows));
                        //fs.unlinkSync(yaml_dir);
                        logger.info('删除老文件成功！');
                        console.log('删除老文件成功！', err);
                    });
                }


                if((len = old_data.length) > 0) {
                    let last_msg = old_data[len-1], last_datetime = last_msg.datetime.substr(8,2), today = moment().format("DD");
                    //如果到了第二天，则删除前一天的内容
                    if(today != last_datetime) {
                        fs.unlinkSync(yaml_dir);
                        old_data = [];
                    }
                }

                let data = {};
                let keys_format = null;
                if(msg_0 == 1) {
                    keys_format = ['t0', 'real_time', 'body', 'former_value', 'predicted_value', 'published_value', 'star', 'influnce', 'publish_time', 'country', 't10', 'calendar_id', 'dateid', 't12'];
                }
                else {
                    keys_format = ['t0', 'importance', 'publish_time', 'body', 'more_link', 't5', 'image', 't7', 't8', 'time_detail', 't10', 'dateid'];
                }

                msg.split('#').forEach((val, index)=>{
                    data[keys_format[index]] = val;
                });

                data['created_time'] = now;
                data['updated_time'] = now;

                let yaml_data = null, detail_temp = "";
                if(msg_0 == 0) {
                    yaml_data = {
                        "tpl": 0,
                        "vip": 1-data['importance'],
                        "time": data['publish_time'].substr(11),
                        "datetime": data['publish_time'],
                        "content": data['body'],
                        "id": data['dateid']
                    };

                    //下载图片
                    if(keys_format.includes('image') && data['image']) {
                        let url = data['image'].includes('http')?data['image']: "http://image.jin10.com/" + data['image'].replace(/^[\/]+/, "");
                        url = url.replace('_lite', '');
                        let day_now = moment().format("YYYYMMDD");
                        let filename = path.basename(url),
                            dirname = path.join(config.crawl.download_dir, day_now);
                        download(url, dirname, filename);
                        data['image'] = path.join(day_now, filename);
                        yaml_data['image'] = data['image'];
                    }

                    //将详情页填到redis中
                    if(keys_format.includes('more_link') && data['more_link']) {
                        if(data['more_link'].includes('news.jin10'))
                        {
                            redis_client.zadd("detail_pages", 0, data['more_link']);
                            id = querystring.parse(url.parse(data['more_link']).query)['id'];
                            if(id) {
                                yaml_data['id'] = id;
                            }
                        }
                    }

                    detail_temp = `---\ntitle: ${data['publish_time']}资讯\ndate: ${data['publish_time']}\nlayout: post-scsj\n---\n${data['body']}`;
                    console.log(detail_temp);
                }
                else{
                    yaml_data = {
                        "tpl": 1,
                        "vip": data['star'] > 2?1:0,
                        "time": data['real_time'],
                        "datetime": data['publish_time'],
                        "title": data['body'],
                        "flag": data['country'],
                        "var1": data['former_value'],
                        "var2": data['predicted_value'],
                        "var3": data['published_value'],
                        "pk1": data['influnce'],
                        "star": data['star'],
                        "id": data['dateid']
                    };

                    let detail_body = `${data['real_time']} ${data['body']}\n重要程度: ${data['star']}\n前值: ${data['former_value']}\n预期值: ${data['predicted_value']}\n公布值: ${data['published_value']}\n对金银价格理论影响:${data['influnce']}\n公布时间: ${data['publish_time']}`;
                    detail_temp = `---\ntitle: ${data['publish_time']}资讯\ndate: ${data['publish_time']}\nlayout: post-scsj\n---\n${detail_body}`;
                }

                old_data.unshift(yaml_data);
                let json_string =  JSON.stringify(old_data);
                logger.info("开始写入文件，" + yaml_dir);
                fs.writeFile(yaml_dir, json_string, function(err, data){
                    if(err) {
                        logger.info('yaml error' + err);
                    }
                    else{
                        logger.info('yaml success' + data);
                    }
                });

                //写入详情
                if(detail_temp){
                    console.log(detail_dir);
                    detail_dir = path.join(detail_dir, yaml_data.id + ".md")
                    fs.writeFile(detail_dir, detail_temp, function(err, data){
                        if(err) {
                            logger.info('detail error' + err);
                        }
                        else{
                            logger.info('detail success' + data);
                        }
                    });
                }

                let values = [];
                Object.values(data).forEach(x=>(values.push("'"+x+"'")));

                let insert_sql = `insert into crawl_jin10_kuaixun(${Object.keys(data).join(',')}) values(${values.join(',')})`;
                mysqlconnection.query(insert_sql, function(err, rows, fields) {
                    if (err) logger.error('error sql: ' + insert_sql);
                    else{
                        logger.info('插入数据成功, ' + insert_sql);
                    }
                });
            }
        });
    }
    else if(msg_0 == 2) {
        let [type, dateid, body] = msg.split(msg);
        let update_sql = `update crawl_jin10_kuaixun set body='${body}' where dateid='${dateid}';`;
        mysqlconnection.query(update_sql, function(err, rows, fields) {
            if (err) throw err;
            logger.info('更新数据成功, ' + update_sql);
        });
    }
    else if(msg_0 == 7) {
        let [type, calendar_id, former_value] = msg.split('#');
        let update_sql = `update crawl_jin10_kuaixun set former_value='${former_value}' where calendar_id='${calendar_id}';`;
        mysqlconnection.query(update_sql, function(err, rows, fields) {
            if (err) throw err;
            logger.info('更新数据成功, ' + update_sql);
        });
    }
    else if(msg_0 == 4) {
        //广告过滤掉
        logger.info("过滤掉一个广告, " + msg);
    }
    else{
        //其他
        logger.info("无法解析类型, " + msg);
    }
});