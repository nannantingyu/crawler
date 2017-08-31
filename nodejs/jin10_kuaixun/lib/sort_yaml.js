const moment = require("moment"),
    fs = require('fs'),
    path = require('path'),
    root_path = path.dirname(__dirname);
const config = require(path.join(root_path, "config/config"));

let yaml_dir = path.join(config.crawl.yaml_dir, config.crawl.yaml_root), detail_dir = config.crawl.detail_dir;
fs.readFile(yaml_dir, function(err, file_data) {
    if (err) {
        console.log("Read old json file err, ", err);
    }
    else {
        let old_data = [];
        try {
            old_data = file_data.toString() ? Array.from(JSON.parse(file_data.toString())) : [];
            for(let dt of old_data) {
                console.log(dt.datetime);
            }
            old_data = old_data.sort(function(a, b) {
                return (a['datetime'] < b['datetime'])?1 : -1;
            });

            console.log("\n\n___________________\n\n");
            for(let dt of old_data) {
                console.log(dt.datetime);
            }

            let json_string =  JSON.stringify(old_data);
            console.log("开始写入文件，" + yaml_dir);
            fs.writeFile(yaml_dir, json_string, function(err, data){
                if(err) {
                    console.log('排序失败，' + err);
                }
                else{
                    console.log('排序成功');
                }
            });
        }
        catch (err) {
            console.log("No file at ", yaml_dir);
            console.log(err);
        }
    }
});