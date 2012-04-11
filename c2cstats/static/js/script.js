/* Author:

 */

txtattr = { font: "inherit" };

function   pieplot(data, chartdiv) {
    var labels = [];
    $.each(data.labels, function(index, label) {
        labels.push(label+' ('+data.values[index]+')');
    });

    $('#'+chartdiv).before('<h2>'+data.title+'</h2>');

    var r = Raphael(chartdiv, 700, 300);
    var pie = r.piechart(150, 150, 120, data.values, { legend: labels, legendpos: "east"}).attr(txtattr);
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


function   barplot(data, chartdiv) {

    $('#'+chartdiv).before('<h3>'+data.title+'</h3>');

    var width = 30*data.labels.length,
        height = 250;

    var r = Raphael(chartdiv, width+90, height+20);

    var fin = function () {
      this.flag = r.popup(this.bar.x, this.bar.y, this.bar.value || "0").insertBefore(this);
    };
    var fout = function () {
      this.flag.animate({opacity: 0}, 300, function () {this.remove();});
    };

    r.barchart(80, 10, width, height, [data.values], {type: "soft"})
    .hover(fin, fout)
    .label([data.labels], true);

    // var xs = [];
    // for(var i=0; i<data.values.length; i++){
    //     xs.push(i);
    // }
    // ys = data.values,
    // // axisy = data.values,
    // r.dotchart(10, 10, 420, 260, xs, ys, data.values, {
    //     symbol: "o",
    //     max: 10,
    //     heat: true,
    //     axis: "0 0 1 0",
    //     axisxstep: data.labels.length-1, axisxlabels: data.labels, axisxtype: " "
    // }).hover(function () {
    //     this.marker = this.marker || r.tag(this.x, this.y, this.value, 0, this.r + 2).insertBefore(this);
    //     this.marker.show();
    // }, function () {
    //     this.marker && this.marker.hide();
    // }).attr(txtattr);
}

function plot_cotation_globale_per_activity(data, chartdiv) {

  $('#'+chartdiv).before('<h2>'+data.title+'</h2>');
  var r = Raphael(chartdiv);

  var fin2 = function () {
    var y = [], res = [];
    for (var i = this.bars.length; i--;) {
      y.push(this.bars[i].y);
      if (this.bars[i].value) {
        res.push(data.labels[i] + " : " + this.bars[i].value);
      }
    }
    this.flag = r.popup(this.bars[0].x, Math.min.apply(Math, y), res.join("\n ")).insertBefore(this);
  };
  var fout2 = function () {
    this.flag.animate({opacity: 0}, 300, function () {this.remove();});
  };

  r.barchart(80, 80, 420, 260, data.values, {stacked: true, type: "soft"})
    .hoverColumn(fin2, fout2)
    .label(data.xlabels, true);
}

function renderplot(data) {
    if (data === null || data.length === 0) {
        $("#charts").html('Error retrieving data');
        return 1;
    }

    $("#nb_outings").text(data.nb_outings);
    $("#date_generated").text(data.date_generated);
    $("#download_time").text(data.time.download);
    $("#parse_time").text(data.time.parse);
    $("#generation_time").text(data.time.generation);
    $("#total_time").text(data.time.total);
    $("#origin-link").attr({href: data.url});

    pieplot(data.global.activities, 'chart_activities');
    pieplot(data.global.area, 'chart_area');

    // plot_cotation(data.global.cotation, 'chart_cot_globale');
    plot_cotation_globale_per_activity(data.global.cotation_per_activity, 'chart_cot_globale');

    $.each(data.activities, function(index, value) {
      if (data[value] &&
          data[value].cotation.values != null &&
          data[value].cotation.values.length > 0)
      {
        $("#charts").append('<div id="'+value+'"></div>');
        $("#"+value).append('<h2>'+data[value].full_name+'</h2>');

        $("#"+value).append('<div id="cotation_'+value+'" class="chart"></div>');
        barplot(data[value].cotation, 'cotation_'+value);

        $("#"+value).append('<div id="outings_'+value+'" class="chart"></div>');
        barplot(data[value].outings_per_year, 'outings_'+value);
      }
    });
}
