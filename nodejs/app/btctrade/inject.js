const moneyconfig = {coin:"rmb", sign:"￥"};
function ua_refresh(){
    if(rate_timer == 3){
        $.get('/coin/' + moneyconfig.coin + '/rate.js?t=' + btvsn, function(d){
            window.callPhantom({
                message: d
            });

            for(var coin in d) {
                console.log(coin, d);
            }
        }, 'json');
        rate_timer = 0;
    }
    else{
        rate_timer++;
    }
}