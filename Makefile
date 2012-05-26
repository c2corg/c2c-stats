
js:
	cat c2cstats/static/js/libs/{bootstrap-transition.js,bootstrap-tab.js,jquery.flot.js,jquery.flot.pie.js,jquery.flot.resize.js,jquery.sparkline.min.js} > c2cstats/static/js/libs/libs.js
	uglifyjs c2cstats/static/js/libs/libs.js > c2cstats/static/js/libs/libs.min.js
