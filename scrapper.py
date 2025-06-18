import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    HRFlowable,
)
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors


class PDFWebScraper:
    def __init__(self, delay=0.5):
        """
        Initializes the scraper.

        Args:
            delay: Delay between requests in seconds
        """
        self.delay = delay
        self.visited_urls = set()
        self.results = []
        self.output_dir = "webs"

        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 Created directory: {self.output_dir}")

    def read_urls_json(self, filename="urls.json"):
        """
        Reads URLs and depth configuration from JSON file.

        Expected format: [{"url": "https://example.com", "profundidad": 2}, ...]

        Returns:
            list: List of dictionaries with URL configurations
        """
        try:
            with open(filename, "r", encoding="utf-8") as f:
                configs = json.load(f)

            # Ensure it's a list
            if not isinstance(configs, list):
                configs = [configs]

            print(f"📋 {len(configs)} URL configurations loaded")
            return configs
        except FileNotFoundError:
            print(f"❌ File {filename} not found")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            return []

    def scrape_url(self, url):
        """
        Scrapes a single URL and extracts structured content.

        Returns:
            dict: Scraped data including titles, paragraphs, and links
        """
        if url in self.visited_urls:
            return None

        self.visited_urls.add(url)

        try:
            response = requests.get(
                url,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract structured content
            data = {
                "url": url,
                "title": soup.title.string if soup.title else "No title",
                "headings": [],
                "paragraphs": [],
                "links": [],
                "child_urls": [],
            }

            # Extract all headings (h1 to h6)
            for i in range(1, 7):
                for heading in soup.find_all(f"h{i}"):
                    data["headings"].append(
                        {"level": i, "text": heading.get_text(strip=True)}
                    )

            # Extract paragraphs
            for p in soup.find_all("p"):
                text = p.get_text(strip=True)
                if text:  # Only add non-empty paragraphs
                    data["paragraphs"].append(text)

            # Extract links
            for link in soup.find_all("a", href=True):
                link_text = link.get_text(strip=True)
                link_url = urljoin(url, link["href"])
                data["links"].append(
                    {"text": link_text if link_text else "Link", "url": link_url}
                )

                # Check if it's a valid child URL (same domain)
                parsed = urlparse(link_url)
                if (
                    parsed.scheme in ["http", "https"]
                    and self._same_domain(url, link_url)
                    and link_url not in self.visited_urls
                ):
                    data["child_urls"].append(link_url)

            return data

        except Exception as e:
            print(f"⚠️  Error on {url}: {e}")
            return {"url": url, "error": str(e)}

    def _same_domain(self, url1, url2):
        """Check if two URLs belong to the same domain."""
        return urlparse(url1).netloc == urlparse(url2).netloc

    def create_pdf(self, data, filename):
        """
        Creates a PDF file from scraped data with improved formatting.

        Args:
            data: Dictionary containing scraped content
            filename: Output PDF filename
        """
        filepath = os.path.join(self.output_dir, filename)

        # Create PDF document with better margins
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50,
        )

        # Container for the 'Flowable' objects
        story = []

        # Define styles
        styles = getSampleStyleSheet()

        # Custom styles with better formatting
        url_style = ParagraphStyle(
            "URLStyle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#666666"),
            spaceAfter=6,
            alignment=TA_LEFT,
        )

        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontSize=28,
            textColor=colors.HexColor("#2C3E50"),
            spaceAfter=20,
            spaceBefore=10,
            alignment=TA_LEFT,
            leading=32,
        )

        # Heading styles with better hierarchy
        heading_styles = {
            1: ParagraphStyle(
                "Heading1",
                parent=styles["Heading1"],
                fontSize=20,
                textColor=colors.HexColor("#34495E"),
                spaceAfter=12,
                spaceBefore=20,
                borderWidth=0,
                borderPadding=0,
                borderColor=colors.HexColor("#3498DB"),
                borderRadius=0,
                leading=24,
            ),
            2: ParagraphStyle(
                "Heading2",
                parent=styles["Heading2"],
                fontSize=18,
                textColor=colors.HexColor("#34495E"),
                spaceAfter=10,
                spaceBefore=16,
                leading=22,
            ),
            3: ParagraphStyle(
                "Heading3",
                parent=styles["Heading3"],
                fontSize=16,
                textColor=colors.HexColor("#34495E"),
                spaceAfter=8,
                spaceBefore=12,
                leading=20,
            ),
            4: ParagraphStyle(
                "Heading4",
                parent=styles["Heading4"],
                fontSize=14,
                textColor=colors.HexColor("#34495E"),
                spaceAfter=6,
                spaceBefore=10,
                leading=18,
            ),
            5: ParagraphStyle(
                "Heading5",
                parent=styles["Heading5"],
                fontSize=12,
                textColor=colors.HexColor("#34495E"),
                spaceAfter=4,
                spaceBefore=8,
                leading=16,
            ),
            6: ParagraphStyle(
                "Heading6",
                parent=styles["Heading6"],
                fontSize=11,
                textColor=colors.HexColor("#34495E"),
                spaceAfter=4,
                spaceBefore=6,
                leading=14,
            ),
        }

        paragraph_style = ParagraphStyle(
            "CustomParagraph",
            parent=styles["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#2C3E50"),
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16,
            firstLineIndent=0,
        )

        link_style = ParagraphStyle(
            "LinkStyle",
            parent=styles["Normal"],
            textColor=colors.HexColor("#3498DB"),
            fontSize=10,
            leftIndent=20,
            spaceAfter=4,
        )

        section_header_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=16,
            textColor=colors.HexColor("#2C3E50"),
            spaceAfter=12,
            spaceBefore=24,
            alignment=TA_LEFT,
            borderWidth=1,
            borderColor=colors.HexColor("#BDC3C7"),
            borderPadding=10,
            backColor=colors.HexColor("#ECF0F1"),
        )

        # Add header with URL
        story.append(Paragraph(f"<b>URL:</b> {data['url']}", url_style))
        story.append(Spacer(1, 4))

        # Add a line separator
        from reportlab.platypus import HRFlowable

        story.append(
            HRFlowable(width="100%", thickness=1, color=colors.HexColor("#BDC3C7"))
        )
        story.append(Spacer(1, 12))

        # Add title
        story.append(Paragraph(data.get("title", "Sin título"), title_style))

        # Add error message if exists
        if "error" in data:
            error_style = ParagraphStyle(
                "ErrorStyle",
                parent=styles["Normal"],
                textColor=colors.red,
                fontSize=12,
                borderWidth=1,
                borderColor=colors.red,
                borderPadding=10,
                backColor=colors.HexColor("#FFEBEE"),
            )
            story.append(Paragraph(f"<b>Error:</b> {data['error']}", error_style))
            doc.build(story)
            return

        # Add main content section
        content_added = False

        # Group content by type for better organization
        if data.get("headings") or data.get("paragraphs"):
            story.append(Paragraph("Contenido Principal", section_header_style))
            story.append(Spacer(1, 12))

            # Create a mixed content list with headings and paragraphs
            # This would require more complex logic to maintain document order
            # For now, we'll keep them separate but well-formatted

            # Add headings
            if data.get("headings"):
                for heading in data["headings"]:
                    level = heading["level"]
                    text = heading["text"]
                    if text:
                        # Clean and escape text for XML
                        clean_text = self._clean_text_for_pdf(text)
                        story.append(
                            Paragraph(
                                clean_text, heading_styles.get(level, heading_styles[3])
                            )
                        )
                        content_added = True

            # Add paragraphs
            if data.get("paragraphs"):
                for para in data["paragraphs"]:
                    if para and len(para.strip()) > 0:
                        # Clean and escape text for XML
                        clean_text = self._clean_text_for_pdf(para)
                        story.append(Paragraph(clean_text, paragraph_style))
                        content_added = True

        # Add links section if there are links
        if data.get("links"):
            story.append(Spacer(1, 20))
            story.append(Paragraph("Enlaces Encontrados", section_header_style))
            story.append(Spacer(1, 12))

            # Group links by text to avoid duplicates
            unique_links = {}
            for link in data["links"]:
                link_text = link["text"] or "Link"
                link_url = link["url"]
                if link_text not in unique_links or len(link_url) < len(
                    unique_links[link_text]
                ):
                    unique_links[link_text] = link_url

            # Add links in a more organized way
            for link_text, link_url in list(unique_links.items())[
                :30
            ]:  # Limit to 30 links
                if link_text and link_url:
                    # Format link text
                    if link_text == link_url or link_text == "Link":
                        link_display = f"• {link_url}"
                    else:
                        link_display = f"• <b>{self._clean_text_for_pdf(link_text)}:</b> {link_url}"

                    story.append(Paragraph(link_display, link_style))

        # If no content was added, add a message
        if not content_added and not data.get("links"):
            no_content_style = ParagraphStyle(
                "NoContent",
                parent=styles["Normal"],
                fontSize=12,
                textColor=colors.HexColor("#7F8C8D"),
                alignment=TA_CENTER,
                spaceAfter=12,
                spaceBefore=12,
            )
            story.append(
                Paragraph(
                    "No se encontró contenido estructurado en esta página.",
                    no_content_style,
                )
            )

        # Add footer with timestamp
        story.append(Spacer(1, 30))
        story.append(
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#BDC3C7"))
        )

        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#7F8C8D"),
            alignment=TA_CENTER,
        )
        story.append(Spacer(1, 6))
        story.append(
            Paragraph(
                f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}",
                footer_style,
            )
        )

        # Build PDF
        try:
            doc.build(story)
            print(f"   📄 PDF creado: {filename}")
        except Exception as e:
            print(f"   ❌ Error creando PDF {filename}: {e}")

    def _clean_text_for_pdf(self, text):
        """
        Cleans text for safe inclusion in PDF.
        Escapes XML special characters and removes problematic unicode.
        """
        if not text:
            return ""

        # Replace XML special characters
        text = str(text)
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&apos;")

        # Remove or replace problematic characters
        text = text.replace("\x00", "")  # Null bytes
        text = text.replace("\r\n", " ")  # Windows line endings
        text = text.replace("\n", " ")  # Unix line endings
        text = text.replace("\t", " ")  # Tabs

        # Normalize multiple spaces
        text = " ".join(text.split())

        return text.strip()

    def scrape_recursive(self, url, max_depth, current_depth=0, parent_index=""):
        """
        Recursively scrapes URLs up to the specified depth.

        Args:
            url: URL to scrape
            max_depth: Maximum depth to scrape
            current_depth: Current depth level
            parent_index: Index string for naming (e.g., "1", "1-2")
        """
        if current_depth >= max_depth or url in self.visited_urls:
            return

        # Scrape current URL
        data = self.scrape_url(url)
        if not data:
            return

        # Generate PDF filename
        if current_depth == 0:
            # Parent URL
            pdf_filename = f"web{parent_index}.pdf"
        else:
            # Child URL
            pdf_filename = f"web{parent_index}.pdf"

        # Create PDF for this page
        self.create_pdf(data, pdf_filename)

        # Process child URLs if not at max depth
        if current_depth < max_depth - 1 and "child_urls" in data:
            for idx, child_url in enumerate(data["child_urls"], 1):
                time.sleep(self.delay)

                # Create index for child
                if current_depth == 0:
                    child_index = f"{parent_index}-{idx}"
                else:
                    child_index = f"{parent_index}-{idx}"

                self.scrape_recursive(
                    child_url, max_depth, current_depth + 1, child_index
                )

    def scrape_all(self, config_file="urls.json"):
        """
        Main method to process all URLs from configuration file.
        """
        configs = self.read_urls_json(config_file)
        if not configs:
            return

        print(f"🚀 Starting PDF web scraping...")
        print(f"📁 Output directory: {self.output_dir}")

        for idx, config in enumerate(configs, 1):
            url = config.get("url")
            depth = config.get("profundidad", 1)

            if not url:
                print(f"⚠️  Skipping config {idx}: No URL specified")
                continue

            print(f"\n📍 Processing config {idx}/{len(configs)}:")
            print(f"   URL: {url}")
            print(f"   Depth: {depth}")

            # Reset visited URLs for each parent configuration
            self.visited_urls.clear()

            # Start recursive scraping
            self.scrape_recursive(url, depth, parent_index=str(idx))

            time.sleep(self.delay)

        print(f"\n✅ Scraping completed!")
        print(f"📄 PDFs saved in: {self.output_dir}/")


def create_example_json(filename="urls.json"):
    """Creates an example JSON configuration file."""
    example = [
        {"url": "https://example.com", "profundidad": 2},
        {"url": "https://example.org", "profundidad": 1},
    ]

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(example, f, indent=2, ensure_ascii=False)

    print(f"📝 Example file created: {filename}")


if __name__ == "__main__":
    # Check if configuration file exists
    if not os.path.exists("urls.json"):
        print("⚠️  Configuration file not found. Creating example...")
        create_example_json()
        print("Please edit urls.json with your URLs and run again.")
    else:
        # Create scraper instance and run
        scraper = PDFWebScraper()
        scraper.scrape_all()
