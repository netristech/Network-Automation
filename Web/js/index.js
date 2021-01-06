$(document).ready(function(){
    $.getJSON("/data/data.json", function(data){
        for (i = 0; i < data.length; i++) {
            $("#sites").append([
                `<tr id="${data[i].name}">`,
                '<th scope="col">',
                `<button type="button" class="btn btn-link">${data[i].name}</button>`,
                '</th>',
                '<th scope="col">',
                `<a href="https://maps.google.com/?q=${encodeURIComponent(data[i].address)}" target="_blank">${data[i].address}</a>`,
                '</th>',
                '<th scope="col">',
                `${data[i].subnets.toString()}`,
                '</th>',
                '</tr>'
            ].join('\n'));
        }
    }).fail(function(){
        console.log("Error reading JSON data file");
    });

    $('#sites').on('click', '.btn', function(e) {
        e.preventDefault();
        alert($(this).html());
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