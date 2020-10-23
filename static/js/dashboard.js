/* globals Chart:false, feather:false */

(function () {
	'use strict'
	// Graphs
	// Create a new FormData instance
	var datareq = new FormData();
	// Create a XMLHTTPRequest instance
	var request = new XMLHttpRequest();
	// Set the response type
	request.responseType = "json";

	var week = "Week 4";
	datareq.append("week", week);
	// request load handler (transfer complete)
	request.addEventListener("load", function (e) {

	if (request.status == 200) {
		var datares = [request.response.datares];
		console.log(datares)
		feather.replace()
	var ctx = document.getElementById('myChart');
	var myChart = new Chart(ctx, {
	  
		type: 'bar',
		data: {
		  labels: [
			'Sunday',
			'Monday',
			'Tuesday',
			'Wednesday',
			'Thursday',
			'Friday',
			'Saturday'
		  ],
		  datasets: [{
					backgroundColor: "#BDEDFF",
					borderColor: "#3BB9FF",
					borderWidth: 2,
					data: datares[0]
				}]
		},
		options: {
			responsive: true,
			legend: {
				position: 'top',
			},
			title: {
				display: true,
				text: 'WEEK DATA'
			}
		}
	  });
	}
	else {
	  alert("error in response");
	}

	});
	// request error handler
	request.addEventListener("error", function (e) {
	reset();
	alert("error in while uploading");
	});
	// Open and send the request
	request.open("post", "/weekData");
	request.send(datareq);

}())


