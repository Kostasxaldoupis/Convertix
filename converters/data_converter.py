import pandas as pd

def csv_to_json(input_file,output_file):
    df = pd.read_csv(input_file)
    df.to_json(output_file)