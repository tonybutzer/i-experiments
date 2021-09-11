import sys
sys.path.append(".")

from fidolib import Fido

asset = 'https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/23/K/NR/2020/12/S2A_23KNR_20201229_0_L2A/B04.tif'
dest = 's3://dev-et-data/usmart/RIO/23/K/NR/2020/12/S2A_23KNR_20201229_0_L2A_B04.tif'


fido = Fido(asset,dest)

fido.__repr__()


print(fido)


fido.wget_asset()
