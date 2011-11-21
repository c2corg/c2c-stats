/* Author:

 */

barWidth = 0.6;

function plot_pie(raw, chartdiv) {
    var data = [];
    $.each(raw.values, function(index, value) {
        data.push({label: value[0],  data: value[1]});
    });

    $(chartdiv).before('<h2 class="chart_title">'+raw.title+'</h2>');
    $.plot($(chartdiv), data, {
	series: {
            pie: { show: true },
        },
        legend: { show: false },
        grid: {
            hoverable: true,
            clickable: true
        }
    });
}

function plot_cotation(raw, chartdiv) {
    var data = [];
    $.each(raw.values, function(index, value) {
        data.push([index, value]);
    });

    var labels = [];
    $.each(raw.labels, function(index, value) {
        labels.push([index + barWidth/2., value]);
    });

    $(chartdiv).before('<h2 class="chart_title">'+raw.title+'</h2>');
    $.plot($(chartdiv), [data], {
        series: {
            bars: { show: true, barWidth: barWidth },
        },
        xaxis: {
            show: true,
            ticks: labels,
        },
        grid: {
            hoverable: true,
            backgroundColor: { colors: ["#fff", "#eee"] }
        },
    });
}


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
            clickable: true
        }
    });

}

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

    plot_pie(data.global.activities, '#chart_activities');
    plot_pie(data.global.area, '#chart_area');
    // plot_cotation(data.global.cotation_globale, '#chart_cot_globale');
    plot_cotation_globale_per_activity(data.global.cotation_per_activity);

    $.each(data.activities, function(index, value) {
        if (data[value].cotation.values != null && data[value].cotation.values.length > 0) {
            $("#charts").append('<div id="cotation_'+value+'" class="chart"></div>');
            plot_cotation(data[value].cotation, '#cotation_'+value);
        }
    });
}
