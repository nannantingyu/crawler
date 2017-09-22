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

page.onError = function(msg, trace) {
    var msgStack = ['wallstreetcn ERROR: ' + msg];
    if (trace && trace.length) {
        msgStack.push('TRACE:');
        trace.forEach(function(t) {
            msgStack.push(' -> ' + t.file + ': ' + t.line + (t.function ? ' (in function "' + t.function +'")' : ''));
        });
    }

    console.error(msgStack.join('\n'));
};