const argv = process.argv.slice(2),
    moment = require("moment"),
    path = require('path'),
    root_path = process.cwd(),
    log4js = require('log4js'),
    request = require("request"),
    url = require('url'),
    fs = require('fs'),
    config = require(path.join(root_path, "config")),
    forever = require('forever-monitor'),
    redis = require('redis'),
    redis_client = redis.createClient(config.redis.port, config.redis.server),
    report_saver = require(path.join(root_path, "app/jin10_report/report_saver")),
    tmp_file = path.join(root_path, "data/jin10_report/all_data.json");

log4js.configure(config.log4js);
const logger = log4js.getLogger('jin10report');

if(fs.existsSync(tmp_file)) {
    fs.unlinkSync(tmp_file);
}

var child_process = require('child_process');
var spawnObj = child_process.spawn('phantomjs', [path.join(root_path, 'app/jin10_report/page.js')], {encoding: 'utf-8'});

spawnObj.stdout.on('data', function(content) {
    var content = content.toString();
    fs.appendFileSync(tmp_file, content, 'utf8');
});
spawnObj.stderr.on('data', (data) => {
    logger.error(`jin10_report 发生错误，时间${moment().format("YYYY-MM-DD HH:mm:ss")}, 错误：${data}`);
    try{
	console.log(spawnObj);
        //process.kill(child.child.pid);
    }
    catch(error) {
        logger.error(`jin10_report kill pid ${child.child.pid} 失败，时间${moment().format("YYYY-MM-DD HH:mm:ss")}, 错误：${data}`);
    }
});
spawnObj.on('close', function(code) {
    console.log('close code : ' + code);
    //process.exit();
});

spawnObj.on('exit', (code) => {
    logger.error(`jin10_report 脚本退出，时间${moment().format("YYYY-MM-DD HH:mm:ss")}`);
    fs.readFile(tmp_file, 'utf8', function(err, data){
        data = JSON.parse(data);

        report_saver.parse_etf(data['dc_etf_sliver'], 'dc_etf_sliver');
        report_saver.parse_etf(data['dc_etf_gold'], 'dc_etf_gold');
        report_saver.parse_nonfarm_payrolls(data['dc_nonfarm_payrolls'], 'dc_nonfarm_payrolls', '美国非农就业人数');
        report_saver.parse_nonfarm_payrolls(data['dc_eia_crude_oil'], 'dc_eia_crude_oil', '美国EIA原油库存(万桶)');
        report_saver.parse_cme_energy_report(data['dc_cme_energy_report'], 'dc_cme_energy_report');

        report_saver.parse_cftc_nc_report(data['dc_cftc_nc_report'], 'dc_cftc_nc_report');
        report_saver.parse_cftc_c_report(data['dc_cftc_c_report'], 'dc_cftc_c_report');
        report_saver.parse_cme_report(data['dc_cme_report'], 'dc_cme_report');
        report_saver.parse_cme_fx_report(data['dc_cme_fx_report'], 'dc_cme_fx_report');
        report_saver.parse_lme_report(data['dc_lme_report'], 'dc_lme_report');
        report_saver.parse_lme_traders_report(data['dc_lme_traders_report'], 'dc_lme_traders_report');
        report_saver.parse_cftc_merchant_goods(data['dc_cftc_merchant_goods'], 'dc_cftc_merchant_goods');
        report_saver.parse_cftc_merchant_currency(data['dc_cftc_merchant_currency'], 'dc_cftc_merchant_currency');
    });
});

//var child = forever.start([ 'phantomjs', path.join(root_path, 'app/jin10_report/page.js') ], {
//    max : 1,
//    silent : true
//});
//
//child.on('stderr', function(data) {
//    logger.error(`jin10_report 发生错误，时间${moment().format("YYYY-MM-DD HH:mm:ss")}, 错误：${data}`);
//    try{
//        process.kill(child.child.pid);
//    }
//    catch(error) {
//        logger.error(`jin10_report kill pid ${child.child.pid} 失败，时间${moment().format("YYYY-MM-DD HH:mm:ss")}, 错误：${data}`);
//    }
//
//    child.stop();
//});
//
//child.on('exit:code', function(code) {
//    logger.error(`jin10_report 脚本退出，时间${moment().format("YYYY-MM-DD HH:mm:ss")}`);
//    fs.readFile(tmp_file, 'utf8', function(err, data){
//        data = JSON.parse(data);
//
//        report_saver.parse_etf(data['dc_etf_sliver'], 'dc_etf_sliver');
//        report_saver.parse_etf(data['dc_etf_gold'], 'dc_etf_gold');
//        report_saver.parse_nonfarm_payrolls(data['dc_nonfarm_payrolls'], 'dc_nonfarm_payrolls', '美国非农就业人数');
//        report_saver.parse_nonfarm_payrolls(data['dc_eia_crude_oil'], 'dc_eia_crude_oil', '美国EIA原油库存(万桶)');
//        report_saver.parse_cme_energy_report(data['dc_cme_energy_report'], 'dc_cme_energy_report');
//
//        report_saver.parse_cftc_nc_report(data['dc_cftc_nc_report'], 'dc_cftc_nc_report');
//        report_saver.parse_cftc_c_report(data['dc_cftc_c_report'], 'dc_cftc_c_report');
//        report_saver.parse_cme_report(data['dc_cme_report'], 'dc_cme_report');
//        report_saver.parse_cme_fx_report(data['dc_cme_fx_report'], 'dc_cme_fx_report');
//        report_saver.parse_lme_report(data['dc_lme_report'], 'dc_lme_report');
//        report_saver.parse_lme_traders_report(data['dc_lme_traders_report'], 'dc_lme_traders_report');
//        report_saver.parse_cftc_merchant_goods(data['dc_cftc_merchant_goods'], 'dc_cftc_merchant_goods');
//        report_saver.parse_cftc_merchant_currency(data['dc_cftc_merchant_currency'], 'dc_cftc_merchant_currency');
//    });
//});
//
//child.on('restart', function() {
//    logger.error(`jin10_report 重启脚本${argvs[0]}第${child.times}次，【错误发生】，时间：${moment().format("YYYY-MM-DD HH:mm:ss")}`);
//});
//
//child.on('stdout', function (content) {
//    var content = content.toString();
//    fs.appendFileSync(tmp_file, content, 'utf8');
//});
