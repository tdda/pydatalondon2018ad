from pmmif import featherpmm
from tdda.constraints import detect_df

path = 'data/items.feather'
df = featherpmm.read_dataframe(path).df

v = detect_df(df, 'constraints.tdda', detect_per_constraint=True,
              detect_output_fields=[])
bads_df = v.detected()
print(bads_df)
