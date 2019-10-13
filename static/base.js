var sheet_name;
var geojson_data;
var map;
var base_url;

function get_sheet_name() {
    var _url = window.location.href;
    var _url_items = _url.split("/");

    var _base_url_slice = _url_items.slice(0, _url_items.length - 1);
    base_url = _base_url_slice.join("//")

    var _map_url = _url_items[_url_items.length - 1].replace("map-", "")
    //    console.log(_map_url)
    sheet_name = _map_url
    return _map_url
}

function load_data() {
    var data_url = base_url + "/" + 'mapData-' + sheet_name;

    map.addSource('listings',
        {
            'type': 'geojson',
            'data': data_url
        }
    )

    var mx_zoom = 15
    map.addLayer({
        "id": "listings-heat",
        "type": "heatmap",
        "source": "listings",
        "maxzoom": 14,
        "paint": {
            // Increase the heatmap weight based on frequency and property magnitude
            "heatmap-weight": [
                "interpolate",
                ["linear"],
                ["get", "Price"],
                350000, 0,
                500000, 1
            ],
            // Increase the heatmap color weight weight by zoom level
            // heatmap-intensity is a multiplier on top of heatmap-weight
            "heatmap-intensity": [
                "interpolate",
                ["linear"],
                ["zoom"],
                0, 0,
                12, 0.5
            ],
            // Color ramp for heatmap.  Domain is 0 (low) to 1 (high).
            // Begin color ramp at 0-stop with a 0-transparancy color
            // to create a blur-like effect.
            "heatmap-color": [
                "interpolate",
                ["linear"],
                ["heatmap-density"],
                0, 'rgba(0, 104, 55, 0)',
                0.25, 'rgba(134, 203, 102, 1)',
                0.5, 'rgba(254, 254, 189, 1)',
                0.75, 'rgba(248, 139, 81, 1)',
                1, 'rgba(165, 0, 38, 1)'
            ],
            // Adjust the heatmap radius by zoom level
            "heatmap-radius": [
                "interpolate",
                ["linear"],
                ["zoom"],
                0, 0,
                14, 50
            ],
            // Transition from heatmap to circle layer by zoom level
            "heatmap-opacity": [
                "interpolate",
                ["linear"],
                ["zoom"],
                13, 0.8,
                15, 0,
            ],
        }
    });


    map.addLayer({
        'id': 'listings-circles',
        'type': 'circle',
        'source': 'listings',
        'min_zoom': 10,
        // 'source-layer': 'sf2010',
        'paint': {
            // make circles larger as the user zooms from z12 to z22
            'circle-radius':
                [
                    "interpolate", ["linear"], ['zoom'],
                    // zoom is 5 (or less) -> circle radius will be 1px
                    7, 5,
                    // zoom is 10 (or greater) -> circle radius will be 5px
                    12, 10
                ],
            'circle-color':
                [
                    'interpolate',
                    ['linear'],
                    ['get', 'Price'],
                    300000, 'rgba(0, 104, 55, 1)',
                    // 350000, 'rgba(134, 203, 102, 1)',
                    // 400000, 'rgba(254, 254, 189, 1)',
                    // 450000, 'rgba(248, 139, 81, 1)',
                    500000, 'rgba(165, 0, 38, 1)'
                ],
            'circle-opacity': 0.8,
            "circle-opacity": [
                "interpolate",
                ["linear"],
                ["zoom"],
                12, 0,
                13, 1
                ]

        }
    });
    // console.log(cmap_data[0]);
    map.on('mousedown', function (e) {
        features = map.queryRenderedFeatures(e.point, { layers: ['listings-circles'] });
        if (features.length > 0) {
            console.log(features.length)
            console.log({
                'price': features[0].properties.Price,
            })
        }
        // document.getElementById('features').innerHTML = JSON.stringify(features, null, 2);
    });
}
var features;
function get_geojson() {
    var data_url = base_url + "/" + 'mapData-' + sheet_name;
    $.getJSON(data_url, function (_data) {
        geojson_data = _data;
    });
}
// console.log('test');
function start_work() {
    get_sheet_name();
    load_map();
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
        get_geojson();
        load_data();
    });

}

$(document).ready(start_work)