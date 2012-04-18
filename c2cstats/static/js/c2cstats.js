/* Author:

 */

txtattr = { font: "inherit" };

function pieplot(data, chartdiv) {
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


function barplot(data, chartdiv) {

    $('#'+chartdiv).before('<h2>'+data.title+'</h2>');

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