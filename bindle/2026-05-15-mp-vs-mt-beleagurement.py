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
    from matplotlib import pyplot as plt
    import pandas as pd
    import requests
    import seaborn as sns
    from teeplot import teeplot as tp
    from watermark import watermark

    return mo, pd, plt, requests, sns, tp, watermark


@app.cell
def _():
    from conduitpylib.viz import _get_defaults as cfg

    from conduitpylib.viz import beleaguerment_facetplot, beleaguerment_regplot

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
    mo.md(
        """
    ## Prep Data
    """
    )
    return


@app.cell
def describe_data(pd, requests, retrieve_and_prepare_delta_dataframes):
    def apply(df: pd.DataFrame) -> pd.DataFrame:
        row_distiller = lambda row: {
            k: v for k, v in row.items() if k in ("Num Nodes", "Num Processes")
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    ## Example Plot
    """
    )
    return


@app.cell
def _(data, pathlib, plt, sns, tp, types):
    with tp.teed(
        sns.lmplot,
        data=data[data["Instrumentation"] == "Longitudinal"],
        x="Messages Received Per Second",
        y="Messages Sent Per Second",
        hue="Multiprocessing",
        teeplot_show=True,
        teeplot_subdir=pathlib.Path(__file__).stem,
    ) as g:
        ax = g.axes.flat[0]
        sns.move_legend(
            g,
            "lower center",
            bbox_to_anchor=(0.5, 1),
            ncol=2,
            title=None,
            frameon=False,
        )
        g.set(xlabel="Sent per Second", ylabel="Recv per Second")
        g.set(xlim=(0, None), ylim=(0, None))
        g.figure.set_size_inches(5, 2)
        ax.set_aspect("equal", adjustable="box")
        plt.ticklabel_format(axis="both", style="sci", scilimits=(0, 0))
        ax.axline((0, 0), (1, 1), color="k", ls=":")
        ax.xaxis.get_offset_text().offset_text_position = "top"

        # adapted from https://stackoverflow.com/a/47381719/17332200
        pad = (
            plt.rcParams["xtick.major.size"] + plt.rcParams["xtick.major.pad"]
        )

        def bottom_offset(self, bboxes, bboxes2):
            bottom = self.axes.bbox.ymin
            self.offsetText.set(va="top", ha="left")
            oy = bottom - pad * self.figure.dpi / 72.0
            self.offsetText.set_position((1, oy))

        ax.xaxis._update_offset_text_position = types.MethodType(
            bottom_offset, ax.xaxis
        )

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
