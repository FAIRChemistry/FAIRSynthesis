# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.11.14",
#     "numpy==2.2.4",
#     "polars==1.26.0",
#     "pandas==2.2.3",
#     "matplotlib==3.10.1",
#     "scipy==1.15.2",
#     "pybaselines==1.2.0",
#     "seaborn==0.13.2",
# ]
# ///

import marimo

__generated_with = "0.12.5"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# PXRD Analysis""")
    return


@app.cell
def _(clear_files_button, mo):
    clear_files_button.value
    ui_files_samples = mo.ui.file(kind="area", multiple=True)
    ui_files_pure = mo.ui.file(kind="area", multiple=True)
    ui_files_blank = mo.ui.file(kind="area", multiple=True)
    ui_file_jxdl = mo.ui.file()
    return ui_file_jxdl, ui_files_blank, ui_files_pure, ui_files_samples


@app.cell
def _(ui_files_blank, ui_files_pure, ui_files_samples):
    files_samples = {_.name: _.contents for _ in ui_files_samples.value}
    files_pure = {_.name: _.contents for _ in ui_files_pure.value}
    files_blank = {_.name: _.contents for _ in ui_files_blank.value}
    return files_blank, files_pure, files_samples


@app.cell
def _(mo):
    mo.md(r"""## 0. Import""")
    return


@app.cell
def _(mo):
    clear_files_button = mo.ui.button(label="Clear", kind="danger")
    return (clear_files_button,)


@app.cell
def _(Path, mo):
    def file_picker(_ui_files):
        _file_format = mo.md(
            f"""
            /// details | **File format**
                type: info

            The uploaded files schould each provide two columns. 
            The first column features the angle in the form of $2 \\theta / °$, the second column includes the information about CPS intensity.
            An example file can be downloaded here: {mo.download(Path("public/PXRD_KE-163.xyd").read_text(), "example.csv")}
            ///
            """
        )
        if not _ui_files.value:
            _ = mo.vstack([_ui_files, _file_format])
        else:
            _ = mo.md(f"""
            /// details | **Change files**
                type: info
            {_ui_files}

            {_file_format}
            """)
        return _
    return (file_picker,)


@app.cell
def _(
    clear_files_button,
    file_picker,
    mo,
    ui_file_jxdl,
    ui_files_blank,
    ui_files_pure,
    ui_files_samples,
):
    clear_files_button.value
    _ = mo.md(f"""
    ### 0.1 PXRD Measurement Samples
    {file_picker(ui_files_samples)}

    ### 0.2 Pure Component PXRD Measurements
    {file_picker(ui_files_pure)}

    ### 0.3 Blank PXRD Measurements
    {file_picker(ui_files_blank)}

    ### 0.4 JXDL File
    Upload the JXDL file here: {ui_file_jxdl}

    """)
    _file_ui = [
        ui_files_samples.value,
        ui_files_pure.value,
        ui_files_blank.value,
        ui_file_jxdl.value,
    ]


    def any_file(file_ui=[ui_files_samples, ui_files_pure, ui_files_blank, ui_file_jxdl]):
        if isinstance(file_ui, mo.ui.file):
            return True if file_ui.value else False

        return any([_file_ui.value for _file_ui in file_ui])


    def all_files(file_ui=[ui_files_samples, ui_files_pure, ui_files_blank, ui_file_jxdl]):
        if isinstance(file_ui, mo.ui.file):
            return True if file_ui.value else False

        return all([_file_ui.value for _file_ui in file_ui])


    if not all_files():
        _ = _
    else:
        _ = mo.md(
            f"""
            /// details | **File pickers** {clear_files_button}
                type: info

            {_}
            ///
            """
        )
    _
    return all_files, any_file


