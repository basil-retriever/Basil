import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
from markdownify import markdownify as md  # Importeer markdownify

# Zorg dat de uitvoer wordt opgeslagen in een submap van de 'content/' map in de monorepo root
# Pas dit pad aan als je monorepo structuur anders is dan /monorepo-root/backend/website_scanner.py
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'content', 'scraped_pages'))

# Pas dit aan naar je werkelijke website URL! Dit wordt gebruikt om interne links te filteren.
BASE_URL = "https://jacouxit.be"


def html_to_readable_markdown(html_content, url):
    """
    Converteert HTML naar goed leesbare Markdown, met behoud van structuur.
    Voegt bovenaan de bron-URL toe.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Verwijder elementen die meestal geen nuttige content bevatten voor RAG
    for tag in soup(["script", "style", "meta", "link", "footer", "nav", "header", "form", "svg", "button", "img"]):
        tag.extract()

    # Zoek naar de hoofdcontent van de pagina. Pas dit aan voor jouw specifieke website!
    # Dit is cruciaal voor schone output. Probeer CSS-selectors van de hoofdcontent container.
    main_content_element = soup.find('main') or \
                           soup.find('div', class_='main-content') or \
                           soup.find('article') or \
                           soup.find('body')  # Fallback naar de body als niets specifieks gevonden

    if not main_content_element:
        main_content_element = soup.body  # Altijd een fallback

    # Converteer de content van het element naar Markdown
    # Gebruik 'strip_links=False' om links te behouden, wat goed is voor RAG bronnen.
    # 'heading_style="ATX"' geeft # Hoofdingen
    markdown_output = md(str(main_content_element), heading_style="ATX", strip_links=False)

    # Voeg bovenaan de titel en bron-URL toe als een soort frontmatter
    title = soup.title.string if soup.title else os.path.basename(urlparse(url).path) or "Geen titel"

    final_markdown = f"# {title.strip()}\n\n"
    final_markdown += f"Bron: {url.strip()}\n\n"
    final_markdown += markdown_output

    return final_markdown.strip()


def scrape_page(url, output_dir):
    """Haalt een URL op en slaat de content op als een Markdown-bestand."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Gooi een fout als de statuscode geen succes is

        markdown_content = html_to_readable_markdown(response.text, url)

        # Maak een veilige en leesbare bestandsnaam van de URL
        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p]  # Verwijder lege delen
        filename_base = '_'.join(path_parts) if path_parts else "index"

        # Voeg de domeinnaam toe om botsingen te voorkomen bij het scannen van meerdere sites
        domain_prefix = parsed_url.netloc.replace('.', '_') + '_'

        output_filepath = os.path.join(output_dir, f"{domain_prefix}{filename_base}.md")

        os.makedirs(output_dir, exist_ok=True)  # Zorg dat de output directory bestaat

        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"Opgeslagen: {output_filepath}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Fout bij ophalen van {url}: {e}")
        return False


def discover_and_scrape_site(start_url, max_pages=50):
    """
    Ontdekt pagina's op een site en scraped ze naar Markdown-bestanden.
    """
    visited_urls = set()
    urls_to_visit = [start_url]

    parsed_start_url = urlparse(start_url)
    base_domain = parsed_start_url.netloc

    count = 0
    # Verwijder bestaande scraped content voor een schone start
    if os.path.exists(OUTPUT_DIR):
        import shutil
        shutil.rmtree(OUTPUT_DIR)
        print(f"Bestaande map '{OUTPUT_DIR}' geleegd.")

    while urls_to_visit and count < max_pages:
        current_url = urls_to_visit.pop(0)

        # Normaliseer URL om dubbele bezoeken te voorkomen (bijv. met/zonder trailing slash)
        current_url = current_url.rstrip('/')
        if current_url in visited_urls:
            continue

        print(f"Scraping: {current_url} ({count + 1}/{max_pages})")
        if scrape_page(current_url, OUTPUT_DIR):
            visited_urls.add(current_url)
            count += 1

            # Vind links op de huidige pagina en voeg toe aan lijst om te bezoeken
            try:
                response = requests.get(current_url, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(current_url, href)
                    parsed_full_url = urlparse(full_url)

                    # Zorg ervoor dat we binnen hetzelfde domein blijven en geen ankers (#) of query params (?) volgen
                    if parsed_full_url.netloc == base_domain and \
                            full_url.split('#')[0].split('?')[0].rstrip('/') not in visited_urls and \
                            full_url.startswith(('http://', 'https://')):  # Zorg dat het een volledige URL is

                        # Voeg alleen de basis-URL toe, zonder ankers of query parameters
                        clean_url = full_url.split('#')[0].split('?')[0].rstrip('/')
                        if clean_url not in urls_to_visit and clean_url not in visited_urls:
                            urls_to_visit.append(clean_url)
            except requests.exceptions.RequestException as e:
                print(f"Fout bij analyseren van links op {current_url}: {e}")

    print(f"\nScraping voltooid. Totaal {count} pagina's gescraped en opgeslagen in '{OUTPUT_DIR}'.")


if __name__ == "__main__":
    # BELANGRIJK: PAS DIT AAN! De start-URL van de website die je wilt scannen.
    START_URL_TO_SCAN = BASE_URL

    discover_and_scrape_site(START_URL_TO_SCAN, max_pages=50)  # Limiteer het aantal pagina's voor testen!