var page = require('webpage').create();
page.open('https://wallstreetcn.com/live/global', function(status) {
    if(status == "success") {
        page.injectJs("inject.js");
    }
});

page.onCallback = function(data) {
    console.log(JSON.stringify(data));
};

page.onLoadFinished = function(status) {

}