import os, csv, xlsxwriter
from apachelogs import LogParser
from datetime import datetime, timedelta
import logging
import subprocess

CURRENT_DATETIME_OBJ = (datetime.now() - timedelta(minutes=5))
current_dir = os.getcwd()
ZABBIX_HOST_IP = '172.16.7.221'
HOST_NAME = 'blastlite01.banglalink.net'
# current_hour = datetime.now().strftime("%d/%b/%Y:%H")
current_hour = CURRENT_DATETIME_OBJ.strftime("%d/%b/%Y:%H")
current_hour_file = CURRENT_DATETIME_OBJ.strftime("%d.%b.%Y.%H:%M")
current_date = CURRENT_DATETIME_OBJ.strftime("%Y-%m-%d")
log_path_file = current_dir + f"/log_rsync/access_log.{current_date}"
TODAY = CURRENT_DATETIME_OBJ.strftime("%d%m%y")
LOG_FORMAT = "%h %l %u %t \"%r\" %>s %{X-Forwarded-For}i %b  \"%{Referer}i\" \"%{User-Agent}i\" %T %{ms}T %D "
api_log_path = "{}/api_logs_{}".format(current_dir, TODAY)
reporting_path = "{}/reports".format(current_dir)
REPORT_TO_ZABBIX_LOG = "report_to_zabbix.log"
REPORT_TO_ZABBIX_CSV = "report_to_zabbix.csv"
NOW = CURRENT_DATETIME_OBJ.strftime("%d/%b/%Y:%H:%M")
ZABBIX_DATA = {
    "purchase_total_hits": 0,
    "purchase_success_hits": 0,
    "purchase_success_ratio": 0.0,
    "purchase_avrg_rtt": 0.0,
    "purchase_avrg_tps": 0.0,
    "purchase_total_tps": 0.0
}
GREP_PARAMS = f'{NOW}'
# if 4 < int(NOW[-1]) < 10:
#     GREP_PARAMS = f'{NOW[:-1]}[5-9]'
# else:
#     GREP_PARAMS = f'{NOW[:-1]}[0-4]'

# TODO: Make it Dynamic {us}ing list and string replace
# APIS = {
#     "purchase": "/offer.purchase*/",
#     "priyojon-status": "/priyojon.status*/",
#     "balance-summary": "/balance.summary*/",
#     "amar-offer-buy": "/amar.offer.buy*/",
#     "all-products": "/all.products*/",
#     "amar-offer-content_for-home ": "/amar.offer.content.for.home*/",
#     "verify-otp": "/verify.otp*/",
# }

if not os.path.isfile(REPORT_TO_ZABBIX_LOG):
    try:
        file = open(REPORT_TO_ZABBIX_LOG, 'x')
        file.close()
    except FileExistsError:
        pass

if not os.path.isfile(REPORT_TO_ZABBIX_CSV):
    try:
        file = open(REPORT_TO_ZABBIX_CSV, 'x')
        writer = csv.writer(file)
        header = ["Time", "purchase_total_hits", "purchase_success_hits", "purchase_success_ratio", "purchase_avrg_rtt", "purchase_avrg_tps", "purchase_total_tps"]
        writer.writerow(header)
        file.close()
    except FileExistsError:
        pass

logging_format = "[%(levelname)s] %(asctime)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=logging_format, datefmt='%d-%b-%y %H:%M:%S',
                    handlers=[logging.FileHandler(REPORT_TO_ZABBIX_LOG), logging.StreamHandler()])

if not os.path.exists(api_log_path):
    os.mkdir(api_log_path)
if not os.path.exists(reporting_path):
    os.mkdir(reporting_path)

# for key in APIS:
#     file = '{}/{}.csv'.format(reporting_path, key)
#     if not os.path.isfile(file):
#         try:
#             file = open(file, 'x')
#             file.close()
#         except FileExistsError:
#             pass

chunked_logs_path = {"master": ""}
data = {}
def calculate_max_tps(log_path):
    max_tps = 0
    for i in range(60):
        grep_params = GREP_PARAMS+f":{i:02}"
        command = f"""grep {grep_params} {log_path} | wc -l """
        tps = int(subprocess.check_output([command], shell=True))
        max_tps = max(max_tps, tps)
    return max_tps



def analyze_log(chunked_logs):
    parser = LogParser(LOG_FORMAT)
    for key, value in chunked_logs.items():
        with open(value, "r") as logs:
            lines = logs.readlines()
            total_hits = 0
            success_hits = 0
            error_hits = 0
            total_rtt = 0
            for line in lines:
                total_hits += 1
                parsed_line = parser.parse(line)
                total_rtt += parsed_line.request_duration_milliseconds
                if parsed_line.final_status == 200 or parsed_line.final_status == 220:
                    success_hits += 1
                else:
                    error_hits += 1
            max_tps = calculate_max_tps(log_path=value)
        ZABBIX_DATA.update({
            "purchase_total_hits": total_hits,
            "purchase_success_hits": success_hits,
            "purchase_avrg_tps": round((total_hits/60), 4),
            "purchase_avrg_rtt": round((total_rtt / total_hits) / 1000, 4) if total_hits else 0.0,
            "purchase_success_ratio": round(((success_hits / total_hits) * 100), 4) if total_hits else 0.0,
            "purchase_total_tps": max_tps
        })

# zabbix_sender -z 172.16.7.221 -s gzvmyblapiback01.banglalink.net -k mybl_login_error -o 0
def chunk_log_time_wise():
    command = f"""grep {GREP_PARAMS} {log_path_file} > \"{api_log_path}/{current_hour_file}.log\""""
    os.system(command)
    print(command)
    logging.info(command)
    return f"{api_log_path}/{current_hour_file}.log"

def send_to_zabbix(data_dict):
    row = [GREP_PARAMS]
    for key, value in data_dict.items():
        zabbix_key = key
        print(zabbix_key)
        row.append(value)
        try:
            subprocess.run([f"zabbix_sender -z {ZABBIX_HOST_IP} -s {HOST_NAME} -k {zabbix_key} -o {value}"], shell=True)
            logging.info(f"zabbix_sender -z {ZABBIX_HOST_IP} -s {HOST_NAME} -k {zabbix_key} -o {value}")
        except:
            logging.info(f"zabbix_sender -z {ZABBIX_HOST_IP} -s {HOST_NAME} -k {zabbix_key} -o {value}")
            logging.error(f"zabbix_sender is not working.")
    try:
        with open(REPORT_TO_ZABBIX_CSV, "a") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(row)
            # logging.info(f"Data inserted to csv API:{key} Value:{value}")
    except:
        logging.error("Failed to write data to CSV.")

logging.info(f" Scritp Dirctory - {current_dir}")
from_time = datetime.now()
chunked_logs_path.update({"master": chunk_log_time_wise()})
# Directives Ref --> https://apachelogs.readthedocs.io/en/stable/directives.html
analyze_log(chunked_logs_path)
send_to_zabbix(data_dict=ZABBIX_DATA)
logging.info(f"Script Duration: {(datetime.now() - from_time).seconds}sec.")