@app.cell
def _(baseline_correction, dataclass, io, normalization, np, pl):
    @dataclass
    class PXRDMeasurement:
        filename: str
        content: bytes
        type: str | None = None

        @property
        def data(self):
            _ = pl.from_numpy(
                np.loadtxt(io.StringIO(self.content.decode("utf-8"))),
                schema=["angle", self.filename],
            )
            if type == "Co-Kα1":
                col_names = _.columns
                _ = _.select(
                    pl.col(_.columns[0]),
                    (
                        2
                        * (
                            1.540562
                            / 1.788965
                            * (np.pi / 180 * pl.col(_.columns[1]) / 2).sin()
                        ).arcsin()
                        * 180
                        / np.pi
                    ).alias(_.columns[1]),
                )
            return _

        @classmethod
        def dict_from_marimo_file(cls, marimo_file):
            return {_.name: cls(_.name, _.contents) for _ in marimo_file.value}


    class BlankMeasurement(PXRDMeasurement):
        pass


    class PureProduct(PXRDMeasurement):
        @property
        def background_subtraction(self):
            return background_subtraction(self)

        @property
        def normalized(self):
            return normalization(self)

        @property
        def corrected(self):
            return baseline_correction(self)


    class SampleProduct(PXRDMeasurement):
        pure_products: list[PureProduct]
        blank_measurement: BlankMeasurement
        jxdl: dict

        def __init__(
            self,
            filename,
            content,
            pure_products,
            blank_measurement,
            jxdl,
            type=None,
        ):
            self.filename = filename
            self.content = content
            if blank_measurement:
                blank_measurement.type = type
            for _ in pure_products:
                _.type = type
                _.blank_measurement = blank_measurement
            self.pure_products = pure_products
            self.blank_measurement = blank_measurement
            self.jxdl = jxdl
            self.type = type

        @property
        def background_subtraction(self):
            return background_subtraction(self)

        @property
        def normalized(self):
            return normalization(self)

        @property
        def corrected(self):
            return baseline_correction(self)

        @property
        def composition(self):
            return composition(self)

        @classmethod
        def dict_from_marimo_file_and_guess(
            cls, marimo_file, jxdl, pure_prducts_dict, blank_measurements_dict
        ):
            return {_.name: cls(_.name, _.contents) for _ in marimo_file.value}
    return BlankMeasurement, PXRDMeasurement, PureProduct, SampleProduct


@app.cell
def _(
    BlankMeasurement,
    PXRDMeasurement,
    PureProduct,
    any_file,
    jxdl_filtered,
    mo,
    ui_files_blank,
    ui_files_pure,
    ui_files_samples,
):
    mo.stop(
        not any_file(ui_files_samples),
        output=mo.md("""
            /// warning | **No files uploaded**
            Actions will be performed as soon as files are uploaded.
            ///
    """),
    )

    blank_measurements = BlankMeasurement.dict_from_marimo_file(ui_files_blank)
    pure_products = PureProduct.dict_from_marimo_file(ui_files_pure)
    sample_products_empty = PXRDMeasurement.dict_from_marimo_file(ui_files_samples)
    for _key, _val in sample_products_empty.items():
        _jxdl_key = [_ for _ in jxdl_filtered.keys() if _ in _key][0]
        _cu_co = [_ for _ in ["Cu", "Co"] if _ in _key]
        _cu_co = _cu_co[0] if _cu_co else None
        _blank = [
            _
            for _ in blank_measurements.keys()
            if _.replace("PXRD_Blank_", "").replace(".xyd", "") in _key
        ]
        _blank = _blank[0] if _blank else None
        _pure = [
            _
            for _ in pure_products.keys()
            if _blank.replace("PXRD_Blank_", "").replace(".xyd", "") in _
        ]
        _val.ui = {
            "Cu": mo.ui.dropdown(["Cu", "Co"], value=_cu_co),
            "blank": mo.ui.dropdown(blank_measurements, value=_blank),
            "pure": mo.ui.multiselect(pure_products, value=_pure),
            "jxdl_entry": mo.ui.dropdown(jxdl_filtered, value=_jxdl_key),
        }
    return blank_measurements, pure_products, sample_products_empty


