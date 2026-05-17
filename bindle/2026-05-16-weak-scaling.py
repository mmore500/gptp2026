import marimo

__generated_with = "0.23.2"
app = marimo.App(width="full")


@app.cell
def import_std():
    import pathlib

    return (pathlib,)


@app.cell
def import_pkg():
    import marimo as mo
    from matplotlib import pyplot as plt
    import numpy as np
    import pandas as pd
    import requests
    from scipy import stats as scipy_stats
    import seaborn as sns
    from teeplot import teeplot as tp
    from watermark import watermark

    return mo, np, pd, plt, requests, scipy_stats, sns, tp, watermark


@app.cell
def _():
    from conduitpylib.wrangle import retrieve_and_prepare_delta_dataframes

    return (retrieve_and_prepare_delta_dataframes,)


@app.cell(hide_code=True)
def do_watermark(mo, watermark):
    mo.md(
        f"""
    ```Text
    {watermark(
        current_date=True,
        iso8601=True,
        machine=True,
        updated=True,
        python=True,
        iversions=True,
        globals_=globals(),
    )}
    ```
    """
    )
    return


@app.cell(hide_code=True)
def delimit_prep_data(mo):
    mo.md("""
    ## Prep Data
    """)
    return


@app.cell
def _(requests, retrieve_and_prepare_delta_dataframes):
    for slug in "2rdj6", "9utpr":
        with open(f"/tmp/{slug}", "wb") as _fp:
            _fp.write(
                requests.get(
                    f"https://osf.io/{slug}/download", allow_redirects=True
                ).content,
            )

    _, df_snapshot_diffs = retrieve_and_prepare_delta_dataframes(
        df_inlet_url="/tmp/2rdj6",
        df_outlet_url="/tmp/9utpr",
    )
    return (df_snapshot_diffs,)


@app.cell
def _(df_snapshot_diffs):
    df_snapshot_diffs
    return


@app.cell
def peek_data(df_snapshot_diffs, np):
    df_snapshot_diffs[
        ~np.isfinite(df_snapshot_diffs["Latency Simsteps Outlet"])
        | ~np.isfinite(df_snapshot_diffs["Latency Simsteps Inlet"])
        | ~np.isfinite(df_snapshot_diffs["Delivery Failure Rate"])
        | ~np.isfinite(df_snapshot_diffs["Delivery Clumpiness"])
        | ~np.isfinite(df_snapshot_diffs["Simstep Period Outlet (ns)"])
        | ~np.isfinite(df_snapshot_diffs["Simstep Period Inlet (ns)"])
        | ~np.isfinite(df_snapshot_diffs["Latency Walltime Inlet (ns)"])
        | ~np.isfinite(df_snapshot_diffs["Latency Walltime Outlet (ns)"])
    ][
        [
            "Latency Simsteps Inlet",
            "Latency Simsteps Outlet",
            "Snapshot",
            "Runtime Seconds Elapsed Outlet",
            "Hostname",
            "Replicate",
            "Num Simels Per Cpu",
            "Cpus Per Node",
            "Num Processes",
        ]
    ]
    return


@app.cell
def _(df_snapshot_diffs):
    df_snapshot_diffs["Simstep Period Inlet (ms)"] = (
        df_snapshot_diffs["Simstep Period Inlet (ns)"] / 10**6
    )
    df_snapshot_diffs["Latency Walltime Inlet (ms)"] = (
        df_snapshot_diffs["Latency Walltime Inlet (ns)"] / 10**6
    )
    df_snapshot_diffs["Simstep Period Outlet (ms)"] = (
        df_snapshot_diffs["Simstep Period Outlet (ns)"] / 10**6
    )
    df_snapshot_diffs["Latency Walltime Outlet (ms)"] = (
        df_snapshot_diffs["Latency Walltime Outlet (ns)"] / 10**6
    )
    return


@app.cell
def _(df_snapshot_diffs):
    df_compare = df_snapshot_diffs[
        df_snapshot_diffs["Num Processes"].isin([64, 256])
    ].copy()
    df_compare
    return (df_compare,)


@app.cell
def _(df_compare):
    data_median = (
        df_compare.copy()
        .groupby(
            [
                "Execution Instance UUID",
            ]
        )
        .median(numeric_only=True)
        .reset_index()
        .astype(
            {
                "Num Processes": "int64",
                "Allocated Tasks Per Node": "int64",
                "Cpus Per Node": "int64",
                "Num Simels Per Cpu": "int64",
            }
        )[
            [
                "Num Processes",
                "Cpus Per Node",
                "Num Simels Per Cpu",
                "Latency Simsteps Outlet",
                "Delivery Failure Rate",
                "Delivery Clumpiness",
                "Simstep Period Outlet (ms)",
                "Latency Walltime Outlet (ms)",
            ]
        ]
        .melt(
            id_vars=[
                "Num Processes",
                "Cpus Per Node",
                "Num Simels Per Cpu",
            ],
            var_name="Metric",
            value_name="Value",
        )
    )

    data_median["Kind"] = "median"
    data_median
    return (data_median,)


