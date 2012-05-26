/* Author:

 */

barWidth = 0.8;

function pieplot(raw, chartdiv) {
  var data = [];
  $.each(raw.values, function(index, value) {
    data.push({label: raw.labels[index],  data: value});
  });

  var $chartdiv = $(chartdiv);
  $chartdiv.before('<h2>'+raw.title+'</h2>');

  var plot = $.plot($chartdiv, data, {
    series: {
      pie: { show: true },
    },
    legend: {
      show: true,
      labelBoxBorderColor: null
    },
    grid: {
      hoverable: true,
      // clickable: true
    }
  });
  $chartdiv.resize(function () {
    plot.setupGrid();
    plot.draw();
  });
}

function barplot(raw, chartdiv) {
  var data = [];
  $.each(raw.values, function(index, value) {
    data.push([index, value]);
  });

  var labels = [];
  $.each(raw.labels, function(index, value) {
    labels.push([index + barWidth/2., value]);
  });

  var $chartdiv = $(chartdiv);
  $chartdiv.before('<h2 class="chart_title">'+raw.title+'</h2>');

  var width = 30*raw.labels.length;
  $chartdiv.width(width)

  $.plot($chartdiv, [data], {
    series: {
      bars: {
        show: true,
        barWidth: barWidth,
        lineWidth: 0,
        fillColor: "rgba(0, 0, 255, 0.8)",
        horizontal: false
      },
    },
    xaxis: {
      show: true,
      ticks: labels,
    },
    grid: {
      hoverable: true,
      // backgroundColor: { colors: ["#fff", "#eee"] }
      backgroundColor: null,
      borderWidth: 0
    },
  });
}
