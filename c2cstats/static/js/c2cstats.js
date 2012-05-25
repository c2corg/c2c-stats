/* Author:

 */

barWidth = 0.6;

function pieplot(raw, chartdiv) {
  var data = [];
  $.each(raw.values, function(index, value) {
    data.push({label: raw.labels[index],  data: value});
  });

  $(chartdiv).before('<h2>'+raw.title+'</h2>');
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

function barplot(raw, chartdiv) {
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
