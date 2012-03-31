/* Author:

 */

barWidth = 0.6;
mainFont = "inherit";

function plot_pie(raw, chartdiv) {
    var data = {labels: [], values: []};
    $.each(raw.values, function(index, value) {
        data.labels.push(value[0]+' ('+value[1]+')');
        data.values.push(value[1]);
    });

    $('#'+chartdiv).before('<h2 class="chart_title">'+raw.title+'</h2>');

    var r = Raphael(chartdiv);
    var pie = r.piechart(150, 150, 120, data.values, { legend: data.labels, legendpos: "east"}).attr({ font: mainFont });
    pie.hover(function () {
        this.sector.stop();
        this.sector.scale(1.1, 1.1, this.cx, this.cy);
        if (this.label) {
            this.label[0].stop();
            this.label[0].attr({ r: 7.5 });
            this.label[1].attr({ "font-weight": 800 });
        }
    }, function () {
        this.sector.animate({ transform: 's1 1 ' + this.cx + ' ' + this.cy }, 500, "bounce");
        if (this.label) {
            this.label[0].animate({ r: 5 }, 500, "bounce");
            this.label[1].attr({ "font-weight": 400 });
        }
    });
}


function plot_cotation(raw, chartdiv) {

    $('#'+chartdiv).before('<h2 class="chart_title">'+raw.title+'</h2>');

    var r = Raphael(chartdiv);
    // var fin = function () {
    //     this.flag = r.popup(this.bar.x, this.bar.y, this.bar.value || "0").insertBefore(this);
    // };
    // var fout = function () {
    //     this.flag.animate({opacity: 0}, 300, function () {this.remove();});
    // };
    // r.barchart(40, 10, 320, 220, [raw.values], {legend: raw.labels, type: "soft", axis: "0 0 1 1"}).hover(fin, fout);

    var labels_ind = [];
    for(var i=0; i<raw.values.length; i++){
        labels_ind.push(i);
    }

    xs = labels_ind,
    ys = raw.values,
    data = raw.values,
    // axisy = raw.values,
    axisx = raw.labels;
    r.dotchart(10, 10, 420, 260, xs, ys, data, {
        symbol: "o",
        max: 10,
        heat: true,
        axis: "0 0 1 0", axisxstep: raw.labels.length-1, axisxlabels: axisx,
        axisxtype: " "
    }).hover(function () {
        this.marker = this.marker || r.tag(this.x, this.y, this.value, 0, this.r + 2).insertBefore(this);
        this.marker.show();
    }, function () {
        this.marker && this.marker.hide();
    }).attr({ font: mainFont });
}

/*
function plot_cotation_globale_per_activity(data) {
    var d = [];
    $.each(data.values, function(index, value) {
        val = [];
        $.each(value, function(index2, value2) {
            val.push([index2, value2]);
        });
        d.push({
            label: data.labels[index],
            data: val
        });
    });

    var labels = [];
    $.each(data.xlabels, function(index, value) {
        labels.push([index + barWidth/2., value]);
    });

    $('#chart_cot_globale').before('<h2 class="chart_title">'+data.title+'</h2>');
    $.plot($('#chart_cot_globale'), d,  {
	series: {
            stack: true,
            bars: { show: true, barWidth: barWidth }
        },
        legend: { show: true },
        xaxis: {
            show: true,
            ticks: labels,
        },
        grid: {
            hoverable: true,
            clickable: true,
            backgroundColor: { colors: ["#fff", "#eee"] }
        }
    });

}
*/

function renderplot(data) {
    if (data === null || data.length === 0) {
        $("#charts").html('Error retrieving data');
        return 1;
    }

    $("#nb_outings").text(data.nb_outings);
    $("#date_generated").text(data.date_generated);
    $("#download_time").text(data.download_time);
    $("#parse_time").text(data.parse_time);
    $("#generation_time").text(data.generation_time);
    $("#total_time").text(data.total_time);
    $("#origin-link").attr({href: data.url});

    plot_pie(data.global.activities, 'chart_activities');
    plot_pie(data.global.area, 'chart_area');

    /*
    // plot_cotation(data.global.cotation_globale, '#chart_cot_globale');
    plot_cotation_globale_per_activity(data.global.cotation_per_activity);
    */

    $.each(data.activities, function(index, value) {
        if (data[value].cotation.values != null && data[value].cotation.values.length > 0) {
            $("#charts").append('<div id="cotation_'+value+'" class="chart"></div>');
            plot_cotation(data[value].cotation, 'cotation_'+value);
        }
    });
}
