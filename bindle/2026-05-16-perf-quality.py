import marimo

__generated_with = "0.23.2"
app = marimo.App(width="full")


@app.cell
def import_std():
    import pathlib

    return (pathlib,)


@app.cell
def import_pkg():
    from cliffs_delta import cliffs_delta
    import marimo as mo
    import matplotlib as mpl
    from matplotlib import pyplot as plt
    import numpy as np
    import pandas as pd
    import requests
    from scipy import stats as scipy_stats
    import seaborn as sns
    from teeplot import teeplot as tp
    from watermark import watermark

    return (
        cliffs_delta,
        mo,
        mpl,
        np,
        pd,
        plt,
        requests,
        scipy_stats,
        sns,
        tp,
        watermark,
    )


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
    mo.md(
        """
    ## Prep Data
    """
    )
    return


@app.cell
def _(np, pd, requests):
    with open("/tmp/dkj9n", "wb") as _fp:
        _fp.write(
            requests.get(
                "https://osf.io/dkj9n/download", allow_redirects=True
            ).content,
        )

    ds_proc = pd.read_csv("/tmp/dkj9n")

    ds_proc["ncpus"] = ds_proc["nthreads"] * ds_proc["nprocs"]
    ds_proc["conflicts per cpu"] = (
        ds_proc["conflicts total"] / ds_proc["ncpus"]
    )
    ds_proc["updates per cpu-second"] = (
        ds_proc["updates total"] / ds_proc["ncpus"] / ds_proc["seconds"]
    )
    ds_proc["Update Walltime (ms)"] = 1_000 / ds_proc["updates per cpu-second"]

    ds_proc["log conflicts per cpu"] = np.log(ds_proc["conflicts per cpu"])

    ds_proc
    return (ds_proc,)


@app.cell
def peek_data(pd, requests):
    with open("/tmp/3jz4w", "wb") as _fp:
        _fp.write(
            requests.get(
                "https://osf.io/3jz4w/download", allow_redirects=True
            ).content,
        )
    ds_control = pd.read_csv("/tmp/3jz4w")
    ds_control["ncpus"] = ds_control["nthreads"] * ds_control["nprocs"]

    ds_control
    return


@app.cell
def _(cliffs_delta, ds_proc, pd, scipy_stats):
    filtered_procs = ds_proc[
        (ds_proc["nthreads"] == 1)
        & (ds_proc["asynchronicity mode"].isin([0, 3]))
    ]

    _res = []
    for (_mode, _exec), _group in filtered_procs.groupby(
        ["asynchronicity mode", "executable"]
    ):
        _g1, _g2 = (
            _group.loc[_group["ncpus"] == 1, "Update Walltime (ms)"],
            _group.loc[_group["ncpus"] == 64, "Update Walltime (ms)"],
        )

        _res.append(
            {
                "mode": _mode,
                "exec": _exec,
                "n": len(_group),
                "%": 100 * (_g2.mean() / _g1.mean() - 1),
                **dict(
                    zip(
                        ["wstat", "p"],
                        scipy_stats.wilcoxon(_g1, _g2, alternative="less"),
                    )
                ),
                **dict(zip(["delta", "interp"], cliffs_delta(_g1, _g2))),
            },
        )

    pd.DataFrame(_res)
    return (filtered_procs,)


@app.cell
def _(cliffs_delta, filtered_procs, pd, scipy_stats):
    _res = []
    for (_mode, _exec), _group in filtered_procs.groupby(
        ["asynchronicity mode", "executable"]
    ):
        _g1, _g2 = (
            _group.loc[_group["ncpus"] == 16, "Update Walltime (ms)"],
            _group.loc[_group["ncpus"] == 64, "Update Walltime (ms)"],
        )

        _res.append(
            {
                "mode": _mode,
                "exec": _exec,
                "n": len(_group),
                "%": 100 * (_g2.mean() / _g1.mean() - 1),
                **dict(
                    zip(
                        ["wstat", "p"],
                        scipy_stats.wilcoxon(_g1, _g2, alternative="less"),
                    )
                ),
                **dict(zip(["delta", "interp"], cliffs_delta(_g1, _g2))),
            },
        )

    pd.DataFrame(_res)
    return


