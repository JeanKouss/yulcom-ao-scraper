import json
import os
import csv
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy
from models.AOYulcom import AOYulcom


jobListExtracSchema = {
    "name": "Jobs",
    "baseSelector": ".awsm-job-listings .awsm-job-listing-item.awsm-list-item",
    "fields": [
        {
            "name": "title",
            "selector": "h2.awsm-job-post-title a",
            "type": "text"
        },
        {
            "name": "url",
            "selector": "h2.awsm-job-post-title a",
            "attribute": "href",
            "type": "attribute",
        }
    ]
}

full_load_js_script = [
    """
        const jobsMutationObserver = new MutationObserver(loadMoreJobs);
        window.addEventListener('load', function() {
            let jobListElement = document.querySelector('#top > div.btContentWrap.btClear > div > div > div > div > div > div.awsm-job-listings.awsm-lists');
            jobsMutationObserver.observe(jobListElement, { childList: true });
            loadMoreJobs();
        });
        function loadMoreJobs() {
            let jobsLoadButton = document.querySelector('#top > div.btContentWrap.btClear > div > div > div > div > div > div.awsm-job-listings.awsm-lists > div.awsm-jobs-pagination.awsm-load-more-main > a');
            if (jobsLoadButton) {
                jobsLoadButton.click();
            } else {
                console.log('No more jobs to load');
                jobsMutationObserver.disconnect();
            }
        }
    """,
]

wait_for_js_script = """() => {
    let jobsLoadButton = document.querySelector('#top > div.btContentWrap.btClear > div > div > div > div > div > div.awsm-job-listings.awsm-lists > div.awsm-jobs-pagination.awsm-load-more-main > a');
    return !jobsLoadButton;
}"""

async def extract_jobs_links():

    extraction_strategy = JsonCssExtractionStrategy(jobListExtracSchema, verbose=True)

    crawler_config = CrawlerRunConfig(
        cache_mode = CacheMode.BYPASS,
        extraction_strategy=extraction_strategy,
        js_code=full_load_js_script,
        wait_for=f"js:{wait_for_js_script}",
    )

    browser_config = BrowserConfig(
        browser_type = "chromium",
        verbose = True,
        headless = False,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://yulcom-technologies.com/fr/jobs/",
            config=crawler_config,
        )

        if not result.success:
            print("Crawl failed:", result.error_message)
            return

        # 5. Parse the extracted JSON
        data = json.loads(result.extracted_content)
        print(len(data), "jobs found")
        # print(json.dumps(data, indent=2) if data else "No data found")
        return data


async def extract_job_info(jobUrl="https://yulcom-technologies.com/fr/jobs/developpeur-senior-drupal-cote-divoire/") :
    extraction_strategy = LLMExtractionStrategy(
        provider="groq/deepseek-r1-distill-llama-70b",
        # provider="groq/llama-guard-3-8b",
        api_token=os.getenv("GROQ_API_KEY"),
        schema=AOYulcom.model_json_schema(),
        extraction_type="schema",
        instruction=(
            "Extrait les information suivantes de cette page"
            "'title' : le titre de l'offre"
            "'category' : la catégorie de profil attendu (Ex : Développeur, IT, ...)"
            "'type' : le type de contrat"
            "'level' : le niveau technique attendu"
            "'location' : le lieu de l'offre. Ex : Ouagadougou, Remote, Hybride, ..."
            "'starts_at' : la date de début de l'offre"
            "'description' : la description de l'offre. Ici, rester le plus fidèle possible à l'offre et récupérer l'entièreté du contenu de l'offre"
            "'url' : l'url de l'offre"
            "'offer_ends_at' : date d'expiration de l'offre"
            "Pour certaines informations comme 'category', 'type', 'level', 'location', 'starts_at', 'offer_ends_at', Tu pourrais avoir besoin d'analyser la page pour les déduire, mais reste aussi fidèle que possible si tu trouves les valeurs exactes"
            "Si tu ne trouve pas une valeur tu peux mettre 'none'"
        ),
        input_format="markdown",
        verbose=True,
    )

    crawl_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS,
        css_selector=".btContentWrap.btClear",
    )

    async with AsyncWebCrawler() as crawler:
        # 4. Let's say we want to crawl a single page
        result = await crawler.arun(
            url=jobUrl,
            config=crawl_config
        )
    
    if result.success:
        print("Crawl succeeded")
        data = json.loads(result.extracted_content)
        # print(json.dumps(data, indent=2) if data else "No data found")
        return data
    else:
        return []

def store_jobs_to_csv(jobs, filename):
    headers = jobs[0].keys()

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for job in jobs:
            writer.writerow(job)