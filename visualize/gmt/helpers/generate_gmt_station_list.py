import numpy as np
import click

CEA_NETWORKS = ["AH", "BJ", "BU", "CQ", "FJ", "GD", "GS", "GX", "GZ", "HA", "HB", "HE", "HI", "HL", "HN",
                "JL", "JS", "JX", "LN", "NM", "NX", "QH", "SC", "SD", "SH", "SN", "SX", "TJ", "XJ", "XZ", "YN", "ZJ"]


@click.command()
@click.option('--stations_file', required=True, type=str)
@click.option('--output_file', required=True, type=str)
def main(stations_file, output_file):
    stations = np.loadtxt(stations_file, dtype=np.str)
    with open(output_file, "w") as f:
        for row in stations:
            net = row[1]
            if(net in CEA_NETWORKS):
                net = 0
            elif(net == "BO"):
                net = 1
            elif(net == "KG"):
                net = 2
            elif(net == "XL"):
                net = 3
            elif(net == "8B"):
                net = 4
            elif(net == "YP"):
                net = 5
            elif(net == "X4"):
                net = 6
            else:
                net = 7
            f.write(f"{row[3]} {row[2]} {net}\n")


if __name__ == "__main__":
    main()
