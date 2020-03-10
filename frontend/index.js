$(document).ready(function() {

    // set timeout for ajax functions
    $.ajaxSetup({timeout: 1000});

    let addr_formats = null;

    // load formats
    $.getJSON("http://localhost:5000/formats").done(function(response) {
        addr_formats = response;
        for (let country in addr_formats) {
            $("#country_dropdown").append(`<option value="${country}">${addr_formats[country]['name']}</option>`);
        }

        $("#loading").hide();
        $("#insert_form").show();

        // TODO: We should not default to the first country
        // Let's leave blank and put a msg:
        // Please select a country
        // When empty can search all countries.
        // set the form to the first country by default
        let start = Object.keys(addr_formats)[0];
        $("#country_dropdown").val(null);
    }).fail(function(request, status, err) {
        $("#loading").html("Failed to load country formats. No response from server.");
    });

    // change fields when the dropdown changes
    $("#country_dropdown").change(function(){
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
                form_content += '<select id="">';
                for (let option in format[field]) {
                    form_content += '<option value="' + option + '">' + format[field][option] + '</option>';
                }
                form_content += '</select>';
            }

            // otherwise, plain text
            else {
                form_content += '<input id=""  size="34">';
            }

            form_content += '</div>';
        }

        $("#fields").html(form_content);
    }

    $("#search").click(function() {
        // $.get("/addresses")
    });

    $("#create").click(function() {
        // $.post("/addresses")
    });

});