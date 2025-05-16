import os

from ai.llm_openai import LlmOpenAi
from dotenv import load_dotenv
import pandas as pd

load_dotenv(os.path.join(os.path.dirname(__file__), "../src/ai/.env"))


def pricing_openai(path="Pricing - OpenAI API.html"):
    with open(path) as fp:
        df_list = pd.read_html(fp)
        df = pd.DataFrame()
        for k, dfk in enumerate(df_list):
            if [x for x in dfk.columns if str(x) in ("Input", "Output")]:
                df = pd.concat((df, dfk), ignore_index=True)
    return df


def main():
    # you must manually download the html for the url: https://platform.openai.com/docs/pricin
    input_path = "pricing_openai.html"
    output_path = "pricing_openai.csv"
    df = pricing_openai(path=input_path)
    df.to_csv(output_path, index=False)


if __name__ == '__main__':
    main()
