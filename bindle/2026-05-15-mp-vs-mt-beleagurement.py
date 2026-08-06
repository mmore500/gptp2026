import marimo

__generated_with = "0.23.2"
app = marimo.App(width="full")


@app.cell
def import_std():
    import pathlib
    import types

    return pathlib, types


@app.cell
def import_pkg():
    import marimo as mo
    import matplotlib as mpl
    from matplotlib import pyplot as plt
    import pandas as pd
    import requests
    from scipy import stats as scipy_stats
    import seaborn as sns
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from teeplot import teeplot as tp
    from watermark import watermark

    return mo, mpl, pd, plt, requests, scipy_stats, sm, smf, sns, tp, watermark


@app.cell
def _():
    from conduitpylib.wrangle import (
        retrieve_and_prepare_delta_dataframes,
        wrangle_instrumentation_longform,
    )

    return (
        retrieve_and_prepare_delta_dataframes,
        wrangle_instrumentation_longform,
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
    mo.md("""
    ## Prep Data
    """)
    return


@app.cell
def describe_data(pd, requests, retrieve_and_prepare_delta_dataframes):
    def apply(df: pd.DataFrame) -> pd.DataFrame:
        def row_distiller(row):
            return {
                k: v
                for k, v in row.items()
                if k in ("Num Nodes", "Num Processes")
            }

        df["Multiprocessing"] = df.apply(
            lambda row: {
                frozenset(
                    {"Num Nodes": 1, "Num Processes": 2}.items()
                ): "Intranode",
                frozenset(
                    {"Num Nodes": 2, "Num Processes": 2}.items()
                ): "Internode",
            }[frozenset(row_distiller(row).items())],
            axis=1,
        )
        return df

    with open("/tmp/4ys9v", "wb") as fp:
        fp.write(
            requests.get(
                "https://osf.io/download/4ys9v", allow_redirects=True
            ).content,
        )

    with open("/tmp/aum7w", "wb") as fp:
        fp.write(
            requests.get(
                "https://osf.io/download/aum7w", allow_redirects=True
            ).content,
        )

    longitudinal_df, snapshot_df = retrieve_and_prepare_delta_dataframes(
        df_inlet_url="/tmp/4ys9v",
        df_outlet_url="/tmp/aum7w",
        apply=apply,
        treatment_column="Multiprocessing",
    )
    return longitudinal_df, snapshot_df


@app.cell
def peek_data(longitudinal_df, snapshot_df, wrangle_instrumentation_longform):
    data = wrangle_instrumentation_longform(
        longitudinal_df=longitudinal_df,
        snapshot_df=snapshot_df,
    )
    data
    return (data,)


@app.cell
def _(data):
    data["Hostname"].unique()
    return


@app.cell
def _(data, pd):
    data_ = data.copy().reset_index(drop=True)
    data_["indexx"] = data_.index
    df_long = data_.melt(
        id_vars=[
            "Instrumentation",
            "Multiprocessing",
            "indexx",
            "Execution Instance UUID",
            "Hostname",
            "proc",
            "Replicate",
        ],
        value_vars=[
            "Messages Received Per Second",
            "Messages Sent Per Second",
        ],
        var_name="Message Type",
        value_name="Count Per Second",
    )
    df_long["Type"] = pd.Categorical(
        df_long["Message Type"].replace(
            {
                "Messages Sent Per Second": "Sent        ",
                "Messages Received Per Second": "        Recv",
            },
        ),
        categories=["        Recv", "Sent        "],
        ordered=True,
    )
    return (df_long,)


@app.cell
def _():
    palette = {
        "lac-361": "#EFB743",
        "lac-221": "#E72F52",
        "lac-220": "#0D95D0",
    }
    return (palette,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Helpers
    """)
    return


@app.cell
def _(plt):
    # # adapted from https://stackoverflow.com/a/47381719/17332200
    def bottom_offset(self, bboxes, bboxes2):
        pad = (
            plt.rcParams["xtick.major.size"] + plt.rcParams["xtick.major.pad"]
        )
        self.offsetText.set(va="top", ha="left")
        _oy = self.axes.bbox.ymin - pad * self.figure.dpi / 72.0
        self.offsetText.set_position((1, _oy))

    return (bottom_offset,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Example Plot
    """)
    return


@app.cell
def _(bottom_offset, data, pathlib, plt, sns, tp, types):
    with tp.teed(
        sns.lmplot,
        data=data[data["Instrumentation"] == "Longitudinal"],
        x="Messages Received Per Second",
        y="Messages Sent Per Second",
        hue="Multiprocessing",
        teeplot_show=True,
        teeplot_subdir=pathlib.Path(__file__).stem,
    ) as _g:
        _ax = _g.axes.flat[0]
        sns.move_legend(
            _g,
            "lower center",
            bbox_to_anchor=(0.5, 1),
            ncol=2,
            title=None,
            frameon=False,
        )
        _g.set(xlabel="Sent per Second", ylabel="Recv per Second")
        _g.set(xlim=(0, None), ylim=(0, None))
        _g.figure.set_size_inches(5, 2)
        _ax.set_aspect("equal", adjustable="box")
        plt.ticklabel_format(axis="both", style="sci", scilimits=(0, 0))
        _ax.axline((0, 0), (1, 1), color="k", ls=":")
        _ax.xaxis.get_offset_text().offset_text_position = "top"

        # adapted from https://stackoverflow.com/a/47381719/17332200
        _ax.xaxis._update_offset_text_position = types.MethodType(
            bottom_offset, _ax.xaxis
        )
    return


@app.cell
def _(bottom_offset, data, pathlib, plt, sns, tp, types):
    with tp.teed(
        sns.lmplot,
        data=data[data["Instrumentation"] == "Longitudinal"],
        x="Messages Received Per Second",
        y="Num Try Puts Attempted",
        hue="Multiprocessing",
        teeplot_show=True,
        teeplot_subdir=pathlib.Path(__file__).stem,
    ) as _g:
        _ax = _g.axes.flat[0]
        sns.move_legend(
            _g,
            "lower center",
            bbox_to_anchor=(0.5, 1),
            ncol=2,
            title=None,
            frameon=False,
        )
        _g.set(xlabel="Updates Elapsed", ylabel="Recv per Second")
        _g.set(xlim=(0, None), ylim=(0, None))
        _g.figure.set_size_inches(5, 2)
        plt.ticklabel_format(axis="both", style="sci", scilimits=(0, 0))
        _ax.xaxis.get_offset_text().offset_text_position = "top"
        _ax.xaxis._update_offset_text_position = types.MethodType(
            bottom_offset, _ax.xaxis
        )
    return


@app.cell
def _(data):
    replicates = data[data["Messages Received Per Second"] > 2e5]["Replicate"]
    replicates
    return


@app.cell
def _(df_long, mpl, palette, pathlib, plt, sns, tp):
    df_long["special"] = df_long["Replicate"].isin([1, 4, 6, 9])
    with tp.teed(
        sns.relplot,
        data=df_long[df_long["Instrumentation"] == "Longitudinal"],
        x="Type",
        y="Count Per Second",
        col="Multiprocessing",
        col_order=[" Intranode ", "Internode"],
        style="indexx",
        hue="Hostname",
        alpha=0.5,
        kind="line",
        legend=False,
        palette=palette,
        teeplot_show=True,
        teeplot_subdir=pathlib.Path(__file__).stem,
    ) as _g:
        _ax = _g.axes.flat[0]
        sns.lineplot(
            data=df_long[
                (df_long["Instrumentation"] == "Longitudinal")
                & (df_long["Multiprocessing"] == "Intranode")
            ],
            x="Type",
            y="Count Per Second",
            style="indexx",
            hue="special",
            alpha=0.5,
            ax=_ax,
            legend=False,
            palette=["#EFB743", "#A1331C"],
        )
        _g.set_titles(template="{col_name}")
        _g.set(ylim=(0, None), ylabel="Message per Sec", xlabel=None)
        plt.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        _g.figure.set_size_inches(2.5, 1.3)
        _ax.yaxis.get_offset_text().set_x(-0.2)

        # Left facet legend — NUMA symmetry, bottom
        _ax0 = _g.axes.flat[0]
        _numa_handles = [
            mpl.patches.Patch(color="#EFB743", label="NUMA-\nSymmetric"),
            mpl.patches.Patch(color="#A1331C", label="NUMA-\nAsymmetric"),
        ]
        _ax0.legend(
            handles=_numa_handles,
            loc="lower center",
            ncol=1,
            frameon=False,
            fontsize="x-small",
        )

        # Right facet legend — Hostname, top
        _ax1 = _g.axes.flat[1]
        _hostname_colors = [palette[h] for h in ["lac-220", "lac-221"]]
        _host_handles = [
            mpl.patches.Patch(color=_hostname_colors[0], label="lac-220"),
            mpl.patches.Patch(color=_hostname_colors[1], label="lac-221"),
        ]
        _ax1.legend(
            handles=_host_handles,
            loc="lower center",
            ncol=1,
            frameon=False,
            fontsize="x-small",
        )
    return


@app.cell
def _(data, sm, smf):
    _data = data[
        (data["Instrumentation"] == "Longitudinal")
        & (data["Multiprocessing"] == "Intranode")
    ]
    _data["received"] = _data["Messages Received Per Second"]
    _data["sent"] = _data["Messages Sent Per Second"]

    _model = smf.glm(
        formula="sent ~ received", data=_data, family=sm.families.Gaussian()
    ).fit()

    print(_model.summary())
    return


@app.cell
def _(data, mo, palette, pathlib, plt, scipy_stats, sns, tp):
    data["Updates per Second"] = 1 / data["Simstep Period Inlet (s)"]
    _data = data[
        (data["Instrumentation"] == "Longitudinal")
        & (data["Multiprocessing"] == "Internode")
    ]
    with tp.teed(
        sns.catplot,
        data=_data,
        y="Updates per Second",
        hue="Hostname",
        x="Hostname",
        kind="box",
        legend=False,
        notch=True,
        order=["lac-220", "lac-221"],
        palette=palette,
        teeplot_show=True,
        teeplot_subdir=pathlib.Path(__file__).stem,
    ) as _g:
        _ax = _g.axes.flat[0]
        _g.set_titles(template="{col_name}")
        _g.set(ylabel="Updates per Sec", xlabel=None)
        plt.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        _g.figure.set_size_inches(1, 2)
        _ax.yaxis.get_offset_text().set_x(-0.2)
        _ax.set_xticklabels(["lac\n220", "lac\n221"])

    _pivot = _data.pivot(
        index="Execution Instance UUID",
        columns="Hostname",
        values="Updates per Second",
    )

    for x in [
        _pivot,
        _pivot.mean(),
        _pivot.std(),
        scipy_stats.wilcoxon(_pivot["lac-221"], _pivot["lac-220"]),
    ]:
        mo.output.append(x)
    return


@app.cell
def _(data, mo, palette, pathlib, plt, scipy_stats, sns, tp):
    data["ms per Update"] = data["Simstep Period Inlet (s)"] * 1000
    _data2 = data[
        (data["Instrumentation"] == "Longitudinal")
        & (data["Multiprocessing"] == "Internode")
    ]
    with tp.teed(
        sns.catplot,
        data=_data2,
        y="ms per Update",
        hue="Hostname",
        x="Hostname",
        kind="box",
        legend=False,
        notch=True,
        order=["lac-220", "lac-221"],
        palette=palette,
        teeplot_show=True,
        teeplot_subdir=pathlib.Path(__file__).stem,
    ) as _g:
        _ax = _g.axes.flat[0]
        _g.set_titles(template="{col_name}")
        _g.set(ylabel="ms per Update", xlabel=None)
        plt.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        _g.figure.set_size_inches(0.8, 1.5)
        _ax.yaxis.get_offset_text().set_x(-0.2)
        _ax.set_xticklabels(["lac\n220", "lac\n221"])

    _pivot2 = _data2.pivot(
        index="Execution Instance UUID",
        columns="Hostname",
        values="ms per Update",
    )

    for _x in [
        _pivot2,
        _pivot2.mean(),
        _pivot2.std(),
        scipy_stats.wilcoxon(_pivot2["lac-221"], _pivot2["lac-220"]),
    ]:
        mo.output.append(_x)
    return


@app.cell
def _(data, sm, smf):
    _data = data[
        (data["Instrumentation"] == "Longitudinal")
        & (data["Multiprocessing"] == "Internode")
    ]
    _data["received"] = _data["Messages Received Per Second"]
    _data["sent"] = _data["Messages Sent Per Second"]

    _model = smf.glm(
        formula="sent ~ received",
        data=_data,
        family=sm.families.Gaussian(),
    ).fit()

    print(_model.summary())
    return


@app.cell
def _(data, sm, smf):
    _data = data[
        (data["Instrumentation"] == "Longitudinal")
        & (data["Multiprocessing"] == "Internode")
    ]
    _data["received"] = _data["Messages Received Per Second"]
    _data["sent"] = _data["Messages Sent Per Second"]

    _model = smf.glm(
        formula="sent ~ received + C(Hostname)",
        data=_data,
        family=sm.families.Gaussian(),
    ).fit()

    print(_model.summary())
    return


if __name__ == "__main__":
    app.run()
