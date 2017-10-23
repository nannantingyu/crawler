//chartIndexDb.remove('dc_eia_crude_oil', '', function(d){
//    console.log("remove success")
//});

indexedDB.deleteDatabase('jin10chart-database-20171001');
chartIndexDb.close();
console.log('deleted');