@app.cell
def _(cliffs_delta, filtered_procs, pd, scipy_stats):
    _res = []
    for (_mode, _exec), _group in filtered_procs.groupby(
        ["asynchronicity mode", "executable"]
    ):
        _g1, _g2 = (
            _group.loc[_group["ncpus"] == 1, "Update Walltime (ms)"],
            _group.loc[_group["ncpus"] == 64, "Update Walltime (ms)"],
        )

        _res.append(
            {
                "mode": _mode,
                "exec": _exec,
                "n": len(_group),
                "%": 100 * (_g2.mean() / _g1.mean() - 1),
                **dict(
                    zip(
                        ["wstat", "p"],
                        scipy_stats.wilcoxon(_g1, _g2, alternative="less"),
                    )
                ),
                **dict(zip(["delta", "interp"], cliffs_delta(_g1, _g2))),
            },
        )

    pd.DataFrame(_res)
    return


@app.cell
def _(filtered_procs, mpl, np, pathlib, plt, sns, target_y, tp, va):
    with tp.teed(
        sns.relplot,
        data=filtered_procs,
        x="ncpus",
        y="Update Walltime (ms)",
        col="executable",
        hue="executable",
        row="asynchronicity mode",
        row_order=[3, 0],
        err_style=None,
        facet_kws=dict(margin_titles=True, sharey="col"),
        kind="line",
        legend=False,
        teeplot_show=True,
        teeplot_subdir=pathlib.Path(__file__).stem,
    ) as _g:

        # adapted from https://github.com/mwaskom/seaborn/issues/2410#issuecomment-753474050
        for _i, (_ax, (_signif1, _signif2)) in enumerate(
            zip(
                _g.axes.flat,
                [
                    ("**", "n.s."),
                    ("***", "n.s."),
                    ("***", "***"),
                    ("***", "***"),
                ],
            )
        ):
            for line in _ax.lines:
                _x, _y = line.get_xydata().T
                _ax.fill_between(
                    _x, _y.min(), _y, color=line.get_color(), alpha=0.2
                )

                _target_y = max(_y.max(), _y.min() * 1.3, _y.min() + 0.7)
                _ax.hlines(_, 1, 64, color="gray", ls=":", alpha=0.5)

                _pct_change = ((_y[3] - _y[0]) / abs(_y[0])) * 100
                _va = {True: "bottom", False: "top"}[
                    target_y < np.mean(_ax.get_ylim())
                ]
                _ax.text(
                    x=1,
                    y=target_y
                    + np.ptp(_ax.get_ylim())
                    * {"bottom": 0.05, "top": -0.05}[_va],
                    s=f"|+{_pct_change:.0f}%{_signif1}",
                    alpha=1.0,
                    color="gray",
                    ha="left",
                    fontsize=9,
                    va=_va,
                )

                _pct_change = ((_y[3] - _y[2]) / abs(_y[2])) * 100
                _va = "bottom"
                # _ax.hlines(target_y + np.ptp(_ax.get_ylim()) * 0, 16, 64, color="beige", ls="--")
                _ax.text(
                    x=16,
                    y=target_y
                    + np.ptp(_ax.get_ylim())
                    * {"bottom": 0.05, "top": -0.05}[va],
                    s=f"|+{_pct_change:.0f}%{_signif2}",
                    alpha=1.0,
                    color="gray",
                    ha="left",
                    fontsize=9,
                    va=_va,
                )

        _g.map_dataframe(
            sns.lineplot,
            x="ncpus",
            y="Update Walltime (ms)",
            color="k",
            errorbar="sd",
            err_style="bars",
            legend=False,
            lw=0,
        )

        _g.set(ylim=(0, None))
        _g.set(xscale="log")
        _g.figure.set_size_inches(6, 2)
        _g.set_titles(col_template="{col_name}", row_template="")
        plt.subplots_adjust(hspace=0.3)

        for i, _ax in enumerate(_g.axes.flat):
            _ax.minorticks_off()
            _ax.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
            _ax.set_xticks([1, 4, 16, 64])
            if i % 2 != 0:
                sns.despine(ax=_ax, bottom=True)
            if i < 2:
                _ax.set_title(
                    {
                        0: "Digital Evo Walltime (ns)",
                        1: "Graph Color Walltime (ns)",
                    }[i],
                    fontsize=11,
                )

        _g.axes[0, 0].set_ylabel("Best\nEffort")
        _g.axes[1, 0].set_ylabel("Global\nSync")
    return


@app.cell
def _(cliffs_delta, filtered_procs, pd, scipy_stats):
    _res = []
    for (_mode, _exec), _group in filtered_procs.groupby(
        ["asynchronicity mode", "executable"]
    ):
        _g1, _g2 = (
            _group.loc[_group["ncpus"] == 1, "conflicts per cpu"],
            _group.loc[_group["ncpus"] == 64, "conflicts per cpu"],
        )

        _res.append(
            {
                "mode": _mode,
                "exec": _exec,
                "n": len(_group),
                "%": 100 * (_g2.mean() / _g1.mean() - 1),
                **dict(
                    zip(
                        ["wstat", "p"],
                        scipy_stats.wilcoxon(_g1, _g2, alternative="less"),
                    )
                ),
                **dict(zip(["delta", "interp"], cliffs_delta(_g1, _g2))),
            },
        )

    pd.DataFrame(_res)
    return


