"""
Plot the profile using generate numpy npy data.
"""
import matplotlib.pyplot as plt
import numpy as np
import click
import numba
import tqdm
from scipy.interpolate import RegularGridInterpolator

resolution = 101


def prepare_mesh(data, rawminlon, rawmaxlon, rawminlat, rawmaxlat, rawmindep, rawmaxdep):
    rawlonnpts, rawlatnpts, rawdepnpts = data.shape
    lon_list = np.linspace(rawminlon, rawmaxlon, rawlonnpts)
    lat_list = np.linspace(rawminlat, rawmaxlat, rawlatnpts)
    dep_list = np.linspace(rawmindep, rawmaxdep, rawdepnpts)
    # x_mesh = np.zeros_like(data)
    # y_mesh = np.zeros_like(data)
    # z_mesh = np.zeros_like(data)
    # for i in tqdm.tqdm(range(rawlonnpts)):
    #     for j in range(rawlatnpts):
    #         for k in range(rawdepnpts):
    #             x_mesh[i, j, k], y_mesh[i, j, k], z_mesh[i, j, k], _ = lld2xyzr(
    #                 lat_list[j], lon_list[i], dep_list[k])
    # return x_mesh, y_mesh, z_mesh
    return lon_list, lat_list, dep_list


@numba.njit()
def lld2xyzr(lat, lon, dep):
    R_EARTH_KM = 6371.0
    r = (R_EARTH_KM-dep)/R_EARTH_KM
    theta = 90-lat
    phi = lon

    z = r*cosd(theta)
    h = r*sind(theta)
    x = h*cosd(phi)
    y = h*sind(phi)

    return (x, y, z, r)


@numba.njit()
def cosd(x):
    return np.cos(np.deg2rad(x))


@numba.njit()
def sind(x):
    return np.sin(np.deg2rad(x))


@numba.njit()
def interp_value(lat, lon, dep, x_mesh, y_mesh, z_mesh, value_mesh):
    x, y, z, _ = lld2xyzr(lat, lon, dep)
    distance2 = (x_mesh-x)**2+(y_mesh-y)**2+(z_mesh-z)**2
    mindistance2 = np.min(distance2)
    coors = np.where(distance2 == mindistance2)
    value = value_mesh[coors[0][0], coors[1][0], coors[2][0]]
    return value