@app.cell
def _(df_compare):
    data_max = (
        df_compare.copy()
        .groupby(
            [
                "Execution Instance UUID",
            ]
        )
        .max(numeric_only=True)
        .reset_index()
        .astype(
            {
                "Num Processes": "int64",
                "Allocated Tasks Per Node": "int64",
                "Cpus Per Node": "int64",
                "Num Simels Per Cpu": "int64",
            }
        )[
            [
                "Num Processes",
                "Cpus Per Node",
                "Num Simels Per Cpu",
                "Latency Simsteps Outlet",
                "Delivery Failure Rate",
                "Delivery Clumpiness",
                "Simstep Period Outlet (ms)",
                "Latency Walltime Outlet (ms)",
            ]
        ]
        .melt(
            id_vars=[
                "Num Processes",
                "Cpus Per Node",
                "Num Simels Per Cpu",
            ],
            var_name="Metric",
            value_name="Value",
        )
    )

    data_max["Kind"] = "max"
    data_max
    return (data_max,)


@app.cell
def _(data_max, data_median, np, pathlib, pd, plt, scipy_stats, sns, tp):
    _data_all = pd.concat([data_max, data_median], ignore_index=True).replace(
        {
            "Metric": {
                "Simstep Period Outlet (ms)": "Update Walltime\n(ms)",
                "Latency Simsteps Outlet": "Latency\n(updates)",
                "Latency Walltime Outlet (ms)": "Latency\n(ms)",
                "Delivery Clumpiness": "Bunching",
                "Delivery Failure Rate": "Message\nDrop Rate",
            },
        },
    )

    def _pvalue_to_sig(p, baseline, treatment):
        if p > 0.05:
            return "n.s."
        sign = "+" if np.median(treatment) >= np.median(baseline) else "−"
        if p < 0.001:
            return f"{sign}***"
        elif p < 0.01:
            return f"{sign}**"
        else:
            return f"{sign}*"

    _sig_palette = {
        "+***": "#d73027",
        "+**": "#f46d43",
        "+*": "#fdae61",
        "n.s.": "lightgray",
        "−*": "#c7eae5",
        "−**": "#5ab4ac",
        "−***": "#01665e",
    }
    _sig_full_order = [
        "+***",
        "+**",
        "+*",
        "n.s.",
        "−*",
        "−**",
        "−***",
    ]

    for (_cpus, _simels), _cond_df in _data_all.groupby(
        ["Cpus Per Node", "Num Simels Per Cpu"]
    ):
        _cond_df = _cond_df.copy()
        _cond_df["Significance"] = "n.s."
        for (_metric, _kind), _grp in _cond_df.groupby(["Metric", "Kind"]):
            _baseline = _grp.loc[
                _grp["Num Processes"] == 64, "Value"
            ].to_numpy()
            _treatment = _grp.loc[
                _grp["Num Processes"] == 256, "Value"
            ].to_numpy()
            _n = min(len(_baseline), len(_treatment))
            if _n < 1:
                _sig = "n.s."
            else:
                try:
                    _, _p = scipy_stats.mannwhitneyu(_baseline, _treatment)
                    _sig = _pvalue_to_sig(_p, _baseline, _treatment)
                except ValueError:
                    _sig = "n.s."
            _mask = (
                (_cond_df["Metric"] == _metric)
                & (_cond_df["Kind"] == _kind)
                & (_cond_df["Num Processes"] == 256)
            )
            _cond_df.loc[_mask, "Significance"] = _sig

        _hue_order = [
            _s
            for _s in _sig_full_order
            if _s in _cond_df["Significance"].unique()
        ]
        with tp.teed(
            sns.catplot,
            data=_cond_df,
            col="Metric",
            col_order=[
                "Update Walltime\n(ms)",
                "Latency\n(ms)",
                "Latency\n(updates)",
                "Message\nDrop Rate",
                "Bunching",
            ],
            row="Kind",
            x="Num Processes",
            order=[64, 256],
            y="Value",
            hue="Significance",
            hue_order=_hue_order,
            palette=_sig_palette,
            clip_on=False,
            kind="strip",
            linewidth=1,
            margin_titles=True,
            marker="+",
            s=10,
            sharey=False,
            dodge=False,
            teeplot_outattrs={
                "cpus_per_node": str(_cpus),
                "num_simels_per_cpu": str(_simels),
            },
            teeplot_show=True,
            teeplot_subdir=pathlib.Path(__file__).stem,
        ) as _g:
            _g.figure.set_size_inches(9, 2.2)
            _g.set_titles(col_template="{col_name}", row_template="{row_name}")
            _g.set(ylim=(0, None), xlabel="Num Processes", ylabel="")
            plt.subplots_adjust(hspace=0.2, wspace=0.2)
            for _ax in _g.axes.flat:
                _ax.ticklabel_format(style="sci", axis="y", scilimits=(-4, 3))
                _ax.yaxis.get_offset_text().set_x(-0.25)
                _ax.yaxis.get_offset_text().set_y(0.5)
            for _ax in _g.axes[1, :].flat:
                _ax.set_ylim(1.6 * np.array(_ax.get_ylim()))
            sns.despine(fig=_g.figure, bottom=True)
            sns.move_legend(
                _g,
                loc="center right",
                bbox_to_anchor=(1.04, 0.5),
                frameon=False,
                title=None,
                markerscale=3,
                handletextpad=0.1,
            )
    return


if __name__ == "__main__":
    app.run()
