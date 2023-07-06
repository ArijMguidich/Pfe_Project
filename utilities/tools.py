"""
tools used in the main methode
author : HaJa
"""
import json
import logging

import pandas as pd
from networkx.classes.reportviews import NodeView

from Visualisation_plotly import edges
from data_preparation.preparing_data import prepare_data, prepare_all_data


def assign_color_to_each_node(list_of_nodes: NodeView) -> list:
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    |       assign a color for each node based on it's name
    |       :param list_of_nodes: list of all nodes
    |       :return: list of color assigned to each node
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    color_list = []
    for node in list_of_nodes:
        color_index = '#1978a5'

        if 'SWP' in node:
            color_index = '#1fbfb8'
        elif 'Switch' in node:
            color_index = '#05716c'
        elif 'Controller' in node:
            color_index = '#4d5198'

        color_list.append(color_index)

    return color_list


def assign_symbol_to_each_node(list_of_nodes: NodeView) -> list:
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    |       assign symbol to each node based on it's name
    |       :param list_of_nodes: list of all nodes
    |       :return: list of color assigned to each node
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    sympbol_list = []
    for node in list_of_nodes:

        sympbol = 'square'

        if 'SWP' in node:
            sympbol = 'circle'

        elif 'Switch' in node:
            sympbol = 3

        elif 'Controller' in node:
            sympbol = "diamond-x"

        sympbol_list.append(sympbol)

    return sympbol_list


def assign_color_to_each_relation(vlan_label_list: list, selected_vlan_list: list) -> list:
    """
    assign color to each relation
    :param selected_vlan_list: selected vlan
    :param vlan_label_list: which represent the relatio
    :return:
    """
    color_list = []
    color_dict = {}
    for vlan_label in vlan_label_list:

        vlan_labels = get_vlan_list_from_selected_one(vlan_combinations=vlan_label)
        for vlan in vlan_labels:
            for selected_vlan in selected_vlan_list:
                if vlan in selected_vlan:
                    color_index = 'red'
                    color_dict[vlan_label] = color_index
                    color_list.append(color_index)

                else:
                    color_index = '#A9A9A9'
                    color_dict[vlan_label] = color_index
                    color_list.append(color_index)

    return color_list


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


def get_vlan_list(config_path: str, data_path,include_port_swicth=None):
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    |       get all vlans  from topologie_Ethernet data
    |       :return: vlan_combination : list of all vlans combination
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    if include_port_swicth is None:
        include_port_swicth = ['include port switch to port switch relation']
    ecu_list = get_ecu_list(config_path,data_path=data_path)
    data = prepare_all_data(csv_data_path=data_path,
                            ecu_names=ecu_list, include_port_switch=include_port_swicth,
                            config_path=config_path)
    vlan_combinations = list(data['vlann_label'])
    vlans_list = []
    # extracting all vlans
    for vlan_combination in vlan_combinations:
        vlan_combination = vlan_combination.lstrip().strip()
        vlan_sub_list = vlan_combination.split(" ")
        vlans_list.extend(vlan_sub_list)
    # removing white strings
    while "" in vlans_list:
        vlans_list.remove("")
    # removing duplicated elements
    vlans_list = list(set(vlans_list))
    return vlans_list


def get_vlan_list_from_selected_one(vlan_combinations):
    """
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    get vlan list from selected in UI
    :param vlan_combinations:
    :return:
    ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    vlans_list = []
    # extracting all vlans

    vlan_combinations = vlan_combinations.lstrip().strip()
    vlan_sub_list = vlan_combinations.split(" ")
    vlans_list.extend(vlan_sub_list)
    # removing white strings
    while "" in vlans_list:
        vlans_list.remove("")
    # removing duplicated elements
    vlans_list = list(set(vlans_list))
    return vlans_list


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


def get_propreties_fom_config() -> dict:
    """
       ------------------------------------------------------------------------------------------------------------------------------------------------------------
       parse config_file.json file
       :return:
       ------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    with open('data/config.json', 'r') as config_file:
        config_dict = json.load(config_file)

    return config_dict


def get_source_target_ecu(ecu_names: list, include_port_swicth: list, config_path: str):
    ecu_list = list(set(list(edges['Source']) + list(set(edges['Target']))))
    i = 0
    cleaned_ecu_list = []
    while i < len(ecu_list):
        if not ('SWP' in ecu_list[i] or 'Controller' in ecu_list[i] or 'Switch' in ecu_list[i]):
            cleaned_ecu_list.append(ecu_list[i])
        i += 1
    return cleaned_ecu_list
