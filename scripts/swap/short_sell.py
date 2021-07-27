# deposit WETH into aave
# use WETH to borrown DAI
# sell the DAI for more WETH

from scripts.chainlink.chainlink import get_asset_price
from web3.main import Web3
from ...scripts.aave.aave_borrow import borrow_erc20, get_borrowable_data, get_lending_pool
from brownie import network, config, interface, accounts
from ...scripts.side_script import get_weth, approve_erc20
from web3 import Web3
from ...scripts.chainlink.chainlink import get_asset_price
from ...scripts.swap.swap import swap

# 0.1 ETH in Wei
amount = Web3.toWei(0.1, "ether")

def main():
    # Pull in accounts
    account = accounts[0]
    # Get WETH, DAI, Uniswap address from brownie-config - different networks, differrent addresses
    weth_address = config["networks"][network.show_active()]["weth_token"]
    dai_address = config["networks"][network.show_active()]["dai_token"]
    uniswapv2_router02 = config["networks"][network.show_active()]["uniswapv2_router02"]
    get_weth(account=account)

    lending_pool = get_lending_pool()
    approve_erc20(amount, lending_pool.address, weth_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(
        weth_address, amount, account.address, 0, {"from": account}
    )
    print("Deposited!")
    tx.wait(1)
    borrowable_eth, total_debt_eth = get_borrowable_data(lending_pool, account)

    # Aave Borrow some DAI
    # Call get asset price from chainlink - use to figure out how much can borrow
    # every 1 dai = dai_eth_price ETH
    # every 1 ETH == x dai
    # 0.95 so we stay within healthy threshold
    dai_eth_price = get_asset_price()
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    borrow_erc20(lending_pool, amount_dai_to_borrow, account, erc20_address=dai_address)

    # Short sell / Buy on margin
    amount_dai_to_borrow = Web3.toWei(amount_dai_to_borrow, "ether")
    tx_approve = approve_erc20(
        amount_dai_to_borrow, uniswapv2_router02, dai_address, account
    )
    tx_approve.wait(1)
    price_feed_address = config["networks"][network.show_active()]["dai_eth_price_feed"]
    swap(
        dai_address,
        weth_address,
        amount_dai_to_borrow - Web3.toWei(1, "ether"),
        account,
        price_feed_address,
        uniswapv2_router02
    )
    print(
        f"Ending WETH Balance is: {interface.IERC20(weth_address).balanceOf(account.address)}"
    )
    print(
        f"Ending DAI Balance is: {interface.IERC20(dai_address).balanceOf(account.address)}"
    )

