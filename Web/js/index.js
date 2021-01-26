var view = 'sites';
//var site_color = '#00ff00';

$(document).ready(function(){
    drawScreen();

    $('#login').on('click', '#login-btn', function(e) {
        e.preventDefault();
        $('#login-btn .spinner-border').removeClass('hide');
        //var server = $('#server').val();
        var username = $('#username').val();
        var password = $('#password').val();
        $.ajax({
            url: 'functions.php',
            type: 'post',
            data: 'action=login&username='+username+'&password='+password,
            success: function(response) {
                if (response == 0) {
                    //alert('success');
                    window.location.replace('/main.php');
                } else {
                    //alert('fail');
                    showError();
                    $('#login-btn .spinner-border').addClass('hide');
                }
            },
        });
    });

    $('#nav').on('click', '#sign-out-btn', function(e) {
        e.preventDefault();
        $.ajax({
            url: 'functions.php',
            type: 'post',
            data: 'action=logout',
            success: function() {
                window.location.replace('/index.php');
            },
        });
    });

    $('#sites-table').on('click', '.btn', function(e) {
        e.preventDefault();
        alert($(this).html());
    });

    $('#import-modal').on('click', '#import-btn', function(e) {
        e.preventDefault();
        clearError();
        var fd = new FormData();
        var files = $('#import-file')[0].files[0];
        fd.append('file', files);

        $.ajax({
            url: 'upload.php',
            type: 'post',
            data: fd,
            contentType: false,
            processData: false,
            success: function(response) {
                if (response != 0) {
                    //alert(response);
                    parseCSV(response);
                    $('#import-modal').modal('hide');
                } else {
                    showError();
                }
            },
        });
    });

    $('#nav').on('click', '#import-btn', function(e) {
        e.preventDefault();
        $('#import-form').trigger('reset');
        clearError();
    });
});

function hideElements(elems) {
    $.each(elems, function(index, value) {
        $(value).addClass('hide');
    });
}

function showElements(elems) {
    $.each(elems, function(index, value) {
        $(value).removeClass('hide');
    });
}

function clearError() {
    $('.alert-danger').each(function() {
        $(this).hide();
    });
    $('input').each(function() {
        $(this).removeClass('error');
    });
}

function showError() {
    $('.alert-danger').each(function() {
        $(this).show();
    });
    $('input').each(function() {
        $(this).addClass('error');
    });
}

function drawScreen() {
    switch(view) {
        case 'sites':
            showElements(['#import-btn', '#export-btn']);
            $.getJSON("/data/data.json", function(data){
                for (i = 0; i < data.length; i++) {
                    $("#sites-table tbody").append([
                        '<tr>',
                        `<td id="${data[i].name}"><button type="button" class="btn btn-link data-item" style="padding: 0px;">${data[i].name}</button></td>`,
                        `<td class="align-middle"><a href="https://maps.google.com/?q=${encodeURIComponent(data[i].address)}" target="_blank" class="data-item">${data[i].address}</a></td>`,
                        `<td class="align-middle"><span class="data-item">${data[i].subnets.toString()}</span></td>`,
                        /*`<td class="align-middle text-center"><i class="fas fa-circle data-item" style="color: ${site_color};"></i></td>`,*/
                        '</tr>'
                    ].join('\n'));
                }
            }).fail(function(){
                console.log("Error reading JSON data file");
            });
            break;
        case 'devices':
            showElements(['#import-btn', '#export-btn']);
            break;
    }
}

function parseCSV(file) {
    var reader = new FileReader();
    reader.onload = function(e) {
        fileContent = reader.result;
    }
    reader.readAsText(file);
    return fileContent;
}