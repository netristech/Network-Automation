var view = 'sites';
var site_color = '#00ff00';

$(document).ready(function(){
    drawScreen();
    $.getJSON("/data/data.json", function(data){
        for (i = 0; i < data.length; i++) {
            $("#sites-table tbody").append([
                '<tr>',
                `<td id="${data[i].name}"><button type="button" class="btn btn-link data-item">${data[i].name}</button></td>`,
                `<td class="align-middle"><a href="https://maps.google.com/?q=${encodeURIComponent(data[i].address)}" target="_blank" class="data-item">${data[i].address}</a></td>`,
                `<td class="align-middle"><span class="data-item">${data[i].subnets.toString()}</span></td>`,
                `<td class="align-middle text-center"><i class="fas fa-circle data-item" style="color: ${site_color};"></i></td>`,
                '</tr>'
            ].join('\n'));
        }
    }).fail(function(){
        console.log("Error reading JSON data file");
    });

    $('#sites-table').on('click', '.btn', function(e) {
        e.preventDefault();
        alert($(this).html());
    });

    $('#nav').on('click', '#edit-btn', function(e) {
        e.preventDefault();
        //alert('test');
        view = 'edit';
        $('.data-item').each(function() {
            $(this).replaceWith(`<input type="text" class="data-item" value="${$(this).html()}" />`);
        });
        drawScreen();
    });
});

function drawScreen() {
    switch(view) {
        case 'sites':
            hideElements(['#add-btn', '#save-btn', '#cancel-btn']);
            showElements(['#edit-btn', '#export-btn']);
            break;
        case 'edit':
            hideElements(['#edit-btn', '#export-btn']);
            showElements(['#add-btn', '#save-btn', '#cancel-btn']);
            break;
    }
}

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