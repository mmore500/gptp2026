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
def _(filtered_procs, mpl, np, pathlib, plt, sns, tp):
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
                # _ax.hlines(_target_y + np.ptp(_ax.get_ylim()) * 0, 16, 64, color="beige", ls="--")
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
                        0: "Digital Evo Walltime (ms)",
                        1: "Graph Color Walltime (ms)",
                    }[i],
                    fontsize=11,
                )

        _g.axes[0, 0].set_ylabel("Best\nEffort")
        _g.axes[1, 0].set_ylabel("Global\nSync")

        for _ax in _g.axes[-1, :]:
            _ax.set_xlabel("Num Processes")
    return


@app.cell(hide_code=True)
def delimit_besteffort_sync(mo):
    mo.md(
        """
    ## Best-Effort vs. Synchronous Comparisons

    The tables above compare problem sizes within a fixed asynchronicity
    mode. The tables below instead compare the two asynchronicity modes
    against each other --- best-effort (mode 3) vs. synchronous (mode 0)
    --- at each problem size, for each performance measure: digital
    evolution speed, graph coloring speed, and graph coloring error.

    Each row reports a two-sided Wilcoxon signed-rank test (paired by
    replicate) alongside Cliff's delta, mirroring the scaling tables
    above. The `%` column gives the synchronous mean relative to the
    best-effort mean, so positive values mean synchronous ran slower
    (walltime) or accrued more error (conflicts). A negative `delta`
    likewise indicates lower best-effort values than synchronous.
    """
    )
    return


