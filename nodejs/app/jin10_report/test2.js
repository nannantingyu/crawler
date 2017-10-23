var webPage = require('webpage');
var page = webPage.create();

page.viewportSize = { width: 1920, height: 1080 };
page.open("https://datacenter.jin10.com/reportType/dc_cftc_merchant_currency", function start(status) {
    page.render('datacenter.jpeg', {format: 'jpeg', quality: '100'});
    phantom.exit();
});