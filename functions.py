def bar_dict(df, x, y, mode="sum"):
    df_dict = {key: 0 for key in df[x]}
    for i in df_dict.keys():
        if mode=='sum':
            df_dict[i]=df.loc[(df[x] == i), y].sum()
        elif mode=='count':
            df_dict[i]=df.loc[(df[x] == i), y].count()
    return df_dict
           

    