@app.cell
def _(json, ui_file_jxdl):
    jxdl = json.loads(ui_file_jxdl.value[0].contents.decode("utf8"))
    return (jxdl,)


@app.cell
def _(jxdl):
    jxdl_filtered = {
        _["Metadata"]["_description"]: _["Procedure"]["Step"]
        for _ in jxdl["XDL"]["Synthesis"]
    }
    return (jxdl_filtered,)


@app.cell
def _(mo, sample_products_empty):
    ui_selected_samples = mo.ui.table(
        [
            {
                "key": key,
                "X-Ray Source": val.ui["Cu"],
                "Blank Measurement": val.ui["blank"],
                "Pure Components": val.ui["pure"],
                "JXDL": val.ui["jxdl_entry"],
            }
            for key, val in sample_products_empty.items()
        ],
        initial_selection=list(range(len(sample_products_empty))),
        page_size=50,
        freeze_columns_left=["key"],
    )
    ui_selected_samples
    return (ui_selected_samples,)


@app.cell
def _(SampleProduct, mo, sample_products_empty, ui_selected_samples):
    mo.stop(
        not ui_selected_samples.value,
        output=mo.md(
            """
            /// warning | **No samples selected**
            Actions will be performed as soon as selection includes at least one entry.
            ///
            """
        ),
    )

    sample_products = {}
    for _ui in ui_selected_samples.value:
        _key = _ui["key"]
        _old_sample = sample_products_empty[_key]
        sample_products |= {
            _key: SampleProduct(
                filename=_key,
                content=_old_sample.content,
                pure_products=_old_sample.ui["pure"].value,
                blank_measurement=_old_sample.ui["blank"].value,
                jxdl=_old_sample.ui["jxdl_entry"].value,
                type=_old_sample.ui["Cu"].value,
                # _old_sample.
            )
        }
    return (sample_products,)


@app.cell
def _(mo):
    ui_background_file = mo.ui.file()
    mo.md(
        f"""
        ## 1. Background Subtraction
        """
    )
    return (ui_background_file,)


@app.cell
def _(pl):
    def background_subtraction(sample):
        return (
            (
                sample.data.join(
                    sample.blank_measurement.data, on="angle", how="inner", coalesce=True
                )
                .with_columns(
                    [
                        (pl.col(_key) - pl.col(sample.blank_measurement.filename)).alias(
                            _key
                        )
                        for _key in sample.data.columns
                        if _key != "angle"
                    ]
                )
                .drop(sample.blank_measurement.filename)
            )
            if sample.blank_measurement
            else sample.data
        )
    return (background_subtraction,)


@app.cell
def _(mo, sample_products):
    sample_selected_for_plot = mo.ui.multiselect(
        sample_products, value=[list(sample_products.values())[0].filename]
    )
    return (sample_selected_for_plot,)


@app.cell
def _(mo, plt, sample_selected_for_plot):
    _fig, _ax = plt.subplots(1, 2, figsize=(12, 5))
    for _val in sample_selected_for_plot.value:
        _ax[0].plot(
            _val.data.to_numpy()[:, 0],
            _val.data.to_numpy()[:, 1],
        )
        _ax[1].plot(
            _val.background_subtraction.to_numpy()[:, 0],
            _val.background_subtraction.to_numpy()[:, 1],
        )
    _ax[0].set_title("Before")
    _ax[1].set_title("After")
    for _ax_ in _ax:
        _ax_.set_xlabel("angle")
        _ax_.set_ylabel("intensity")

    mo.vstack([sample_selected_for_plot, _fig])
    return


@app.cell
def _(mo):
    mo.md(r"""## 2. Normalization""")
    return


