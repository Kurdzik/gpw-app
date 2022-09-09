
var csv_path = '/static/dropdown/tickers_preds.csv'; //Host this file on server



$(document).ready(function() {
  var renderCSVDropdown6 = function(csv) {
    var options = csv.split(',');

    var dropdown = $('select#selectTickersPreds');
    for (var i = 0; i < options.length; i++) {
      var record = options[i];
      var entry = $('<option>').html(record);
      dropdown.append(entry);
    }
  };

  // UnComment this code once you have file on the server
  $.get(csv_path, function(data6) {				
  	renderCSVDropdown6(data6);
  });

//   renderCSVDropdown();
});

