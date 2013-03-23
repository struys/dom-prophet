$(function() {
	var userBreakDown = $('.user-breakdown');
	var histogram = $('.histogram');
	
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
	
	if(histogram) {
		chart = new Chart(histogram[0].getContext("2d"));
		
		chart.Line({
			labels: window.histogram.labels,
			datasets: [
			   {
				   	fillColor : "rgba(220,220,220,0.5)",
					strokeColor : "rgba(220,220,220,1)",
					pointColor : "rgba(220,220,220,1)",
					pointStrokeColor : "#fff",
					data: window.histogram.mouseenter
			   },
			   {
					fillColor : "rgba(151,187,205,0.5)",
					strokeColor : "rgba(151,187,205,1)",
					pointColor : "rgba(151,187,205,1)",
					pointStrokeColor : "#fff",
					data: window.histogram.click
			   }
			]
		})
	}

});