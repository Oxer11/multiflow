import os
import sys
import pickle
import argparse
import pandas as pd
import numpy as np

from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from multiflow.data import protein


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input_dir", type=str)
parser.add_argument("-o", "--output_dir", type=str)
args = parser.parse_known_args()[0]

if __name__ == "__main__":
    input_dir = os.path.expanduser(args.input_dir)
    output_dir = os.path.expanduser(args.output_dir)
    
    os.makedirs(output_dir, exist_ok=True)

    fnames = [f for f in os.listdir(input_dir) if f.endswith(".pdb")]
    columns = ["pdb_name", "processed_path", "num_chains", "seq_len", "modeled_seq_len"]
    rows = []
    for fname in tqdm(fnames, "Dumping .pdb into .pkl"):
        input_fname = os.path.join(input_dir, fname)
        # name = "_".join(fname.split("_")[:2]) + ".pkl"
        name = ".".join(fname.split(".")[:-1]) + ".pkl"
        output_fname = os.path.join(output_dir, name)

        with open(input_fname, "r") as f:
            pdb_string = f.read()
        try:
            data_object = protein.from_pdb_string(pdb_string).to_dict()
            data_object["modeled_idx"] = np.array([i for i in range(len(data_object["aatype"]))])
        except:
            print(fname, "is not dumped")
            continue
        row = [
            os.path.basename(fname).split(".")[0],
            output_fname,
            1,
            len(data_object["aatype"]),
            len(data_object["aatype"])
        ]
        rows.append(row)

        with open(output_fname, "wb") as f:
            pickle.dump(data_object, f, protocol=pickle.HIGHEST_PROTOCOL)
    df = pd.DataFrame(data=rows, columns=columns)
    df.to_csv(os.path.join(output_dir, "metadata.csv"), index=False)
