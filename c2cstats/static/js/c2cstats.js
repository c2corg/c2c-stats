/* Author:

 */

barWidth = 0.8;
colors = ['#4575B4', '#D73027', '#91BFDB', '#FC8D59', '#E0F3F8', '#FEE090', '#FFFFBF'];

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
    colors: colors,
    legend: {
      show: true,
      labelBoxBorderColor: null,
      labelFormatter: function(label, series) {
        // series is the series object for the label
        return '<span rel="tooltip" data-original-title="' + series.data[0][1] + ' sorties (' + Math.round(series.percent) + ' %)">' + label + '</span>';
      }
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
  $chartdiv.before('<h2>'+raw.title+'</h2>');

  var width = 30*raw.labels.length;
  $chartdiv.width(width)

  $.plot($chartdiv, [data], {
    series: {
      bars: {
        show: true,
        barWidth: barWidth,
        lineWidth: 0,
        fillColor: colors[0],
        horizontal: false
      },
    },
    xaxis: {
      show: true,
      ticks: labels,
    },
    grid: {
      hoverable: true,
      backgroundColor: null,
      borderWidth: 0
    },
  });
}

function lineplot(raw, chartdiv) {
  var $chartdiv = $(chartdiv);
  $($chartdiv).before('<h2>'+raw.title+'</h2>');

  var data = [];
  $.each(raw.values_per_month, function(i, year) {
    var d = [];
    $.each(year, function(j, value) {
      d.push([j, value]);
    });
    data.push({
      data: d,
      label: raw.labels[i],
    });
  });

  var months = ["jan", "fev", "mar", "avr", "mai", "jui", "jui", "aou", "sep", "oct", "nov", "dec"];
  var labels = [];
  $.each(months, function(index, value) {
    labels.push([index, value]);
  });

  $.plot($chartdiv, data, {
    series: {
      lines: { show: true },
      points: { show: true }
    },
    legend: {
      labelBoxBorderColor: null,
      position: "nw"
    },
    grid: {
      hoverable: true,
      backgroundColor: null,
      borderWidth: 0
    },
    xaxis: {
      show: true,
      ticks: labels
      // ticks: [[0, "jan"] [1, "feb"] [2, "mar"] [3, "apr"] [4, "maj"] [5, "jun"]
      //         [6, "jul"] [7, "aug"] [8, "sep"] [9, "okt"] [10, "nov"] [11, "dec"]]
    },
  });
}
