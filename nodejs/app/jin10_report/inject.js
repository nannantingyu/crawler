var index = 0, all_types = null, all_data = {};

chartIndexDb.getEntities("reportType", function(data){
    all_types = data;
    console.log(JSON.stringify(data));
    for(var i = 0; i < data.length; i ++) {
        get_data(data[i]['name']);
    }
});


function get_data(table) {
    chartIndexDb.getEntities(table, function(data){
        //window.callPhantom({name: table, value: data});
        all_data[table] = data;
        index ++;
        if(index == all_types.length) {
            window.callPhantom(all_data);
        }
    });
}
