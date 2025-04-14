import polars as pl
import holoviews as hv
import panel as pn
from datetime import timedelta

hv.extension('bokeh')
pn.extension()


def make_dashboard():
    # Initialize empty pane holders
    style = {'height': '33vh'}  # 1/3 of viewport height

    co2_pane = pn.pane.HoloViews(sizing_mode='stretch_width', styles=style)
    temp_pane = pn.pane.HoloViews(sizing_mode='stretch_width', styles=style)
    rh_pane = pn.pane.HoloViews(sizing_mode='stretch_width', styles=style)

    dashboard = pn.Column(co2_pane, temp_pane, rh_pane)

    def update_data():
        try:
            data = pl.read_parquet('co2data.parquet')
            data = data.with_columns(
                co2_rolling=pl.col('co2').rolling_median_by('timestamp', window_size='5m'),
                temp_rolling=pl.col('temp').rolling_median_by('timestamp', window_size='5m'),
                rh_rolling=pl.col('rh').rolling_median_by('timestamp', window_size='5m')
            )
            time_now = data['timestamp'][-1]
            time_start = time_now - timedelta(days=1)
            data = data.filter(pl.col('timestamp') >= time_start)

            co2 = hv.Curve((data['timestamp'], data['co2_rolling']), kdims=['Time'], vdims=['CO2 Concentration (ppm)']).opts(
                color='orange', tools=['hover'], alpha=0.5) * hv.Scatter((data['timestamp'], data['co2_rolling']),
                                                                          kdims=['Time'],
                                                                          vdims=['CO2 Concentration (ppm)']).opts(
                marker='o', color='orange', size=3, tools=['hover'])

            temp_f = data['temp_rolling'] * 9 / 5 + 32
            temp = hv.Curve((data['timestamp'], temp_f), kdims=['Time'], vdims=['Temperature (F)']).opts(
                color='red', tools=['hover'], alpha=0.5) * hv.Scatter((data['timestamp'], temp_f),
                                                                      kdims=['Time'],
                                                                      vdims=['Temperature (F)']).opts(
                marker='o', color='red', size=3, tools=['hover'])

            rh = hv.Curve((data['timestamp'], data['rh_rolling']), kdims=['Time'], vdims=['Relative Humidity (%)']).opts(
                color='green', tools=['hover'], alpha=0.5) * hv.Scatter((data['timestamp'], data['rh_rolling']),
                                                                        kdims=['Time'],
                                                                        vdims=['Relative Humidity (%)']).opts(
                marker='o', color='green', size=3, tools=['hover'])

            # Update the pane objects directly
            co2_pane.object = co2
            temp_pane.object = temp
            rh_pane.object = rh

        except Exception as e:
            print("Error updating data:", e)

    # Call it once before starting
    update_data()

    # Schedule periodic update every 5 seconds
    pn.state.add_periodic_callback(update_data, period=1000)

    return dashboard


# Start the app
pn.serve(make_dashboard, port=5006, websocket_origin=['*'])
