from ..settings.settings import apifyclient

def scrapeUserWebsite(url_negocio, conversationCostCalculator):
    # El json dentro del archivo "apify_run_input_page_scraping.txt" se lo vamos a entregar al actor de apify para que haga el scraping de la página web del usuario. En sentido práctico, le entregas un url, y el scraper extrae los elementos más importantes de la página web. 
    
    run_input = {
        "runMode": "DEVELOPMENT",
        "startUrls": [{ "url": url_negocio }],
        "pageFunction": """
    async function pageFunction(context) {
        const $ = context.jQuery;

        function extractRelevantInfo() {
            let relevantInfo = {};

            relevantInfo.title = $('title').text();
            relevantInfo.metaDescription = $('meta[name="description"]').attr('content');

            relevantInfo.headings = $('h1, h2, h3')
                .slice(0, 3) // Limit to the first 3 headings
                .map((_, el) => $(el).text().trim())
                .filter((_, text) => text.length > 10 && text.length < 200) // Tighten length constraints
                .toArray();

            relevantInfo.paragraphs = $('p')
                .slice(0, 5) // Limit to the first 5 paragraphs
                .map((_, el) => $(el).text().trim())
                .filter((_, text) => text.length > 50 && text.length < 500) // Tighten length constraints
                .toArray();

            relevantInfo.structuredData = $('script[type="application/ld+json"]')
                .map((_, el) => {
                    try {
                        return JSON.parse($(el).html());
                    } catch (e) {
                        return null;
                    }
                })
                .get()
                .filter(item => item !== null);

            return relevantInfo;
        }

        const detailedInfo = extractRelevantInfo();

        return {
            url: context.request.url,
            pageTitle: detailedInfo.title,
            metaDescription: detailedInfo.metaDescription,
            headings: detailedInfo.headings,
            paragraphs: detailedInfo.paragraphs,
            structuredData: detailedInfo.structuredData
        };
    }
    """,
        "proxyConfiguration": {"useApifyProxy": True},
        "injectJQuery": True,
        "waitUntil": ["networkidle2"],
        "maxConcurrency": 10,  # Adjust as needed
        "pageLoadTimeoutSecs": 60,
        "maxPagesPerCrawl": 0,  # Set a limit if needed
    }


    # Corremos el actor web scraper 
    run = apifyclient.actor("apify/web-scraper").call(run_input=run_input)

    website_content = []

    # Extraemos el contenido al que le hicimos scraping. 
    for item in apifyclient.dataset(run["defaultDatasetId"]).iterate_items():
        website_content.append(str(item))

    type = "website"

    # Calcular costos de generar imagen con lightroom
    conversationCostCalculator.apify_run_costs(run, type=type)
    
    website_content = ''.join(website_content)

    return website_content