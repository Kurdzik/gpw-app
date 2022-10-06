
var csv_path2 = '/static/dropdown/dates_from.csv'; //Host this file on server



$(document).ready(function() {
  var renderCSVDropdown2 = function(csv) {
    var options = csv.split(',');

    var dropdown = $('select#selectDatesFrom');
    for (var i = 0; i < options.length; i++) {
      var record = options[i];
      var entry = $('<option>').html(record);
      dropdown.append(entry);
    }
  };

  // UnComment this code once you have file on the server
  $.get(csv_path2, function(data2) {				
  	renderCSVDropdown2(data2);
  });

  // renderCSVDropdown2('1','2','3','4');
});

