$(document).ready(function(){
    $.getJSON("/data/data.json", function(data){
        for (i = 0; i < data.length; i++) {
            $("#sites-table tbody").append([
                '<tr>',
                `<td id="${data[i].name}"><button type="button" class="btn btn-link">${data[i].name}</button></td>`,
                `<td><a href="https://maps.google.com/?q=${encodeURIComponent(data[i].address)}" target="_blank">${data[i].address}</a></td>`,
                `<td>${data[i].subnets.toString()}</td>`,
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

    $('#nav')
});

// class for sites
class Site {
    constructor(params) {
        this.name = params.name;
        this.address = params.address;
        this.subnets = params.subnets;
    }
}