var sheet_name;
var base_url;

var map;

var geojson_data;
var unique_geojson;
var tin_grid;

var clickpoint;
var click_grid;
var price_estimation;


function get_sheet_name() {
    var _url = window.location.href;
    var _url_items = _url.split("/");

    var _base_url_slice = _url_items.slice(0, _url_items.length - 1);
    base_url = _base_url_slice.join("//")

    var _map_url = _url_items[_url_items.length - 1].replace("map-", "")
    sheet_name = _map_url
    return _map_url
}

function calculate_tin_map(data) {
    console.log("Loading Tin");
    var options = { gridType: 'points', property: 'Price', units: 'kilometers' };
    var grid = turf.interpolate(unique_geojson, 2, options);
    tin_grid = turf.tin(grid, 'Price')
    tin_grid = turf.rewind(tin_grid)
    console.log('Tin Generated');

    // map.on('click', get_tin_point);
    map.on('click', feature_overlay);
}

function get_tin_point(_clickpoint) {
    click_grid = undefined;
    var _price_estimation = 0;

    // var _clickpoint = get_map_click(e);
    for (var i in tin_grid['features']) {
        var tg = tin_grid['features'][i];
        if (turf.booleanPointInPolygon(_clickpoint, tg) === true) {
            _click_grid = tg;
            _price_estimation = turf.planepoint(_clickpoint, _click_grid);
            _price_estimation = Math.round(_price_estimation, 0);
            // console.log("Estimated Price: " + _price_estimation);

            click_grid = _click_grid;
            price_estimation = _price_estimation;

            return _price_estimation
        }
    }

    console.log("Unable to obtain estimation\nOutside TIN Area?")
    return _price_estimation
}

function get_listing_price(e) {
    var features = map.queryRenderedFeatures(e.point, { layers: ['listings-circles'] });
    if (features.length > 0) {
        // console.log(features.length)
        // console.log("Listing Price: " + features[0].properties.Price)
    }
}

function get_map_click(e) {
    var feat = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [e.lngLat['lng'], e.lngLat['lat']]
        },
        "properties": {
        }
    }
    clickpoint = feat;
    return feat;
}

function load_tin_geojson(data_source) {
    $.getJSON(data_source, function (data) {
        unique_geojson = data;
        calculate_tin_map(data);
    });
}


function load_data_geojson(data_source) {
    $.getJSON(data_source, function (data) {
        geojson_data = data;
        load_data(data);
    });
}

function load_data(data_source) {
    map.addSource('listings',
        {
            'type': 'geojson',
            'data': data_source
        }
    )
    map.addLayer({
        'id': 'listings-circles',
        'type': 'circle',
        'source': 'listings',
        'paint': {
            'circle-radius':
                [
                    "interpolate", ["linear"], ['zoom'],
                    // zoom is 5 (or less) -> circle radius will be 1px
                    10, 2,
                    // zoom is 10 (or greater) -> circle radius will be 5px
                    12, 12
                ],
            'circle-color':
                [
                    'interpolate',
                    ['linear'],
                    ['get', 'Price'],
                    300000, 'rgba(0, 104, 55, 1)',
                    350000, 'rgba(134, 203, 102, 1)',
                    400000, 'rgba(254, 254, 189, 1)',
                    450000, 'rgba(248, 139, 81, 1)',
                    500000, 'rgba(0, 0, 0, 0)'
                ],
            "circle-opacity": [
                "interpolate",
                ["linear"],
                ["zoom"],
                9, 0,
                10, 1
            ],
            'circle-blur': 0.2,
            'circle-stroke-color': [
                'interpolate',
                ['linear'],
                ['get', 'Price'],
                499999, 'rgba(0, 0, 0, 0)',
                500000, 'rgba(165, 0, 38, 1)'
            ],
            "circle-stroke-width": 1
        }
    });

}


function load_map() {
    mapboxgl.accessToken = 'pk.eyJ1IjoiamNvZHlzY290dCIsImEiOiJjaWk3c29xeGgwMjlvdHptMDdldDljamo5In0.h3XDeqo9J3oyLvEiJ4DAPQ';
    map = new mapboxgl.Map({
        container: 'map', // container id
        style: 'mapbox://styles/mapbox/dark-v9',
        // style: 'mapbox://styles/mapbox/outdoors-v10', // stylesheet location
        center: [-80.479835, 43.454449], // starting position [lng, lat]
        zoom: 10 // starting zoom
    });

    map.on('load', function () {
        load_tin_geojson(base_url + "/" + 'mapData-Collected-' + sheet_name);
        load_data_geojson(base_url + "/" + 'mapData-' + sheet_name);
    });

}

var overlay = document.getElementById('map-overlay');

var tmp_feat;
function feature_overlay(e) {
    overlay.innerHTML = '';
    
    var buff = 20;
    var bbox = [[e.point.x - buff, e.point.y - buff], [e.point.x + buff, e.point.y + buff]];
    var features = map.queryRenderedFeatures(bbox, { layers: ['listings-circles'] });
  
    if (features.length === 0) {
        overlay.style.display = 'none';
        return
    }

    var feature = features[0]; 
    var _est_price = get_tin_point(feature);
    _est_price = "$ " + _est_price.toLocaleString();

    var _price = feature.properties.Price;
    _price = "$ " + _price.toLocaleString();

    var _address = feature.properties.Address;
    var _listing_url = feature.properties.URL;
    var _id = feature.properties.Id;

    var title = document.createElement('strong');
    title.textContent = "Address: " + _address;

    overlay.appendChild(title);

    
    var arr = [["Id", _id], ["Price", _price], ["Estimated Price", _est_price]];
    for (var f in arr) {
        f = arr[f]
        var _content = document.createElement('div');
        _content.textContent += f.join(": ");
        overlay.appendChild(_content);
    }

    var _content = document.createElement('div');
    var _link_content = document.createElement('a');
    _link_content.textContent += "Realtor Link";
    _link_content.setAttribute('href', _listing_url);
    _link_content.setAttribute('target', "_blank");
    _content.appendChild(_link_content);
    overlay.appendChild(_content);

    overlay.style.display = 'block';
}

$(document).ready(function () {
    get_sheet_name();
    load_map();
})

function update_heatmap(key, new_value) {
    map.setPaintProperty('listings-heat', key, new_value);
}

function update_listing_circles(key, new_value) {
    map.setPaintProperty('listings-circles', key, new_value);
}