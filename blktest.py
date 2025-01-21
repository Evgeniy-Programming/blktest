import argparse
import subprocess
import os
import json
import tempfile

def run_fio(test_name, filename, iodepth):
    fio_cmd = [
        "fio",
        "--ioengine=libaio",
        "--direct=1",
        "--bs=4k",
        "--size=1G",
        "--numjobs=1",
        "--name=" + test_name,
        "--filename=" + filename,
        "--rw=randread,randwrite",
        "--iodepth=" + str(iodepth),
        "--output-format=json",
    ]
    
    result = subprocess.run(fio_cmd, capture_output=True, text=True)
    if result.returncode != 0:
       print("Error running FIO:", result.stderr)
       return None
    
    try:
       return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Error decoding FIO output:", result.stdout)
        return None

def parse_fio_output(fio_json):
     if not fio_json or 'jobs' not in fio_json:
         return {}

     data = {}
     for job in fio_json['jobs']:
        if job['type'] == 'read':
          data['read_latency'] = job['lat_ns']['mean']/1000000.0 #to ms
        elif job['type'] == 'write':
          data['write_latency'] = job['lat_ns']['mean']/1000000.0 #to ms
     return data

def generate_plot_data(filename, test_name):
    results = {}
    iodepths = [1, 2, 4, 8, 16, 32, 64, 128, 256]
    for iodepth in iodepths:
       fio_output = run_fio(test_name, filename, iodepth)
       if fio_output:
           latency_data = parse_fio_output(fio_output)
           results[iodepth] = latency_data

    return results

def generate_gnuplot_script(data, output_filename):
    with open("plot.gp", "w") as f:
        f.write(f"set terminal png size 800,600\n")
        f.write(f"set output '{output_filename}'\n")
        f.write("set title 'Latency vs. IODepth'\n")
        f.write("set xlabel 'IODepth'\n")
        f.write("set ylabel 'Latency (ms)'\n")
        f.write("set logscale x 2\n")
        f.write("plot '-' with lines title 'randread' , '-' with lines title 'randwrite'\n")
        
        read_data = []
        write_data = []
        for iodepth, latency_values in data.items():
            if 'read_latency' in latency_values:
               read_data.append(f"{iodepth} {latency_values['read_latency']}")
            if 'write_latency' in latency_values:
               write_data.append(f"{iodepth} {latency_values['write_latency']}")


        f.write("\n".join(read_data)+"\n")
        f.write("e\n")
        f.write("\n".join(write_data)+"\n")
        f.write("e\n")


def run_gnuplot(output_filename):
    try:
        subprocess.run(["gnuplot", "plot.gp"], check=True)
    except subprocess.CalledProcessError as e:
        print("Error running gnuplot:", e)

def main():
    parser = argparse.ArgumentParser(description="Run FIO tests and generate a latency vs. iodepth plot.")
    parser.add_argument("-name", type=str, required=True, help="Test name")
    parser.add_argument("-filename", type=str, required=True, help="Path to the file to test")
    parser.add_argument("-output", type=str, required=True, help="Path to the output PNG file")
    
    args = parser.parse_args()
    
    test_data = generate_plot_data(args.filename, args.name)
    if not test_data:
        print("No test data received")
        return

    generate_gnuplot_script(test_data, args.output)
    run_gnuplot(args.output)
    print(f"Plot generated at: {args.output}")