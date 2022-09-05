function addRowHandlers() {
    var table = document.getElementById("opponent_ranker_fixtures_table");
    var rows = table.getElementsByTagName("tr");
    for (i = 0; i < rows.length; i++) {
        var currentRow = table.rows[i];
        var createClickHandler =
            function(row)
            {
                return function() {
                                        var cell1 = row.getElementsByTagName("td")[2];
                                        var cell2 = row.getElementsByTagName("td")[3];
                                        var id1 = cell1.innerHTML;
                                        var id2 = cell2.innerHTML;
                                        var matchRef = id1 + id2;
                                 };
            };

        currentRow.onclick = createClickHandler(currentRow);
    }
}

$(document).ready(function(){
    window.onload = addRowHandlers();
});


