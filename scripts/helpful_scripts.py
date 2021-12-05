from brownie import (
    network,
    accounts,
    config,
    Contract,
    MockV3Aggregator,
    MockWETH,
    MockDAI,
)
from web3 import Web3

FORKED_LOCAL_ENRIVONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "mainnet-fork-dev",
    "development",
    "ganache-local",
]  # this is a list of local networks so that we know when to deploy mocks

DECIMALS = 18
INITIAL_AMOUNT = Web3.toWei(4500, "ether")


def get_account(index=None, id=None):
    # index will choose one of the addresses inside accounts array
    # id will use one of the accounts saved inside brownie -> $ brownie accounts list
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENRIVONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_to_usd_price_feed": MockV3Aggregator,
    "dai_to_usd_price_feed": MockV3Aggregator,
    "weth_token": MockWETH,
    "fau_token": MockDAI,
}


def get_contract(contract_name):
    """The function will grab the contract addresses from the brownie config if
    defined, otherwise, it will deploy a mock version of the contract
    and return that mock contract.

        Arg:
            contract_name (string)

        Return:
            brownie.network.contract.ProjectContract: The most recently deployed version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
    ):  # check if we are using a local blockchain
        if len(contract_type) <= 0:  # check if mocks have already been deployed
            deploy_mocks()
        contract = contract_type[-1]
    else:  # if you want to deploy to a test net
        contract_address = config["networks"][network.show_active()][contract_name]
        # to interact with a contract on a test net we need the ABI and the address
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def deploy_mocks():
    """
    Use this script if you want to deploy mocks to a testnet
    """
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    account = get_account()

    print("Deploying Mock WETH_TOKEN...")
    mock_weth = MockWETH.deploy({"from": account})
    print(f"Mock Weth Token deployed to {mock_weth.address}")

    print("Deploying Mock DAI_TOKEN...")
    mock_dai = MockDAI.deploy({"from": account})
    print(f"Mock Weth Token deployed to {mock_dai.address}")

    print("Deploying Mock V3 Aggregator...")
    mock_v3_aggragator = MockV3Aggregator.deploy(
        DECIMALS, INITIAL_AMOUNT, {"from": account}
    )
    print(f"MockV3Aggregator deployed to {mock_v3_aggragator.address}")
    print("All done!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=Web3.toWei(0.1, "ether")
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    funding_tx = link_token.transfer(contract_address, amount, {"from": account})
    funding_tx.wait(1)
    print(f"Funded {contract_address}")
    return funding_tx
