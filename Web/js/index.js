$(document).ready(function(){
    $.getJSON("/data/data.json", function(data){
        for (i = 0; i < data.length; i++) {
            $("#sites").append([
                `<div id="${data[i].name}" class="row">`,
                '<div class="col-2">',
                `<button type="button" class="btn btn-link">${data[i].name}</button>`,
                '</div>',
                '<div class="col-5">',
                `<a href="https://maps.google.com/?q=${encodeURIComponent(data[i].address)}" target="_blank">${data[i].address}</a>`,
                '</div>',
                '<div class="col-5">',
                `${data[i].subnets.toString()}`,
                '</div>',
                '</div>'
            ].join('\n'));
        }
    }).fail(function(){
        console.log("Error reading JSON data file");
    });

    $('#sites').on('click', '.btn', function(e) {
        e.preventDefault();
        alert('test');
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