import pandas as pd
from geojson import Feature, Point, FeatureCollection
from geojson import dumps as gj_dumps

import google_service_api

import os

spreadsheet_id = os.getenv('spreadsheet_id')
complete_sheet_name = os.getenv('complete_sheet_name')
active_sheet_name = os.getenv('active_sheet_name')


def load_local_test():
    df = pd.read_excel('MLS Listings.xlsx', 'Complete')
    return df


def load_sheet_data(service):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=active_sheet_name).execute()
    values = result.get('values', [])

    df_old = pd.DataFrame(columns=values[0], data=values[1:])
    df_old = df_old.astype({'Id': 'int64'})
    return df_old


def update_dataframe(data_frame):
    data_frame['Price'] = data_frame['Price'].apply(lambda x: int(x))
    data_frame['Latitude'] = data_frame['Latitude'].apply(lambda x: float(x))
    data_frame['Longitude'] = data_frame['Longitude'].apply(lambda x: float(x))

    def rd(x, base=25000):
        mx = int(base * round(float(x) / base))

        return '{}-{}'.format((mx - base) + 1, mx)

    data_frame['Price Category'] = data_frame['Price'].apply(rd)
    data_frame['Address'] = data_frame['Address'].apply(lambda x: str(x))
    return data_frame


def _create_geojson(data_frame):
    fld = ['Address', 'Price', 'Price Category', 'GoogleLink', 'URL']
    geom_fld = ['Latitude', 'Longitude']
    sub_data = data_frame[fld + geom_fld]

    feature_list = []
    for i in sub_data.iterrows():
        _index, value = i
        geom = Point((value['Longitude'], value['Latitude']))
        props = value[fld].to_dict()
        feature = Feature(geometry=geom, properties=props)
        feature_list.append(feature)

    feature_collection = FeatureCollection(feature_list)

    return feature_collection


def get_mappings():
    # service = google_service_api.get_service()
    # df = load_sheet_data(service)

    df = load_local_test()

    df = update_dataframe(df)

    _geo_json = _create_geojson(df)

    return gj_dumps(_geo_json)
