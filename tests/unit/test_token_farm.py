from scripts.helpful_scripts import (
    get_account,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    INITIAL_AMOUNT,
    DECIMALS,
    get_contract,
)
from scripts.deploy import deploy_token_farm_and_dapp_token, KEPT_BALANCE
from brownie import network, exceptions
import pytest
from web3 import Web3


def test_set_price_feed_contract():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    # Arrange
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()

    # Act
    token_farm.setPriceFeedContract(
        dapp_token.address, get_contract("eth_to_usd_price_feed"), {"from": account}
    )

    # Assert
    assert token_farm.tokenToPriceFeed(dapp_token.address) == get_contract(
        "eth_to_usd_price_feed"
    )

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract(
            dapp_token.address,
            get_contract("eth_to_usd_price_feed"),
            {"from": non_owner},
        )


def test_stake_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    # Arrange
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # ACT
    dapp_token.approve(token_farm.address, amount_staked, {"from": account}).wait(1)
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account}).wait(1)
    # ASSERT
    # amount 0
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.stakeTokens(0, dapp_token.address, {"from": account}).wait(1)
    # spend more than allowed
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.stakeTokens(
            amount_staked + 1, dapp_token.address, {"from": account}
        ).wait(1)
    # try staking not allowed token
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.stakeTokens(amount_staked, account.address, {"from": account}).wait(
            1
        )
    # check if balance updated in mapping
    assert (
        token_farm.stakingBalance(dapp_token.address, account.address) == amount_staked
    )
    # check if counter updated to 1 and user added to array
    assert token_farm.uniqueTokensStaked(account) == 1
    # check if user address added inside the stackers array
    assert token_farm.stakers(0) == account.address
    return token_farm, dapp_token


def test_issue_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    # Arrange
    account = get_account()
    not_owner = get_account(index=1)
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    user_starting_balance = dapp_token.balanceOf(account.address)
    # ACT
    token_farm.issueTokens({"from": account}).wait(1)
    # we are staking 1 Dapp token which is equal in price to 1 ETH. (the price for eth in usd is 4500)
    # ASSERT
    assert (
        dapp_token.balanceOf(account.address) == user_starting_balance + INITIAL_AMOUNT
    )


def test_stake_unapproved_tokens(random_erc20, amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    random_erc20.approve(token_farm.address, amount_staked, {"from": account})
    # Assert
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.stakeTokens(amount_staked, random_erc20.address, {"from": account})


def test_unstake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    # Act
    token_farm.unStakeTokens(dapp_token.address, {"from": account})
    # Assert
    assert dapp_token.balanceOf(account.address) == KEPT_BALANCE
    assert token_farm.stakingBalance(dapp_token.address, account.address) == 0
    assert token_farm.uniqueTokensStaked(account.address) == 0


def test_get_user_total_balance_with_different_tokens_and_amounts(
    amount_staked, random_erc20
):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    # Act
    token_farm.addAllowedToken(random_erc20.address, {"from": account})
    # The random_erc20 is going to represent DAI
    # Since the other mocks auto deploy
    token_farm.setPriceFeedContract(
        random_erc20.address, get_contract("eth_to_usd_price_feed"), {"from": account}
    )
    random_erc20_stake_amount = amount_staked * 2
    random_erc20.approve(
        token_farm.address, random_erc20_stake_amount, {"from": account}
    )
    token_farm.stakeTokens(
        random_erc20_stake_amount, random_erc20.address, {"from": account}
    )
    # Act
    total_eth_balance = token_farm.getUserTotalValue(account.address)
    assert total_eth_balance == INITIAL_AMOUNT * 3
    # Improve by adding different mock price feed default values


def test_get_token_eth_price():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act / Assert
    assert token_farm.getTokenValue(dapp_token.address) == (
        INITIAL_AMOUNT,
        DECIMALS,
    )


def test_get_user_token_staking_balance_eth_value(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})
    # Assert
    eth_balance_token = token_farm.getUserSingleTokenValue(
        account.address, dapp_token.address
    )
    assert eth_balance_token == INITIAL_AMOUNT


def test_issue_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)
    # Act
    token_farm.issueTokens({"from": account})
    # Assert
    assert dapp_token.balanceOf(account.address) == starting_balance + INITIAL_AMOUNT
