var page = require('webpage').create();
page.open('https://www.btctrade.com/', function(status) {
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

page.onError = function(msg, trace) {
    var msgStack = ['btctrade ERROR: ' + msg];
    if (trace && trace.length) {
        msgStack.push('TRACE:');
        trace.forEach(function(t) {
            msgStack.push(' -> ' + t.file + ': ' + t.line + (t.function ? ' (in function "' + t.function +'")' : ''));
        });
    }

    console.error(msgStack.join('\n'));
};