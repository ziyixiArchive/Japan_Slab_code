"""
use the generated auxiliary file, update the asdf file.
"""
import pyasdf
import pickle
import click
import numpy as np


@click.command()
@click.option('--obs_path', required=True, type=str, help="the obs hdf5 file path")
@click.option('--pkl_path', required=True, type=str, help="the pickle file to store the auxiliary info")
def main(obs_path, pkl_path):
    with open(pkl_path, 'rb') as handle:
        results = pickle.load(handle)
    with pyasdf.ASDFDataSet(obs_path, mode="a") as obs_ds:
        for item in results:
            for key in results[item]:
                if(results[item][key] == None):
                    results[item][key] = -1

            # print(item, (np.zeros(0, dtype=np.float)), (
            #     "Traveltimes"), (item.replace(".", "/")), (results[item]))
            obs_ds.add_auxiliary_data(
                np.zeros(0, dtype=np.float), data_type="Traveltimes", path=item.replace(".", "_"), parameters=results[item])


if __name__ == "__main__":
    main()
