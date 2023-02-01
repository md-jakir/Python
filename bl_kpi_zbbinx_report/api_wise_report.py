import os, csv
import shutil
from datetime import datetime, timedelta
import logging
import subprocess

DATE_FORMAT = "%Y-%m-%d"
CURRENT_DATETIME_OBJ = (datetime.now() - timedelta(minutes=5))
current_dir = os.getcwd()
ZABBIX_HOST_IP = '172.16.7.221'
HOST_NAME = 'blastlite01.banglalink.net'
# current_hour = datetime.now().strftime("%d/%b/%Y:%H")
current_hour = CURRENT_DATETIME_OBJ.strftime("%d/%b/%Y:%H")
current_hour_file = CURRENT_DATETIME_OBJ.strftime("%d.%b.%Y.%H")
current_date = CURRENT_DATETIME_OBJ.strftime(DATE_FORMAT)
log_path_file = current_dir + f"/log_rsync/access_log.{current_date}"
# TODAY = CURRENT_DATETIME_OBJ.strftime("%d%m%y")
LOG_FORMAT = "%h %l %u %t \"%r\" %>s %{X-Forwarded-For}i %b  \"%{Referer}i\" \"%{User-Agent}i\" %T %{ms}T %D "
api_log_path_prefix = f"{current_dir}/log_rsync/api_logs_"
api_log_path = f"{api_log_path_prefix}{current_date}"
reporting_path = "{}/reports".format(current_dir)
REPORT_TO_ZABBIX_LOG = "api_wise_report_to_zabbix.log"
REPORT_TO_ZABBIX_CSV = "api_wise_report_to_zabbix.csv"
ten_minutes_params = CURRENT_DATETIME_OBJ.strftime("%d/%b/%Y:%H:%M")[:-1]
# TODO: Make it Dynamic using list and string replace
APIS = {
    "purchase": "/offer.purchase*/",
    "priyojon_status": "/priyojon.status*/",
    "balance_summary": "/balance.summary*/",
    "amar_offer": "/amar.offer.buy*/",
    "all_products": "/all.products*/",
    "home_amar_offer_content": "/amar.offer.content.for.home*/",
    "verify_otp": "/verify.otp*/",
    "initiate_payment": "/initiate.payment*/",
    "rgw_payment_gateways": "/rgw.payment.gateways.private*/"
}
ZABBIX_DATA = {
    'api_purchase': 0,
    'api_priyojon_status': 0,
    'api_balance_summary': 0,
    'api_amar_offer': 0,
    'api_all_products': 0,
    'api_home_amar_offer_content': 0,
    'api_initiate_payment': 0,
    'api_rgw_payment_gateways': 0,
    'api_verify_otp': 0,
    'api_rtt_verify_otp': 0
}
payment_apis = ["initiate_payment", "rgw_payment_gateways"]

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
        header = ["Time", "API Name", 'Success Hit']
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

for key in APIS:
    file = '{}/{}.csv'.format(reporting_path, key)
    if not os.path.isfile(file):
        try:
            file = open(file, 'x')
            file.close()
        except FileExistsError:
            pass

chunked_logs = {}
data = {}


def analyze_apis():
    for key, value in chunked_logs.items():
        total_count_cmd = f"""cat {value} | wc -l"""
        if key in payment_apis:
            success_count_cmd = f"""cat {value} | awk '{'{'}if($9 <= 500) print $0{'}'}' | wc -l"""
        else:
            success_count_cmd = f"""cat {value} | awk '{'{'}if($9 == 200 || $9 == 220) print $0{'}'}' | wc -l"""
        total_count = int(subprocess.check_output([total_count_cmd], shell=True))
        success_count = int(subprocess.check_output([success_count_cmd], shell=True))

        z_key = f'api_{key}'
        ZABBIX_DATA[z_key] = round(((success_count / total_count) * 100), 4) if total_count else 0
        if key == "verify_otp" and total_count:
            total_rtt_cmd = f"""cat {value} |  awk '{'{'}sum+=$(NF -1);{'}'} END {'{'}print sum;{'}'}'"""
            total_rtt = int(subprocess.check_output([total_rtt_cmd], shell=True))
            average_rtt = round(total_rtt / total_count, 2) if total_count else 0
            z_key = f'api_{key}_avrg_rtt'
            ZABBIX_DATA[z_key] = average_rtt
        if os.path.exists(value):
            os.remove(value)