@app.cell
def _(mo):
    ui_normalization_cu_reset = mo.ui.button(label="Reset", kind="danger")
    ui_normalization_co_reset = mo.ui.button(label="Reset", kind="danger")
    return ui_normalization_co_reset, ui_normalization_cu_reset


@app.cell(hide_code=True)
def _(mo, ui_normalization_cu_reset):
    _ = ui_normalization_cu_reset.value
    ui_normalization_cu_range_start = mo.ui.number(start=0, stop=180, step=0.1, value=38)
    ui_normalization_cu_range_end = mo.ui.number(start=0, stop=180, step=0.1, value=40)

    mo.md(
        f"""
        For normalization, of Cu X-Ray source the intensity data between 
        {ui_normalization_cu_range_start}° and {ui_normalization_cu_range_end}°.
        {ui_normalization_cu_reset}
        """
    )
    return ui_normalization_cu_range_end, ui_normalization_cu_range_start


@app.cell(hide_code=True)
def _(mo, ui_normalization_co_reset):
    _ = ui_normalization_co_reset.value
    ui_normalization_co_range_start = mo.ui.number(start=0, stop=180, step=0.1, value=1.5)
    ui_normalization_co_range_end = mo.ui.number(start=0, stop=180, step=0.1, value=1.8)

    mo.md(
        f"""
        For normalization, of Co X-Ray source the intensity data between 
        {ui_normalization_co_range_start}° and {ui_normalization_co_range_end}°.
        {ui_normalization_co_reset}
        """
    )
    return ui_normalization_co_range_end, ui_normalization_co_range_start


@app.cell
def _(
    pl,
    ui_normalization_co_range_end,
    ui_normalization_co_range_start,
    ui_normalization_cu_range_end,
    ui_normalization_cu_range_start,
):
    def normalization(sample):
        _data = sample.background_subtraction

        _norm = None
        if sample.type == "Cu":
            _norm = [
                ui_normalization_cu_range_start.value,
                ui_normalization_cu_range_end.value,
            ]
        elif sample.type == "Co":
            _norm = [
                ui_normalization_co_range_start.value,
                ui_normalization_co_range_end.value,
            ]

        return _data.with_columns(
            [
                (
                    pl.col(_key)
                    / pl.col(_key)
                    .filter(pl.col("angle").is_between(_norm[0], _norm[1]))
                    .mean()
                ).alias(_key)
                for _key in _data.columns
                if _key != "angle"
            ]
        )
    return (normalization,)


@app.cell
def _(mo, plt, sample_selected_for_plot):
    _fig, _ax = plt.subplots(1, 2, figsize=(12, 5))
    for _val in sample_selected_for_plot.value:
        _ax[0].plot(
            _val.background_subtraction.to_numpy()[:, 0],
            _val.background_subtraction.to_numpy()[:, 1],
        )
        _ax[1].plot(_val.normalized.to_numpy()[:, 0], _val.normalized.to_numpy()[:, 1])
    _ax[0].set_title("Before")
    _ax[1].set_title("After")
    for _ax_ in _ax:
        _ax_.set_xlabel("angle")
        _ax_.set_ylabel("intensity")

    mo.vstack([sample_selected_for_plot, _fig])
    return


@app.cell
def _(mo):
    _ = mo.md(r"""## 3. Baseline Determination and Peak Detection""")
    _
    return


@app.cell
def _(Baseline, np):
    # baseline determination can be performed using diffrent algorithms and parameters
    # if baselines do not fit your problem, try tweaking the parameters in baseline_fitter.snip
    # or use a different algorithm from the pybaselines package


    def _baseline_determination(x, y):
        _bool = np.isnan(y)
        _y_org = y.copy()
        y = y[~np.isnan(y)].copy()
        baseline_fitter = Baseline(x_data=x[~_bool])
        base, _ = baseline_fitter.snip(
            y, max_half_window=40, decreasing=True, smooth_half_window=3
        )
        y_detrend = np.ones_like(x) * np.nan
        y_detrend[~_bool] = y - base
        return y_detrend


    def baseline_correction(sample):
        _data = sample.normalized
        return _data.with_columns(
            **{
                _key: _baseline_determination(
                    _data["angle"].to_numpy(),
                    _data[_key].to_numpy(),
                )
                for _key in _data.columns[1:]
            }
        )
    return (baseline_correction,)


