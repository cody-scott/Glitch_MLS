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
    map.addLayer({
        'id': 'listings',
        'type': 'circle',
        'source': {
            type: 'geojson',
            data: data_url
        },
        // 'source-layer': 'sf2010',
        'paint': {
            // make circles larger as the user zooms from z12 to z22
            'circle-radius':
                [
                    "interpolate", ["linear"], ['get', 'Price'],
                    // zoom is 5 (or less) -> circle radius will be 1px
                    0, 10,
                    // zoom is 10 (or greater) -> circle radius will be 5px
                    400000, 20
                ],

            'circle-color': [
                'to-rgba',
                // ['at', 1, ['literal', test_data]],
                [
                    'at',
                    [
                        "interpolate",
                        ["linear"],
                        ['get', 'Price'],
                        300000, 0,
                        500000, 255,
                    ],
                    ['literal', cmap_rgba_list]
                ]
                // 0,
                // 0,
            ]

            // color circles by ethnicity, using a match expression
            // https://docs.mapbox.com/mapbox-gl-js/style-spec/#expressions-match
            //     'circle-color': [
            //         'match',
            //         ['get', 'ethnicity'],
            //         'White', '#fbb03b',
            //         'Black', '#223b53',
            //         'Hispanic', '#e55e5e',
            //         'Asian', '#3bb2d0',
            // /* other */ '#ccc'
            //     ]
        }
    });
    console.log(cmap_data[0]);
    map.on('mousedown', function (e) {
        features = map.queryRenderedFeatures(e.point, { layers: ['listings'] });
        if (features.length > 0) {
            console.log(features[0])
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