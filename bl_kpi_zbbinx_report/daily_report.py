import os, csv, xlsxwriter
from apachelogs import LogParser
from datetime import datetime

current_dir = os.getcwd()
log_path_file = current_dir + "/access_log-20220529"
TODAY = datetime.now().strftime("%d%m%y")
LOG_FORMAT = "%h %l %u %t \"%r\" %>s %{X-Forwarded-For}i %b  \"%{Referer}i\" \"%{User-Agent}i\" %T %{ms}T %D "
api_log_path = "{}/api_logs_{}".format(current_dir, TODAY)
reporting_path = "{}/reports".format(current_dir)

if not os.path.exists(api_log_path):
    os.mkdir(api_log_path)
if not os.path.exists(reporting_path):
    os.mkdir(reporting_path)

# TODO: Make it Dynamic using list and string replace
APIS = {
    "purchase": "/offer.purchase*/",
    "verify-otp": "/verify.otp*/"
}

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


def get_command_sh(apis):
    log_line = "print $0"
    command_sh = f"""cat {log_path_file} | awk '{'{'}"""
    flag = False
    for key, value in apis.items():
        if not flag:
            command_sh += f"if($7 ~ {value}) {'{'} {log_line} >> \"{api_log_path}/{key}_{TODAY}.log\"{'}'}"
            flag = True
            chunked_logs.update({key: "{}/{}_{}.log".format(api_log_path, key, TODAY)})
        else:
            command_sh += f" else if($7 ~ {value}) {'{'} {log_line} >> \"{api_log_path}/{key}_{TODAY}.log\"{'}'}"
            chunked_logs.update({key: "{}/{}_{}.log".format(api_log_path, key, TODAY)})
    command_sh += "}'"

    print(command_sh)
    return command_sh


def process_apache_log_file():
    com = get_command_sh(apis=APIS)
    os.system(com)


def analyze_apis():
    parser = LogParser(LOG_FORMAT)
    for key, value in chunked_logs.items():
        with open(value, "r") as logs:
            lines = logs.readlines()
            total_hits = 0
            success_hits = 0
            error_hits = 0
            for line in lines:
                total_hits += 1

                parsed_line = parser.parse(line)
                if parsed_line.final_status == 200 or parsed_line.final_status == 220:
                    success_hits += 1
                else:
                    error_hits += 1
                # print(parsed_line.request_line)
                # print(parsed_line.bytes_sent)
                # print(parsed_line.headers_in['X-Forwarded-For'])
                # print(parsed_line.final_status)
            logs.close()
            data.update({key: {
                "total_hits": total_hits,
                "success_hits": success_hits,
                "error_hits": error_hits,
                "ratio": (success_hits / total_hits) * 100
            }})


def generate_csv():
    for d in data:
        row = [data[d][key] for key in data[d]]
        with open('{}/{}.csv'.format(reporting_path, d), "a") as file:
            writer = csv.writer(file)
            writer.writerow(row)


current_hour = datetime.now().strftime("%d/%b/%Y:%H")


def chunk_log_time_wise():
    # current_hour = datetime.now().strftime("%d/%b/%Y:%H")
    current_hour = "29/May/2022:02"
    current_hour_file = "29.May.2022.02"
    command = f"""grep {current_hour} {log_path_file} > \"{api_log_path}/{current_hour_file}.log\""""
    os.system(command)
    process_apache_log_file()


from_time = datetime.now()
print(datetime.now())
chunk_log_time_wise()

# Directives REF --> https://apachelogs.readthedocs.io/en/stable/directives.html
analyze_apis()

generate_csv()
print(from_time - datetime.now())
# Deploy in 160
print(os.path.dirname('main.py'))