@click.command()
@click.option('--region', required=True, type=str, help="minlon/maxlon/minlat/maxlat/mindep/maxdep, min and max only represents for corresponding points")
@click.option('--rawregion', required=True, type=str, help="minlon/maxlon/minlat/maxlat/mindep/maxdep, raw region in npy files")
@click.option('--data', required=True, type=str, help="the npy file")
@click.option('--parameter', required=True, type=str, help="physicial parameter to plot")
@click.option('--npts', required=True, type=str, help="nlon/nlat/ndep")
def main(region, rawregion, data, parameter, npts):
    # region
    minlon, maxlon, minlat, maxlat, mindep, maxdep = [
        float(item) for item in region.split("/")]
    rawminlon, rawmaxlon, rawminlat, rawmaxlat, rawmindep, rawmaxdep = [
        float(item) for item in rawregion.split("/")]
    if(rawminlon > rawmaxlon):
        # interpolation: The points in dimension 0 must be strictly ascending
        rawminlon, rawmaxlon = rawmaxlon, rawminlon
        rawminlat, rawmaxlat = rawmaxlat, rawminlat
    # data
    data = np.load(data)
    # latnpts and lonnpts should be the same if plot vertically
    lonnpts, latnpts, depnpts = [int(item) for item in npts.split("/")]

    plot_vertically = True
    if(mindep == maxdep):
        plot_vertically = False

    hnpts, vnpts = None, None
    if(plot_vertically):
        if(lonnpts != latnpts):
            raise Exception(
                "latnpts and lonnpts should be the same when plotting vertically")
        hnpts = latnpts
        vnpts = depnpts
        print("plot vertically")
    else:
        hnpts = lonnpts
        vnpts = latnpts
        print("plot horizontally")

    print("preparing mesh:")
    lon_list, lat_list, dep_list = prepare_mesh(
        data, rawminlon, rawmaxlon, rawminlat, rawmaxlat, rawmindep, rawmaxdep)

    # get mesh to plot
    print("interp values:")
    lat_mesh, lon_mesh, dep_mesh = None, None, None
    plot_values = np.zeros((hnpts, vnpts))
    array_to_interpolate = np.zeros((hnpts, vnpts, 3))
    if(plot_vertically):
        lat_mesh = np.linspace(minlat, maxlat, hnpts)
        lon_mesh = np.linspace(minlon, maxlon, hnpts)
        dep_mesh = np.linspace(mindep, maxdep, vnpts)
        for ih in tqdm.tqdm(range(hnpts)):
            for iv in range(vnpts):
                # plot_values[ih, iv] = interp_value(
                #     lat_mesh[ih], lon_mesh[ih], dep_mesh[iv], x_mesh, y_mesh, z_mesh, data)
                array_to_interpolate[ih, iv, :] = [
                    lon_mesh[ih], lat_mesh[ih], dep_mesh[iv]]
    else:
        lat_mesh = np.linspace(minlat, maxlat, vnpts)
        lon_mesh = np.linspace(minlon, maxlon, hnpts)
        for ih in tqdm.tqdm(range(hnpts)):
            for iv in range(vnpts):
                # plot_values[ih, iv] = interp_value(
                #     lat_mesh[iv], lon_mesh[ih], mindep, x_mesh, y_mesh, z_mesh, data)
                array_to_interpolate[ih, iv, :] = [
                    lon_mesh[iv], lat_mesh[ih], mindep]

    # build up the interpolation function
    interpolating_function = RegularGridInterpolator(
        (lon_list, lat_list, dep_list), data, method="nearest")
    plot_values = interpolating_function(array_to_interpolate)

    # * plot figures
    print("start to plot")
    plt.figure()
    # get vmin and vmax
    vmin_round = round(np.min(plot_values), 2)
    if(vmin_round < np.min(plot_values)):
        vmin = vmin_round
    else:
        vmin = vmin_round-0.01
    vmax_round = round(np.max(plot_values), 2)
    if(vmax_round > np.max(plot_values)):
        vmax = vmax_round
    else:
        vmax = vmax_round+0.01
    # ! set vmin and vmax here
    # vmin = -0.03
    # vmax = 0.03

    v = np.arange(vmin, vmax, 0.01)

    if(plot_vertically):
        # decide to use lat or lon
        lat_diff = np.abs(maxlat-minlat)
        lon_diff = np.abs(maxlon-minlon)
        plot_on = None
        if(lat_diff >= lon_diff):
            mesh_plot_h, mesh_plot_v = np.meshgrid(
                lat_mesh, dep_mesh, indexing="ij")
            plot_on = "latitude"
        else:
            mesh_plot_h, mesh_plot_v = np.meshgrid(
                lon_mesh, dep_mesh, indexing="ij")
            plot_on = "longitude"
        plt.contourf(mesh_plot_h, mesh_plot_v, plot_values,
                     resolution, cmap=plt.cm.seismic_r, vmin=vmin, vmax=vmax)
        plt.colorbar(ticks=v, label="perturbation")
        plt.gca().invert_yaxis()
        plt.xlabel(
            f"{plot_on}(°) between (lon: {minlon}°, lat: {minlat}°) and (lon: {maxlon}°, lat: {maxlat}°)")
        plt.ylabel("depth(km)")
        plt.title(f"parameter: {parameter}")
        plt.show()
    else:
        mesh_plot_h, mesh_plot_v = np.meshgrid(
            lon_mesh, lat_mesh, indexing="ij")
        plt.contourf(mesh_plot_h, mesh_plot_v, plot_values,
                     resolution, cmap=plt.cm.seismic_r, vmin=vmin, vmax=vmax)
        plt.colorbar(ticks=v, label="perturbation")
        plt.gca().invert_yaxis()
        plt.ylabel(
            f"longitude(°) between {minlon}° and {maxlon}°")
        plt.ylabel(
            f"latitude(°) between {minlat}° and {maxlat}°")
        plt.title(f"depth: {mindep}km, parameter: {parameter}")
        plt.show()


if __name__ == "__main__":
    main()
