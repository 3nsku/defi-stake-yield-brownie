from scripts.helpful_scripts import get_account, get_contract
from brownie import DappToken, TokenFarm, config, network
from web3 import Web3
import yaml
import json
import shutil
import os

KEPT_BALANCE = Web3.toWei(1000, "ether")


def deploy_token_farm_and_dapp_token(front_date_update=False):
    account = get_account()

    dapp_token = DappToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(
        dapp_token.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    # trasfer tokens from personal address to smart contract address, and keep a little bit to yourself for testing
    tx = dapp_token.transfer(
        token_farm.address, dapp_token.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    tx.wait(1)

    # dapp_token, weth_token, fau_token/dai
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    dict_of_allowed_tokens = {
        dapp_token: get_contract("dai_to_usd_price_feed"),
        fau_token: get_contract("dai_to_usd_price_feed"),
        weth_token: get_contract("eth_to_usd_price_feed"),
    }
    if front_date_update:
        update_front_end()
    add_allowed_tokens(account, token_farm, dict_of_allowed_tokens)
    return token_farm, dapp_token


def add_allowed_tokens(_account, _token_farm, dict_of_allowed_tokens):
    for token, price_feed in dict_of_allowed_tokens.items():
        _token_farm.addAllowedToken(token.address, {"from": _account}).wait(1)
        _token_farm.setPriceFeedContract(
            token.address, price_feed, {"from": _account}
        ).wait(1)


def update_front_end():
    # send build folder to front end
    copy_folder_to_front_end("./build", "./front_end/src/chain_info")

    # sending to front end bronwie config in json format
    with open("brownie-config.yaml", "r") as brownie_config:
        conf_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(conf_dict, brownie_config_json)
    print("Front End Updated!")


def copy_folder_to_front_end(src, dest):
    # check if destination exists, and delete it
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def main():
    deploy_token_farm_and_dapp_token(front_date_update=True)
