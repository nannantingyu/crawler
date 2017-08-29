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

const serverArr = ['https://sshcdhpjfh.jin10.com:8080','https://sshibioeed.jin10.com:8082','https://sshibiealf.jin10.com:8081','https://sshibidkfk.jin10.com:8080','https://sshcdhpjle.jin10.com:8083','https://sshcdhpjne.jin10.com:8081','https://sshcdhgemp.jin10.com:8081','https://sshcdhpjnm.jin10.com:8081','https://sshibidkfk.jin10.com:8082','https://sshaekhdha.jin10.com:8083','https://sshcdhpjnm.jin10.com:8080','https://sshcdhpjig.jin10.com:8082','https://sshcdhpjod.jin10.com:8082','https://sshcdhgjaf.jin10.com:8083','https://sshibjpiog.jin10.com:8082','https://sshibjpiog.jin10.com:8081','https://sshahmgghj.jin10.com:8080','https://sshcdhpjig.jin10.com:8083','https://sshcdhpjig.jin10.com:8080','https://sshcdhpjeg.jin10.com:8081','https://sshcdhpjdf.jin10.com:8083','https://sshcdhpjeg.jin10.com:8080','https://sshcdhpjii.jin10.com:8080','https://sshcdhpjkl.jin10.com:8083','https://sshcdhpjfo.jin10.com:8082','https://sshcdhpjdf.jin10.com:8082','https://sshcdhpjfo.jin10.com:8080','https://sshcdhpjnb.jin10.com:8083','https://sshcdhpjfh.jin10.com:8082','https://sshcdhpjoj.jin10.com:8083','https://sshibiealf.jin10.com:8080','https://sshcdhpjne.jin10.com:8083','https://sshcdhpipi.jin10.com:8080','https://sshiemhiae.jin10.com:8080','https://sshcdhpjib.jin10.com:8080','https://sshibjgkdk.jin10.com:8080','https://sshaekhdha.jin10.com:8080','https://sshcdhpjnb.jin10.com:8081','https://sshahmgghj.jin10.com:8081','https://sshcdhpjnb.jin10.com:8080'];
const i = Math.floor(Math.random() * serverArr.length + 1) - 1, n = serverArr[i];
let socket = io(n);
let timeout = 3e4;
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
        request(url).pipe(fs.createWriteStream(dir + "/" + filename));
    });
};

socket.on('user message', function (msg) {
    msg_0 = msg.charAt(0);
    let now = moment().format("YYYY-MM-DD HH:mm:ss");

    if (msg_0 == 1 || msg_0 == 0) {
        let yaml_dir = path.join(config.crawl.yaml_dir, config.crawl.yaml_root);
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
                        if (err) throw err;

                        old_data = JSON.parse(JSON.stringify(rows));
                        fs.unlinkSync(yaml_dir);
                        logger.info('re qurey 成功');
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

                let yaml_data = null;
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
                        let filename = path.basename(url),
                            dirname = config.crawl.download_dir + moment().format("YYYYMMDD") + "/";
                        download(url, dirname, filename);
                        data['image'] = dirname + filename;
                        yaml_data['more'] = true;
                    }
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
                }

                old_data.push(yaml_data);
                let json_string =  JSON.stringify(old_data);
                fs.writeFile(yaml_dir, json_string, function(err, data){
                    if(err) {
                        console.log('yaml error', err);
                    }
                    else{
                        console.log('yaml success');
                    }
                })
                let values = [];
                Object.values(data).forEach(x=>(values.push("'"+x+"'")));

                let insert_sql = `insert into crawl_jin10_kuaixun(${Object.keys(data).join(',')}) values(${values.join(',')})`;
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
            }
        });
    }
    else if(msg_0 == 2) {
        let [type, dateid, body] = msg.split(msg);
        let update_sql = `update crawl_jin10_kuaixun set body='${body}' where dateid='${dateid}';`;
        mysqlconnection.query(update_sql, function(err, rows, fields) {
            if (err) throw err;
            console.log("add one");
            logger.info('更新数据成功, ' + update_sql);
        });
    }
    else if(msg_0 == 7) {
        let [type, calendar_id, former_value] = msg.split('#');
        let update_sql = `update crawl_jin10_kuaixun set former_value='${former_value}' where calendar_id='${calendar_id}';`;
        mysqlconnection.query(update_sql, function(err, rows, fields) {
            if (err) throw err;
            logger.info('更新数据成功, ' + update_sql);
            console.log("update one");
        });
    }
    else if(msg_0 == 4) {
        //广告过滤掉
        logger.info("过滤掉一个广告, " + msg);
        console.log("filter one");
    }
    else{
        //其他
        console.log("cannot one");
        logger.info("无法解析类型, " + msg);
    }
});