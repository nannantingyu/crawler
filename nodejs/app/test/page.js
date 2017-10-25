var fs = require('fs'), report_dir = "data/jin10_report/";
var page = require('webpage').create();

page.open('https://datacenter.jin10.com/reportType/dc_etf_gold', function(status){
    console.log(status);
});