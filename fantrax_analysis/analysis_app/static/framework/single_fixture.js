var formationData;

$(document).ready(function() {
        var svg = document.getElementById('pitch-svg');
        $.getJSON('/formations.json', function(result) {
            formationData = JSON.parse(result);
            console.log(formationData);
        });
})
