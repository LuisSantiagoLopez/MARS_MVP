from settings.settings import apifyclient
import os 

def scrapeUserWebsite(url_negocio):
    # El json dentro del archivo "apify_run_input_page_scraping.txt" se lo vamos a entregar al actor de apify para que haga el scraping de la página web del usuario. En sentido práctico, le entregas un url, y el scraper extrae los elementos más importantes de la página web. 
    
    with open("apify_run_input_page_scraping.txt","r") as scraper_instructions: 
        scraper_instructions = scraper_instructions.read()
        
    run_input = {scraper_instructions}

    # Corremos el actor web scraper 
    run = apifyclient.actor("apify/web-scraper").call(run_input=run_input)

    website_content = []

    # Extraemos el contenido al que le hicimos scraping. 
    for item in apifyclient.dataset(run["defaultDatasetId"]).iterate_items():
        website_content.append(str(item))
    
    website_content = ''.join(website_content)

    return website_content