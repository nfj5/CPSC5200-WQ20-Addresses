$(document).ready(function() {

    let addr_formats = null;

    // load formats
    $.get("http://localhost:5000/formats", function(response){
        addr_formats = response.result;
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
                form_content += '<input id="">';
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