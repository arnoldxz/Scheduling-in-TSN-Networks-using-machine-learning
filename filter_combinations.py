# %%
from config_provider import ConfigService
from distribution_provider import Provider
import pandas as pd

configService = ConfigService()
config = configService.config

N_STREAMS = configService.networkConfig["n_streams"]
DISTR_FILENAME = config["distributions"]
FILENAME =  config["results_filename"]
BASE_PATH = config["base_path"]
RESULTS_PATH = f"{BASE_PATH}\\{N_STREAMS}\\{FILENAME}"
# %%

def bit_rate(streams):
    def calc(size, period):
        return (size*8)/(period/1000)
    rates = [calc(s['Size'], s['Period']) for s in streams]
    return sum(rates)

def line_to_stream(l):
    return [configService.streamsConfig[i-1] for i in l]

# %%
lines = Provider.readlines(DISTR_FILENAME)
filters = []
for line in lines:
    l = Provider.processline(line)
    streams = line_to_stream(l)
    br = bit_rate(streams)
    v = "<"
    if(br > configService.bandwidth):
        # print(line, streams, configService.bandwidth, br, br > configService.bandwidth)
        v=">"
        filters.append(line)
    # print(f"{line} = {br} {v} {configService.bandwidth}")
# %%
print(len(filters),"filtered from total of", len(lines), "combinations")
if len(filters) >= 0:
    # exit(0)
    pass
    
input("Enter to save...")
filtered_list = list(filter(lambda x: x not in filters, lines))
Provider.writelines(DISTR_FILENAME,filtered_list)
# %%
# Add to CSV the obvious results
processed = list(map(lambda x: Provider.processline(x), filters))

# %%
counts=[]
for distr in processed:
    possible_flows = [1, 2, 3]
    counts.append([distr.count(e) for e in list(set(possible_flows))])
df = pd.DataFrame(counts, columns=['T1', 'T2', 'T3'])
df['Feasibility'] = False
df['Exceeds_Bw'] = True
df.to_csv(f"{RESULTS_PATH}\\{FILENAME}.csv", index=False)
