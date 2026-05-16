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
    import seaborn as sns
    from teeplot import teeplot as tp
    from watermark import watermark

    return mo, np, pd, plt, requests, sns, tp, watermark


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
def _(requests):
    with open("/tmp/4ys9v", "wb") as fp:
        fp.write(
            requests.get(
                "https://osf.io/download/4ys9v", allow_redirects=True
            ).content,
        )
    return


@app.cell
def _(pd):
    data = pd.read_csv("/tmp/aum7w", compression="gzip")
    data
    return (data,)


@app.cell
def _(data, pd):
    group_cols = ["SLURM_NNODES", "Replicate", "proc"]
    value_cols = ["Num Pulls Attempted", "Row Final Timepoint (ns)"]

    diffs = data.groupby(group_cols)[value_cols].diff().add_suffix(" Diff")

    result = pd.concat(
        [data[[*group_cols, "Row Final Timepoint (ns)"]], diffs], axis=1
    )

    result["Row Final Timepoint (ns) Rel"] = result[
        "Row Final Timepoint (ns)"
    ] - result.groupby(group_cols)["Row Final Timepoint (ns)"].transform("min")

    result["Updates per Sec"] = (
        result["Num Pulls Attempted Diff"]
        / result["Row Final Timepoint (ns) Diff"]
        * 10**9
    )

    result["rank"] = result.groupby(group_cols)[
        "Row Final Timepoint (ns)"
    ].transform("rank")

    result
    return group_cols, result


@app.cell
def _(group_cols, np, pathlib, pd, plt, result, sns, tp):
    newdf = pd.DataFrame(np.repeat(result.values, 2, axis=0))
    newdf.columns = result.columns

    newdf["rank2"] = newdf.groupby(group_cols).cumcount() - 2

    newdf["special"] = newdf["Replicate"].isin([1, 4, 6, 9])

    newdf["rank3"] = newdf["rank2"].replace(
        {i: (i // 4) * 40 + [0, 8, 9, 39][i % 4] for i in range(25)}
    )

    newdf["rp"] = newdf["Replicate"].astype(str) + newdf["proc"].astype(str)

    with tp.teed(
        sns.relplot,
        data=newdf[newdf["SLURM_NNODES"] == 1],
        x="rank3",
        y="Updates per Sec",
        row="special",
        hue="special",
        row_order=[True, False],
        errorbar=("pi", 100),
        kind="line",
        # estimator=None,
        sort=True,
        legend=False,
        err_kws=dict(alpha=0.4, lw=2),
        lw=0,
        palette=["#EFB743", "#A1331C"],
        teeplot_show=True,
        teeplot_subdir=pathlib.Path(__file__).stem,
    ) as _g:
        _g.set(ylim=(0, None))
        _g.figure.set_size_inches(3, 2)
        _g.set_titles("")

        _g.map_dataframe(
            sns.scatterplot,
            x="rank3",
            y="Updates per Sec",
            # hue="special",
            # dashes=[(1, 0)],
            marker=".",
            size=0.1,
            # linewidth=0.3,
            legend=None,
            # estimator=None,
            # style="proc",
            color="black",
            # sort=True,
        )

        for _ax in _g.axes.flat:
            for i in (0, 40, 80, 120, 160, 200):
                _ax.axvspan(
                    0 + i, 8.5 + i, color="gray", alpha=0.08, zorder=-1
                )

        plt.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        _g.axes.flat[0].set_ylabel("")
        _g.axes.flat[1].set_ylabel("               Updates per Sec")

        _g.set(
            xlabel="Time", xticklabels=[], xticks=[4, 44, 84, 124, 164, 204]
        )

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
