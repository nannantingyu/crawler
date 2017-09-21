//const spawn = require('child_process').spawn;
//
//var du = spawn('node', ['child.js']);
//du.stdout.on("data", function(data){
//    console.log(data.toString());
//    console.log(JSON.parse(data.toString()));
//});

const root_path = process.cwd(),
    path = require('path'),
    redis = require('redis'),
    config = require(path.join(root_path, "config"));

const redis_client = redis.createClient(config.redis.port, config.redis.server);

redis_client.set("a", null);