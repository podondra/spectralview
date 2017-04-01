// inspired by https://bost.ocks.org/mike/chart/

// bar chart inspired by https://bost.ocks.org/mike/bar/
// closure  with getter-setter methods
function barChart() {
    var width = 720,    // default width
        height = 200;    // default height

    function my(selection) {
        // generate chart here, using 'width' and 'height'
        selection.each(function(d, i) {
            var margin = {top: 20, right: 30, bottom: 30, left: 60},
                my_width = width - margin.left - margin.right,
                my_height = height - margin.top - margin.bottom;

            var x = d3.scaleBand().rangeRound([0, my_width]).padding(0.1)
                .domain(d.map(function(d) { return d.name; }));
            var y = d3.scaleLinear().rangeRound([my_height, 0])
                .domain([0, d3.max(d, function(d) { return d.value; })]);

            var svg = d3.select(this)
                .attr("width", my_width + margin.left + margin.right)
                .attr("height", my_height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + ", " + margin.top + ")");

            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0, " + my_height + ")")
                .call(d3.axisBottom(x));

            svg.append("g")
                .attr("class", "y axis")
                .call(d3.axisLeft(y));

            svg.selectAll(".bar")
                .data(d)
                .enter()
                .append("rect")
                .attr("class", "bar")
                .attr("x", function(d) { return x(d.name); })
                .attr("y", function(d) { return y(d.value); })
                .attr("width", x.bandwidth())
                .attr("height", function(d) { return my_height - y(d.value) });
        })
    }

    my.width = function(value) {
        if (!arguments.length) return width;
        width = value;
        return my;
    };

    my.height = function(value) {
        if (!arguments.length) return height;
        height = value;
        return my;
    };

    return my;
}

// line chart
function lineChart() {
    var width = 400,    // default width
        height = 200;    // default height

    function my(selection) {
        // generate chart here, using 'width' and 'height'
        selection.each(function(json, i) {
            var data = json["data"];

            var svg = d3.select(this)
                .attr("width", width)
                .attr("height", height);

            var margin = {top: 20, right: 20, bottom: 30, left: 50},
                my_width = width - margin.left - margin.right,
                my_height = height - margin.top - margin.bottom;

            var g = svg.append("g")
                .attr("transform", "translate(" + margin.left + ", " + margin.top + ")");

            var x = d3.scaleLinear()
                .range([0, my_width])
                .domain(d3.extent(data, function(d) { return d.wave; }));

            var y = d3.scaleLinear()
                .range([my_height, 0])
                .domain(d3.extent(data, function(d) { return d.flux; }));

            var line = d3.line()
                .x(function(d) { return x(d.wave); })
                .y(function(d) { return y(d.flux); });

            g.append("g")
                .attr("transform", "translate(0," + my_height + ")")
                .call(d3.axisBottom(x))

            g.append("g")
                .call(d3.axisLeft(y))

            g.append("path")
                .datum(data)
                .attr("fill", "none")
                .attr("stroke", "steelblue")
                .attr("stroke-width", 1)
                .attr("d", line);

            var halpha = 6562.8;
            g.append("line")
                .attr("x1", x(halpha))
                .attr("x2", x(halpha))
                .attr("y1", 0)
                .attr("y2", my_height)
                .attr("stroke-width", 1)
                .attr("stroke-dasharray", "5, 5")
                .attr("stroke", "black");
        })
    }

    my.width = function(value) {
        if (!arguments.length) return width;
        width = value;
        return my;
    };

    my.height = function(value) {
        if (!arguments.length) return height;
        height = value;
        return my;
    };

    return my;
}
