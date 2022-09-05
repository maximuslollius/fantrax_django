$(document).ready(function(){
    var myTableArray = []; rows=[];
    var starts = 0; wins=0; draws=0; losses=0;
    var start_list = []; fpts_list = [];
    var imageSource = document.getElementById('image-source').innerHTML;
    document.getElementById('player-pic').src =  imageSource;

    var playerGames = $('tbody tr').length;

    $('tbody tr td.starts').each(function(){
        start_list.push($(this).html());
        if($(this).html() == 1) {
            starts += 1;
        }
    });

    $('tbody tr td.f-pts').each(function(){
        fpts_list.push($(this).html());
    });

    $('#project-list-table > tbody > tr').each(function(){
        row = $(this);
        rows.push(row);
    });

    /*$('table#project-list-table tr').each(function() {
        var arrayOfThisRow = [];
        var tableData = $(this).find('td');
        if(tableData.length > 0) {
            tableData.each(function() { arrayOfThisRow.push($(this).text()); });
            myTableArray.push(arrayOfThisRow);
        }
    });*/


    document.getElementById('info1').innerHTML =  starts;
    results = get_wins(start_list);
    document.getElementById('info2').innerHTML =  results[0];
    document.getElementById('info3').innerHTML =  results[1];
    document.getElementById('info4').innerHTML =  results[2];
    document.getElementById('info5').innerHTML =  parseFloat(100*((3*results[0])+(results[1]))/(3*starts)).toFixed(2);
});

function get_wins(start_list) {
    for(i = 0, f = start_list[0]; i < start_list.length; f = start_list[++i]) {
        if (f == 1 && fpts_list[i] > 11.99) {
            wins +=1;
            rows[i][0].style.backgroundColor = "green";
        } else if (f == 1 && fpts_list[i] > 9.99) {
            draws +=1;
            score = rows[i][0].cells[8].innerText;
            console.log(score);
            if (score > 11.99)
                rows[i][0].style.backgroundColor = "#B2D732";
            else if (score > 9.99)
                rows[i][0].style.backgroundColor = "yellow";
        } else if (f == 1 && fpts_list[i] < 9.99) {
            losses +=1;
            score = rows[i][0].cells[8].innerText;
            if (score > 11.99)
                rows[i][0].style.backgroundColor = "#B2D732";
            else if (score > 9.99)
                rows[i][0].style.backgroundColor = "#FCCC1A";
            else if (score < 9.99)
                rows[i][0].style.backgroundColor = "red";
        }
    }
    return [wins, draws, losses];
}