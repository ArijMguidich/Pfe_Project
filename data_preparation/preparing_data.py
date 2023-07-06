"""
prepare needed data
author : HaJA
"""
import json
import logging

import numpy as np
import pandas as pd
from pandas import DataFrame, Series

logger = logging.getLogger(__name__)
import pandas as pd

def import_all_data(csv_data_path: str) -> DataFrame:
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    |       import ETHERNET_FIBEX_topology.csv
    |       :param csv_data_path: csv data path
    |       :return: ETHERNET_FIBEX_topology pandas data frame
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    data = None
    try:
        data = pd.read_csv(csv_data_path, sep=";")
    except IOError as ex:
        logger.error(ex)
    else:
        logger.debug(f"{csv_data_path} readed successfully ")
    return data


def prepare_data(data: DataFrame, config_path: str) -> DataFrame:
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    |       1- replace nan values by white spaces
    |       2- create vlan column and concatenate all columns
    |       3- delete left and right white spaces
    |       :param data: ETHERNET_FIBEX_topology data frame
    |       :return:
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    # repalce nan value by empty strings
    data = data.replace(np.nan, "")
    # create vlan column
    vlans_data = data.iloc[:, 9:]
    # create vlan columns
    data['vlan'] = vlans_data.apply(lambda x: " ".join(x), axis=1)
    data['vlan'] = data['vlan'].apply(lambda x: x.lstrip().rstrip())
    data['vlan'] = data['vlan'].apply(lambda x: x.lstrip().rstrip())
    data['vlan'] = data['vlan'].apply(lambda x: x.strip())
    return data



def prepare_controller_to_ecu_data_set(data: DataFrame, ecu: str) -> tuple:
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    |       prepare controller to ecu relation data set
    |       :param ecu: name of the target ecu
    |       :param data:  ETHERNET_FIBEX_topology pandas data frame
    |       :param vlans: vlans combination
    |       :return: controller_data controller to ecu relation data set
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    # initialize elements
    controller_to_ecu_dict = {}
    ecu_list = []
    controller_list = []
    vlans_list = []
    # prepare data
    for i in range(len(data['Switch'])):
        if data['Type.1'][i] == 'Controller' and \
                (data['ECU'][i] == ecu or data['ECU.1'][i] == ecu):
            ecu_list.append(data['ECU'][i])
            controller_list.append(data['Switch|Ctrl'][i])
            vlans_list.append(data['vlan'][i])

    controller_to_ecu_dict['ECU'] = ecu_list
    controller_to_ecu_dict['Controller'] = controller_list
    controller_to_ecu_dict['vlan'] = vlans_list
    # create controller data
    controller_data = pd.DataFrame(controller_to_ecu_dict)
    # create controller_data.csv data frame
    controller_data.to_csv('Controller_data.csv', index=False)
    return controller_to_ecu_dict, ecu_list, controller_list, vlans_list


def prepare_ecu_switch_data_set(data: DataFrame, ecu: str) -> tuple:
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    |       prepare ecu to switch relation data
    |       :param ecu: name of the target ecu
    |       :param data:ETHERNET_FIBEX_topology pandas data frame
    |       :param vlans: vlans combination
    |       :return: ecu to switch relation data set
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    # initialize variables
    ecu_to_switch_dict = {}
    ecu_list = []
    Switcher_list = []
    vlans_list = []
    # prepare data
    for i in range(len(data['Type.1'])):
        if data['Type.1'][i] == 'SwitchPort' and \
                (data['ECU'][i] == ecu or data['ECU.1'][i] == ecu):
            # adding the principal ecu
            ecu_list.append(data['ECU'][i])
            Switcher_list.append(data['Switch'][i])
            vlans_list.append(data['vlan'][i])
        if data['ECU.1'][i] == ecu and data['Type.1'][i] == 'SwitchPort':
            # adding the principal ecu
            ecu_list.append(data['ECU.1'][i])
            Switcher_list.append(data['Switch|Ctrl'][i])
            vlans_list.append(data['vlan'][i])

    ecu_to_switch_dict['ECU'] = ecu_list
    ecu_to_switch_dict['Switcher'] = Switcher_list
    ecu_to_switch_dict['vlan'] = vlans_list

    # create switcher data frame
    Switcher_data = pd.DataFrame(ecu_to_switch_dict)

    # create switcher_data.csv file
    Switcher_data.to_csv('Switcher_data.csv', index=False)
    return ecu_to_switch_dict, ecu_list, Switcher_list, vlans_list


