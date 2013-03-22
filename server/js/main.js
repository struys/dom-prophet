$(function() {


    var userBreakDown = $('.user-breakdown');

    if(userBreakDown.length > 0 && window.percentBreakdown) {
        chart = new Chart(userBreakDown[0].getContext("2d"));
        chart.Doughnut([
            {
                value: percentBreakdown.logged_in,
                color: "#F7464A"
            },
            {
                value: percentBreakdown.logged_out,
                color: "#E2EAE9"
            }
        ]);
    }

});