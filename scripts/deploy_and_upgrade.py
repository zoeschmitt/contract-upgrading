from brownie import (
    network,
    Box,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    BoxV2,
)
from scripts.helpful_scipts import encode_function_data, get_account, upgrade


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    # implementation
    box = Box.deploy({"from": account})

    # proxy admin
    proxy_admin = ProxyAdmin.deploy({"from": account})
    # initializer = box.store, 1
    box_encoded_initializer_func = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_func,
        {"from": account, "gas_limit": 1000000},  # gas limit optional
    )
    print(f"Proxy deplpoyed to {proxy}, you can now upgrade to v2!")
    # assigning proxy address the abi of the box contract. Works
    # bc the proxy will delegate all its calls to box
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})
    # print(proxy_box.retrieve())

    # upgrade to v2
    box_v2 = BoxV2.deploy({"from": account})
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_transaction.wait(1)
    print("Proxy has been upgraded")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve()) # returns 2 bc it has 1 from Box (v1) storage (see line 32)