def prepare_switch_port_to_controller_data(data: DataFrame, ecu: str) -> tuple:
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    |       prepare switch to controller relation data
    |       :param ecu: name of the target ecu
    |       :param data:ETHERNET_FIBEX_topology pandas data frame
    |       :param vlans: vlans combination
    |       :return: ecu to switch relation data set
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    # initialize data
    controller_to_switch_dict = {}
    swport_list = []
    controller_list = []
    vlans_list = []
    # prepare data
    for i in range(len(data['Type.1'])):
        if data['Type.1'][i] == 'Controller' and \
                (data['ECU'][i] == ecu or data['ECU.1'][i] == ecu):
            swport_list.append(data['SwPort'][i])
            controller_list.append(data['Switch|Ctrl'][i])
            vlans_list.append(data['vlan'][i])

    controller_to_switch_dict['SwPort'] = swport_list
    controller_to_switch_dict['Controller'] = controller_list
    controller_to_switch_dict['vlan'] = vlans_list
    # create switcher data frame
    controller_data = pd.DataFrame(controller_to_switch_dict)

    # create switcher_data.csv file
    controller_data.to_csv('Switcher_data.csv', index=False)
    return controller_to_switch_dict, swport_list, controller_list, vlans_list


def prepare_switch_port_to_switch_port_data(data: DataFrame, ecu: str) -> tuple:
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    |       prepare switch to controller relation data
    |       :param ecu: name of the target ecu
    |       :param data:ETHERNET_FIBEX_topology pandas data frame
    |       :param vlans: vlans combination
    |       :return: ecu to switch relation data set
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    # initialize data
    controller_to_switch_dict = {}
    swport1_list = []
    swport2_list = []
    vlans_list = []
    # prepare data
    for i in range(len(data['Switch'])):
        if (data['SwPort|None'][i]) and \
                (data['ECU'][i] == ecu or data['ECU.1'][i] == ecu):
            swport1_list.append(data['SwPort'][i])
            swport2_list.append(data['SwPort|None'][i])
            vlans_list.append(data['vlan'][i])

    controller_to_switch_dict['SwPort_source'] = swport1_list
    controller_to_switch_dict['SwPort_target'] = swport2_list
    controller_to_switch_dict['vlan'] = vlans_list
    # create switcher data frame
    controller_data = pd.DataFrame(controller_to_switch_dict)

    # create switcher_data.csv file
    controller_data.to_csv('Switcher_data.csv', index=False)
    return controller_to_switch_dict, swport1_list, swport2_list, vlans_list


def prepare_switch_to_port_switch_data(data: DataFrame, ecu: str) -> tuple:
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    |       prepare switch to port switch data set
    |       :param ecu: ecu list
    |       :param data: ETHERNET_FIBEX_topology pandas data frame
    |       :param vlans: vlans combination
    |       :return: switch to port switch data set
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    # initialize data
    switch_switch_port_dict = {}
    switch_list = []
    Switch_port_list = []
    vlans_list = []
    # prepare data
    for i in range(len(data['Switch'])):
        if data['ECU'][i] == ecu or data['ECU.1'][i] == ecu:
            switch_list.append(data['Switch'][i])
            Switch_port_list.append(data['SwPort'][i])
            vlans_list.append(data['vlan'][i])

    switch_switch_port_dict['Switch'] = switch_list
    switch_switch_port_dict['SwPort'] = Switch_port_list
    switch_switch_port_dict['vlan'] = vlans_list
    # create switcher data frame
    Switch_port_data = pd.DataFrame(switch_switch_port_dict)

    # create switcher_data.csv file
    Switch_port_data.to_csv('Switcher_data.csv', index=False)

    return switch_switch_port_dict, switch_list, Switch_port_list, vlans_list


