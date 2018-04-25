from __future__ import division
from __future__ import print_function
from collections import OrderedDict

import numpy as np
import pandas as pd

from pmmif import featherpmm
from tdda.constraints.pd.constraints import verify_df
from tdda.referencetest.checkpandas import default_csv_writer


def get_2d_outlier_dataframe():
    return featherpmm.read_dataframe('data/items.feather').df


def show_df(df, title=None, show=True, all_cols=False):
    if show:
        if title:
            print(title)
        if all_cols:
            print(df)
        else:
            print(df[['id', 'category', 'price']])
        print()


def find_nulls(df, col, show=False):
    okcol = col + '_nonnull_ok'
    df[okcol] = df[col].notna()
    null_rows = df[df[okcol] == False]
    if len(null_rows) > 0:
        show_df(null_rows, 'NULLS IN %s' % col, show)
    elif show:
        print('No nulls in column %s' % col)
    return null_rows


def find_all_nulls(df, show=False):
    for c in list(df):
        find_nulls(df, c)


def find_dup_ids(df, show=False):
    df['id_unique_ok'] = df.groupby('id')['id'].transform('count') == 1
    dup_ids = df[df.id_unique_ok == False]['id']
    if len(dup_ids) > 0:
        cid = dup_ids.groupby(df.id).count()
        cid.rename(columns={'id': 'count'}).reset_index()
        if show:
            show_df(cid, 'DUPLICATE IDs', show, all_cols=True)
    return dup_ids


def find_bad_prices(df, show=False):
    df['price_ok'] = np.logical_and(df['price'] >= 0, df['price'] <= 1000.0)
    bad_prices = df[df.price_ok == False]
    if len(bad_prices) > 0:
        show_df(bad_prices, 'BAD PRICES', show)
    return bad_prices


def find_bad_categories(df, show=False):
    allowed = ["AA", "CB", "QT", "KA", "TB"]
    df['category_ok'] = df['category'].isin(allowed)
    bad_cats = df[df.category_ok == False]
    if len(bad_cats) > 0:
        show_df(bad_cats, 'BAD CATEGORIES', show)
    return bad_cats


def find_bad_records(df, show=True):
    bads = df.query('not (id_nonnull_ok and id_unique_ok and price_nonnull_ok '
                    'and price_ok and category_nonnull_ok and category_ok)')
    show_df(df, 'BAD RECORDS (FOUND EXPLICITLY)', show, all_cols=True)
    return bads


def save_good_records(df):
    goods = df.query('(id_nonnull_ok and id_unique_ok and price_nonnull_ok'
                     ' and price_ok and category_nonnull_ok and category_ok)')
    goods = goods[['id', 'category', 'price']]
    ds = featherpmm.Dataset(goods, name='good_items')
    featherpmm.write_dataframe(ds, 'data/good_items.feather')
    return goods


def find_with_tdda(df, show=True):
    v = verify_df(df, 'constraints.tdda', detect=True,
                  detect_per_constraint=True, detect_output_fields=[])
    bads = v.detected()
    show_df(bads, 'BAD RECORDS (FOUND WITH TDDA)', show, all_cols=True)
    return bads


if __name__ == '__main__':
    pd.set_option('display.width', 200)
    df = get_2d_outlier_dataframe()
    show_df(df, 'INITIAL DATA', show=True)
    find_all_nulls(df, show=False)
    find_dup_ids(df, show=False)
    find_bad_prices(df, show=False)
    find_bad_categories(df, show=False)

    find_bad_records(df, show=True)
    save_good_records(df)
    df = get_2d_outlier_dataframe()
    bads = find_with_tdda(df, show=True)

