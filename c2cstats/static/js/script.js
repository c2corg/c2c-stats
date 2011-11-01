/* Author:

 */


function plot_cotation(data, chartdiv) {
    plo12 = $.jqplot(chartdiv, [data.cotation.values],{
        title: data.cotation.title,
        seriesDefaults:{
            renderer:$.jqplot.BarRenderer,
            //pointLabels: { show: true },
            //showMarker: false
        },
        axes: {
            xaxis: {
                renderer: $.jqplot.CategoryAxisRenderer,
                ticks: data.cotation.labels
            }
        },
        highlighter: { show: false }
    });
}

function renderplot(data) {
    if (data === null || data.length === 0) {
        $("#charts").html('Error retrieving data');
        return 1;
    }
    $("#nb_outings").text(data.nb_outings);
    $("#date_generated").text(data.date_generated);

    $.each(data.activities, function(index, value) {
        if (data[value].cotation.values != null && data[value].cotation.values.length > 0) {
            $("#charts").append('<div id="cotation_'+value+'" class="chart" style="margin:20px auto; width:400px; height:300px;"></div>')
            plot_cotation(data[value], 'cotation_'+value);
        }

    });
}
