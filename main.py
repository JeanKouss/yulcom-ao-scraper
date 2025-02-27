from utils.crawl_utils import extract_jobs_links , extract_job_info, store_jobs_to_csv
import asyncio
import json
from dotenv import load_dotenv
import time

load_dotenv()

async def extract_jobs():
    jobLinks = await extract_jobs_links()
    jobInfos = []
    for job in jobLinks:
        infos = await extract_job_info(job['url'])
        if len(infos) == 0:
            print("url : ", job['url'])
            print(infos)
            continue
        infos[0]['url'] = job['url']
        jobInfos.append(infos[0])
        time.sleep(5)
    print(json.dumps(jobInfos, indent=2))
    # testJobInfo = await extract_job_info("https://yulcom-technologies.com/fr/jobs/developpeur-senior-drupal-cote-divoire/")
    # testJobInfo = await extract_job_info("https://yulcom-technologies.com/fr/jobs/developpeur-lead-montreal/")
    # testJobInfo = await extract_job_info(jobLinks[0]['url'])
    # print(json.dumps(testJobInfo, indent=2))
    store_jobs_to_csv(jobInfos, "jobs.csv")
    

asyncio.run(extract_jobs())