@app.cell
def _(cliffs_delta, filtered_procs, pd, scipy_stats):
    _res = []
    for (_mode, _exec), _group in filtered_procs.groupby(
        ["asynchronicity mode", "executable"]
    ):
        _g1, _g2 = (
            _group.loc[_group["ncpus"] == 16, "conflicts per cpu"],
            _group.loc[_group["ncpus"] == 64, "conflicts per cpu"],
        )

        _res.append(
            {
                "mode": _mode,
                "exec": _exec,
                "n": len(_group),
                "%": 100 * (_g2.mean() / _g1.mean() - 1),
                **dict(
                    zip(
                        ["wstat", "p"],
                        scipy_stats.wilcoxon(_g1, _g2, alternative="less"),
                    )
                ),
                **dict(zip(["delta", "interp"], cliffs_delta(_g1, _g2))),
            },
        )

    pd.DataFrame(_res)
    return


@app.cell
def _(filtered_procs, mpl, np, pathlib, plt, sns, tp):
    with tp.teed(
        sns.relplot,
        data=filtered_procs,
        x="ncpus",
        y="conflicts per cpu",
        col="executable",
        col_order=["channel_selection"],
        hue="executable",
        row="asynchronicity mode",
        row_order=[3, 0],
        err_style=None,
        facet_kws=dict(margin_titles=True, sharey="col"),
        kind="line",
        legend=False,
        teeplot_show=True,
        teeplot_subdir=pathlib.Path(__file__).stem,
    ) as _g:

        # adapted from https://github.com/mwaskom/seaborn/issues/2410#issuecomment-753474050
        for _i, (_ax, (_signif1, _signif2)) in enumerate(
            zip(_g.axes.flat, [("n.s.", "n.s."), ("***", "***")])
        ):
            for _line in _ax.lines:
                _x, _y = _line.get_xydata().T
                _ax.fill_between(
                    _x, _y.min(), _y, color=_line.get_color(), alpha=0.2
                )

                _target_y = max(_y.max(), _y.min() + 10)
                _ax.hlines(_target_y, 1, 64, color="gray", ls=":", alpha=0.5)

                _pct_change = ((_y[3] - _y[0]) / abs(_y[0])) * 100
                _va = {True: "bottom", False: "top"}[
                    _target_y < np.mean(_ax.get_ylim())
                ]
                _ax.text(
                    x=1,
                    y=_target_y
                    + np.ptp(_ax.get_ylim())
                    * {"bottom": 0.05, "top": -0.05}[_va],
                    s=f"|+{_pct_change:.0f}%{_signif1}",
                    alpha=1.0,
                    color="gray",
                    ha="left",
                    fontsize=9,
                    va=_va,
                )

                _pct_change = ((_y[3] - _y[2]) / abs(_y[2])) * 100
                _va = "bottom"
                # _ax.hlines(target_y + np.ptp(_ax.get_ylim()) * 0, 16, 64, color="beige", ls="--")
                _ax.text(
                    x=16,
                    y=_target_y
                    + np.ptp(_ax.get_ylim())
                    * {"bottom": 0.05, "top": -0.05}[_va],
                    s=f"|+{_pct_change:.0f}%{_signif2}",
                    alpha=1.0,
                    color="gray",
                    ha="left",
                    fontsize=9,
                    va=_va,
                )

        _g.map_dataframe(
            sns.lineplot,
            x="ncpus",
            y="conflicts per cpu",
            color="k",
            errorbar="sd",
            err_style="bars",
            legend=False,
            lw=0,
        )

        _g.set(ylim=(0, None))
        _g.set(xscale="log")
        _g.figure.set_size_inches(6, 2)
        _g.set_titles(col_template="{col_name}", row_template="")
        plt.subplots_adjust(hspace=0.3)

        for _i, _ax in enumerate(_g.axes.flat):
            _ax.minorticks_off()
            _ax.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
            _ax.set_xticks([1, 4, 16, 64])
            if _i == 0:
                sns.despine(ax=_ax, bottom=True)
            if _i == 0:
                _ax.set_title(
                    {
                        0: "Graph Color Soln Quality",
                    }[_i],
                    fontsize=11,
                )

        _g.axes[0, 0].set_ylabel("Best\nEffort")
        _g.axes[1, 0].set_ylabel("Global\nSync")
    return


if __name__ == "__main__":
    app.run()
