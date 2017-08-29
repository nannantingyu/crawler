const moment = require("moment");
const fs = require('fs');
const argv = process.argv.slice(2);
const config = JSON.parse(fs.readFileSync(argv[0], 'utf-8'));
const log4js = require('log4js');
log4js.configure(config.log4js);
const logger = log4js.getLogger('jin10');
logger.warn('repair');
const path = require("path");
const mysql = require('mysql');

let yaml_dir = path.join(config.crawl.yaml_dir, config.crawl.yaml_root);
const mysqlconnection = mysql.createConnection(config.mysql);
mysqlconnection.connect();

mysqlconnection.query("select * from crawl_jin10_kuaixun where date(publish_time)='"+moment().format("YYYY-MM-DD")+"' order by publish_time asc limit 2", function(err, rows, fields) {
    if (err) throw err;

    console.log(JSON.stringify(rows));
    for(let row of rows) {
        //console.log(JSON.stringify(row));
        //console.log(row.id);
    }
    logger.info('re qurey³É¹¦');
});