@app.cell
def _(mo, plt, sample_selected_for_plot):
    _fig, _ax = plt.subplots(1, 2, figsize=(12, 5))
    for _val in sample_selected_for_plot.value:
        _ax[0].plot(_val.normalized.to_numpy()[:, 0], _val.normalized.to_numpy()[:, 1])
        if len(sample_selected_for_plot.value) <= 1:
            _ax[0].plot(
                _val.corrected.to_numpy()[:, 0],
                _val.normalized.to_numpy()[:, 1] - _val.corrected.to_numpy()[:, 1],
            )
        _ax[1].plot(
            _val.corrected.to_numpy()[:, 0],
            _val.corrected.to_numpy()[:, 1],
        )
    _ax[0].set_title("Before")
    _ax[1].set_title("After")
    for _ax_ in _ax:
        _ax_.set_xlabel("angle")
        _ax_.set_ylabel("intensity")

    mo.vstack([sample_selected_for_plot, _fig])
    return


@app.cell
def _(mo):
    mo.md(r"""## 4. Analysis""")
    return


@app.cell
def _(mo):
    mo.md(r"""### 4.1. Composition""")
    return


@app.cell(hide_code=True)
def _():
    # peaks = {}
    # for _key in data_normalized.columns[1:]:
    #    _peak, _data = sp.signal.find_peaks(
    #        data_detrend[_key],
    #        height=data_detrend[_key].max() / 40,
    #        width=0.05 * len(data_detrend["angle"]) / data_detrend["angle"].max(),
    #        prominence=data_detrend[_key].max() / 40,
    #    )
    #    _integral = [
    #        np.trapezoid(
    #            data_detrend[_key].to_numpy()[
    #                _data["left_bases"][i] : _data["right_bases"][i]
    #            ],
    #            x=data_detrend["angle"].to_numpy()[
    #                _data["left_bases"][i] : _data["right_bases"][i]
    #            ],
    #        )
    #        for i in range(len(_peak))
    #    ]
    #    _y = data_detrend[_key].to_numpy()
    #    _x = data_detrend["angle"].to_numpy()[~np.isnan(_y)]
    #    _y = _y[~np.isnan(_y)]
    #    _tot_trapz = np.trapezoid(
    #        _y,
    #        x=_x,
    #    )
    #    print(_tot_trapz)
    #    _purity = [_integral[i] / _tot_trapz for i in range(len(_peak))]
    #    peaks[_key] = {"peaks": _peak, "integral": _integral, "purity": _purity}
    #
    # hide(mo.vstack([table(data_detrend), peaks]), label="Show Data")
    return


@app.cell(hide_code=True)
def _():
    # ui_col = mo.ui.dropdown(data_detrend.columns[1:], value=data_detrend.columns[1])
    # ui_col
    return


