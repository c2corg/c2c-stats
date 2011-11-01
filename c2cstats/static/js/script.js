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
        $("#chart1").html(getLoadText('Error retrieving data', 0));
        return 1;
    }
    plot_cotation(data.Rando, 'cotation_rando');
    plot_cotation(data.Glace, 'cotation_glace');
}
