
var csv_path = '/static/dropdown/databases.csv'; //Host this file on server



$(document).ready(function() {
  var renderCSVDropdown = function(csv) {
    var options = csv.split(',');

    var dropdown = $('select#selectDatabases');
    for (var i = 0; i < options.length; i++) {
      var record = options[i];
      var entry = $('<option>').html(record);
      dropdown.append(entry);
    }
  };

  // UnComment this code once you have file on the server
  $.get(csv_path, function(data) {				
  	renderCSVDropdown(data);
  });

//   renderCSVDropdown();
});

