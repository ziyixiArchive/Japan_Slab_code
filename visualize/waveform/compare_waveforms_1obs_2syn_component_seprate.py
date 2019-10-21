import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt
import obspy
import pyasdf
from obspy.geodetics.base import gps2dist_azimuth, locations2degrees
from obspy.taup import TauPyModel
from recordtype import recordtype
import numpy as np
import click
import matplotlib as mpl
import tqdm

label_size = 25
mpl.rcParams['xtick.labelsize'] = label_size

to_plot_trace = recordtype("to_plot_trace", [
                           "obs_z", "syn1_z", "syn2_z", "obs_r", "syn1_r", "syn2_r",  "obs_t", "syn1_t", "syn2_t",  "info"])


def build_to_plot_traces(obs_ds, syn1_ds, syn2_ds, trace_length):
    # obs_ds,syn_ds opened asdf file
    # get keys
    key_obs = set(obs_ds.waveforms.list())
    key_syn1 = set(syn1_ds.waveforms.list())
    key_syn2 = set(syn2_ds.waveforms.list())
    keys = key_obs & key_syn1 & key_syn2
    result = {}
    # for each item in keys, get info
    # since the window is selected according to the two asdf files, we can just use keys
    for key in keys:
        axkey = key.replace(".", "_")
        tag_obs = obs_ds.waveforms[key].get_waveform_tags()[0]
        tag_syn1 = syn1_ds.waveforms[key].get_waveform_tags()[0]
        tag_syn2 = syn2_ds.waveforms[key].get_waveform_tags()[0]

        # here we use syn1_ds, which is not the normal case
        info = obs_ds.auxiliary_data.Traveltimes[axkey].parameters
        obs_st = obs_ds.waveforms[key][tag_obs].copy()
        syn1_st = syn1_ds.waveforms[key][tag_syn1].copy()
        syn2_st = syn2_ds.waveforms[key][tag_syn2].copy()

        # slice
        obs_st.trim(obs_st[0].stats.starttime,
                    obs_st[0].stats.starttime+trace_length)
        syn1_st.trim(syn1_st[0].stats.starttime,
                     syn1_st[0].stats.starttime+trace_length)
        syn2_st.trim(syn2_st[0].stats.starttime,
                     syn2_st[0].stats.starttime+trace_length)

        obs_r = obs_st[0]
        obs_t = obs_st[1]
        obs_z = obs_st[2]
        syn1_r = syn1_st[0]
        syn1_t = syn1_st[1]
        syn1_z = syn1_st[2]
        syn2_r = syn2_st[0]
        syn2_t = syn2_st[1]
        syn2_z = syn2_st[2]

        result[key] = to_plot_trace(
            obs_z, syn1_z, syn2_z, obs_r, syn1_r, syn2_r, obs_t, syn1_t, syn2_t, info)
    return result


