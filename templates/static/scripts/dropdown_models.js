
var csv_path3 = '/static/dropdown/models.csv'; //Host this file on server



$(document).ready(function() {
  var renderCSVDropdown3 = function(csv) {
    var options = csv.split(',');

    var dropdown = $('select#selectModel');
    for (var i = 0; i < options.length; i++) {
      var record = options[i];
      var entry = $('<option>').html(record);
      dropdown.append(entry);
    }
  };

  // UnComment this code once you have file on the server
  $.get(csv_path3, function(data3) {				
  	renderCSVDropdown3(data3);
  });

  // renderCSVDropdown('1','3','45','5');
});

