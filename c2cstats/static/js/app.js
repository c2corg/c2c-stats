$(document).ready(function(){
  $tohide = $('.hide');
  $nav = $('.nav');

  $('#loading')
    .hide()  // hide it initially
    .ajaxStart(function() {
      $tohide.hide();
      $nav.hide();
      $(this).show();
    })
    .ajaxSuccess(function() {
      $(this).hide();
      $tohide.show();
      $nav.show();
      $.sparkline_display_visible();
    })
    .ajaxError(function() {
      $tohide.hide();
      $nav.hide();
      $(this).hide();
      $(this).after('<div class="alert alert-error">Erreur lors du chargement des données</div>');
    });
  $.getJSON(jsonurl, renderplot);

  // fix sub nav on scroll
  var $win = $(window)
  , $subnav = $('.subnav')
  , navTop = $('.subnav').length && $('.subnav').offset().top
  , tabsTop = $('#tabs').offset().top
  , isFixed = 0

  processScroll()

  // hack sad times - holdover until rewrite for 2.1
  $subnav.on('click', function () {
    if (!isFixed) {
      setTimeout(function () {  $win.scrollTop($win.scrollTop()) }, 10)
    } else
    {
      $win.scrollTop(tabsTop - 50)
    }
  })

  $win.on('scroll', processScroll)

  function processScroll() {
    var i, scrollTop = $win.scrollTop()
    if (scrollTop >= navTop && !isFixed) {
      isFixed = 1
      $subnav.addClass('subnav-fixed')
    } else if (scrollTop <= navTop && isFixed) {
      isFixed = 0
      $subnav.removeClass('subnav-fixed')
    }
  }

});

function renderplot(data) {
    if (data === null || data.length === 0) {
        $("#charts").html('Error retrieving data');
        return 1;
    }

    $("#nb_outings").text(data.nb_outings);
    $("#date_generated").text(data.date_generated);
    $("#download_time").text(data.time.download);
    $("#total_time").text(data.time.total);
    $("#origin-link").attr({href: data.url});
    $("#origin-profile").attr({href: data.user_url});

    pieplot(data.global.activities, '#chart_activities');
    pieplot(data.global.area, '#chart_area');

    // plot_cotation(data.global.cotation, 'chart_cot_globale');
    // plot_cotation_globale_per_activity(data.global.cotation_per_activity, 'chart_cot_globale');

    $.each(data.activities, function(index, value) {
      if (data[value])
      {
        $(".nav").append('<li><a href="#'+value+'" data-toggle="pill">'+value+'</a></li>');
        $("#tabs").append('<div id="'+value+'" class="tab-pane fade"></div>');

        if (data[value].cotation != null &&
            data[value].cotation.values.length > 0)
        {
          $("#"+value).append('<div id="cotation_'+value+'" class="chart"></div>');
          barplot(data[value].cotation, '#cotation_'+value);
        }

        if (data[value].cotation_globale != null &&
            data[value].cotation_globale.values.length > 0)
        {
          $("#"+value).append('<div id="cotation_globale_'+value+'" class="chart"></div>');
          barplot(data[value].cotation_globale, '#cotation_globale_'+value);
        }

        $("#"+value).append('<div id="outings_'+value+'" class="chart"></div>');
        barplot(data[value].outings_per_year, '#outings_'+value);

        $("#"+value).append('<div id="gain_'+value+'" class="chart"></div>');
        barplot(data[value].gain_per_year, '#gain_'+value);

        // $("#"+value).append('<div id="gain_cumul_'+value+'" class="chart"></div>');
        // lineplot(data[value].gain_per_year, 'gain_cumul_'+value);
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
    $('#sparkline').sparkline(spark_data,
                              { type: 'bar', barColor: '#0088cc', barWidth: bar_width });

    $('.legendLabel span').tooltip();
}
