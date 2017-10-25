const mysql = require('mysql'),
    root_path = process.cwd(),
    path = require('path'),
    moment = require("moment"),
    redis = require('redis'),
    config = require(path.join(root_path, "config")),
//mysqlconnection = mysql.createConnection(config.mysql),
    redis_client = redis.createClient(config.redis.port, config.redis.server),
    fs = require('fs');

function handleDisconnect() {
    mysqlconnection = mysql.createConnection(config.mysql);
    mysqlconnection.connect(function(err) {
        if(err) {
            console.log('error when connecting to db:', err);
            setTimeout(handleDisconnect, 2000);
        }
    });
    mysqlconnection.on('error', function(err) {
        console.log('db error', err);
        if(err.code === 'PROTOCOL_CONNECTION_LOST') {
            handleDisconnect();
        } else {
            throw err;
        }
    });
}

handleDisconnect();

var sql_queue = [], ind = 0, querying = false;

const maps = {
    'build_dc_cftc_merchant_currency': build_position,
    'build_dc_cftc_merchant_goods': build_position,
    'build_dc_lme_traders_report': build_position,
    'build_dc_cftc_nc_report': build_position,
    'build_dc_cftc_c_report': build_position,
    'build_dc_cme_fx_report': build_contract,
    'build_dc_cme_report': build_contract,
    'build_dc_cme_energy_report': build_contract,
    'build_dc_etf_sliver': build_etf,
    'build_dc_etf_gold': build_etf,
    'build_dc_lme_report': build_dc_lme_report,
    'build_dc_nonfarm_payrolls': build_dc_nonfarm_payrolls
};

function build(data, dbname) {
    redis_client.get(dbname, function(err, datedb){
        if(!datedb) {
            datedb = '19700101';
        }


        maps['build_' + dbname](0, data.filter(function(line){
            return line.date > datedb;
        }), dbname, '');
    });
}

module.exports = {
    'parse_etf': build,
    'parse_nonfarm_payrolls': function(data, dbname, cat_name) {
        var sql = "", index = 0;

        redis_client.get(dbname, function(err, datedb){
            if(!datedb) {
                datedb = '19700101';
            }

            build_dc_nonfarm_payrolls(index, data.filter(function(line){
                return line.date > datedb;
            }), dbname, cat_name, sql);
        });


    },
    'parse_cme_energy_report': build,
    'parse_cftc_nc_report': build,
    'parse_cftc_c_report': build,
    'parse_cme_report': build,
    'parse_cme_fx_report': build,
    'parse_lme_report': build,
    'parse_lme_traders_report': build,
    'parse_cftc_merchant_goods': build,
    'parse_cftc_merchant_currency': build
}

function build_position(index, alldata, dbname, sql) {
    if(index < alldata.length) {
        var line = alldata[index], datatime = moment(line.date).format('YYYY-MM-DD 00:00:00'), data_line = line.datas, tb_name = 'crawl_jin10_' + dbname.replace('dc_', '');

        redis_client.get(dbname, function(err, dt){
            if(line.date > dt) {
                redis_client.set(dbname, line.date);
            }

            index ++;
            for(var name in data_line) {
                var long_positions = data_line[name][0],
                    short_position = data_line[name][1], now = moment().format("YYYY-MM-DD HH:mm:ss");

                sql += `insert into ${tb_name}(cat_name, time, long_positions, short_position, updated_time, created_time) values('${name}', '${datatime}', '${long_positions}', '${short_position}', '${now}', '${now}');`;
            }

            build_position(index, alldata, dbname, sql);
        });
    }
    else if(sql) {
        console.log(maps['build_' + dbname]);
        query_sql(sql);
    }
    else{
        check_and_exit();
    }
}

function check_and_exit() {
    ind ++;
    if(ind >= 12) {
        process.exit();
    }
}

function query_sql(sql) {
    console.log("add sql");

    if(sql) {
        sql_queue.push(sql);
    }

    if(!querying && sql_queue.length > 0) {
        querying = true;
        all_sql = sql_queue.pop();
        //sql_queue.length = 0;

        mysqlconnection.query(all_sql, function(err, rows, fields){
            if(err) {
                console.log('insert failed, ');
                fs.appendFile('err.log', err, function(err, data){ console.log('write err to file;'); })
            }
            else{
                console.log('insert success');
            }

            querying = false;

            if(sql_queue.length > 0) {
                query_sql();
            }
            else if(ind >= 12){
                process.exit();
            }
        });

        //fs.writeFile("sql_" + ind, all_sql, function(err, data){
        //    console.log("write sql");
        //});

        ind ++;
    }
}

