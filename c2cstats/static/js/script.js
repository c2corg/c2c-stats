/* Author:

 */

function plot_pie(raw, chartdiv) {
    var labels = [];
    var values = [];
    $.each(raw.values, function(index, value) {
        labels.push(value[0]+' ('+value[1]+' - %%)');
        values.push(value[1]);
    });

    $('#'+chartdiv).before('<h2 class="chart_title">'+raw.title+'</h2>');

    var r = Raphael(chartdiv);
    var pie = r.g.piechart(150, 150, 120, values, { legend: labels, legendpos: "east"});
    // r.text(320, 100, "Interactive Pie Chart").attr({ font: "20px sans-serif" });
    pie.hover(function () {
        this.sector.stop();
        this.sector.scale(1.1, 1.1, this.cx, this.cy);
        if (this.label) {
            this.label[0].stop();
            this.label[0].attr({ r: 7.5 });
            this.label[1].attr({ "font-weight": 800 });
        }
    }, function () {
        // this.sector.animate({ transform: 's1 1 ' + this.cx + ' ' + this.cy }, 500, "bounce");
        this.sector.scale(1, 1, this.cx, this.cy);
        if (this.label) {
            this.label[0].animate({ r: 5 }, 500, "bounce");
            this.label[1].attr({ "font-weight": 400 });
        }
    });
}


function plot_cotation(raw, chartdiv) {
    $('#'+chartdiv).before('<h2 class="chart_title">'+raw.title+'</h2>');

    var r = Raphael(chartdiv);
    var fin = function () {
        this.flag = r.g.popup(this.bar.x, this.bar.y, this.bar.value || "0").insertBefore(this);
    };
    var fout = function () {
        this.flag.animate({opacity: 0}, 300, function () {this.remove();});
    };

    chart = r.g.barchart(10, 10, 320, 220, [raw.values], {type: "soft"}).hover(fin, fout);
    r.g.txtattr = {font:"12px Fontin-Sans, Arial, sans-serif", fill:"#000", "font-weight": "bold"};
    chart.label([raw.labels], true);
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
