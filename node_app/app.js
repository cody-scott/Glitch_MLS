const turf = require('@turf/turf')
const express = require('express')
const app = express()
const port = 8000;
var bodyParser = require("body-parser");
app.use(bodyParser.json({ limit: '10mb', extended: true }))
app.use(bodyParser.urlencoded({ limit: '10mb', extended: true }))

function calculate_tin_map(data) {
  console.log("Loading Tin");
  var options = { gridType: 'points', property: 'Price', units: 'kilometers' };
  var grid = turf.interpolate(data, 2, options);
  var tin_grid = turf.tin(grid, 'Price')
  tin_grid = turf.rewind(tin_grid)
  console.log('Tin Generated');
  return tin_grid;
}

function get_tin_point(_point, _tmap) {
  var _click_grid = undefined;
  var _price_estimation = 0;

  for (var i in _tmap['features']) {
    var tg = _tmap['features'][i];
    if (turf.booleanPointInPolygon(_point, tg) === true) {
      _click_grid = tg;
      _price_estimation = turf.planepoint(_point, _click_grid);
      _price_estimation = Math.round(_price_estimation, 0);
      return _price_estimation;
    }
  }
  return _price_estimation;
}

function parse_row(row) {
  var geometry = {
    "type": "Point",
    "coordinates": [
      parseFloat(row['Longitude']),
      parseFloat(row['Latitude'])
    ]
  }
  var properties = {
    'Id': parseInt(row['Id']),
    'Price': parseInt(row['Price'])
  }
  var feature = turf.feature(geometry, properties);
  return feature;
}

function _generate_feature_collection(_data) {
  var _out_data = [];
  for (var row in _data) {
    var feature = parse_row(_data[row]);
    _out_data.push(feature);
  }
  var _fc = turf.featureCollection(_out_data);
  return _fc;
}


function process_complete_data(_data) {
  return new Promise((resolve, reject) => {
    var _fc = _generate_feature_collection(_data);
    var t_map = calculate_tin_map(_fc)
    resolve(t_map)
  })
}

function process_active_data(_data, _tmap) {
  console.log("Processing active records");
  var _out_data = {};
  // var _out_data = [["Id", "Estimate"]];
  for (var row in _data) {
    var _feature = parse_row(_data[row]);
    var _p_est = get_tin_point(_feature.geometry, _tmap);
    var _fid = _feature.properties.Id;
    // _out_data.push(
    //   { _fid, _p_est }
    // );
    _out_data[_fid] = _p_est;
  }
  return _out_data;
}

app.post('/', (req, res) => {
  var _a_list = JSON.parse(req.body.active);
  var _c_list = JSON.parse(req.body.complete);
  var _outdata = [];
  var _tmap = process_complete_data(_c_list).then(function (value) {
    _outdata = process_active_data(_a_list, value);
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(_outdata));
    console.log("Done");
  })
})

app.listen(port, () => console.log(`Example app listening on port ${port}!`))
