/*
# Copyright (c) 2012 Simon C. <contact at saimon.org>
# see https://github.com/saimn/c2c-stats/LICENSE
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
    },
    grid: {
      hoverable: true,
      // clickable: true
    },
    tooltip: true,
    tooltipOpts: {
      content: "%s, %y sorties (%p.0%)",
      shifts: {
        x: 20,
        y: 0
      },
      defaultTheme: false
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
    xaxis: { ticks: labels },
    yaxis: { tickDecimals: 0 },
    grid: {
      hoverable: true,
      borderWidth: 0,
    },
    tooltip: true,
    tooltipOpts: {
      content: "%y",
      shifts: {
        x: 0,
        y: 20
      },
      defaultTheme: false
    }
  });
}

function lineplot(raw, chartdiv) {
  var $chartdiv = $(chartdiv);
  $($chartdiv).before('<h2>'+raw.title+'</h2>');

  var data = [];
  $.each(raw.values_per_month, function(i, year) {
    var d = [];
    $.each(year, function(j, value) {
      d.push([j+1, value]);
    });
    data.push({
      data: d,
      label: raw.labels[i],
    });
  });

  var months = ["jan", "fev", "mar", "avr", "mai", "jui",
                "jui", "aou", "sep", "oct", "nov", "dec"];
  var labels = [];
  $.each(months, function(index, value) {
    labels.push([index+1, value]);
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
      borderWidth: 0,
    },
    xaxis: {
      show: true,
      ticks: labels
    },
    tooltip: true,
    tooltipOpts: {
      content: "%x/%s : %y m",
      shifts: {
        x: -50,
        y: 20
      },
      defaultTheme: false
    }
  });
}
