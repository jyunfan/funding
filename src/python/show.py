import glob
import pandas as pd

df = pd.concat(map(pd.read_csv, glob.glob('data/dydx/csv/PBTC-USDC/*.csv')))
print(df['fundingRate'].rolling(window=24).sum()*60*60*365)