@app.cell(hide_code=True)
def _():
    # mo.stop(not ui_col.value)
    #
    # _fig, _ax = plt.subplots()
    # _fig2, _ax2 = plt.subplots()
    ## drop nans
    ## _ax.plot(data_normalized["angle"], _data_detrend)
    # for _ in [_ax, _ax2]:
    #    _.set_xlim((0, 15))
    #
    # _val = ui_col.value
    #
    # _ax.plot(data_normalized["angle"], data_normalized[_val])
    # _ax2.plot(data_detrend["angle"], data_detrend[_val])
    # for _peak in peaks[_val]["peaks"]:
    #    _ax.axvline(data_detrend["angle"].to_numpy()[_peak], color="red", linestyle=":")
    #    _ax2.axvline(data_detrend["angle"].to_numpy()[_peak], color="red", linestyle=":")
    #    # _ax2.scatter(
    #    #    data_detrend["angle"].to_numpy()[peaks[_val]["peaks"]],
    #    #    data_detrend[_val].to_numpy()[peaks[_val]["peaks"]],
    #    #    s=np.array(peaks[_val]["purity"]) * 300,
    #    #    color="red",
    #    # )
    # for _val in ui_col.options:
    #    for _peak in peaks[_val]["peaks"]:
    #        # background
    #        _ax.axvline(
    #            data_detrend["angle"].to_numpy()[_peak],
    #            color="gray",
    #            linestyle="--",
    #            alpha=0.5,
    #            zorder=-10,
    #        )
    #        _ax2.axvline(
    #            data_detrend["angle"].to_numpy()[_peak],
    #            color="gray",
    #            linestyle="--",
    #            alpha=0.5,
    #            zorder=-10,
    #        )
    # _ax.plot(data_normalized["angle"], data_normalized[ui_col.value])
    # _ax.plot(
    #    data_normalized["angle"],
    #    data_normalized[ui_col.value] - data_detrend[ui_col.value],
    # )
    # _ax2.plot(data_detrend["angle"], data_detrend[ui_col.value])
    # _ax2.scatter(
    #    data_detrend["angle"].to_numpy()[peaks[ui_col.value]["peaks"]],
    #    data_detrend[ui_col.value].to_numpy()[peaks[ui_col.value]["peaks"]],
    #    s=np.array(peaks[ui_col.value]["purity"]) * 300,
    #    color="red",
    # )
    # mo.hstack([_fig, _fig2])
    return


@app.cell
def _(np):
    from scipy.optimize import nnls as _nnls


    def composition(sample):
        phases = {_.filename: _.corrected.to_numpy().T[1] for _ in sample.pure_products}
        phases_list = list(phases)
        sample_corrected = sample.corrected.to_numpy().T[1]

        min_len = min(
            *([len(phase) for phase in phases.values()] + [len(sample_corrected)])
        )

        for key, phase in phases.items():
            phases[key] = phase[:min_len]
        sample_corrected = sample_corrected[:min_len]

        A = np.vstack([phases[_] for _ in phases_list]).T
        weights, _ = _nnls(A, sample_corrected)

        weights = np.minimum(weights, 1)

        friendly_name = []
        for phase_name in phases_list:
            if "MOCOF-1" in phase_name:
                friendly_name.append("MOCOF-1")
            elif "COF-366-Co" in phase_name:
                friendly_name.append("COF-366-Co")
            else:
                friendly_name.append(phase_name)
        return {key: weight for key, weight in zip(phases_list, weights)} | {
            "unknown": 1 - np.sum(weights)
        }
    return (composition,)


@app.cell
def _(composition, mo, plt, sample_selected_for_plot):
    _fig, _ax = plt.subplots(1, 2, figsize=(12, 5))
    if len(sample_selected_for_plot.value) <= 1:
        for _val in sample_selected_for_plot.value:
            for _pure in _val.pure_products:
                _ax[0].plot(
                    _pure.corrected.to_numpy()[:, 0],
                    _pure.corrected.to_numpy()[:, 1],
                    label=_pure.filename,
                )
            _ax[1].plot(
                _val.corrected.to_numpy()[:, 0],
                _val.corrected.to_numpy()[:, 1],
                label="sample",
            )
            _sum = 0
            for _pure in _val.pure_products:
                _sum += _val.composition[_pure.filename] * _pure.corrected.to_numpy()[:, 1]
            _ax[1].plot(
                _val.pure_products[0].corrected.to_numpy()[:, 0],
                _sum,
                label="linear combination",
            )

        _ax[0].set_title("Pure Components")
        _ax[0].legend()
        _ax[1].legend()
        _ax[1].set_title("Linear Combination")
        for _ax_ in _ax:
            _ax_.set_xlabel("angle")
            _ax_.set_ylabel("intensity")

    mo.vstack(
        [
            sample_selected_for_plot,
            _fig,
            composition(list(sample_selected_for_plot.value)[0]),
        ]
    ) if len(sample_selected_for_plot.value) <= 1 else mo.md("""
            /// warning | **Too many samples selected**
            This plot can only show one sample.
            ///
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""### 4.2 Parameter Analysis""")
    return


