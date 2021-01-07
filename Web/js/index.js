var view = 'sites';

$(document).ready(function(){
    if (view != 'edit') {
        $('#add-btn').addClass('hide');
        $('#save-button').addClass('hide');
        $('#cancel-button').addClass('hide');
    }
    $.getJSON("/data/data.json", function(data){
        for (i = 0; i < data.length; i++) {
            $("#sites-table tbody").append([
                '<tr>',
                `<td id="${data[i].name}"><button type="button" class="btn btn-link data-item">${data[i].name}</button></td>`,
                `<td class="align-middle"><a href="https://maps.google.com/?q=${encodeURIComponent(data[i].address)}" target="_blank" class="data-item">${data[i].address}</a></td>`,
                `<td class="align-middle"><span class="data-item">${data[i].subnets.toString()}</span></td>`,
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
        $('.data-item').each(function() {
            $(this).replaceWith(`<input type="text" class="data-item" value="${$(this).html()}" />`);
        });
    });
});

// class for sites
class Site {
    constructor(params) {
        this.name = params.name;
        this.address = params.address;
        this.subnets = params.subnets;
    }
}