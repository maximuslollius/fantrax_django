var myTableArray = [];
var playerName;
var outputData = [];
var colors = ['#ff7f0e', '#afc406']
var row;
var list_of_outputData = []
var drawChart = function() {
    nv.addGraph(function() {
    var chart = nv.models.lineChart()
        .useInteractiveGuideline(true)
        ;

    chart.xAxis
        .axisLabel('GameWeeks')
        .tickFormat(d3.format(',r'))
        ;


    chart.yAxis
        .axisLabel('Points')
        .tickFormat(d3.format('.02f'))
        ;

    d3.select('#chart1 svg')
        .datum(outputPlotData())
        .transition().duration(500)
        .call(chart)
        ;

    nv.utils.windowResize(chart.update);

    return chart;
    });
};

$(document).ready(function() {
    $('#chart1').hide();
    drawChart();
    $('table#project-list-table tr').each(function() {
        var arrayOfThisRow = [];
        var tableData = $(this).find('td');
        if(tableData.length > 0) {
            tableData.each(function() { arrayOfThisRow.push($(this).text()); });
            myTableArray.push(arrayOfThisRow);
        }
    });

    $('#dv-filter').keyup(function() {
        /*alert ("Handler for .keyup() called.");*/
        var t = $('table');
        $('#project-list-table').multiFilter({ column: 'Name', word: this.value});
    });

    $('#clear-output-button').click(function(){
        $('.activated').removeClass('activated');
        outputPlotData();
        list_of_outputData = [];
        $('#chart1').hide();

    });

    $('#club').change(function() {
        var selection = $(this).val();
        var dataset = $('tbody').find('tr');

        dataset.show();

        dataset.filter(function(index, item) {
          return $(item).find('td:nth-child(2)').text().split(',').indexOf(selection) === -1;
    }).hide();

  });
});

function get_outputData() {
    $('#project-list-table > tbody > tr').click(function(){
        row = ($(this).index());
        playerName = myTableArray[row][0];
        outputData = [];
        for (var i=4; i<42; ++i)
            outputData.push({x: (i - 3), y: parseFloat(myTableArray[row][i])})
    });
    console.log(list_of_outputData);
    list_of_outputData.push({values: outputData, key: playerName});
    if (list_of_outputData[0]['key'] == undefined) {
        list_of_outputData.shift(); // remove first element from outputData as it is an empty template from the page load.
    }
    console.log(list_of_outputData);
    return list_of_outputData;
}

var outputPlotData = function() {
    mydata = get_outputData();
    return mydata;
}

$(function() {
    $('#project-list-table > tbody > tr').click(function(){
        $('#chart1').show();
        drawChart();
        /*$('.activated').removeClass('activated');*/
        $(this).toggleClass('activated');
        row = ($(this).index());
        playerName = myTableArray[row][0];
    });
});

/* Filters for the Player Name */
(function($){
    $.fn.multiFilter = function(filters) {
        var $table = $(this);
        return $table.find('tbody > tr').each(function() {
            var tr = $(this);

            // Make it an array to avoid special cases later.
            if(!$.isArray(filters))
                filters = [ filters ];

            howMany = 0;
            for(i = 0, f = filters[0]; i < filters.length; f = filters[++i]) {
                var index = 0;
                $table.find('thead > tr > th').each(function(i){
                    if($(this).text() == f.column) {
                        index = i;
                        return false;
                    }
                });
                var text = tr.find('td:eq(' + index + ')').text();
                if(text.toLowerCase().indexOf(f.word.toLowerCase()) != -1)
                    ++howMany;
            }
            if(howMany == filters.length)
                tr.show();
            else
                tr.hide();
        });
    };
})(jQuery);
