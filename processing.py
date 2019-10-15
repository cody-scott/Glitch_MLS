import requests
import json
import urllib
import os

import pandas as pd
from collections import OrderedDict
import datetime

import logging

base_url = 'https://api2.realtor.ca/Listing.svc/PropertySearch_Post'

config_file = r'config.json'

spreadsheet_id = os.getenv('spreadsheet_id')
complete_sheet_name = os.getenv('complete_sheet_name')
active_sheet_name = os.getenv('active_sheet_name')


def get_query_string(_query_data):
    return "&".join(
        ["{}={}".format(key, _query_data[key]) for key in _query_data])


def load_query_data():
    data = None
    with open(config_file) as fl:
        data = json.loads(fl.read())
    return data


def request_data(_query_parameters, current_page=1):
    query_string = get_query_string(_query_parameters)
    query_string = "{}&CurrentPage={}".format(query_string, current_page)
    response = requests.post(base_url, data=query_string)
    return response


def get_listings(query_parameters):
    response = request_data(query_parameters)

    # print(response.content.decode("utf-8"))
    data = json.loads(response.content.decode("utf-8"))
    if response.status_code != 200:
        logging.error("ERROR in request")
        logging.error(data)

    out_data = []
    out_data.extend(data['Results'])

    total_pages = data['Paging']['TotalPages']
    current_page = data['Paging']['CurrentPage']

    if total_pages > 1:
        for i in range(current_page + 1, total_pages + 1):
            response = request_data(query_parameters, current_page=i)
            data = json.loads(response.content.decode("utf-8"))
            if response.status_code != 200:
                logging.error("ERROR")
                logging.error(data)
            out_data.extend(data['Results'])
    print(len(out_data))
    return out_data


def get_freehold_listings(listings=None):
    only_list = ["Freehold"]
    type_list = ["Single Family"]
    freehold_listings = []

    for item in listings:
        props = item.get('Property')
        if props is None:
            continue

        o_type = props.get('OwnershipType')
        t_type = props.get("Type")
        if (o_type is None) or (t_type is None):
            continue

        if (o_type in only_list) or ((o_type is None) and (t_type in type_list)):
            freehold_listings.append(item)
    
    # freehold_listings = [item for item in listings if
    #                      item['Property']['OwnershipType'] in only_list]
    print(len(freehold_listings))
    return freehold_listings


def listings_to_dataframe(listings):
    pandas_raw = []
    for fh in listings:
        var = OrderedDict({
            'Id': int(fh['Id']),
            'MlsNumber': fh["MlsNumber"],
            'Address': fh["Property"]["Address"]["AddressText"].replace("|",
                                                                        " "),
            'Latitude': float(fh["Property"]["Address"]["Latitude"]),
            'Longitude': float(fh["Property"]["Address"]["Longitude"]),
            'PropertyType': fh["Property"]["Type"],
            'OwnershipType': fh["Property"]["OwnershipType"],
            'Price': int(
                fh["Property"]["Price"].replace("$", "").replace(",", "")),
            'PriceChangeDateUTC': fh.get('PriceChangeDateUTC', ""),
            'Active': True,
            "GoogleLink": "https://www.google.ca/maps/@{},{},20z".format(
                fh["Property"]["Address"]["Latitude"],
                fh["Property"]["Address"]["Longitude"],
            ),
            'URL': "https://www.realtor.ca{}".format(fh["RelativeDetailsURL"]),
            "CreateDate": datetime.datetime.now().strftime(
                "%Y-%m-%d 00:00:00 AM"),
        })
        pandas_raw.append(var)
    df = pd.DataFrame(pandas_raw)
    df = df.drop_duplicates(subset="Id")
    return df


def load_old_data(service, _spreadsheet_id=None, _sheet_name=None):
    if _spreadsheet_id is not None:
        sheet_id = _spreadsheet_id
    else:
        sheet_id = spreadsheet_id

    if _sheet_name is not None:
        sheet_name = _sheet_name
    else:
        sheet_name = complete_sheet_name

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=sheet_name).execute()
    values = result.get('values', [])

    df_old = pd.DataFrame(columns=values[0], data=values[1:])
    df_old = df_old.astype({'Id': 'int64'})
    return df_old


def generate_new_frames(new_listings, old_listings):
    old_listings.loc[
        old_listings["Id"].isin(new_listings["Id"]), "Active"] = True
    old_listings.loc[
        ~old_listings["Id"].isin(new_listings["Id"]), "Active"] = False

    # new listings
    old_id_active = old_listings.loc[
        old_listings["Id"].isin(new_listings["Id"])]
    new_freehold = new_listings.loc[
        ~new_listings["Id"].isin(old_id_active['Id'])]

    # new full list (second tab)
    new_full_list = pd.concat([old_listings, new_freehold], sort=False)

    # new active listings
    active_listings = pd.concat([old_id_active, new_freehold], axis=0, sort=False)
    active_listings = active_listings.drop_duplicates('Id', keep='last')
    active_listings = active_listings.drop(columns=["Active"])

    active_listings["CreateDate"] = pd.to_datetime(
        active_listings["CreateDate"])
    new_full_list["CreateDate"] = pd.to_datetime(new_full_list["CreateDate"])

    def fix_dt(x):
        if type(x) == pd.Timestamp:
            return x.strftime("%Y-%m-%d 00:00:00")
        else:
            return ''
    active_listings["CreateDate"] = active_listings["CreateDate"].apply(fix_dt)
    new_full_list["CreateDate"] = new_full_list["CreateDate"].apply(fix_dt)

    return active_listings, new_full_list


def save_to_sheets(active_df, full_df, service):
    save_to_sheet(active_df, active_sheet_name, service)
    save_to_sheet(full_df, complete_sheet_name, service)


def save_to_sheet(_df, sheet_range, service):
    values = [_df.columns.tolist()] + _df.values.tolist()
    body = {
        'values': values
    }
    value_input_option = "USER_ENTERED"
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=sheet_range,
        valueInputOption=value_input_option, body=body).execute()
    pass

def clear_active_sheet(service):
    range_ = active_sheet_name  # TODO: Update placeholder value.

    clear_values_request_body = {
    }

    request = service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id, range=range_,
        body=clear_values_request_body)
    response = request.execute()

# endregion
def process(service):
    # clear_active_sheet(service)

    logging.info("Getting listings")

    query_parameters = load_query_data()
    new_listings = []
    for param in query_parameters:
        new_listings += get_listings(param)

    logging.info("{} listings found".format(len(new_listings)))
    logging.info("Getting freehold")
    freehold_listings = get_freehold_listings(new_listings)
    logging.info("{} freehold listings found".format(len(freehold_listings)))
    logging.info("Converting to dataframe")
    freehold_data_frame = listings_to_dataframe(freehold_listings)

    logging.info("Loading old data")
    old_excel_list = load_old_data(service)

    logging.info("Updating Data")
    active_df, full_df = generate_new_frames(freehold_data_frame,
                                             old_excel_list)

    logging.info("Saving Tables")
    save_to_sheets(active_df, full_df, service)

    
def current_listings_csv(service, _format=None):    
    df = load_old_data(service)
    if _format=="JSON":
        return df.to_json()
    else:
        return df.to_csv()

    return df.to_csv()
