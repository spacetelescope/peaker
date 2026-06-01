"""Utilities to create all plots"""

import numpy as np
import matplotlib
from matplotlib import pyplot as plt

from .utils import convert_units


def _plot_test(testname, data, plt_dir, show_plt=False, show_plt_path=False):
    # Set up generals for the plot
    font = {"weight": "normal",
            "size": 12}
    matplotlib.rc("font", **font)
    alpha = 0.5
    fig, axs = plt.subplots(2, 1, figsize=(12, 10))
    test_instmode = testname.split("_M_")
    plot_title = test_instmode[0] + "  Instrument_mode: " + test_instmode[1]
    fig.suptitle(plot_title)

    # Set the data arrays to plot
    dates = np.array(data["date"])
    times = np.array(data["time"])
    peakmems, units = convert_units(np.array(data["peakmem"]))

    # Calculate the stats on peak memory usage
    mean = np.mean(peakmems)
    median = np.median(peakmems)
    if isinstance(peakmems, np.float64):
        max = peakmems
        date_max_peakmem = dates[0].strftime("%Y-%m-%dT%H:%M:%S")
        times_max_peakmem = times
    else:
        max_peakmem_idx = np.argmax(peakmems)
        max = peakmems[max_peakmem_idx]
        date_max_peakmem = dates[max_peakmem_idx].strftime("%Y-%m-%dT%H:%M:%S")
        times_max_peakmem = times[max_peakmem_idx]
    mean_time, median_time = np.mean(times), np.median(times)
    mean_peakmem = "mean peakmem = {:1.3f} [{}], {:1.0f} [s]".format(mean, units, mean_time)
    median_peakmem = "median peakmem = {:1.3f} [{}], {:1.0f} [s]".format(median, units, median_time)
    stddev_peakmem = "stddev = {:1.3f} [{}], {:1.0f} [s]".format(np.std(peakmems), units, np.std(times))
    max_peakmem = "max peakmem = {:1.3f} [{}], {:1.0f} [s] on {}".format(max, units, times_max_peakmem, date_max_peakmem)

    axs[0].axhline(mean, linewidth=1, color="green", linestyle="--", label="Mean")
    axs[0].axhline(median, linewidth=1, color="red", linestyle=":", label="Median")
    axs[0].scatter(dates, peakmems, marker="*", color="blue", alpha=alpha)#, label="peakmem")
    axs[0].tick_params(axis="both", which="both", bottom=True, top=True, right=True, direction="in", labelbottom=True)
    axs[0].minorticks_on()
    axs[0].set(xlabel="Dates [Local time]", ylabel="Peak Memory ["+units+"]")
    axs[0].tick_params(axis='x', rotation=70)
    axs[0].legend()
    axs[1].axhline(mean_time, linewidth=1, color="green", linestyle="--", label="Mean")
    axs[1].axhline(median_time, linewidth=1, color="red", linestyle=":", label="Median")
    axs[1].scatter(dates, times, marker=".", color="black", alpha=alpha)#,  label="times")
    axs[1].tick_params(axis="both", which="both", bottom=True, top=True, right=True, direction="in", labelbottom=True)
    axs[1].minorticks_on()
    axs[1].set(xlabel="Dates [Local time]", ylabel="Times [s]")
    axs[1].tick_params(axis='x', rotation=70)
    axs[1].legend()
    stats_x, stats_y = 0.01, 2.51
    axs[1].text(stats_x, stats_y, max_peakmem, transform=axs[1].transAxes)
    axs[1].text(stats_x, stats_y+0.06, mean_peakmem, transform=axs[1].transAxes)
    axs[1].text(stats_x, stats_y+0.12, median_peakmem, transform=axs[1].transAxes)
    axs[1].text(stats_x, stats_y+0.18, stddev_peakmem, transform=axs[1].transAxes)
    plt.subplots_adjust(bottom=0.13, hspace=0.42, top=0.85)

    # Show and/or save plots
    plt_name = testname + ".png"
    plt_path = plt_dir / plt_name
    plt.savefig(plt_path)
    if show_plt_path:
        print('Plot saved: ', plt_path)
    if show_plt:
        plt.show()
    plt.close(fig)
    return plt_path


def mk_plots(output):
    """
    Creates plots for all tests ran.
    
    Parameters
    ----------
    output : class
        A dataclass with the following elements:
        outdir - Full path for the output directory.
        tests_ran - Dictionary will have the test name are the keys and a subdictionary
            containing an array of dates, peak memory, and corresponding run times.
        local_sdate - Start date (Local time) for files with data.
        local_edate - End date (Local time) for files with data.
        report_table - Table of test data organized by test name and class.
        plots - List of plots.
    """
    
    # Create the plots directory
    plt_dir = output.outdir / "plots"
    plt_dir.mkdir(exist_ok=True, parents=True)
    
    # Plot every test
    print(" Making plots...")
    plots = []
    show_plt, show_plt_path = False, False
    for test, data in output.tests_ran.items():
        plt_path = _plot_test(test, data, plt_dir,
                              show_plt=show_plt, show_plt_path=show_plt_path)
        plots.append(plt_path)
    output.plots = plots

    if not show_plt_path:
        print(" Plots saved at: ", plt_dir)

