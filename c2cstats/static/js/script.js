/* Author:

 */


function plot_area(data) {
    var plot1 = jQuery.jqplot ('chart_area', [data.values], {
        title: data.title,
        seriesDefaults: {
            // Make this a pie chart.
            renderer: jQuery.jqplot.PieRenderer,
            rendererOptions: {
                // Put data labels on the pie slices.
                // By default, labels show the percentage of the slice.
                showDataLabels: true
            }
        },
        legend: { show:true, location: 'e' }
    });
}

function plot_cotation(data, chartdiv) {
    plo12 = $.jqplot(chartdiv, [data.cotation.values], {
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

    plot_area(data.global.area);

    $.each(data.activities, function(index, value) {
        if (data[value].cotation.values != null && data[value].cotation.values.length > 0) {
            $("#charts").append('<div id="cotation_'+value+'" class="chart"></div>')
            plot_cotation(data[value], 'cotation_'+value);
        }

    });
}
