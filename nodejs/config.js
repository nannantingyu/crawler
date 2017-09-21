const path = require('path'),
    root_path = path.join(path.dirname(__dirname), "nodejs");

module.exports = {
    "mysql": {
        "host": "127.0.0.1",
        "user": "root",
        "password": "abc123",
        "database": "crawl"
    },
    "log4js": {
        "appenders": {
            "jin10": {
                "type": "dateFile",
                "filename": path.join(root_path, "logs/jin10.log")
            },
            "message": {
                "type": "dateFile",
                "filename": path.join(root_path, "logs/message.log")
            },
            "fx678": {
                "type": "dateFile",
                "filename": path.join(root_path, "logs/fx678.log")
            },
            "wallstreet": {
                "type": "dateFile",
                "filename": path.join(root_path, "logs/wallstreet.log")
            }
        },
        "categories": {
            "default": { "appenders": ["jin10"], "level": "info" },
            "message": { appenders: ['message'], level: 'info' },
            "fx678": { appenders: ['fx678'], level: 'info' },
            "wallstreet": { appenders: ['wallstreet'], level: 'info' }
        }
    },
    "crawl": {
        "download_dir": path.join(root_path, "images"),
        "yaml_dir": path.join(root_path, "source"),
        "yaml_root": "scsj.yml",
        "detail_dir": path.join(root_path, "detail")
    },
    "redis": {
        "server": "127.0.0.1",
        "port": "6379"
    },
    "jin10_server_addr": ['https://sshcdhpjfh.jin10.com:8080','https://sshibioeed.jin10.com:8082','https://sshibiealf.jin10.com:8081','https://sshibidkfk.jin10.com:8080','https://sshcdhpjle.jin10.com:8083','https://sshcdhpjne.jin10.com:8081','https://sshcdhgemp.jin10.com:8081','https://sshcdhpjnm.jin10.com:8081','https://sshibidkfk.jin10.com:8082','https://sshaekhdha.jin10.com:8083','https://sshcdhpjnm.jin10.com:8080','https://sshcdhpjig.jin10.com:8082','https://sshcdhpjod.jin10.com:8082','https://sshcdhgjaf.jin10.com:8083','https://sshibjpiog.jin10.com:8082','https://sshibjpiog.jin10.com:8081','https://sshahmgghj.jin10.com:8080','https://sshcdhpjig.jin10.com:8083','https://sshcdhpjig.jin10.com:8080','https://sshcdhpjeg.jin10.com:8081','https://sshcdhpjdf.jin10.com:8083','https://sshcdhpjeg.jin10.com:8080','https://sshcdhpjii.jin10.com:8080','https://sshcdhpjkl.jin10.com:8083','https://sshcdhpjfo.jin10.com:8082','https://sshcdhpjdf.jin10.com:8082','https://sshcdhpjfo.jin10.com:8080','https://sshcdhpjnb.jin10.com:8083','https://sshcdhpjfh.jin10.com:8082','https://sshcdhpjoj.jin10.com:8083','https://sshibiealf.jin10.com:8080','https://sshcdhpjne.jin10.com:8083','https://sshcdhpipi.jin10.com:8080','https://sshiemhiae.jin10.com:8080','https://sshcdhpjib.jin10.com:8080','https://sshibjgkdk.jin10.com:8080','https://sshaekhdha.jin10.com:8080','https://sshcdhpjnb.jin10.com:8081','https://sshahmgghj.jin10.com:8081','https://sshcdhpjnb.jin10.com:8080']
}