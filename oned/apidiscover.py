from pmmif import featherpmm
from tdda.constraints import discover_df

path = 'data/good_items.feather'
df = featherpmm.read_dataframe(path).df

constraints = discover_df(df, inc_rex=True)
with open('autoconstraints.tdda', 'w') as f:
    f.write(constraints.to_json())
