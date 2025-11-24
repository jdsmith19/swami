from datetime import datetime

def log(log_path, log_data, log_type = "file", calling_file = ""):
    # Generate a timestamp for l ogs
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not type(log_data) == 'str':
        log_data = str(log_data)
        
    # Teamplate to start each log
    log_data = f"""[{ ts } :: { calling_file }] """ + log_data

    # Do we want to print this only to file or...
    if (log_type == "file" or log_type == "all"):
        try:
            with open(log_path, 'a') as f:
                f.write(f"{ log_data }\n")
        except Exception as e:
            print(f"Loggit error saving to file: { e }")

    # Also to stdout
    if (log_type == "print" or log_type == "all"):
        print(log_data)