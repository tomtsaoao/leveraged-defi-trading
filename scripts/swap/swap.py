import brownie
from brownie import accounts, config, interface, network, chain
from web3 import Web3
from scripts.side_script import get_weth, approve_erc20
from scripts.chainlink.chainlink import get_asset_price
from chainlink_mapping import price_feed_mapping

amount_to_swap = Web3.toWei(0.1, "ether")

def swap(
    address_from_token,
    address_to_token,
    amount,
    account,
    price_feed_address,
    swap_router_address,
    reverse_feed=False,
):
    path = [
        address_from_token,
        address_to_token,
    ]
    # The pool jumping path to swap your token
    from_to_price = get_asset_price(address_price_feed=price_feed_address)
    if reverse_feed:
        from_to_price = 1 / from_to_price
    # amountOutMin = int((from_to_price * 0.5) * 10 ** 18)
    # 98 is 2% slippage
    # I get a little weird with units here
    # from_to_price isn't in wei, but amount is
    # someone could front-run and buy a lot of WETH - and sell it back to us for a profit
    # which is why we have amountOutMin
    # Worst case 0.90 means 10% slippage
    amountOutMin = int((from_to_price * 0.90) * amount)
    # give expiry time (120 seconds from now)
    timestamp = chain[brownie.web3.eth.get_block_number()]["timestamp"] + 120
    # every time interact with contract - need ABI and Address - interface compiles to ABI
    routerv2 = interface.IUniswapV2Router02(swap_router_address)
    # Call the swap function from Uniswap contract
    swap_tx = routerv2.swapExactTokensForTokens(
        amount, amountOutMin, path, account.address, timestamp, {"from": account}
    )
    swap_tx.wait(1)
    return swap_tx


# Starting ETH Balance is: 1000000000000000000
# Starting DAI Balance is: 0
# Ending   ETH Balance is: 975655842557031085
# Ending   DAI Balance is: 10480