def build_plottting_structure(plot_traces, azimuth_width):
    # we assume 360%azimuth_width==0
    num_azimuths = 360//azimuth_width
    result = [[] for i in range(num_azimuths)]
    # for each item in plot_traces, seprate them into different []
    for key in plot_traces:
        value = plot_traces[key]
        info = value.info
        azimuth = info["azimuth"]
        index_azimuth = int(azimuth//azimuth_width)
        result[index_azimuth].append((key, value))

    # for each azimuth bin, sort them according to the gcarc
    def sort_func(item):
        return item[1].info["gcarc"]
    for index_azimuth in range(num_azimuths):
        result[index_azimuth] = sorted(result[index_azimuth], key=sort_func)
    return result


@click.command()
@click.option('--obs_asdf', required=True, type=str)
@click.option('--syn1_asdf', required=True, type=str)
@click.option('--syn2_asdf', required=True, type=str)
@click.option('--azimuth_width', required=True, type=int)
@click.option('--output_pdf', required=True, type=str)
@click.option('--waves_perpage', required=True, type=int)
@click.option('--trace_length', required=True, type=int)
def main(obs_asdf, syn1_asdf, syn2_asdf, azimuth_width, output_pdf, waves_perpage, trace_length):
    obs_ds = pyasdf.ASDFDataSet(obs_asdf, mode="r")
    syn1_ds = pyasdf.ASDFDataSet(syn1_asdf, mode="r")
    syn2_ds = pyasdf.ASDFDataSet(syn2_asdf, mode="r")

    plot_traces = build_to_plot_traces(obs_ds, syn1_ds, syn2_ds, trace_length)
    plotting_structure = build_plottting_structure(plot_traces, azimuth_width)

    # plot figures
    pdf = matplotlib.backends.backend_pdf.PdfPages(output_pdf)
    figs = plt.figure()

    num_azimuths = 360//azimuth_width
    for index_azimuth in tqdm.tqdm(range(num_azimuths)):
        # # ! for developing
        # if(index_azimuth == 2):
        #     break
        # for each azimuth bin
        azimuth_bin_plot_traces = plotting_structure[index_azimuth]
        num_azimuth_bin_plot_traces = len(azimuth_bin_plot_traces)
        # get num_pages for this azimuth bin
        if(num_azimuth_bin_plot_traces % waves_perpage == 0):
            num_pages = num_azimuth_bin_plot_traces // waves_perpage
        else:
            num_pages = (num_azimuth_bin_plot_traces // waves_perpage)+1

        for ipage in range(num_pages):
            start_index = ipage*waves_perpage
            end_index = (ipage+1)*waves_perpage
            azimuth_bin_plot_traces_this_page = azimuth_bin_plot_traces[start_index:end_index]

            fig_z = plt.figure(figsize=(150, 150))
            fig_r = plt.figure(figsize=(150, 150))
            fig_t = plt.figure(figsize=(150, 150))
            index_count = 1
            axr, axz, axt = None, None, None  # get the last axes
            xticks = None
            for each_plot_trace_all in azimuth_bin_plot_traces_this_page:
                each_plot_trace = each_plot_trace_all[1]
                each_plot_id = each_plot_trace_all[0]
                # z
                axz = fig_z.add_subplot(waves_perpage, 1, index_count)
                obs = each_plot_trace.obs_z
                syn1 = each_plot_trace.syn1_z
                syn2 = each_plot_trace.syn2_z
                x_obs = np.linspace(0, obs.stats.endtime -
                                    obs.stats.starttime, obs.stats.npts)
                x_syn1 = np.linspace(0, syn1.stats.endtime -
                                     syn1.stats.starttime, syn1.stats.npts)
                x_syn2 = np.linspace(0, syn2.stats.endtime -
                                     syn2.stats.starttime, syn2.stats.npts)
                y_obs = obs.data
                y_syn1 = syn1.data
                y_syn2 = syn2.data
                axz.plot(x_obs, y_obs, color="k", linewidth=6.0)
                axz.plot(x_syn1, y_syn1, color="r", linewidth=6.0)
                axz.plot(x_syn2, y_syn2, color="b", linewidth=6.0)

                axz.get_yaxis().set_ticklabels([])
                # index_count += 1
                # r
                axr = fig_r.add_subplot(waves_perpage, 1, index_count)
                obs = each_plot_trace.obs_r
                syn1 = each_plot_trace.syn1_r
                syn2 = each_plot_trace.syn2_r
                x_obs = np.linspace(0, obs.stats.endtime -
                                    obs.stats.starttime, obs.stats.npts)
                x_syn1 = np.linspace(0, syn1.stats.endtime -
                                     syn1.stats.starttime, syn1.stats.npts)
                x_syn2 = np.linspace(0, syn2.stats.endtime -
                                     syn2.stats.starttime, syn2.stats.npts)
                y_obs = obs.data
                y_syn1 = syn1.data
                y_syn2 = syn2.data
                axr.plot(x_obs, y_obs, color="k", linewidth=6.0)
                axr.plot(x_syn1, y_syn1, color="r", linewidth=6.0)
                axr.plot(x_syn2, y_syn2, color="b", linewidth=6.0)

                axr.get_yaxis().set_ticklabels([])
                # index_count += 1
                # t
                axt = fig_t.add_subplot(waves_perpage, 1, index_count)
                obs = each_plot_trace.obs_t
                syn1 = each_plot_trace.syn1_t
                syn2 = each_plot_trace.syn2_t

                # we should remove the abnormal at the two side
                obs.detrend("demean")
                obs.detrend("linear")
                obs.taper(max_percentage=0.05, type="hann")
                syn1.detrend("demean")
                syn1.detrend("linear")
                syn1.taper(max_percentage=0.05, type="hann")
                syn2.detrend("demean")
                syn2.detrend("linear")
                syn2.taper(max_percentage=0.05, type="hann")

                x_obs = np.linspace(0, obs.stats.endtime -
                                    obs.stats.starttime, obs.stats.npts)
                x_syn1 = np.linspace(0, syn1.stats.endtime -
                                     syn1.stats.starttime, syn1.stats.npts)
                x_syn2 = np.linspace(0, syn2.stats.endtime -
                                     syn2.stats.starttime, syn2.stats.npts)
                y_obs = obs.data
                y_syn1 = syn1.data
                y_syn2 = syn2.data
                axt.plot(x_obs, y_obs, color="k", linewidth=6.0)
                axt.plot(x_syn1, y_syn1, color="r", linewidth=6.0)
                axt.plot(x_syn2, y_syn2, color="b", linewidth=6.0)

                axt.get_yaxis().set_ticklabels([])
                index_count += 1

                # add labels
                # axz.set_ylabel(
                #     f"id:{each_plot_id}\ngcarc:{each_plot_trace.info['gcarc']:.2f}\nazimuth:{each_plot_trace.info['azimuth']:.2f}", fontsize=60)
                # axr.set_ylabel(
                #     f"id:{each_plot_id}\ngcarc:{each_plot_trace.info['gcarc']:.2f}\nazimuth:{each_plot_trace.info['azimuth']:.2f}", fontsize=60)
                # axt.set_ylabel(
                #     f"id:{each_plot_id}\ngcarc:{each_plot_trace.info['gcarc']:.2f}\nazimuth:{each_plot_trace.info['azimuth']:.2f}", fontsize=60)
                # get xticks
                xticks = np.arange(np.min(x_obs), np.max(x_obs)+1, 100)
                axz.set_xticks(xticks)
                axr.set_xticks(xticks)
                axt.set_xticks(xticks)
                axz.tick_params(axis="x", labelsize=100)
                axr.tick_params(axis="x", labelsize=100)
                axt.tick_params(axis="x", labelsize=100)
                axz.tick_params(axis="y", labelsize=100)
                axr.tick_params(axis="y", labelsize=100)
                axt.tick_params(axis="y", labelsize=100)
                # plot texts
                axz.text(0.90, 0.53, f"id:{each_plot_id}\ngcarc:{each_plot_trace.info['gcarc']:.2f}\nazimuth:{each_plot_trace.info['azimuth']:.2f}",
                         transform=axz.transAxes, fontsize=100)

                # plot title
                if(index_count == 2):
                    axz.set_title(
                        f"azimuth:{azimuth_width*index_azimuth}-{azimuth_width*(index_azimuth+1)}\npage:{ipage}, vertical", fontsize=200)
                    axr.set_title(
                        f"azimuth:{azimuth_width*index_azimuth}-{azimuth_width*(index_azimuth+1)}\npage:{ipage}, radial", fontsize=200)
                    axt.set_title(
                        f"azimuth:{azimuth_width*index_azimuth}-{azimuth_width*(index_azimuth+1)}\npage:{ipage}, tagential", fontsize=200)

                # plot travel times
                info = each_plot_trace.info
                # z
                axz2 = axz.twiny()
                axz2.set_xlim(axz.get_xlim())
                twin_label = []
                plot_travel_times(axz2, "p", info["p"], np.max(
                    x_obs), "blue", twin_label)
                plot_travel_times(
                    axz2, "pp", info["pp"], np.max(x_obs), "y", twin_label)
                plot_travel_times(
                    axz2, "sp", info["sp"], np.max(x_obs), "r", twin_label)
                plot_travel_times(
                    axz2, "rayleigh", info["rayleigh"], np.max(x_obs), "c", twin_label)
                plot_travel_times(axz2, "s", info["s"], np.max(
                    x_obs), "green", twin_label)
                plot_travel_times(
                    axz2, "ss", info["ss"], np.max(x_obs), "black", twin_label)
                twin_x = [item[0] for item in twin_label]
                twin_name = [item[1] for item in twin_label]
                axz2.set_xticks(twin_x)
                axz2.set_xticklabels(twin_name, fontsize=50)
                axz2.xaxis.set_tick_params(rotation=90)
                # r
                axr2 = axr.twiny()
                axr2.set_xlim(axr.get_xlim())
                twin_label = []
                plot_travel_times(axr, "p", info["p"], np.max(
                    x_obs), "blue", twin_label)
                plot_travel_times(
                    axr, "pp", info["pp"], np.max(x_obs), "y", twin_label)
                plot_travel_times(
                    axr, "sp", info["sp"], np.max(x_obs), "r", twin_label)
                plot_travel_times(
                    axr, "rayleigh", info["rayleigh"], np.max(x_obs), "c", twin_label)
                plot_travel_times(axr, "s", info["s"], np.max(
                    x_obs), "green", twin_label)
                plot_travel_times(
                    axr, "ss", info["ss"], np.max(x_obs), "black", twin_label)
                twin_x = [item[0] for item in twin_label]
                twin_name = [item[1] for item in twin_label]
                axr2.set_xticks(twin_x)
                axr2.set_xticklabels(twin_name, fontsize=50)
                axr2.xaxis.set_tick_params(rotation=90)
                # t
                axt2 = axt.twiny()
                axt2.set_xlim(axt.get_xlim())
                twin_label = []
                plot_travel_times(axt, "s", info["s"], np.max(
                    x_obs), "green", twin_label)
                plot_travel_times(
                    axt, "ss", info["ss"], np.max(x_obs), "black", twin_label)
                plot_travel_times(
                    axt, "scs", info["scs"], np.max(x_obs), "magenta", twin_label)
                plot_travel_times(
                    axt, "love", info["love"], np.max(x_obs), "teal", twin_label)
                twin_x = [item[0] for item in twin_label]
                twin_name = [item[1] for item in twin_label]
                axt2.set_xticks(twin_x)
                axt2.set_xticklabels(twin_name, fontsize=50)
                axt2.xaxis.set_tick_params(rotation=90)
                # if(index_count == 4):
                #     axz.legend(loc='upper right')
                #     axr.legend(loc='upper right')
                #     axt.legend(loc='upper right')
            plt.subplots_adjust(wspace=0, hspace=0)
            fig_z.tight_layout()
            pdf.savefig(fig_z)
            fig_r.tight_layout()
            pdf.savefig(fig_r)
            fig_t.tight_layout()
            pdf.savefig(fig_t)
            plt.close(fig=fig_z)
            plt.close(fig=fig_r)
            plt.close(fig=fig_t)
    pdf.close()


def plot_travel_times(ax, phasename, traveltime, length, thecolor, twin_label):
    if(traveltime < 1e-6):
        return
    if(traveltime < length):
        # ax.scatter(traveltime, 0, color=thecolor, label=phasename, s=9)
        ax.axvline(x=traveltime, color="g", linestyle='--', linewidth=3.0)
        # ax.text(traveltime, ylim[0]+(ylim[1]-ylim[0])*0.9, phasename)
        if(phasename == "rayleigh"):
            phasename = "rayl"
        twin_label.append((traveltime, phasename))


def plot_windows(ax, phasename, win, thecolor):
    if(type(win) == type(None)):
        return
    mapper = {
        "p": (3, 4),
        "s": (5, 6),
        "pp": (7, 8),
        "ss": (9, 10),
        "sp": (11, 12),
        "scs": (13, 14),
        "rayleigh": (15, 16),
        "love": (17, 18)
    }
    start_time = win[mapper[phasename][0]]
    end_time = win[mapper[phasename][1]]
    if(start_time == "None" or end_time == "None"):
        return
    else:
        start_time = float(start_time)
        end_time = float(end_time)
        ax.axvspan(start_time, end_time, alpha=0.1, color=thecolor)


if __name__ == "__main__":
    main()
