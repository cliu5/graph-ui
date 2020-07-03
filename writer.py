weekly = "200619"
biweekly = "200626"
quarterly = "200626"
biquarterly = "200925"


def write(USD_USDT):
    header = """

<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width">
    <script src="https://d3js.org/d3.v4.min.js"></script>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <script src= "https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js"></script>
    <link rel ="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">

    <title> Open Interest </title>

    <!--
    <ul>
        <li><a id = "oi" href="/d3bitmex">Open Interest</a></li>
        <li><a href="/d3bitmexliquidations">Liquidations</a></li>
        <li><a href="/d3Prices">Prices</a></li>
        <li><a href="/d3Volume">Volume</a></li>
      </ul>

  </head>
  <body>
 
    <a id = "bitmex" href = "/d3bitmex"> bitmex </a>
    <a id = "binance" href = "/d3binance"> binance </a>
    <a id = "bybit" href = "/d3bybit"> bybit </a>
    <a id = "ftx" href = "/d3ftx"> FTX </a>
    <a id = "huobi" href = "/d3huobi"> huobi </a>
    <a id = "okex" href = "/d3okexUSDswap"> okex </a>
    <a id = "deribit" href = "/d3deribit"> deribit </a>

  -->
  <nav class="navbar navbar-expand-lg navbar-light bg-white py-3 shadow-sm">
    <div class="container">
      <a href="/d3bitmex" class="navbar-brand font-weight-bold">Data Visualization</a>
      <button type="button" data-toggle="collapse" data-target="#navbarContent" aria-controls="navbars" aria-expanded="false" aria-label="Toggle navigation" class="navbar-toggler">
                <span class="navbar-toggler-icon"></span>
            </button>
  
  
      <div id="navbarContent" class="collapse navbar-collapse">
        <ul class="navbar-nav mr-auto">
          <!-- Level one dropdown -->
          <li class="nav-item dropdown">
            <a id="dropdownMenu1" href="#" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" class="nav-link dropdown-toggle">Open Interest</a>
            <ul aria-labelledby="dropdownMenu1" class="dropdown-menu border-0 shadow">
              <li><a href="/d3bitmex" class="dropdown-item">Bitmex </a></li>
              <li><a href="/d3binance" class="dropdown-item">Binance</a></li>
              <li><a href="/d3bybit" class="dropdown-item">Bybit</a></li>
              <li><a href="/d3ftx" class="dropdown-item">FTX</a></li>
              <li><a href="/d3huobi" class="dropdown-item">Huobi</a></li>
              <li><a href="/d3deribit" class="dropdown-item">Deribit</a></li>
  
              <li class="dropdown-divider"></li>
  
              <!-- Level two dropdown-->
              <li class="dropdown-submenu">
                <a id="dropdownMenu2" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" class="dropdown-item dropdown-toggle">Okex</a>
                <ul aria-labelledby="dropdownMenu2" class="dropdown-menu border-0 shadow">
                  <li>
                    <a tabindex="-1" href="/d3okexUSDswap" class="dropdown-item">Coin Margined Swap</a>
                  </li>
  
               
  
                  <li><a href="/d3okexUSDTswap" class="dropdown-item">USDT Margined Swap</a></li>
                  <li><a href="/d3okexUSDfutures" class="dropdown-item">Coin Margined Futures</a></li>
                  <li><a href="/d3okexUSDTfutures" class="dropdown-item">USDT Margined Futures</a></li>
                </ul>
              </li>
              <!-- End Level two -->
              
              
            </ul>
          </li>

          <li class="nav-item dropdown">
            <a id="dropdownMenu5" href="#" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" class="nav-link dropdown-toggle"> Aggregative Open Interest</a>
                     <ul aria-labelledby="dropdownMenu5" class="dropdown-menu border-0 shadow">
                        <li><a href="/d3btc-oi" class="dropdown-item">BTC </a></li>
                        <li><a href="/d3eth-oi" class="dropdown-item">ETH</a></li>
                        <li><a href="/d3xrp-oi" class="dropdown-item">XRP</a></li>
                        <li><a href="/d3bch-oi" class="dropdown-item">BCH</a></li>
                        <li><a href="/d3bsv-oi" class="dropdown-item">BSV</a></li>
                        <li><a href="/d3ltc-oi" class="dropdown-item">LTC</a></li>
                        <li><a href="/d3bnb-oi" class="dropdown-item">BNB</a></li>
                        <li><a href="/d3trx-oi" class="dropdown-item">TRX</a></li>
                        <li><a href="/d3eos-oi" class="dropdown-item">EOS</a></li>
                       <!-- <li><a href="/d3ftxliquidations" class="dropdown-item">FTX</a></li>-->
                       
                       <!-- End Level two -->
                       
                       
                     </ul>
                     </li>
          <!-- End Level one -->
                  <li class="nav-item dropdown">
   <a id="dropdownMenu3" href="#" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" class="nav-link dropdown-toggle">Liquidations</a>
            <ul aria-labelledby="dropdownMenu3" class="dropdown-menu border-0 shadow">
              <li><a href="/d3bitmexliquidations" class="dropdown-item">Bitmex </a></li>
              <li><a href="/d3binanceliquidations" class="dropdown-item">Binance</a></li>
              <li><a href="/d3okexliquidations" class="dropdown-item">Okex</a></li>
              <li><a href="/d3ftxliquidations" class="dropdown-item">FTX</a></li>
              
              <!-- End Level two -->
              
              
            </ul>
            </li>
           
            <li class="nav-item dropdown">
   <a id="dropdownMenu4" href="#" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" class="nav-link dropdown-toggle">Volume</a>
            <ul aria-labelledby="dropdownMenu4" class="dropdown-menu border-0 shadow">
              <li><a href="/d3bitmexvolume" class="dropdown-item">Bitmex </a></li>
              
              <!-- End Level two -->
              
              
            </ul>
            </li>
         
          <li class="nav-item"><a href="/d3Prices" class="nav-link">Prices</a></li>

          <li class="nav-item"> <button> <a  id = "okex" class="nav-link">Refresh Okex</a></li> </button>
          
        </ul>
      </div>
    </div>
  </nav>
  <script>
      $(function() {
  // ------------------------------------------------------- //
  // Multi Level dropdowns
  // ------------------------------------------------------ //
  $("ul.dropdown-menu [data-toggle='dropdown']").on("click", function(event) {
    event.preventDefault();
    event.stopPropagation();

    $(this).siblings().toggleClass("show");


    if (!$(this).next().hasClass('show')) {
      $(this).parents('.dropdown-menu').first().find('.show').removeClass("show");
    }
    $(this).parents('li.nav-item.dropdown.show').on('hidden.bs.dropdown', function(e) {
      $('.dropdown-submenu .show').removeClass("show");
    });

  });
});
  </script>
  <style>
       ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
}
li {
  display: inline;
}
        body {
          font: 14px sans-serif;
          position: absolute;
          margin-left:40px;
        }
        
        .bar{
            fill: grey;
            opacity: .8;
        }
         
        .axis path,
        .axis line {
          fill: none;
          stroke: #000;
          shape-rendering: crispEdges;
        }
        
        .line {
  fill: none;
  stroke: steelblue;
  stroke-width: 2px;
}

.axisSteelBlue text{
  fill: steelblue;
}

.axisRed text{
  fill: red;
}
        
        .tooltip {
          position: absolute;
          width: 200px;
          height: 28px;
          pointer-events: none;
        }

      .dropdown-submenu {
  position: relative;
}

.dropdown-submenu>a:after {
  content: "\f0da";
  float: right;
  border: none;
}

.dropdown-submenu>.dropdown-menu {
  top: 0;
  left: 100%;
  margin-top: 0px;
  margin-left: 0px;
}
  </style>

  <body>


<br> okex BTC-""" + USD_USDT + "-" + weekly + """ OI in USD (converted from contracts)
<button id = "1h" onclick="update12('1h')">  1 Hour </button>
    <button id = "2h" onclick="update12('2h')">  2 Hours </button>
    <button id = "12h" onclick="update12('12h')">  12 Hours </button>
    <button id = "1d" onclick="update12('1d')">  1 Day </button>
    <button id = "1d" onclick="update12('3d')">  3 Days </button>
    <label>
        <input id="check12" type="checkbox" > Coin Denominated
      </label>

    <br>
    <svg id = "svg12" width="890" height="450"></svg>

   <script> 

    $(function() {
          $('a#okex').bind('click', function() {
            $.getJSON('/refresh_binance',
                function(data) {
            });
            return false;
          });
        });

        $(function() {
          $('a#oi').bind('click', function() {
            $.getJSON('/refresh_oi',
            
                function(data) {
            });
            return false;
          });
        });

    const svg12 = d3.select('#svg12');

    const xValue = d => d.date;
      const xLabel = 'Time';
      const yValue = d => d.value;
      const yLabel = 'Open Interest';
      const margin = { left: 100, right: 100, top: 20, bottom: 140 };
      var parseTime = d3.timeParse("%Y-%m-%dT%H:%M:%S");
      const width = svg12.attr('width');
      const height = svg12.attr('height');
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      var y1 = d3.scaleLinear().range([innerHeight, 0]);
      var x = d3.scaleTime().range([0, innerWidth])

      var valueline2 = d3.line()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y1(d.price); });

              

    function update12(selectedVar){
        var isChecked = document.getElementById("check12").checked;
        svg12.selectAll("*").remove();


if (isChecked){
    file_name = 'coin'
}
else{
    file_name = 'usd'
}
            

            //d3.selectAll('svg2 > *').remove();


      const g12 = svg12.append('g')
          .attr('transform', `translate(${margin.left},${margin.top})`);
      const xAxisG = g12.append('g')
          .attr('transform', `translate(0, ${innerHeight})`);
      const yAxisG = g12.append('g');

      xAxisG.append('text')
          .attr('class', 'axis-label')
          .attr('x', innerWidth / 2)
          .attr('y', 100)
          .text(xLabel);

      yAxisG.append('text')
          .attr('class', 'axis-label')
          .attr('x', -innerHeight / 2)
          .attr('y', -60)
          .attr('transform', `rotate(-90)`)
          .style('text-anchor', 'middle')
          .text(yLabel);


            const xScale = d3.scaleTime();
            const yScale = d3.scaleLinear();

            const xAxis = d3.axisBottom()
                .scale(xScale)
                .tickPadding(15)
                .tickSize(-innerHeight);

            const yAxis = d3.axisLeft()
                .scale(yScale)
                .ticks(5)
                .tickPadding(15)
                .tickSize(-innerWidth);
                
            
            const row = d => {
                d.date = new Date(d.date);
                d.value = +d.value;
                return d;
            };



        d3.csv("/static/js/open-interest-price/okex-" + selectedVar + "-BTC-""" + USD_USDT + "-" + weekly + """-open-interest-price.csv", function(error, data) {
      if (error) throw error;
    
      // format the data
      data.forEach(function(d) {
          d.date = parseTime(d.date);
          d.price = +d.price;
          d.oi = +d.oi;
      });
    
      // Scale the range of the data
      x.domain(d3.extent(data, function(d) { return d.date; }));
      y1.domain([d3.min(data, function(d) {return Math.min(d.price);}), d3.max(data, function(d) {return Math.max(d.price); })]);
    
      var tempWidth = innerWidth + 100 

      // Add the valueline2 path.
      svg12.append("path")
          .data([data])
          .attr("class", "line")
          .attr("id", "redLine12")
          .style("stroke", "red")
          .attr("d", valueline2)
          .attr("transform", "translate( 100" + ", 20 )");
    
    
      // Add the Y1 Axis
      svg12.append("g")
          .attr("class", "axisRed")
          .attr("transform", "translate( " + tempWidth + ", 20 )")
          .attr("id", "redAxis12")
          .call(d3.axisRight(y1));
    
    });
    

  // add the red line legend
  svg12.append("text")
     .attr("x", innerWidth + 40)             
     .attr("y", margin.top - 10)    
     .attr("class", "legend")
     .style("fill", "red")         
     .on("click", function(){
       // determine if current line is visible
       var active   = redLine12.active ? false : true,
       newOpacity = active ? 0 : 1;
       // hide or show the elements
       d3.select("#redLine12").style("opacity", newOpacity);
       d3.select("#redAxis12").style("opacity", newOpacity);
       // update whether or not the elements are active
       redLine12.active = active;
     })
     .text("Price Line");



        d3.csv('/static/js/open-interest/okex-' + selectedVar + '-BTC-""" + USD_USDT + "-" + weekly + """-open-interest-' +file_name+ '.csv', row, data => {
           xScale
            .domain(d3.extent(data, xValue))
            .range([0, innerWidth])
            .nice();

            yScale
            .domain(d3.extent(data, yValue))
            .range([innerHeight, 0])
            .nice();

            g12.selectAll('circle').data(data)
            .enter().append('circle')
                .attr('cx', d => xScale(xValue(d)))
                .attr('cy', d => yScale(yValue(d)))
                .attr('fill-opacity', .6)
                .attr('r', 5)
                .style("fill", "steelblue")
            
            xAxisG.call(xAxis);
            yAxisG.call(yAxis);
        });
      }
      update12('2h');
    </script>
    """

    svg = """
<br> okex BTC-""" + USD_USDT + "-" + biweekly + """OI in USD (converted from contracts)
<button id = "1h" onclick="update13('1h')">  1 Hour </button>
    <button id = "2h" onclick="update13('2h')">  2 Hours </button>
    <button id = "12h" onclick="update13('12h')">  12 Hours </button>
    <button id = "1d" onclick="update13('1d')">  1 Day </button>
    <button id = "1d" onclick="update13('3d')">  3 Days </button>
    <label>
        <input id="check13" type="checkbox" > Coin Denominated
      </label>
    <br>
    <svg id = "svg13" width="890" height="450"></svg>

   <script> 


    const svg13 = d3.select('#svg13');

   

    function update13(selectedVar){
        var isChecked = document.getElementById("check13").checked;


if (isChecked){
    file_name = 'coin'
}
else{
    file_name = 'usd'
}
            const width = svg13.attr('width');
      const height = svg13.attr('height');
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;
      
      svg13.selectAll("*").remove();

            //d3.selectAll('svg2 > *').remove();


      const g13 = svg13.append('g')
          .attr('transform', `translate(${margin.left},${margin.top})`);
      const xAxisG = g13.append('g')
          .attr('transform', `translate(0, ${innerHeight})`);
      const yAxisG = g13.append('g');

      xAxisG.append('text')
          .attr('class', 'axis-label')
          .attr('x', innerWidth / 2)
          .attr('y', 100)
          .text(xLabel);

      yAxisG.append('text')
          .attr('class', 'axis-label')
          .attr('x', -innerHeight / 2)
          .attr('y', -60)
          .attr('transform', `rotate(-90)`)
          .style('text-anchor', 'middle')
          .text(yLabel);


            const xScale = d3.scaleTime();
            const yScale = d3.scaleLinear();

            const xAxis = d3.axisBottom()
                .scale(xScale)
                .tickPadding(15)
                .tickSize(-innerHeight);

            const yAxis = d3.axisLeft()
                .scale(yScale)
                .ticks(5)
                .tickPadding(15)
                .tickSize(-innerWidth);
                
            
            const row = d => {
                d.date = new Date(d.date);
                d.value = +d.value;
                return d;
            };
            d3.csv("/static/js/open-interest-price/okex-" + selectedVar + "-BTC-""" + USD_USDT + "-" + biweekly + """-open-interest-price.csv", function(error, data) {
      if (error) throw error;
    
      // format the data
      data.forEach(function(d) {
          d.date = parseTime(d.date);
          d.price = +d.price;
          d.oi = +d.oi;
      });
    
      // Scale the range of the data
      x.domain(d3.extent(data, function(d) { return d.date; }));
      y1.domain([d3.min(data, function(d) {return Math.min(d.price);}), d3.max(data, function(d) {return Math.max(d.price); })]);
    
      var tempWidth = innerWidth + 100 

      // Add the valueline2 path.
      svg13.append("path")
          .data([data])
          .attr("class", "line")
          .attr("id", "redLine13")
          .style("stroke", "red")
          .attr("d", valueline2)
          .attr("transform", "translate( 100" + ", 20 )");
    
    
      // Add the Y1 Axis
      svg13.append("g")
          .attr("class", "axisRed")
          .attr("transform", "translate( " + tempWidth + ", 20 )")
          .attr("id", "redAxis13")
          .call(d3.axisRight(y1));
    
    });
    

  // add the red line legend
  svg13.append("text")
     .attr("x", innerWidth + 40)             
     .attr("y", margin.top - 10)    
     .attr("class", "legend")
     .style("fill", "red")         
     .on("click", function(){
       // determine if current line is visible
       var active   = redLine13.active ? false : true,
       newOpacity = active ? 0 : 1;
       // hide or show the elements
       d3.select("#redLine13").style("opacity", newOpacity);
       d3.select("#redAxis13").style("opacity", newOpacity);
       // update whether or not the elements are active
       redLine13.active = active;
     })
     .text("Price Line");


        d3.csv('/static/js/open-interest/okex-' + selectedVar + '-BTC-""" + USD_USDT + "-" + biweekly + """-open-interest-' +file_name+ '.csv', row, data => {
           xScale
            .domain(d3.extent(data, xValue))
            .range([0, innerWidth])
            .nice();

            yScale
            .domain(d3.extent(data, yValue))
            .range([innerHeight, 0])
            .nice();

            g13.selectAll('circle').data(data)
            .enter().append('circle')
                .attr('cx', d => xScale(xValue(d)))
                .attr('cy', d => yScale(yValue(d)))
                .attr('fill-opacity', .6)
                .attr('r', 5)
                .style("fill", "steelblue")
            
            xAxisG.call(xAxis);
            yAxisG.call(yAxis);
        });
      }
            update13('2h');

    </script>

    """

    isChecked = """
if (isChecked){
    file_name = 'coin'
}
else{
    file_name = 'usd'
}
    """

    axis = """ xAxisG.append('text')
          .attr('class', 'axis-label')
          .attr('x', innerWidth / 2)
          .attr('y', 100)
          .text(xLabel);

      yAxisG.append('text')
          .attr('class', 'axis-label')
          .attr('x', -innerHeight / 2)
          .attr('y', -60)
          .attr('transform', `rotate(-90)`)
          .style('text-anchor', 'middle')
          .text(yLabel);


            const xScale = d3.scaleTime();
            const yScale = d3.scaleLinear();

            const xAxis = d3.axisBottom()
                .scale(xScale)
                .tickPadding(15)
                .tickSize(-innerHeight);

            const yAxis = d3.axisLeft()
                .scale(yScale)
                .ticks(5)
                .tickPadding(15)
                .tickSize(-innerWidth);
                
            
            const row = d => {
                d.date = new Date(d.date);
                d.value = +d.value;
                return d;
            };
    """

    price = """  if (error) throw error;
    
      // format the data
      data.forEach(function(d) {
          d.date = parseTime(d.date);
          d.price = +d.price;
          d.oi = +d.oi;
      });
    
      // Scale the range of the data
      x.domain(d3.extent(data, function(d) { return d.date; }));
      y1.domain([d3.min(data, function(d) {return Math.min(d.price);}), d3.max(data, function(d) {return Math.max(d.price); })]);
    
      var tempWidth = innerWidth + 100 
    """

    counter = 0
    coins = ['BTC', 'LTC', 'ETH', 'ETC', 'XRP', 'EOS', 'BCH', 'BSV', 'TRX', 'ADA', 'DASH', 'LINK', 'NEO', 'XTZ', 'ZEC']
    tokens = []
    for coin in coins:
        #tokens.append(coin + '-USDT-' + 'SWAP')
        
        if coin == 'BTC':
            tokens.append(coin + '-'+ USD_USDT +'-' + quarterly)
            tokens.append(coin + '-'+ USD_USDT +'-' + biquarterly)
        else:
            tokens.append(coin + '-'+ USD_USDT +'-' + weekly)
            tokens.append(coin + '-'+ USD_USDT +'-' + biweekly)
            tokens.append(coin + '-'+ USD_USDT +'-' + quarterly)
            tokens.append(coin + '-'+ USD_USDT +'-' + biquarterly)
    
    path = "templates/"
    file_name = "d3okex" + USD_USDT + "futures.html"
    with open(path + file_name, 'w') as f:
        f.write(header)
        f.write(svg)
    for token in tokens:
        with open (path + file_name, 'a') as f:
            if(counter == 12):
                counter = 14
            f.write("<br> okex " + token + " in USD (converted from contracts) ")
            f.write("""<button id = "1h" onclick="update""" + str(counter) + """('1h')"> 1 Hour </button>""")
            f.write("""<button id = "2h" onclick="update""" + str(counter) + """('2h')"> 2 Hours </button>""")
            f.write("""<button id = "12h" onclick="update""" + str(counter) + """('12h')"> 12 Hours </button>""")
            f.write("""<button id = "1d" onclick="update""" + str(counter) + """('1d')"> 1 Day </button>""")
            f.write("""<button id = "3d" onclick="update""" + str(counter) + """('3d')"> 3 Days </button>""")
            f.write(""" <label> <input id = "check""" + str(counter) + """" type = "checkbox"> Coin Denominated </label> <br>""")
            f.write("""<svg id = "svg""" + str(counter) + """" width = "890" height = "450"> </svg> <script> const svg""" + str(counter) + """ = d3.select("#svg""" + str(counter) + """");""")
            f.write("""function update""" + str(counter) + "(selectedVar){")
            f.write("""var isChecked = document.getElementById("check""" + str(counter) + """").checked;""")
            f.write(isChecked)
            f.write("""const width = svg""" + str(counter) + """.attr('width'); \n""")
            f.write("""const height = svg""" + str(counter) + """.attr('height'); \n""")
            f.write(" const innerWidth = width - margin.left - margin.right; \n")
            f.write(" const innerHeight = height - margin.top - margin.bottom; \n")
            f.write("svg" + str(counter) + """.selectAll("*").remove(); \n""")
            f.write("const g" + str(counter) + "= svg" + str(counter) + """.append('g') \n""")
            f.write (""".attr('transform', `translate(${margin.left},${margin.top})`); \n""")
            f.write ("""const xAxisG = g""" + str(counter) + """.append('g') \n""")
            f.write(""" .attr('transform', `translate(0, ${innerHeight})`); \n""")
            f.write ("""const yAxisG = g""" + str(counter) + """.append('g') \n""")
            f.write(axis)
            f.write("""d3.csv("/static/js/open-interest-price/okex-" + selectedVar + "-""" + token + """-open-interest-price.csv", function(error,data){""")
            f.write(price)
            f.write("svg" + str(counter) + """.append("path")
                        .data([data])
                        .attr("class","line")
                        .attr("id", "redLine""" + str(counter) + """")
                        .style("stroke", "red")
                        .attr("d", valueline2)
                        .attr("transform", "translate( 100" + ",20)");
                    """)
            f.write("svg" + str(counter) + """.append("g")
                        .attr("class","axisRed")
                        .attr("transform", "translate( " + tempWidth + ", 20 )")
                        .attr("id", "redAxis""" + str(counter) + """")
                        .call(d3.axisRight(y1)); });
                    """)
            f.write("svg" + str(counter) + """.append("text")
                        .attr("x", innerWidth + 40)             
                        .attr("y", margin.top - 10)    
                        .attr("class", "legend")
                        .style("fill", "red")         
                        .on("click", function(){
                            var active = redLine""" + str(counter) + """.active ? false : true,
                            newOpacity = active ? 0 : 1;
                        d3.select("#redLine""" + str(counter) + """").style("opacity", newOpacity); 
                        d3.select("#redAxis""" + str(counter) + """").style("opacity", newOpacity);
                        redLine""" + str(counter) + """.active = active;})
                        .text("Price Line"); \n""")
            
            f.write("""d3.csv("/static/js/open-interest/okex-" + selectedVar + "-""" + token + """-open-interest-" + file_name + ".csv", row, data => {""")
            f.write ("""  xScale
            .domain(d3.extent(data, xValue))
            .range([0, innerWidth])
            .nice();

            yScale
            .domain(d3.extent(data, yValue))
            .range([innerHeight, 0])
            .nice();""")
            f.write("g" + str(counter) + """.selectAll('circle').data(data).enter().append('circle')
                        .attr('cx', d => xScale(xValue(d)))
                .attr('cy', d => yScale(yValue(d)))
                .attr('fill-opacity', .6)
                .attr('r', 5)
                .style("fill", "steelblue")
            
                xAxisG.call(xAxis);
                yAxisG.call(yAxis);
                });
                }
                """)
            f.write("update" + str(counter) + "('2h');""")
            f.write( "</script>" )
            counter += 1

    with open ("test.html", 'a') as f:
        f.write ("</body> </html>")


    
if __name__ == '__main__':
    write('USD')
    write('USDT')