/**
 * Created by evgeni on 6/11/17.
 */
var system = require('system');
var args = system.args;

if (args.length === 1) {
  console.log('Try to pass some arguments when invoking this script!');
} else {
  args.forEach(function(arg, i) {
    //console.log(i + ': ' + arg);
  });
}

var url = args[1]

//var page = require('webpage').create();
//page.open(url, function () {
//    console.log(page.content);
//    phantom.exit();
//});

var page = new WebPage()
var fs = require('fs');

page.onLoadFinished = function() {
  //console.log("page load finished");
  //page.render('export.png');
  //fs.write('1.html', page.content, 'w');
    console.log(page.content);
  phantom.exit();
};

page.open(url, function() {
  page.evaluate(function() {
  });
});