function build_dc_lme_report(index, alldata, dbname, sql) {
    if(index < alldata.length) {
        var line = alldata[index], datatime = moment(line.date).format('YYYY-MM-DD 00:00:00'), data_line = line.datas;

        redis_client.get(dbname, function(err, dt){
            if(line.date > dt) {
                redis_client.set(dbname, line.date);
            }

            index ++;
            for(var name in data_line) {
                var stock = data_line[name][0],
                    registered_warehouse_receipt = data_line[name][1], canceled_warehouse_receipt = data_line[name][2], now = moment().format("YYYY-MM-DD HH:mm:ss");

                sql += `insert into crawl_jin10_lme_report(cat_name, time, stock, registered_warehouse_receipt, canceled_warehouse_receipt, updated_time, created_time) values('${name}', '${datatime}', '${stock}', '${registered_warehouse_receipt}', '${canceled_warehouse_receipt}', '${now}', '${now}');`;
            }

            build_dc_lme_report(index, alldata, dbname, sql);
        });
    }
    else if(sql) {
        console.log(maps['build_' + dbname]);
        query_sql(sql);
    }
    else{
        check_and_exit();
    }
}

function build_contract(index, alldata, dbname, sql){
    if(index < alldata.length) {
        var line = alldata[index], datatime = moment(line.date).format('YYYY-MM-DD 00:00:00'), data_line = line.datas, tb_name = 'crawl_jin10_' + dbname.replace('dc_', '');

        redis_client.get(dbname, function(err, dt){
            if(line.date > dt) {
                redis_client.set(dbname, line.date);
            }

            index ++;
            for(var name in data_line) {
                var cat = name.split('-'), cat_name = cat[0], type_name = cat[1], transaction_contract = data_line[name][0],
                    inside_closing_contract = data_line[name][1], outside_closing_contract = data_line[name][2],
                    volume = data_line[name][3], open_contract = data_line[name][4], position_change = data_line[name][5], now = moment().format("YYYY-MM-DD HH:mm:ss");

                sql += `insert into ${tb_name}(cat_name, type_name, time, transaction_contract, inside_closing_contract, outside_closing_contract, volume, open_contract, position_change, updated_time, created_time) values('${cat_name}', '${type_name}', '${datatime}', '${transaction_contract}', '${inside_closing_contract}', '${outside_closing_contract}', '${volume}', '${open_contract}', '${position_change}', '${now}', '${now}');`;
            }

            build_contract(index, alldata, dbname, sql);
        });
    }
    else if(sql) {
        console.log(maps['build_' + dbname]);
        query_sql(sql);
    }
    else{
        check_and_exit();
    }
}

function build_etf(index, alldata, dbname, sql) {
    if(index < alldata.length) {
        var line = alldata[index], datatime = line.dataTime, data_line = line.datas;

        redis_client.get(dbname, function(err, dt) {
            if (line.date > dt) {
                redis_client.set(dbname, line.date);
            }

            for(var name in data_line) {
                var total_inventory = data_line[name][0], increase = data_line[name][1], total_value = data_line[name][2], now = moment().format("YYYY-MM-DD HH:mm:ss");
                sql += `insert into crawl_jin10_etf(cat_name, time, total_inventory, increase, total_value, updated_time, created_time) values('${name}', '${datatime}', '${total_inventory}', '${increase}', '${total_value}', '${now}', '${now}');`;
            }

            index ++;
            build_etf(index, alldata, dbname, sql);
        });
    }
    else if(sql) {
        console.log(maps['build_' + dbname]);
        query_sql(sql);
    }
    else{
        check_and_exit();
    }
}

function build_dc_nonfarm_payrolls(index, alldata, dbname, cat_name, sql) {
    if(index < alldata.length) {
        var line = alldata[index], datatime = moment(line.date).format('YYYY-MM-DD 00:00:00'), data_line = line.datas;

        redis_client.get(dbname, function(err, dt) {
            if (line.date > dt) {
                redis_client.set(dbname, line.date);
            }

            index ++;
            for(var name in data_line) {
                var former_value = data_line[name][0], pub_value = data_line[name][1], expected_value = data_line[name][2], now = moment().format("YYYY-MM-DD HH:mm:ss");
                sql += `insert into crawl_jin10_nonfarm_payrolls(cat_name, time, former_value, pub_value, expected_value, updated_time, created_time) values('${cat_name}', '${datatime}', '${former_value}', '${pub_value}', '${expected_value}', '${now}', '${now}');`;
            }

            build_dc_nonfarm_payrolls(index, alldata, dbname, cat_name, sql);
        });
    }
    else if(sql) {
        console.log(maps['build_' + dbname]);
        query_sql(sql);
    }
    else{
        check_and_exit();
    }
}
