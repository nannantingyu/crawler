var fs = require('fs'), report_dir = "data/jin10_report/";
var page = require('webpage').create(),
    page_queue = [
        'https://datacenter.jin10.com/reportType/dc_etf_gold',
        //'https://datacenter.jin10.com/reportType/dc_etf_sliver',
        //'https://datacenter.jin10.com/reportType/dc_nonfarm_payrolls',
        //'https://datacenter.jin10.com/reportType/dc_eia_crude_oil',
        //'https://datacenter.jin10.com/reportType/dc_cme_energy_report',
        //'https://datacenter.jin10.com/reportType/dc_cftc_nc_report',
        //'https://datacenter.jin10.com/reportType/dc_cftc_c_report',
        //'https://datacenter.jin10.com/reportType/dc_cme_report',
        //'https://datacenter.jin10.com/reportType/dc_cme_fx_report',
        //'https://datacenter.jin10.com/reportType/dc_lme_report',
        //'https://datacenter.jin10.com/reportType/dc_lme_traders_report',
        //'https://datacenter.jin10.com/reportType/dc_cftc_merchant_goods',
        //'https://datacenter.jin10.com/reportType/dc_cftc_merchant_currency'
    ];

var page_index = 0;
function callback(status){
    //console.log(status);
}

page.open(page_queue[page_index], callback);

page.onLoadFinished = function(status){
    page_index ++;
    //console.log(page_index, status, page_queue[page_index]);
    if(page_index < page_queue.length) {
        setTimeout(function(){
            //console.log(page_queue[page_index]);
            page.open(page_queue[page_index], callback);
        }, 2000);
    }
    else {
        page.injectJs("inject.js");
        //page.injectJs("delete.js");
    }
};

page.onCallback = function(data) {
    console.log(JSON.stringify(data));
    phantom.exit();
};

page.onConsoleMessage = function(msg, lineNum, sourceId) {
    //console.log(msg);
};

page.onError = function(msg, trace) {
    var msgStack = ['jin10_report ERROR: ' + msg];
    if (trace && trace.length) {
        msgStack.push('TRACE:');
        trace.forEach(function(t) {
            msgStack.push(' -> ' + t.file + ': ' + t.line + (t.function ? ' (in function "' + t.function +'")' : ''));
        });
    }

    console.error(msgStack.join('\n'));
};
