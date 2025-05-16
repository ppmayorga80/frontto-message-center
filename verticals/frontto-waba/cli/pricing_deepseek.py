import re

import pandas as pd
import requests


# define a helper that only alters strings
def normalize_ascii_spaces(x):
    if isinstance(x, str):
        # 1) non-ASCII → space
        s = re.sub(r'[^\x00-\x7F]', ' ', x)
        # 2) collapse all runs of whitespace to one space, and strip ends
        s= re.sub(r'\s+', ' ', s).strip()
        return s
    return x


def pricing_deepseek():
    url = "https://api-docs.deepseek.com/quick_start/pricing/"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    html = response.text
    df_list = pd.read_html(html)
    df = pd.concat(df_list, ignore_index=True)

    df_clean = df.applymap(normalize_ascii_spaces)

    return df_clean


def main():
    output_path = "pricing_deepseek.csv"
    df = pricing_deepseek()
    df.to_csv(output_path, index=False)
    print(df)


if __name__ == '__main__':
    main()
