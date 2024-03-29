import pandas as pd
from geojson import Feature, Point, FeatureCollection
from geojson import dumps as gj_dumps

import google_service_api

import os

spreadsheet_id = os.getenv('spreadsheet_id')
complete_sheet_name = os.getenv('complete_sheet_name')
active_sheet_name = os.getenv('active_sheet_name')

from flask import current_app, request

def _is_local():
    if os.getenv("local") is not None:
        current_app.logger.info("Is Local")
        return True
    else:
        return False

def load_local_test(sheet_name):
    df = pd.read_excel('MLS Listings.xlsx', sheet_name)
    return df


def load_sheet_data(service, sheet_range=None):
    if sheet_range is None:
        sheet_range = active_sheet_name

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

    data_frame['Latitude'] = data_frame['Latitude'].round(5)
    data_frame['Longitude'] = data_frame['Longitude'].round(5)

    data_frame['Address'] = data_frame['Address'].apply(lambda x: str(x))
    data_frame['Estimate'] = data_frame['Estimate'].fillna(0)

    return data_frame


def _create_geojson(data_frame, fld=None):
    if fld is None:
        fld = ['Id', 'Address', 'Price', 'GoogleLink', 'URL', 'Estimate']

    geom_fld = ['Latitude', 'Longitude']
    sub_data = data_frame[fld + geom_fld]

    feature_list = []
    for i in sub_data.iterrows():
        _index, value = i
        geom = Point((float(value['Longitude']), float(value['Latitude'])))
        props = value[fld].to_dict()
        feature = Feature(geometry=geom, properties=props)
        feature_list.append(feature)

    feature_collection = FeatureCollection(feature_list)

    return feature_collection


def get_unique_lat_long():
    if _is_local():
        df = load_local_test('Complete')
    else:
        service = google_service_api.get_service()
        df = load_sheet_data(service, complete_sheet_name)
    # print(df.shape)
    df = df.loc[~df["CreateDate"].isnull()]
    # print(df.shape)
    df = df.round(5)
    df = df.groupby(['Latitude', "Longitude"]).agg({'Price': 'min'}).reset_index()

    _geo_json = _create_geojson(df, ['Price'])

    return gj_dumps(_geo_json)


def get_mappings(max_price=None):
    if max_price is None:
        max_price = 999999
    
    r = request
    current_app.logger.info("Getting Max price: {}".format(max_price))
    

    if _is_local():
        df = load_local_test('Active')
    else:
        service = google_service_api.get_service()
        df = load_sheet_data(service, active_sheet_name)

    df = update_dataframe(df)
    df = df.loc[df['Price']<=max_price]

    _geo_json = _create_geojson(df)

    return gj_dumps(_geo_json)
