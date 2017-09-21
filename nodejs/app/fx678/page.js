var page = require('webpage').create();
page.open('http://kx.fx678.com/', function(status) {
});

page.onCallback = function(data) {
    message = data['message'];
    console.log(JSON.stringify({"type": "data", "data": message}));
};

page.onLoadFinished = function(status) {
    console.log(JSON.stringify({"type": "message", "data": "load success"}));
    if(status == "success") {
        page.injectJs("inject.js");
    }
}