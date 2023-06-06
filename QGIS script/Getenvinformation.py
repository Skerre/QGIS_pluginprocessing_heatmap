#import sys
#import pandas as pd
#paths = sys.path
#df = pd.DataFrame({'paths':paths})
#df.to_csv(r'C:\Users\martin\PycharmProjects\HeatMapMaker/qgis_sys_paths.csv', index=False)

import os
import json
env = dict(os.environ)
rem = ['SECURITYSESSIONID', 'LaunchInstanceID', 'TMPDIR']
_ = [env.pop(r, None) for r in rem]
with open(r'C:\Users\martin\PycharmProjects\HeatMapMaker/qgis_env.json', 'w') as f:
    json.dump(env, f, ensure_ascii=False, indent=4)