def prepare_switch_to_controller_data(data: DataFrame, ecu: str) -> tuple:
    """
        ------------------------------------------------------------------------------------------------------------------------------------------------------------
        |       prepare switch to port switch data set
        |       :param ecu: ecu list
        |       :param data: ETHERNET_FIBEX_topology pandas data frame
        |       :param vlans: vlans combination
        |       :return: switch to port switch data set
        ------------------------------------------------------------------------------------------------------------------------------------------------------------
        """
    # initialize data
    switch_switch_port_dict = {}
    switch_list = []
    controller_list = []
    vlans_list = []
    # prepare data
    for i in range(len(data['Switch'])):
        if data['ECU'][i] == ecu or data['ECU.1'][i] == ecu and data['Type.1'][i] == 'Controller':
            switch_list.append(data['Switch'][i])
            controller_list.append(data['Switch|Ctrl'][i])
            vlans_list.append(data['vlan'][i])

    switch_switch_port_dict['Switch'] = switch_list
    switch_switch_port_dict['SwPort'] = controller_list
    switch_switch_port_dict['vlan'] = vlans_list

    return switch_switch_port_dict, switch_list, controller_list, vlans_list


def prepare_all_data(csv_data_path: str, ecu_names: list, include_port_switch: list, config_path: str) -> DataFrame:
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    |       :param csv_data_path: ETHERNET_FIBEX_topology csv data path
    |       :param ecu_name: name of the target ecu
    |       :return:
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """

    data_dict = {}
    source = []
    target = []
    vlan = []
    # import data set
    data = import_all_data(csv_data_path)
    # prepare data set
    data = prepare_data(data=data, config_path=config_path)
    if len(include_port_switch) > 0:
        for ecu in ecu_names:
            # create switch to ecu relation dict and update all dict data
            ecu_to_switch_dict, ecu_list, Switcher_list, vlans_list = prepare_ecu_switch_data_set(data=data, ecu=ecu)
            source.extend(ecu_list)
            target.extend(Switcher_list)
            vlan.extend(vlans_list)
            # create switch port to controller data
            switch_switch_port_dict, switch_list, Switch_port_list, vlans_list = prepare_switch_port_to_controller_data(data=data, ecu=ecu)
            source.extend(switch_list)
            target.extend(Switch_port_list)
            vlan.extend(vlans_list)
            # create switch port to switch port data
            controller_to_switch_dict, swport1_list, swport2_list, vlans_list = prepare_switch_port_to_switch_port_data(data=data, ecu=ecu)
            source.extend(swport1_list)
            target.extend(swport2_list)
            vlan.extend(vlans_list)

            # create switch to switch port data
            switch_switch_port_dict, switch_list, Switch_port_list, vlans_list = prepare_switch_to_port_switch_data(data=data, ecu=ecu)
            source.extend(switch_list)
            target.extend(Switch_port_list)
            vlan.extend(vlans_list)
    else:
        for ecu in ecu_names:
            ecu_to_switch_dict, ecu_list, Switcher_list, vlans_list = prepare_ecu_switch_data_set(data=data, ecu=ecu)
            source.extend(ecu_list)
            target.extend(Switcher_list)
            vlan.extend(vlans_list)

            switch_switch_port_dict, switch_list, controller_list, vlans_list = prepare_switch_to_controller_data(data=data, ecu=ecu)
            source.extend(switch_list)
            target.extend(controller_list)
            vlan.extend(vlans_list)
    data_dict['Source'] = source
    data_dict['Target'] = target
    # data_dict['vlann_label'] = vlan
    data = pd.DataFrame(data_dict)
    with open("sample_network.txt", 'w') as outfile:
        for i in range(len(source)):
            line=f"{source[i]} {target[i]}\n"
            outfile.write(line)

    #alldata = pd.DataFrame(data_dict)
    #alldata.to_csv('cleandata.csv')
    return data

def set_logger() -> logging.Logger:
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    |       set logger parameters
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    logger = logging.getLogger("fibex visualisation ")
    logger.setLevel(logging.DEBUG)
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger

def parse_config(config_path) -> tuple:
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    parse config_file.json file
    :return:
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    with open(config_path, 'r') as config_file:
        config_dict = json.load(config_file)

    list_of_config = config_dict['ECU_NAMES']['OLD_NAMES']
    config_value = config_dict['ECU_NAMES']['NEW_VALUE']
    data_path = config_dict['DATA_PATH']
    coopling_prefix = config_dict['COUPLING_PREFIX']
    file_path = config_dict['FILE_PATH']
    file_type = config_dict['FILE_TYPE']
    default_selected_vlan = config_dict['DEFAULT_SELECTED_VLAN']
    defaul_selected_ecu = config_dict['DEFAULT_SELECTED_ECU']
    workspace = config_dict['WORKSPACE']
    include_ecu_naming_in_coupling = config_dict['INCLUDE_ECU_NAMING_IN_COUPLING']

    return list_of_config, config_value, data_path, coopling_prefix, file_path, file_type, \
           default_selected_vlan, defaul_selected_ecu, workspace, include_ecu_naming_in_coupling

def get_ecu_list(config_path, data_path) -> list:
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    |       get all ecu_list from the ETHERNET_FIBEX_topology.csv
    |       :return:
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """

    all_data = pd.read_csv(data_path, sep=";")
    all_data = prepare_data(data=all_data, config_path=config_path)
    ECU_LIST1 = list(all_data['ECU'])
    ECU_SET2 = list(all_data['ECU.1'])
    ECU_LIST1.extend(ECU_SET2)
    ECU_LIST = list(set(ECU_LIST1))

    return ECU_LIST

