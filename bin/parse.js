var JSONStream = require('JSONStream');
var fs = require('fs');

var fileName = 'export.json';
var fd = fs.openSync(fileName, 'r');
var readStream = fs.createReadStream(fileName);
var fileSize = fs.fstatSync(fd)['size'];
console.log('File size: ', fileSize);

var place = 0;

readStream
    .on('data', function (chunk) {
        console.log(Math.round(place / fileSize * 100) / 100 + '%');
        place += chunk.length;
    })
    .pipe(JSONStream.parse('hexes.*'))
    .on('data', function(data) {
        //console.dir(this);
    });
