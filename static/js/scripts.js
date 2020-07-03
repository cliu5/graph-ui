var prices;
var open_interest;
var comparisons;
var liquidations;
var dates;
var standard_prices;

function percent(list){
  var per = [];
  per.push(list[0]);
  for (var i=1;i<list.length;i++) {
    var change = Math.round(((list[i]-list[i-1])/list[i-1]) * 10000)/100
    if (change>0) {
      change='+' + change
    }
    per.push(change+'%') }
  return per;
}

function return_keys(dict){
  var keys = [];
  for (var key in dict){
    keys.push(key)
  };
  return keys;
}

function return_standard_prices(prices){
  var standard_prices = {};
  for (var coin in prices){
    standard_prices[coin] = {};
    for (var exchange in prices[coin]){
      standard_prices[coin][exchange] = {};
      var index='';
      if (exchange=='bitmex'){
        if (coin=='BTC'){
          index='XBTUSD';
        }else if (coin=='ETH'){
          index=coin+'USD';
        }
        else{
          index=coin+'H20';
        }
      }
      else if (exchange=='okex'){
        index = coin+ '-USD-SWAP';
      }
      else if (exchange=='binance'){
        index = coin+ 'USDT';
      }
      else if (exchange=='bybit'){
        index = coin+ 'USD';
      }
      else if (exchange=='deribit'){
        index = coin+ '-PERPETUAL';
      }
      else{
        index = coin;
      }
      // console.log(index);
      standard_prices[coin][exchange] = prices[coin][exchange][index];
    }
  }
  return standard_prices;
}

function return_values_last(dict,coin){
  var values = [];
  for (var key in dict){
    var times = return_keys(dict[key]);
    var length = times.length;
    // values.push(dict[key][times[length-1]]['price']);
    if (length==0){
      values.push(0);
    }
    else{
      values.push(dict[key][times[length-1]]['price']);
    }
  }
  return values;
}

function return_values_comparisons_last(dict){
  var values = [];
  for (var key in dict){
    var times = return_keys(dict[key]);
    var length = times.length;
    // values.push(dict[key][times[length-1]]);
    if (length==0){
      values.push(0);
    }
    else{
      values.push(dict[key][times[length-1]]);
    }
  }
  return values;
}

function return_values_price(dict){
  var values = [];
  for (var key in dict){
    values.push(dict[key]['price'])
  }
  return values;
}

function return_values(dict){

  var values = [];
  for (var key in dict){

    values.push(dict[key]);
  }
  return values;
}

function return_zero(dict) {
  var values=[]
  for (var key in dict){
    if (dict[key]==0){
      values.push(key);
    }
  }
  return values;
}

function repeat(arr, n){
  var a = [];
  for (var i=0;i<n;[i++].push.apply(a,arr));
  return a;
}

function return_hour(timestamp){
  // returns hours since
  var now = new Date();
  //calibrated for 5 hours ahead, but there's something different with the aws timezone
  var secondsSinceEpoch = Math.round(now.getTime() / 1000) + 18000;
  // var secondsSinceEpoch = Math.round(now.getTime() / 1000);
  var t = (secondsSinceEpoch - timestamp)/3600;
  return t;
}

function refresh(emit_name,timeout){
  socket.emit(emit_name);
  setTimeout(refresh, timeout);
}

//can better be done with panda dataframes (fill in previous gaps)

function fill_in_gaps(a,b){
  // a = prices[graph][exchange][trace]
  // b = open_interest[exchange][graph][trace]

  var a_times = return_keys(a);
  var last_time = a_times[0];
  if (a.length != 0){
    for (var time in b){
      if (!a_times.includes(time)){
        a[time] = a[last_time];
      }
      last_time = time;
    }
}

  if (b.length !=0){
    var b_times = return_keys(b);
    var last_time = b_times[0];
    for (var time in a){
      if (!b_times.includes(time)){
        b[time] = b[last_time];
      }
      last_time = time;
    }
}
}

var socket = io.connect('http://' + document.domain + ':' + location.port);

// socket.on('draw_graphs', function(msg) {
//   prices = JSON.parse(JSON.stringify(msg['prices']));
//   open_interest = JSON.parse(JSON.stringify(msg['open_interest']));
//   liquidations = JSON.parse(JSON.stringify(msg['liquidations']));
//   comparisons = JSON.parse(JSON.stringify(msg['comparisons']));
//
//   // if (!$( "all-open-interests" ).hasClass( "hidden" )){
//   //   init_aggregate();
//   // }
//   // else if (!$( "all-liquidations" ).hasClass( "hidden" )){
//   //   init_liquidations();
//   // }
//   // else{
//   //   init_prices();
//   // }
// });
