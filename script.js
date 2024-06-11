var onsen_list = [];
d3.csv("merged_onsen_info.csv", function(data){
    data.forEach(function(d){
        d["kounou"] = kounou(d)
        onsen_list.push(d);
    })
    console.log(onsen_list);

    function kounou(d){
        kounou_list = [];
        if (d.tanjun=="True") kounou_list.push("単純");
        if (d.enka=="True") kounou_list.push("塩化");
        if (d.tansan=="True") kounou_list.push("炭酸");
        if (d.iou=="True") kounou_list.push("硫黄");
        if (d.housya=="True") kounou_list.push("放射能");
        if (d.ryusan=="True") kounou_list.push("硫酸");
        if (d.sansei=="True") kounou_list.push("酸性");
        if (d.gantetsu=="True") kounou_list.push("含鉄");
        if (d.nisan=="True") kounou_list.push("二酸");
        if (d.youso=="True") kounou_list.push("ヨウ素");
        if (kounou_list.length == 0) kounou_list.push("なし");
        return kounou_list;
    }
    

    function dashboard(id, fData){
        var width_m = 600;
        var height_m = 600;
        var color_m = d3.scale.category20();
        var projection_m = d3.geo.mercator()
                            .center([137, 38])
                            .translate([width_m/2, height_m/2])
                            .scale(1200);

        var path_m = d3.geo.path().projection(projection_m);
        
        var svg_m = d3.select(".left").append("svg")
                    .attr("class", "content_m")
                    .attr("min-x", 0)
                    .attr("min-y", 0)
                    .attr("width", width_m)
                    .attr("height", height_m);

        var svg_t = d3.select(".up-right").append("svg")
                    .attr("class", "content_t")
                    .attr("min-x", 0)
                    .attr("min-y", 0)
                    .attr("width", 300)
                    .attr("height", 200);

        svg_t.append("rect")
                    .attr("class", "background")
                    .attr("stroke", "black")
                    .attr("width", 300)
                    .attr("height", 200);
        
        var margin_d = { top: 10, right: 10, bottom: 10, left: 20 };
        var width_d = 500 - margin_d.left - margin_d.right;
        var height_d = 350 - margin_d.top - margin_d.bottom;

        var svg_d = d3.select(".down-right").append("svg")
                    .attr("class", "content_d")
                    .attr("min-x", 0)
                    .attr("min-y", 800)
                    .attr("width", 500)
                    .attr("height", 350)
                    .append("g")
                    .attr("transform", "translate(" + margin_d.left + "," + margin_d.top + ")");

        svg_d.append("rect")
            .attr("class", "background")
            .attr("stroke", "black")
            .attr("width", width_d)
            .attr("height", height_d);
                    
        d3.json("./jp_city.l.topojson", function(v){

            var zoom = d3.behavior.zoom()
            .translate(projection_m.translate())
            .scale(projection_m.scale())
            .scaleExtent([height_m, 9 * height_m])
            .on("zoom", zoomed);


            var target = d3.selectAll("#btn1")
                .on("click", reset);

            var group_m = svg_m
                .append("g")
                .call(zoom);

            var japan = topojson.feature(v, v.objects.city);


            group_m.selectAll("path").data(japan.features)
                .enter()
                .append("path")
                .attr("d", path_m)
                .attr("class", "area")
                .attr("stroke", "white")
                .attr("stroke-width", 0.3)
                .attr("fill","#9ACD32");

            group_m.append("rect")
                .attr("class", "background")
                .attr("stroke", "black")
                .attr("fill", "aqua")
                .attr("width", width_m)
                .attr("height", height_m);

            var tip_m = d3.tip()
                    .attr('class', 'd3-tip')
                    .offset([-3, 0])
                    // .style("position", "absolute")
                    .style("left", '300px')
                    .style("top", "40px")
                    .html(function(d) {
                    return ("<a href="+d.link+" target='_blank'>"+d.name +"</a><br>成分: "+d.kounou);
                })
                    .style("width", "200px")
                    .style("height", "50px");
            
            svg_m.call(tip_m);

            
            
            var pin = svg_m.selectAll(".pin")
                        .data(onsen_list)
                        .enter().append("circle", ".pin")
                        // .attr("class", function(d) {return d.name})
                        .attr("id", function(d) {return [d.kounou, d.name]})
                        .attr("r", 3)
                        .attr("stroke", "gray")
                        .attr("fill", function(d){ return color_m(d.kounou[0])})
                        .attr("visibility", "visible")
                        .attr("transform", function(d) {
                        return "translate(" + projection_m([
                            d.longitude,
                            d.latitude
                        ]) + ")";
                        })
                        .on('mouseover', mouseover)
                        .on('click', click);	

            console.log(pin);

            var checkboxes = d3.selectAll(".checkpin")
            checkboxes.on("click", checking);
    
            function checking(event) {
                    d3.selectAll(".rankbar").remove();
                    pin.attr("visibility", "visible");
                    
                    checkboxes[0].forEach(function (value) {
                        if(value.checked == true) {
                        pin.each(function (d) {
                            if (this.id.includes(value.id) != 1) {
                                d3.select(this).attr("visibility", "hidden");
                            }
                        })
                }
                })

                   
            }

            function mouseover(d){
                pin.attr("r", 3).attr("stroke", "gray");
                d3.select(this).attr("r", 7).attr("stroke", "black");
                svg_d.selectAll(".detail")
                    .remove();
                svg_t.selectAll(".detail")
                    .remove();
                var bar_dataset = [];
                const keys = Object.keys(d);
                const values = Object.values(d);
                for (let i = 0; i < keys.length; i++){
                    if ((i >= 53 && i < 108) && (d[keys[i]] != 0)){
                        bar_dataset.push({"name" :keys[i], "value" : d[keys[i]]});
                    }
                }

                var bar_width = 30;
                const arymax = function(a, b){ return Math.max(a, b)};

                var x_d = d3.scale.sqrt()
                                .domain([0.0, values.slice(53, 107).reduce(arymax)])
                                .range([0, 400]);

                var y_d = d3.scale.ordinal()
                                .domain(bar_dataset.map(function(dx){return dx["name"]}))
                                .rangeRoundBands([0, Math.min(bar_width*bar_dataset.length, 270)], .1);

                var xAxis = d3.svg.axis()
                                .scale(x_d)
                                .orient("top")
                                .ticks(5);

                var yAxis = d3.svg.axis()
                                .scale(y_d)
                                .orient("left");

                svg_d.append("g")
                    .attr("class", "detail")
                    .attr("transform", "translate(" + 50 + "," + 40 + ")")
                    .call(xAxis);
                
                svg_d.append("g")
                    .attr("class", "detail")
                    .attr("transform", "translate(" + 50 + "," + 40 + ")")
                    .call(yAxis);

                var bar = svg_d.selectAll("rect")
                                .data(bar_dataset)
                                .enter()
                                .append("rect");

                svg_d.append("g")
                    .selectAll("rect")
                    .data(bar_dataset)
                    .enter()
                    .append("rect")
                    .attr("class", "detail")
                    .attr("x", 0)
                    .attr("y", function(dx) {return y_d(dx.name);})
                    .attr("width", function(dx) {return x_d(dx.value);})
                    .attr("height", y_d.rangeBand())
                    .attr("transform", "translate(" + 50 + "," + 40 + ")")
                    .attr("fill", "orange");

                svg_d.append("g")
                    .selectAll("text")
                    .data(bar_dataset)
                    .enter()
                    .append("text") // テキスト要素追加
                    .attr("class", "detail")
                    .attr("text-anchor", "middle")
                    .attr("x", 0)
                    .attr("y", function(dx) { return y_d(dx["name"]); })
                    .text(function(dx){ return dx["value"];}) // 配列[1]の文字をラベルにセット
                    .attr("dy", y_d.rangeBand()*2/3)
                    .attr("dx", "8px") // x軸座標を調整
                    .attr("transform", "translate(" + 50 + "," + 40 + ")")
                    .attr("fill", "black") // テキストカラー
                    .attr("font-size", y_d.rangeBand()/2) // フォントサイズ
                    .attr('text-anchor', "start");

                svg_t.append("text")
                    .attr("class", "detail")
                    .style("font-size", "20px")
                    .attr("transform", "translate(10, 25)")
                    .text(d.name)
                    .attr("fill", "blue")
                    .attr("text-decoration", "underline")
                    .on("click", function(){window.open(click_onsen_name())});
                svg_t.append("text")
                    .attr("class", "detail")
                    .attr("transform", "translate(10, 50)")
                    .style("font-size", "12px")
                    .text("泉質：" + d.kounou);
                svg_t.append("text")
                    .attr("class", "detail")
                    .attr("transform", "translate(10, 100)")
                    .style("font-size", "12px")
                    .text("pH：" + d.pH);
                svg_t.append("text")
                    .attr("class", "detail")
                    .attr("transform", "translate(10, 125)")
                    .style("font-size", "12px")
                    .text("Rn(マッヘ)：" + d["Rn(マッヘ)"]);
                svg_t.append("text")
                    .attr("class", "detail")
                    .attr("transform", "translate(10, 150)")
                    .style("font-size", "12px")
                    .text("KMn04消費：" + d["KMnO4消費"]);
                svg_t.append("text")
                    .attr("class", "detail")
                    .attr("transform", "translate(10, 175)")
                    .style("font-size", "12px")
                    .text("調査日：" + d["調査日"]);

                svg_d.selectAll("g")
                    .append("rect")

                function click_onsen_name(){
                    if (d.link == ""){
                        return "https://www.google.com/search?q=" + d.name;
                    } else {
                        return d.link;
                    }
                }

                console.log(svg_d)
            }

            function click(d){
                svg_d.selectAll(".detail")
                    .remove();
                svg_t.selectAll(".detail")
                    .remove();
            }

            function zoomed() {
                projection_m.translate(d3.event.translate).scale(d3.event.scale);
                console.log(d3.event.translate);
                group_m.selectAll("path")
                    .attr("d", path_m)
                    .attr("class", "area")
                    .attr("stroke", "white")
                    .attr("fill","#9ACD32");
                pin.attr("transform", function(d) {
                        return "translate(" + projection_m([
                            d.longitude,
                            d.latitude
                        ]) + ")";
                    })
            }

            function reset(event, d){
                let targets = document.querySelectorAll(`input[type='checkbox']`);
                for (const i of targets) {
                        i.checked = false;
                }
                d3.selectAll(".rankbar").remove();
                pin.attr("visibility", "visible");

                projection_m.translate([width_m/2, height_m/2]).scale(1500);
                group_m.selectAll("path")
                    .attr("d", path_m)
                    .attr("class", "area")
                    .attr("stroke", "white")
                    .attr("fill","#9ACD32");
                pin.attr("transform", function(d) {
                        return "translate(" + projection_m([
                            d.longitude,
                            d.latitude
                        ]) + ")";
                    })
            }

            var selecting = d3.selectAll("select")
                .on("change", ranking);

            function ranking(event) {

                d3.selectAll(".rankbar").remove();

                let targets = document.querySelectorAll(`input[type='checkbox']`);

                for (const i of targets) {
                        i.checked = false;
                }

                var ingr = selecting.node().value;
                console.log(ingr);
                if (ingr == "") {
                    d3.selectAll(".rankbar").remove();
                    pin.attr("visibility", "visible");
                }
                else {
                onsen_list.sort((a, b) => b[ingr] - a[ingr]);
                pin.attr("visibility", "hidden");
                console.log(onsen_list[0].name);
                var rank_dataset = [];
                rank_dataset.push({"name" :onsen_list[1].name, "value" : onsen_list[1][ingr]});
                rank_dataset.push({"name" :onsen_list[0].name, "value" : onsen_list[0][ingr]});
                rank_dataset.push({"name" :onsen_list[2].name, "value" : onsen_list[2][ingr]});
                
                console.log(rank_dataset);

                var rankwidth = 400; // グラフの幅
                var rankheight = 300; // グラフの高さ
                var rankpadding = 50; // スケール表示用マージン

                var xScale = d3.scale.ordinal()
                    .rangeRoundBands([rankpadding, rankwidth-rankpadding], 0.1)
                    .domain(rank_dataset.map(function(d) { return d.name; }));
                                
                var yScale = d3.scale.linear()
                    .domain([0, onsen_list[0][ingr]])
                    .range([rankheight - rankpadding, rankpadding]);
                // 4. 軸の表示
                var xaxis = svg_r.append("g")
                    .attr("class", "rankbar")
                    .attr("transform", "translate(" + 0 + "," + (rankheight - rankpadding) + ")")
                    .call(d3.svg.axis().orient("bottom").scale(xScale));

                xaxis.select(".domain").style({ 'stroke': 'black', 'fill': 'none', 'stroke-width': '1px'});
                
                var yaxis = svg_r.append("g")
                    .attr("class", "rankbar") 
                    .attr("transform", "translate(" + rankpadding + "," + 0 + ")")
                    .call(d3.svg.axis().orient("left").scale(yScale));

                yaxis.select(".domain").style({ 'stroke': 'black', 'fill': 'none', 'stroke-width': '1px'});

                svg_r.append("g")
                    .attr("class", "rankbar")
                    .selectAll("rect")
                    .data(rank_dataset)
                    .enter()
                    .append("rect")
                    .attr("class", "rankbar")
                    .attr("x", function(d) { return xScale(d.name); })
                    .attr("y", rankheight - rankpadding)
                    .attr("width", 50)
                    .attr("height", 0)
                    .transition()
                    .duration(800)
                    .attr("y", function(d) { return yScale(d.value); })
                    .attr("height", function(d) { return rankheight - rankpadding - yScale(d.value); })
                    .attr("transform", "translate(25, 0)")
                    .attr("fill", "teal");


                pin.each(function (d) {
                                // console.log(this);
                                if (this.id.includes(onsen_list[0].name)) {
                                    d3.select(this).attr("visibility", "visible");
                                }
                                else if (this.id.includes(onsen_list[1].name)) {
                                    d3.select(this).attr("visibility", "visible");
                                }
                                else if (this.id.includes(onsen_list[2].name)) {
                                    d3.select(this).attr("visibility", "visible");
                                }
                            })  
            }}           
        })
    }
    dashboard("#dashboard", onsen_list);
})