@app.cell
def _(cliffs_delta, filtered_procs, pd, scipy_stats):
    _res = []
    _data = filtered_procs[filtered_procs["executable"] == "dishtiny"]
    for _ncpus, _group in _data.groupby("ncpus"):
        _g1, _g2 = (
            _group.loc[
                _group["asynchronicity mode"] == 3, "Update Walltime (ms)"
            ],
            _group.loc[
                _group["asynchronicity mode"] == 0, "Update Walltime (ms)"
            ],
        )

        _res.append(
            {
                "ncpus": _ncpus,
                "exec": "dishtiny",
                "n": len(_group),
                "%": 100 * (_g2.mean() / _g1.mean() - 1),
                **dict(
                    zip(
                        ["wstat", "p"],
                        scipy_stats.wilcoxon(
                            _g1, _g2, alternative="two-sided"
                        ),
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
    _data = filtered_procs[filtered_procs["executable"] == "channel_selection"]
    for _ncpus, _group in _data.groupby("ncpus"):
        _g1, _g2 = (
            _group.loc[
                _group["asynchronicity mode"] == 3, "Update Walltime (ms)"
            ],
            _group.loc[
                _group["asynchronicity mode"] == 0, "Update Walltime (ms)"
            ],
        )

        _res.append(
            {
                "ncpus": _ncpus,
                "exec": "channel_selection",
                "n": len(_group),
                "%": 100 * (_g2.mean() / _g1.mean() - 1),
                **dict(
                    zip(
                        ["wstat", "p"],
                        scipy_stats.wilcoxon(
                            _g1, _g2, alternative="two-sided"
                        ),
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
                        0: "Graph Color Solution Error",
                    }[_i],
                    fontsize=11,
                )

        _g.axes[0, 0].set_ylabel("Best\nEffort")
        _g.axes[1, 0].set_ylabel("Global\nSync")

        for _ax in _g.axes[-1, :]:
            _ax.set_xlabel("Num Processes")
    return


@app.cell(hide_code=True)
def delimit_besteffort_sync_error(mo):
    mo.md(
        """
    ### Best-Effort vs. Synchronous: Graph Coloring Error

    Completing the best-effort vs. synchronous comparison with the third
    performance measure: graph coloring solution error (conflicts per
    cpu), reported at each problem size as above.
    """
    )
    return


@app.cell
def _(cliffs_delta, filtered_procs, pd, scipy_stats):
    _res = []
    _data = filtered_procs[filtered_procs["executable"] == "channel_selection"]
    for _ncpus, _group in _data.groupby("ncpus"):
        _g1, _g2 = (
            _group.loc[
                _group["asynchronicity mode"] == 3, "conflicts per cpu"
            ],
            _group.loc[
                _group["asynchronicity mode"] == 0, "conflicts per cpu"
            ],
        )

        _res.append(
            {
                "ncpus": _ncpus,
                "exec": "channel_selection",
                "n": len(_group),
                "%": 100 * (_g2.mean() / _g1.mean() - 1),
                **dict(
                    zip(
                        ["wstat", "p"],
                        scipy_stats.wilcoxon(
                            _g1, _g2, alternative="two-sided"
                        ),
                    )
                ),
                **dict(zip(["delta", "interp"], cliffs_delta(_g1, _g2))),
            },
        )

    pd.DataFrame(_res)
    return


@app.cell
def _(filtered_procs, mpl, np, pathlib, pd, plt, sns, tp):
    _long = filtered_procs.melt(
        id_vars=["ncpus", "asynchronicity mode", "executable"],
        value_vars=["Update Walltime (ms)", "conflicts per cpu"],
        var_name="metric",
        value_name="value",
    )
    _panels = pd.DataFrame(
        [
            {
                "executable": "dishtiny",
                "metric": "Update Walltime (ms)",
                "panel": "Digital Evo Walltime (ms)",
            },
            {
                "executable": "channel_selection",
                "metric": "Update Walltime (ms)",
                "panel": "Graph Color Walltime (ms)",
            },
            {
                "executable": "channel_selection",
                "metric": "conflicts per cpu",
                "panel": "Graph Color Solution Error",
            },
        ]
    )
    _long = _long.merge(_panels, on=["executable", "metric"])

    _col_order = [
        "Digital Evo Walltime (ms)",
        "Graph Color Walltime (ms)",
        "Graph Color Solution Error",
    ]

    with tp.teed(
        sns.relplot,
        data=_long,
        x="ncpus",
        y="value",
        col="panel",
        col_order=_col_order,
        hue="executable",
        row="asynchronicity mode",
        row_order=[3, 0],
        err_style=None,
        facet_kws=dict(margin_titles=True, sharey="col"),
        kind="line",
        legend=False,
        teeplot_show=True,
        teeplot_subdir=pathlib.Path(__file__).stem,
        teeplot_outattrs={"viz": "perf-quality-combined"},
        teeplot_outinclude=["viz"],
        teeplot_transparent=False,
    ) as _g:
        # annotations transferred from the two upstream per-metric figures;
        # flat order is row-major over (row=async mode, col=panel)
        _signif_grid = [
            ("**", "n.s."),
            ("***", "n.s."),
            ("n.s.", "n.s."),
            ("***", "***"),
            ("***", "***"),
            ("***", "***"),
        ]
        for _i, (_ax, (_signif1, _signif2)) in enumerate(
            zip(_g.axes.flat, _signif_grid)
        ):
            _panel = _col_order[_i % len(_col_order)]
            for _line in _ax.lines:
                _x, _y = _line.get_xydata().T
                _ax.fill_between(
                    _x, _y.min(), _y, color=_line.get_color(), alpha=0.2
                )

                if _panel == "Graph Color Solution Error":
                    _target_y = max(_y.max(), _y.min() + 10)
                else:
                    _target_y = max(_y.max(), _y.min() * 1.3, _y.min() + 0.7)
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
            y="value",
            color="k",
            errorbar="sd",
            err_style="bars",
            legend=False,
            lw=0,
        )

        _g.set(ylim=(0, None))
        _g.set(xscale="log")
        _g.figure.set_size_inches(9, 2)
        _g.set_titles(col_template="{col_name}", row_template="")
        plt.subplots_adjust(hspace=0.3)

        for _i, _ax in enumerate(_g.axes.flat):
            _ax.minorticks_off()
            _ax.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
            _ax.set_xticks([1, 4, 16, 64])
            _ax.set_ylabel("")

        for _ax in _g.axes[0, :]:
            _ax.set_title(_ax.get_title(), fontsize=11)

        _g.axes[0, 0].set_ylabel("Best\nEffort")
        _g.axes[1, 0].set_ylabel("Global\nSync")

        for _ax in _g.axes[-1, :]:
            _ax.set_xlabel("Num Processes")
    return


@app.cell
def _(filtered_procs, mpl, pathlib, pd, sns, tp):
    def _lighten(_c, _amt):
        _r, _g, _b = mpl.colors.to_rgb(_c)
        return (
            _r + (1 - _r) * _amt,
            _g + (1 - _g) * _amt,
            _b + (1 - _b) * _amt,
        )

    def _darken(_c, _amt):
        _r, _g, _b = mpl.colors.to_rgb(_c)
        return (_r * (1 - _amt), _g * (1 - _amt), _b * (1 - _amt))

    _long = filtered_procs.melt(
        id_vars=["ncpus", "asynchronicity mode", "executable"],
        value_vars=["Update Walltime (ms)", "conflicts per cpu"],
        var_name="metric",
        value_name="value",
    )
    _panels = pd.DataFrame(
        [
            {
                "executable": "dishtiny",
                "metric": "Update Walltime (ms)",
                "panel": "Digital Evo Walltime (ms)",
            },
            {
                "executable": "channel_selection",
                "metric": "Update Walltime (ms)",
                "panel": "Graph Color Walltime (ms)",
            },
            {
                "executable": "channel_selection",
                "metric": "conflicts per cpu",
                "panel": "Graph Color Solution Error",
            },
        ]
    )
    _long = _long.merge(_panels, on=["executable", "metric"])

    _col_order = [
        "Digital Evo Walltime (ms)",
        "Graph Color Walltime (ms)",
        "Graph Color Solution Error",
    ]

    # signif markers carried over from the two-row figure, keyed by
    # (panel, asynchronicity mode); first entry is the 1-64 delta and
    # the second is the 16-64 delta
    _signif_by_panel = {
        "Digital Evo Walltime (ms)": {0: ("***", "***"), 3: ("**", "n.s.")},
        "Graph Color Walltime (ms)": {0: ("***", "***"), 3: ("***", "n.s.")},
        "Graph Color Solution Error": {
            0: ("***", "***"),
            3: ("n.s.", "n.s."),
        },
    }

    _gray = "#c9c9c9"
    _green = "#67a353"

    with tp.teed(
        sns.relplot,
        data=_long,
        x="ncpus",
        y="value",
        col="panel",
        col_order=_col_order,
        hue="asynchronicity mode",
        hue_order=[0, 3],
        palette={0: _gray, 3: _green},
        err_style=None,
        facet_kws=dict(margin_titles=True, sharey="col"),
        kind="line",
        legend=False,
        teeplot_show=True,
        teeplot_subdir=pathlib.Path(__file__).stem,
        teeplot_outattrs={"viz": "perf-quality-delta-onerow"},
        teeplot_outinclude=["viz"],
        teeplot_transparent=False,
    ) as _g:
        for _i, _ax in enumerate(_g.axes.flat):
            _panel = _col_order[_i]

            # synchronous (mode 0) underneath in light gray, best-effort
            # (mode 3) overlaid in green, each underfilled down to its min
            _lines_y = []
            for _li, _line in enumerate(list(_ax.lines)):
                _x, _y = _line.get_xydata().T
                _ax.fill_between(
                    _x,
                    _y.min(),
                    _y,
                    color=(_gray, _green)[_li],
                    alpha=(0.55, 0.3)[_li],
                )
                _lines_y.append(_y)

            # delta sidebar to the right of the data: a vertical line per
            # mode with an open (bottom) and closed (top) dot tip, one
            # pair for the 1-64 delta and one for the 16-64 delta, each
            # annotated with the percent change rotated over the line.
            # positions are spaced geometrically so they read as evenly
            # spaced on the log x-axis
            for _li, _y in enumerate(_lines_y):
                _mode = (0, 3)[_li]
                _base = ("black", _green)[_li]
                _line_c = _lighten(_base, 0.5)
                _text_c = _darken(_base, 0.3)
                _signif1, _signif2 = _signif_by_panel[_panel][_mode]

                for _xpos, _ysrc, _signif in (
                    ((79, 126)[_li], _y[0], _signif1),
                    ((200, 316)[_li], _y[2], _signif2),
                ):
                    _lo, _hi = min(_ysrc, _y[3]), max(_ysrc, _y[3])
                    _pct = ((_y[3] - _ysrc) / abs(_ysrc)) * 100

                    _ax.plot(
                        [_xpos, _xpos],
                        [_lo, _hi],
                        color=_line_c,
                        lw=1.5,
                        solid_capstyle="butt",
                        zorder=5,
                        clip_on=False,
                    )
                    _ax.plot(
                        [_xpos],
                        [_lo],
                        marker="o",
                        ms=4.5,
                        markerfacecolor="white",
                        markeredgecolor=_line_c,
                        markeredgewidth=1.3,
                        zorder=6,
                        clip_on=False,
                    )
                    _ax.plot(
                        [_xpos],
                        [_hi],
                        marker="o",
                        ms=4.5,
                        markerfacecolor=_line_c,
                        markeredgecolor=_line_c,
                        markeredgewidth=1.3,
                        zorder=6,
                        clip_on=False,
                    )
                    _ax.text(
                        _xpos,
                        (_lo + _hi) / 2,
                        f"|+{_pct:.0f}%{_signif}",
                        rotation=90,
                        rotation_mode="anchor",
                        ha="center",
                        va="center",
                        color=_text_c,
                        fontsize=7,
                        zorder=7,
                        clip_on=False,
                    )

        _g.set(ylim=(0, None))
        _g.set(xscale="log")
        _g.figure.set_size_inches(9, 2)
        _g.set_titles(col_template="{col_name}", row_template="")

        for _ax in _g.axes.flat:
            _ax.minorticks_off()
            _ax.set_xlim(0.85, 380)
            _ax.set_xticks([1, 4, 16, 64, 100, 251])
            _ax.set_xticklabels(
                ["1", "4", "16", "64", "Δ\n1-64", "Δ\n16-64"],
            )
            _ax.set_ylabel("")
            _ax.set_xlabel("Num Processes")
            _ax.set_title(_ax.get_title(), fontsize=11)
    return


if __name__ == "__main__":
    app.run()
