from brownie import accounts, network, config, interface

def get_weth(account=None):
    """
    Mints WETH by depositing ETH
    """
    account = (
        account if account else accounts[0]
    )
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    # Call deposit function from WETH contract
    tx = weth.deposit({"from": account, "value": 1000000000000000000})
    print("Received 1 WETH")
    return tx

def approve_erc20(amount, to, erc20_address, account):
    print("Approving ERC20...")
    erc20 = interface.IERC20(erc20_address)
    tx_hash = erc20.approve(to, amount, {"from": account})
    print("Approved!")
    tx_hash.wait(1)
    return tx_hash