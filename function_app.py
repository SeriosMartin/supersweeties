import azure.functions as func
import logging
import io
import csv
from datetime import datetime
from generate_sweets_data import make_orders, order_count_for_today, write_to_adls

app = func.FunctionApp()

@app.timer_trigger(schedule="0 0 6 * * *",
                   arg_name="mytimer",
                   run_on_startup=False)
def daily_sweets_data(mytimer: func.TimerRequest) -> None:
    n   = order_count_for_today()
    dow = datetime.now().strftime("%A")
    logging.info(f"Generating {n} orders ({dow})")

    orders_h, orders_d = make_orders(n)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(orders_h)
    writer.writerows(orders_d)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    write_to_adls(buf.getvalue(), f"orders_{ts}.csv")
    logging.info("Done.")