# Use LB Server as Log Server

def get_command_sh(apis, log_path):
    log_line = "print $0"
    print(ten_minutes_params)
    command_sh = f"""cat {log_path} | grep {ten_minutes_params}| awk '{'{'}"""
    flag = False
    for key, value in apis.items():
        os.system(f"echo -n > {api_log_path}/{key}_{current_hour_file}.log")

    for key, value in apis.items():
        if not flag:
            command_sh += f"if($7 ~ {value}) {'{'} {log_line} >> \"{api_log_path}/{key}_{current_hour_file}.log\"{'}'}"
            flag = True
            chunked_logs.update({key: "{}/{}_{}.log".format(api_log_path, key, current_hour_file)})
        else:
            command_sh += f" else if($7 ~ {value}) {'{'} {log_line} >> \"{api_log_path}/{key}_{current_hour_file}.log\"{'}'}"
            chunked_logs.update({key: "{}/{}_{}.log".format(api_log_path, key, current_hour_file)})
    command_sh += "}'"

    print(command_sh)
    logging.info(command_sh)
    return command_sh


# zabbix_sender -z 172.16.7.221 -s gzvmyblapiback01.banglalink.net -k mybl_login_error -o 0
def chunk_log_time_wise():
    command = f"""grep {current_hour} {log_path_file} > \"{api_log_path}/{current_hour_file}.log\""""
    os.system(command)
    com = get_command_sh(apis=APIS, log_path=f"{api_log_path}/{current_hour_file}.log")
    os.system(com)
    return f"{api_log_path}/{current_hour_file}.log"


def send_to_zabbix(data_dict):
    row = []
    for key, value in data_dict.items():
        row.append([ten_minutes_params, str(key), value])
        zabbix_key = key
        print(zabbix_key)
        v =value
        if value > 0:
            try:
                subprocess.run([f"zabbix_sender -z {ZABBIX_HOST_IP} -s {HOST_NAME} -k {zabbix_key} -o {v}"], shell=True)
                logging.info(f"zabbix_sender -z {ZABBIX_HOST_IP} -s {HOST_NAME} -k {zabbix_key} -o {v}")
            except:
                logging.info(f"zabbix_sender -z {ZABBIX_HOST_IP} -s {HOST_NAME} -k {zabbix_key} -o {v}")
                logging.error(f"zabbix_sender is not working.")
        else:
            logging.error(f"Could not fetch data.")

    try:
        with open(REPORT_TO_ZABBIX_CSV, "a") as file:
            csv_writer = csv.writer(file)
            for r in row:
                csv_writer.writerow(r)

        # logging.info(f"Data inserted to csv API:{key} Value:{value}")
    except:
        logging.error("Failed to write data to CSV.")


logging.info(f"Scritp Dirctory - {current_dir}")
from_time = datetime.now()
chunk_log_time_wise()
# Directives Ref --> https://apachelogs.readthedocs.io/en/stable/directives.html
analyze_apis()
send_to_zabbix(data_dict=ZABBIX_DATA)
def remove_file():
    # Delete files more than 2 days
    old_date = (datetime.now() - timedelta(days=2))
    file_prefix = current_dir + f"/log_rsync/access_log."
    old_log = file_prefix + f"{old_date.strftime(DATE_FORMAT)}"
    while os.path.exists(old_log):
        os.remove(old_log)
        chunked_api_log_dir = f"{api_log_path_prefix}{old_date.strftime(DATE_FORMAT)}"
        if os.path.exists(chunked_api_log_dir):
            shutil.rmtree(chunked_api_log_dir)
        old_date = old_date - timedelta(1)
        old_log = file_prefix + f"{old_date.strftime(DATE_FORMAT)}"

remove_file()
logging.info(f"Script Duration: {(datetime.now() - from_time).seconds}sec.")
