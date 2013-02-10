$(document).ready(function(){
  $charts = $('#charts');
  $summary = $('#summary');
  $loading = $('#loading');

  // hide it initially
  $loading.hide();

  load_json_stats();

  function load_json_stats() {
    $charts.hide();
    $summary.hide();
    $loading.show();

    $.ajax({
      dataType: "json",
      url: jsonurl,
      cache: false,
      success: function(data) {
        $loading.hide();
        $charts.show();
        $summary.show();
        $.sparkline_display_visible();
        renderplot(data);
      }
    })
    .error(function() {
      document.location = "/";
    });
  }

  // fix sub nav on scroll
  var $win = $(window)
  , $subnav = $('.subnav')
  , navTop = 370 //$('.subnav').length && $('.subnav').offset().top
  , isFixed = 0;

  processScroll();
  $win.on('scroll', processScroll);

  // $subnav.on('click', function () {
  //   setTimeout(function () {  $win.scrollTop($win.scrollTop()); }, 10);
  // });

  function processScroll() {
    var i, scrollTop = $win.scrollTop();
    if (scrollTop >= navTop && !isFixed) {
      isFixed = 1;
      $subnav.addClass('navbar-fixed-top');
    } else if (scrollTop <= navTop && isFixed) {
      isFixed = 0;
      $subnav.removeClass('navbar-fixed-top');
    }
  }

  function renderplot(data) {
    if (data === null || data.length === 0) {
      $("#charts").html('Error retrieving data');
      return 1;
    }

    var source = $("#summary-template").html();
    var summary_template = Handlebars.compile(source);
    var html = summary_template({
      date_generated: data.date_generated,
      time: data.time,
      nb_outings: data.nb_outings,
      origin_link: data.url,
      origin_profile: data.user_url,
      user_id: user_id
    });
    $("#summary").html(html);

    $('#delete-cache').on('click', function () {
      $.ajax({
        url: "/user/" + user_id,
        type: 'DELETE'
      })
        .done(load_json_stats);
    });

    // Remove the chart titles if they are present
    $('#global .chart-title').remove();

    $('#chart_activities').c2cstats('pie', data.global.activities);
    $('#chart_area').c2cstats('pie', data.global.area);

    source = $("#nav-template").html();
    var nav_template = Handlebars.compile(source);
    html = nav_template({activities: data.activities});
    $(".subnav .nav").html(html);

    source = $("#charts-template").html();
    var charts_template = Handlebars.compile(source);

    $.each(data.activities, function(index, value) {
      if (data[value])
      {
        var html = charts_template({activity: value});
        $("#"+value).html(html);

        if (data[value].cotation != null &&
            data[value].cotation.values.length > 0) {
          $('#cotation_'+value).c2cstats('bar', data[value].cotation);
        }

        if (data[value].cotation_globale != null &&
            data[value].cotation_globale.values.length > 0) {
          $('#cotation_globale_'+value).c2cstats('bar', data[value].cotation_globale);
        }

        $('#outings_'+value).c2cstats('bar', data[value].outings_per_year);
        $('#gain_'+value).c2cstats('bar', data[value].gain_per_year);
        $('#gain_cumul_'+value).c2cstats('lines', data[value].gain_per_year);
      }
    });

    var spark_data = [],
        bar_width = 4;

    $.each(data.global.outings_per_month.values, function(index, value) {
      spark_data = spark_data.concat(value);
    });
    if (spark_data.length*5 > 680) {
      bar_width = Math.max(Math.floor(680 / spark_data.length) - 1, 2);
    }
    $('#sparkline').sparkline(spark_data, {
      type: 'bar',
      barColor: '#0088cc',
      barWidth: bar_width
    });
  }
});