# def get_vlan_list(config_path: str, data_path,include_port_swicth=None):
#     """
#     ------------------------------------------------------------------------------------------------------------------------------------------------------------
#     |       get all vlans  from topologie_Ethernet data
#     |       :return: vlan_combination : list of all vlans combination
#     ------------------------------------------------------------------------------------------------------------------------------------------------------------
#     """
#     if include_port_swicth is None:
#         include_port_swicth = ['include port switch to port switch relation']
#     ecu_list = get_ecu_list(config_path,data_path=data_path)
#     data = prepare_all_data(csv_data_path=data_path,
#                             ecu_names=ecu_list, include_port_switch=include_port_swicth,
#                             config_path=config_path)
#     vlan_combinations = list(data['vlann_label'])
#     vlans_list = []
#     # extracting all vlans
#     for vlan_combination in vlan_combinations:
#         vlan_combination = vlan_combination.lstrip().strip()
#         vlan_sub_list = vlan_combination.split(" ")
#         vlans_list.extend(vlan_sub_list)
#     # removing white strings
#     while "" in vlans_list:
#         vlans_list.remove("")
#     # removing duplicated elements
#     vlans_list = list(set(vlans_list))
#     return vlans_list

# if __name__ == '__main__':
#     # ecu_names = ['ICON', 'IDCevo', 'IPB_APP', 'IPF_FAR', 'IPN_MAIN', 'L3_Addon_Safety', 'SFS', 'BAC25_ETH', 'CASP25', 'TestEquipmentExtern', 'TestEquipmentIntern', 'ZIM_H', 'sBAC_Eth_EES25', 'IPF_DAF', 'IPF_HVM']
#     #ecu_names = ['IPN_MAIN']
#     ECU_LIST=get_ecu_list(config_path=r"C:\Users\LENOVO\Documents\GitHub\dash-cytoscape\demos\data\config.json", data_path=r"C:\Users\LENOVO\Desktop\Data\IPB_data.csv" )
#
#     logger = set_logger()
#     data = prepare_all_data(csv_data_path=r"C:\Users\LENOVO\PycharmProjects\Pfe_Project\resources\IPB_data.csv", ecu_names=['icon'], include_port_switch=[True], config_path=r"C:\Users\LENOVO\PycharmProjects\Pfe_Project\resources\config.json")
#     print(data)

