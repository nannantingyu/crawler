const mysql = require('mysql'),
    root_path = process.cwd(),
    path = require('path'),
    moment = require("moment"),
    redis = require('redis'),
    config = require(path.join(root_path, "config")),
    mysqlconnection = mysql.createConnection(config.mysql),
    redis_client = redis.createClient(config.redis.port, config.redis.server),
    fs = require('fs');

module.exports = {
    'parse_etf': function(data, dbname) {
        var sql = "", index = 0;
        build_etf(index, data, dbname, sql);
    },
    'parse_nonfarm_payrolls': function(data, dbname) {
        var sql = "", index = 0;
        build_nonfarm_payrolls(index, data, dbname, sql);
    }
}

function query_sql(sql) {
    mysqlconnection.query(sql, function(err, rows, fields){
        if(err) {
            console.log('insert failed, ', err);
        }
        else{
            console.log('insert success');
        }
    });
}

function build_etf(index, alldata, dbname, sql) {
    if(index < alldata.length) {
        var line = alldata[index], datatime = line.dataTime, data_line = line.datas;
        for(var name in data_line) {
            var total_inventory = data_line[name][0], increase = data_line[name][1], total_value = data_line[name][2], now = moment().format("YYYY-MM-DD HH:mm:ss");

            redis_client.sismember(dbname, datatime, function(is_in){
                redis_client.sadd(dbname, datatime);
                index ++;
                if(!is_in) {
                    sql += `insert into crawl_jin10_etf(cat_name, time, total_inventory, increase, total_value, updated_time, created_time) values('${name}', '${datatime}', '${total_inventory}', '${increase}', '${total_value}', '${now}', '${now}');`;
                }

                build_etf(index, alldata, dbname, sql);
            });
        }
    }
    else if(sql) {
        query_sql(sql);
    }
}

function build_nonfarm_payrolls(index, alldata, dbname, sql) {
    if(index < alldata.length) {
        var line = alldata[index], datatime = moment(line.date).format('YYYY-MM-DD 00:00:00'), data_line = line.datas;
        for(var name in data_line) {
            var former_value = data_line[name][0], pub_value = data_line[name][1], expected_value = data_line[name][2], now = moment().format("YYYY-MM-DD HH:mm:ss");

            redis_client.sismember(dbname, datatime, function(is_in){
                redis_client.sadd(dbname, datatime);
                index ++;
                if(!is_in) {
                    sql += `insert into crawl_jin10_nonfarm_payrolls(cat_name, time, former_value, pub_value, expected_value, updated_time, created_time) values('${name}', '${datatime}', '${former_value}', '${pub_value}', '${expected_value}', '${now}', '${now}');`;
                }

                build_nonfarm_payrolls(index, alldata, dbname, sql);
            });
        }
    }
    else if(sql) {
        query_sql(sql);
    }
}