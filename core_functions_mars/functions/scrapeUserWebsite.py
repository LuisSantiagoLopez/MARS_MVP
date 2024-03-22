from ..settings.settings import apifyclient

def scrapeUserWebsite(url_negocio, conversationCostCalculator):
    try:
        run_input = {
            "runMode": "DEVELOPMENT",
            "startUrls": [{"url": url_negocio}],
            "pageFunction": """
    async function pageFunction(context) {
        const $ = context.jQuery;

        function extractRelevantInfo() {
            let relevantInfo = {};

            relevantInfo.title = $('title').text();
            relevantInfo.metaDescription = $('meta[name="description"]').attr('content');

            relevantInfo.headings = $('h1, h2, h3')
                .slice(0, 3)
                .map((_, el) => $(el).text().trim())
                .filter((_, text) => text.length > 10 && text.length < 200)
                .toArray();

            relevantInfo.paragraphs = $('p')
                .slice(0, 5)
                .map((_, el) => $(el).text().trim())
                .filter((_, text) => text.length > 50 && text.length < 500)
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
            "maxConcurrency": 10,
            "pageLoadTimeoutSecs": 60,
            "maxPagesPerCrawl": 0,
        }

        run = apifyclient.actor("apify/web-scraper").call(run_input=run_input)
        website_content = []

        for item in apifyclient.dataset(run["defaultDatasetId"]).iterate_items():
            website_content.append(str(item))

        type = "website"
        conversationCostCalculator.apify_run_costs(run, type=type)
        website_content = ''.join(website_content)

        return website_content
    except Exception as e:
        return "Hubo un error al realizar la solicitud. ¿Incluiste 'https://' en tu URL y está completa?"