@app.cell
def _():
    return


app._unparsable_cell(
    r"""
    _data = 
    sns.pairplot(penguins.drop(\"year\", axis=1), hue='species');
    """,
    name="_"
)


@app.cell
def _(jxdl_filtered, mo):
    _dict = {}
    for _key, _val in jxdl_filtered.items():
        _dict_ = {}
        for _i, _val1 in enumerate(_val):
            for _key2, _val2 in _val1.items():
                if _key2 == "$xml_type":
                    continue
            _dict_ |= {str(_i) + _key2: _val2}
        _dict |= {_key: _dict_}
    mo.accordion({"Synthesis Procedure Data": _dict})
    return


@app.cell(hide_code=True)
def _():
    # from scipy.interpolate import interp1d
    #
    # # 🔹 Beispielhafte Peak-Daten: 2θ-Werte und zugehörige Integrale
    # peaks_phase1 = peaks["PXRD_KE-326_Cu_capillary_3s-deg_MOCOF-1.xyd"][
    #     "peaks"
    # ]  # 2θ-Werte der Peaks für Phase 1
    # integrals_phase1 = peaks["PXRD_KE-326_Cu_capillary_3s-deg_MOCOF-1.xyd"]["integral"]
    #
    # peaks_phase2 = peaks["PXRD_KE-328_Cu_capillary_3s-deg.xyd"][
    #     "peaks"
    # ]  # 2θ-Werte der Peaks für Phase 2
    # integrals_phase2 = peaks["PXRD_KE-328_Cu_capillary_3s-deg.xyd"]["integral"]
    #
    # peaks_mixed = peaks[ui_col.value]["peaks"]  # 2θ-Werte der Peaks im Mischspektrum
    # integrals_mixed = peaks[ui_col.value]["integral"]
    #
    # # 🔹 Gemeinsames 2θ-Raster für alle Phasen erzeugen
    # theta_common = np.linspace(
    #     min(peaks_phase1.min(), peaks_phase2.min(), peaks_mixed.min()),
    #     max(peaks_phase1.max(), peaks_phase2.max(), peaks_mixed.max()),
    #     10000,
    # )
    #
    # # 🔹 Interpolation der Integrale auf das gemeinsame Raster
    # interp_phase1 = interp1d(
    #     peaks_phase1, integrals_phase1, bounds_error=False, fill_value=0
    # )
    # interp_phase2 = interp1d(
    #     peaks_phase2, integrals_phase2, bounds_error=False, fill_value=0
    # )
    # interp_mixed = interp1d(peaks_mixed, integrals_mixed, bounds_error=False, fill_value=0)
    #
    # integrals_phase1_interp = interp_phase1(theta_common)
    # integrals_phase2_interp = interp_phase2(theta_common)
    # integrals_mixed_interp = interp_mixed(theta_common)
    #
    # # 🔹 Linearkombination lösen mit NNLS (Nicht-negative Least Squares)
    # _A = np.vstack([integrals_phase1_interp, integrals_phase2_interp]).T
    # _weights, _ = nnls(_A, integrals_mixed_interp)
    #
    # _fig, _ax = plt.subplots()
    # _ax.plot(data_detrend["angle"], data_detrend[ui_col.value], label="Mischspektrum")
    # _ax.plot(
    #     data_detrend["angle"],
    #     data_detrend["PXRD_KE-326_Cu_capillary_3s-deg_MOCOF-1.xyd"] * _weights[0]
    #     + data_detrend["PXRD_KE-328_Cu_capillary_3s-deg.xyd"] * _weights[1],
    #     label="Rekonstruiertes Spektrum",
    # )
    # _ax.set_xlim((0, 15))
    # _ax.legend()
    #
    # mo.hstack(
    #     (
    #         mo.md(
    #             f"""
    #         Gewichtete Beiträge: {np.array2string(_weights * 100, precision=2, suppress_small=True)} %
    #         """
    #         ),
    #         _fig,
    #     )
    # )
    return


