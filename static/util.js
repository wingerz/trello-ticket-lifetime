function processData(data) {
    $.each(data.items, function(index, item) {
        item['start'] = new Date(item['start']);
        item['end'] = new Date(item['end']);
    });
}
