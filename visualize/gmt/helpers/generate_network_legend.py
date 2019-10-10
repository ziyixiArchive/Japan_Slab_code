import numpy as np
import click

CEA_NETWORKS = ["AH", "BJ", "BU", "CQ", "FJ", "GD", "GS", "GX", "GZ", "HA", "HB", "HE", "HI", "HL", "HN",
                "JL", "JS", "JX", "LN", "NM", "NX", "QH", "SC", "SD", "SH", "SN", "SX", "TJ", "XJ", "XZ", "YN", "ZJ"]


@click.command()
@click.option('--station_fname', required=True, type=str)
def main(station_fname):
    stations = np.loadtxt(station_fname, dtype=np.str)
    network_set = set()
    for row in stations:
        net = row[1]
        if(net in CEA_NETWORKS):
            net = "CEArray"
        elif(net == "BO"):
            net = "F-net"
        elif(net == "KG"):
            net = "KMA Networks"
        else:
            net = "other Regional or Global Networks"
        network_set.add(net)
    print(len(network_set))
    print(sorted(network_set))


if __name__ == "__main__":
    main()
