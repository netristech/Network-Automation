var view = 'sites';
var site_color = '#00ff00';

$(document).ready(function(){
    drawScreen();

    $('#sites-table').on('click', '.btn', function(e) {
        e.preventDefault();
        alert($(this).html());
    });

    $('#import-modal').on('click', '#import-btn', function(e) {
        e.preventDefault();
        var data = new FormData();
        var files = $('#import-file')[0].files[0];
        data.append('file', files);

        $.ajax({
            url: 'upload.php',
            type: 'post',
            data: data,
            contentType: false,
            processData: false,
            success: function(response) {
                if (response !=0) {
                    //csvToJSON();
                    $('#import-modal').modal('hide');
                    view = 'sites';
                    drawScreen();
                } else {
                    $('#import-form .modal-body').append('<div class="alert alert-danger">Error uploading file, please check file type and size are correct.</div>');
                }
            }
        });
    });

    /*$('#nav').on('click', '#edit-btn', function(e) {
        e.preventDefault();
        //alert('test');
        view = 'edit';
        $('.data-item').each(function() {
            $(this).replaceWith(`<input type="text" class="data-item" value="${$(this).html()}" />`);
        });
        drawScreen();
    });*/
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

function drawScreen() {
    switch(view) {
        case 'sites':
            //hideElements(['#add-btn', '#save-btn', '#cancel-btn']);
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
            //hideElements(['#edit-btn', '#export-btn']);
            showElements(['#import-btn', '#export-btn']);
            break;
    }
}