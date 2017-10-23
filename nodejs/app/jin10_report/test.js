var db_info={
    name: 'jin10chart-database-20171001',
    version: 20171001,
    db: null
};

var version = version || 1;
var request = window.indexedDB.open(db_info.name, db_info.version);
request.onerror = function(e){
    console.log("connect db error");
    console.log(e.currentTarget.error.message);
};
request.onsuccess = function(e){
    console.log("connect db success");
    db_info.db = e.target.result;

    get_type();
};
request.onupgradeneeded = function(e){
    var db = e.target.result;
};

var all_types = [], all_data = {};
function get_type() {
    var db_obj_name = 'reportType';
    var transaction = db_info.db.transaction(db_obj_name, 'readwrite');
    var store = transaction.objectStore(db_obj_name);

    store.openCursor().onsuccess = function(event) {
        var cursor = event.target.result;
        if (cursor) {
            all_types.push(cursor.value);
            cursor.continue();
        }
        else {
            console.log("Got all data, ", all_types.length);
            for(var i = 0; i < all_types.length; i++) {
                all_data[all_types[i].name] = [];
                get_data(all_types[i].name);
            }
        }
    };
}

function get_data(objectStore) {
    console.log(objectStore);
    var transaction = db_info.db.transaction(objectStore, 'readwrite');
    var store = transaction.objectStore(objectStore);

    store.openCursor().onsuccess = function(event) {
        var cursor = event.target.result;
        if (cursor) {
            all_data[objectStore].push(cursor.value);
            cursor.continue();
        }
        else {
            window.callPhantom({name: objectStore, value: all_data[objectStore]});
        }
    };
}