import pandas as pd
import asyncio
from dank_mids import Contract, web3

# yETH
ST_YETH = Contract('0x583019fF0f430721aDa9cfb4fac8F06cA104d0B4')

# Curve Pools
YETH_ETH = Contract('0x69ACcb968B19a53790f43e57558F5E443A91aF22')

# ChainLink Feeds
CL_ETH_USD = Contract('0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419')
CL_CRV_USD = Contract('0xCd627aA160A6fA45Eb793D19Ef54f5062F20f33f')

# Time interval
start_block = 18340000 # Oct-13-2023
end_block = 19624000 # Apr-10-2024 
slice_count = 4_000
step_size = (end_block - start_block) // slice_count

def main():
    asyncio.get_event_loop().run_until_complete(_main())

async def _main():
    data = await asyncio.gather(*[get_data_for_block(i) for i in range(start_block, end_block, step_size)])
    # Create a DataFrame from the collected data
    df = pd.DataFrame(data, columns=['Block', 'Timestamp', 'st_yeth_crvusd', 'eth_crvusd'])
    df.to_csv('dataset.csv', index=False) 

async def get_data_for_block(i):
  block, st_yeth_total_assets, st_yeth_total_supply, yeth_eth_price_oracle, cl_eth_usd, cl_crvusd_usd  = await asyncio.gather(
    web3.eth.get_block(i),
    ST_YETH.totalAssets.coroutine(block_identifier=i, decimals=18),
    ST_YETH.totalSupply.coroutine(block_identifier=i, decimals=18), 
    YETH_ETH.price_oracle.coroutine(block_identifier=i, decimals=18), 
    CL_ETH_USD.latestAnswer.coroutine(block_identifier=i, decimals=8),
    CL_CRV_USD.latestAnswer.coroutine(block_identifier=i, decimals=8),
  )

  st_yeth_crvusd = st_yeth_total_assets / st_yeth_total_supply * yeth_eth_price_oracle * cl_eth_usd / cl_crvusd_usd
  eth_crvusd = cl_eth_usd / cl_crvusd_usd

  return [i, block['timestamp'], st_yeth_crvusd, eth_crvusd]
