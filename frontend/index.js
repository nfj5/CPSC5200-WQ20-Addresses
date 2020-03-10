$(document).ready(function() {

	// set timeout for ajax functions
	$.ajaxSetup({timeout: 1000});

	let addr_formats = null;

	// load formats
	$.getJSON("http://localhost:5000/formats").done(function(response) {
		addr_formats = response;
		for (let country in addr_formats) {
			$("#Country").append(`<option value="${country}">${addr_formats[country]['name']}</option>`);
		}

		$("#loading").hide();
		$("#insert_form").show();

		let start = Object.keys(addr_formats)[0];
		$("#Country").val(null);
	}).fail(function(request, status, err) {
		$("#loading").html("Failed to load country formats. No response from server.");
	});

	// change fields when the dropdown changes
	$("#Country").change(function(){
		setForm($(this).val());
	});

	function setForm(country_code) {
		let country = addr_formats[country_code];
		let format = country['format'];
		let form_content = "";

		for (let field in format) {
			form_content += '<div style="margin-bottom: 10px;">';
			form_content += '<b style="padding-right: 20px;">' + field + '</b><br>';

			// handle dropdown (dictionary?)
			if (typeof format[field] === "object") {
				form_content += '<select id="' + field + '">';
				for (let option in format[field]) {
					form_content += '<option value="' + option + '">' + format[field][option] + '</option>';
				}
				form_content += '</select>';
			}

			// otherwise, plain text
			else {
				form_content += '<input id="' + field + '"  size="34">';
			}

			form_content += '</div>';
		}

		$("#dynamic_fields").html(form_content);
	}

	$("#search").click(function() {
		// $.get("/addresses")
	});

	$("#create").click(function() {
		let request = {};

		$("#fields").find(":input").each(function() {
			request[this.id] = this.val;
		});

		$.ajax({
			type: "POST",
			url: "http://localhost:5000/addresses",
			contentType: "application/json",
			data: JSON.stringify(request),
			dataType: "json"
		}).done(function(response) {
			console.log(response);
		}).fail(function() {
			console.log("Failed");
		});
	});

});