@app.cell(hide_code=True)
def _():
    # 🔹 Definiere die Toleranz für die Peak-Übereinstimmung (±1°)
    # tolerance = 5.0  # Toleranz in Grad
    #
    #
    # # 🔹 Hilfsfunktion zum Zusammenfassen der Integrale von Peaks innerhalb der Toleranz
    # def match_peaks(peaks, integrals, peaks_to_match, tolerance):
    #     matched_integrals = []
    #     matched_peaks = []
    #
    #     for peak, integral in zip(peaks, integrals):
    #         # Finde alle Peaks, die innerhalb der Toleranz zum aktuellen Peak liegen
    #         matching_indices = np.abs(peaks_to_match - peak) <= tolerance
    #         if np.any(matching_indices):
    #             # Summiere die Integrale der übereinstimmenden Peaks
    #             matched_integrals.append(
    #                 np.sum(np.ma.masked_array(integrals, ~matching_indices))
    #             )
    #             matched_peaks.append(peak)
    #
    #     return np.array(matched_peaks), np.array(matched_integrals)
    #
    #
    # # 🔹 Peaks und Integrale der Phasen mit der Toleranz zusammenfassen
    # matched_peaks_phase1, matched_integrals_phase1 = match_peaks(
    #     peaks_phase1, integrals_phase1, peaks_mixed, tolerance
    # )
    # matched_peaks_phase2, matched_integrals_phase2 = match_peaks(
    #     peaks_phase2, integrals_phase2, peaks_mixed, tolerance
    # )
    #
    # # 🔹 Linearkombination lösen mit NNLS (Nicht-negative Least Squares)
    # _A = np.vstack([matched_integrals_phase1, matched_integrals_phase2]).T
    # weights, _ = nnls(A, integrals_mixed)
    #
    # # 🔹 Plot der Ergebnisse
    # fig, ax = plt.subplots()
    # ax.plot(peaks_mixed, integrals_mixed, label="Mischspektrum")
    # ax.plot(peaks_mixed, np.dot(_A, weights), label="Rekonstruiertes Spektrum")
    # ax.set_xlim((0, 15))
    # ax.legend()
    #
    # # 🔹 Ausgabe der Gewichteten Beiträge
    # mo.hstack(
    #     (
    #         mo.md(
    #             f"""
    #         Gewichtete Beiträge: {np.array2string(weights * 100, precision=2, suppress_small=True)} %
    #         """
    #         ),
    #         fig,
    #     )
    # )
    return


@app.cell
def _(mo):
    def hide(content, *, label="details", type=None):
        return mo.md(
            f"""
            /// details | {label} 
                {"type: " + type if type else ""}

            {content}

            ///"""
        )


    table = lambda x: mo.ui.table(x, selection=None, show_column_summaries=False)
    return hide, table


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import numpy as np
    import polars as pl
    from pathlib import Path
    import pandas as pd
    import io
    import matplotlib.pyplot as plt
    import scipy as sp
    from scipy.signal import detrend
    from pybaselines import Baseline, utils
    from dataclasses import dataclass
    import json
    import seaborn as sns
    return (
        Baseline,
        Path,
        dataclass,
        detrend,
        io,
        json,
        np,
        pd,
        pl,
        plt,
        sns,
        sp,
        utils,
    )


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
