"""Adapt the saved Prolens Framer export into Abdessalam's static CV site."""

from html import escape, unescape
from pathlib import Path
import re

ROOT = Path(__file__).parent
source = (ROOT / "prolens.framer.website/prolens.framer.website/index.html").read_text()

# Keep the original Framer markup and CSS. Its runtime would rehydrate the
# template copy, so the CV is published as the rendered static page instead.
source = re.sub(r"<script\b[^>]*>.*?</script>", "", source, flags=re.S | re.I)
source = re.sub(r"<link\b[^>]*rel=\"modulepreload\"[^>]*>", "", source, flags=re.I)

def remove_named_element(html, name):
    start_pattern = re.compile(r'<(div|section)\b[^>]*data-framer-name="' + re.escape(name) + r'"[^>]*>', re.I)
    while (match := start_pattern.search(html)):
        tag = match.group(1)
        token_pattern = re.compile(r'</?' + tag + r'\b[^>]*>', re.I)
        depth = 1
        end = None
        for token in token_pattern.finditer(html, match.end()):
            depth += -1 if token.group(0).startswith('</') else 1
            if depth == 0:
                end = token.end()
                break
        if end is None:
            raise ValueError(f"Could not close {name}")
        html = html[:match.start()] + html[end:]
    return html

for old_section in ("Created and Built", "404", "Remove Me (Remix Button)"):
    source = remove_named_element(source, old_section)

badge_start = source.find('<div id="__framer-badge-container">')
if badge_start >= 0:
    depth = 0
    for token in re.finditer(r'</?div\b[^>]*>', source[badge_start:], flags=re.I):
        depth += -1 if token.group(0).startswith('</') else 1
        if depth == 0:
            source = source[:badge_start] + source[badge_start + token.end():]
            break

def local_asset(match):
    url = match.group(0)
    path = url.split("://", 1)[1].split("?", 1)[0]
    if (ROOT / "prolens.framer.website" / path).is_file():
        return "prolens.framer.website/" + path + ("?" + url.split("?", 1)[1] if "?" in url else "")
    return url

source = re.sub(r"https://(?:framerusercontent\.com|fonts\.gstatic\.com)/[^\s\"')<>]+", local_asset, source)

# Use the supplied personal logo in the template's portrait frames.
portrait_ids = ("UbipOH5I5aV4nPsrZfcpFBsLdg", "rV4XUyJZSrbLuvnKKvNbXWHtPd0")
portrait_pattern = r'(?:https://framerusercontent\.com|prolens\.framer\.website/framerusercontent\.com)/images/(?:' + '|'.join(portrait_ids) + r')[^\s"<> ,]*'
source = re.sub(portrait_pattern, "4k-ab-logo.png", source)
def use_hero_face(match):
    return match.group(1) + match.group(2).replace('4k-ab-logo.png', 'heroface.png').replace('src="heroface.png" alt', 'src="heroface.png" alt="Animated portrait of Abdessalam"') + match.group(3)
source = re.sub(r'(<section\b[^>]*id="home"[^>]*>)(.*?)(</section>)', use_hero_face, source, flags=re.S)
for ring_id, asset in {
    "wYrGKBrZz13yXbZdiNTnnpnXerQ": "assets/hero-ring-inner.png",
    "ANFuRnJlDSqsab9Pdbj8E0qXKXs": "assets/hero-ring-outer.png",
    "evKtH3HNrH5Ax6XiBAPdMLftc0I": "assets/project-ring.png",
}.items():
    source = re.sub(r'(?:https://framerusercontent\.com|prolens\.framer\.website/framerusercontent\.com)/images/' + ring_id + r'[^\s"<> ,]*', asset, source)

replacements = {
    "I build businesses and help entrepreneurs grow theirs through strong strategy, practical insights, and real-world experience.": "I build and run online businesses end to end, combining e-commerce operations, web design, digital marketing and AI automation.",
    "Trusted by businesses": "9 years of hands-on digital work",
    "Entrepreneur": "E-Commerce",
    "Investor": "AI Automation",
    "Business Partner": "Digital Marketing",
    "Advisor": "Web Design",
    "Hello, I’m Dave": "Hello, I’m Abdessalam",
    "Here you’ll find detailed descriptions of what I do and how I can help.": "Based in Casablanca, Morocco, I build practical digital businesses and systems from idea to launch.",
    "I build and scale businesses from concept to market, transforming ideas into sustainable companies through clear strategy, strong execution, and innovation.": "I launched and operated nine online stores, managing sourcing, Shopify builds, fulfilment and customer service across different markets.",
    "I invest in forward-thinking founders and high-potential ventures, providing not only capital but also strategic insight and hands-on support to create lasting value.": "I create sales pipelines, lead routing, email sequences and live Google Sheets dashboards that reduce repetitive work.",
    "I actively support creative professionals and impactful initiatives that advance culture, foster innovation, and contribute to positive change in society.": "I design and develop websites and landing pages with WordPress, Elementor and AI-assisted coding, with a focus on conversion and SEO.",
    "I collaborate closely with founders and teams, offering experience, structure, and long-term commitment to help businesses grow stronger and reach shared ambitions.": "I run Meta advertising campaigns, test audiences and improve results through SEO, conversion optimisation and email marketing.",
    "My mission is to support those who dare to take risks, and create meaningful businesses.": "My mission is to turn ideas into working digital businesses and make them run efficiently.",
    "What I’m Proud of": "What I’m Proud Of",
    "These are projects I’ve created, actively contributed to, or supported as an investor and partner.": "Businesses and systems I have built and operated myself.",
    "Reliable Center": "9 E-Commerce Stores",
    "Childcare Center": "Online retail",
    "Lumina Auto": "COD Operations",
    "Auto Center": "Morocco & Africa",
    "Department of Function": "AI Automation",
    "Healthcare Organization": "Sales & reporting systems",
    "Other projects": "Other projects",
    "Social Networks": "Contact & CV",
    "Where to Find Me": "Get in Touch & Download",
    "Linkedin": "Email Me",
    "Facebook": "English CV",
    "X/Twitter": "French CV",
    "My Way": "My Career",
    "The journey to becoming who I am today wasn’t easy, and I look back on every step with love. Below are my key roles.": "Nine years of independent work in e-commerce, web development, marketing and automation.",
    "Beeza": "Self-Employed — Casablanca",
    "Close AI": "Self-Employed — Remote",
    "Arrana": "Self-Employed — Casablanca",
    "Terracota": "Self-Employed — Remote",
    "2025 → Now": "2024 → Now",
    "2024 → 2025": "2022 → Now",
    "2020 → 2024": "2023 → 2024",
    "2019 → 2020": "2019 → Now",
    "2026": "2019",
    "2025": "2023",
    "Co-Founder, CEO": "AI Automation & Web Development Specialist",
    "Founder, CEO": "Freelance Web Designer & Developer",
    "Co-Founder": "E-Commerce Store Owner — Dropshipping",
    "Founder": "COD E-Commerce Operator — Morocco & Africa",
    "View Full Career": "Download Full CV",
    "Testimonials": "Achievements",
    "People Say": "Results & Capabilities",
    "Dave has an exceptional ability to see opportunities where others see risk. Working with him has been both profitable and inspiring.": "Launched and managed nine e-commerce stores across different markets and product categories.",
    "Soul Cristofer": "9 online stores",
    "Founder, Goora": "E-commerce operations",
    "As a business partner, Dave is transparent, strategic, and deeply committed to long-term success. You always know where you stand with him.": "Built and operated Cash-on-Delivery e-commerce operations across Morocco and Africa, from sourcing through delivery coordination.",
    "Theodore Blake": "COD operations",
    "Brand Manager, Wellox": "Morocco & Africa",
    "Working with Dave has been a transformative experience for our business. He brings sharp strategic insight while staying grounded and practical. His ability to balance vision with execution makes him an great partner.": "Designed responsive websites and high-converting landing pages with WordPress, Elementor and AI-assisted development.",
    "Ava Williams": "Web design",
    "CTO, Hill Communications": "Sites and landing pages",
    "Collaborating with Dave pushed our business to the next level. His strategic thinking and calm decision-making are invaluable.": "Built automations for lead routing, email communication and self-updating reporting dashboards.",
    "Pat Moravich": "Automation systems",
    "CEO, Acronis": "Sales and reporting",
    "Blog": "Education",
    "What I Share": "How I Learned",
    "Here you can read my news, business insights, and other experiences.": "Formal education and continuous learning applied to real business projects.",
    "It’s incredibly important to share knowledge with those who have chosen the same path as you.": "I keep learning by building, testing and improving real projects.",
    "Interview on CBS: New business approach": "Faculté des Sciences Ben M'Sik — Chemistry (no degree)",
    "Article: How to implement business strategy": "Baccalauréat — Scientific Stream",
    "News: What's new in an automobile industry": "E-Commerce & Digital Marketing",
    "Article: Reface implemented some new things": "Web Development & AI Automation",
    "Oct 12, 2025": "Learning",
    "Dave Richardson": "Abdessalam Ouaouane",
    "hello@davewebsite.com": "work@heyabdessalam.info",
    "Message Me:": "Contact Me:",
    "Send message": "Open email draft",
    "Your information will remain private and will not be shared without your permission.": "Your email app will open with the message ready to send.",
    "© 2025 Prolens. All rights reserved.": "© 2026 Abdessalam Ouaouane. All rights reserved.",
}

def plain(html):
    return " ".join(unescape(re.sub(r"<[^>]+>", "", html)).split())

def replace_element(match):
    tag, attrs, inner = match.group(1), match.group(2), match.group(3)
    original = plain(inner)
    if tag == "h1":
        new = '<span style="white-space:nowrap">Abdessalam</span> <span style="white-space:nowrap">Ouaouane</span>'
    elif original in replacements:
        new = escape(replacements[original])
    else:
        return match.group(0)
    return f"<{tag}{attrs}>{new}</{tag}>"

source = re.sub(r"<(h[1-6]|p)(\s[^>]*)>(.*?)</\1>", replace_element, source, flags=re.S | re.I)

# Keep the original review carousel frame; its cards are repurposed below as
# verifiable CV achievements because the PDFs do not contain client reviews.

def expand_about(match):
    content = match.group(2).replace('framer-v-5ggtx6', 'framer-v-nfv152').replace('framer-v-3xjfpx', 'framer-v-ty78oc')
    content = content.replace('data-framer-name="Desktop - Closed"', 'data-framer-name="Desktop - Open"').replace('data-framer-name="Phone closed"', 'data-framer-name="Phone"')
    content = re.sub(r'(<div\b[^>]*class="[^"]*framer-iEy58[^"]*"[^>]*?)\s+data-highlight="true"\s+tabindex="0"', r'\1', content)
    return match.group(1) + content + match.group(3)

source = re.sub(r'(<section\b[^>]*id="about"[^>]*>)(.*?)(</section>)', expand_about, source, count=1, flags=re.S)

def replace_raster_images(content, asset, circle=False):
    def use_asset(image_match):
        tag = image_match.group(0)
        if not re.search(r'(?:src|srcset)="[^"]*/images/[^" ]+\.(?:png|jpg|webp)', tag):
            return tag
        tag = re.sub(r'\s+srcset="[^"]*"', '', tag)
        tag = re.sub(r'\bsrc="[^"]*"', f'src="{asset}"', tag)
        if circle:
            tag = tag.replace('style="', 'style="clip-path:circle(50% at 50% 50%) !important;border-radius:50% !important;', 1)
        return tag
    return re.sub(r'<img\b[^>]*>', use_asset, content)

photo_map = {
    "yAG0hcslaT1HuLZqR7lvd2XKlBc": "assets/project-ecommerce.png",
    "EZPdxHJFMQRxzqRvx1GyhvTTztU": "assets/project-cod.png",
    "YbuCwyJttsm4vcOxLxzjRFbQP3U": "assets/project-automation.png",
    "8S0SqoU0WbwP9dgtbt95c7eJy8": "assets/education-chemistry.png",
    "dkEkHFLxM0xFafRUG7p2jn5U": "assets/education-chemistry.png",
    "CMmT8DwlIAW7NN43qMo87x2slP4": "assets/education-science.png",
    "Mwayvg5Fvw51sixvqOv4zkpR5g": "assets/project-ecommerce.png",
    "4SbEtm6IVdY2Sz5rBOjRy45olI": "assets/project-automation.png",
}
for original_id, asset in photo_map.items():
    source = re.sub(r'(?:https://framerusercontent\.com|prolens\.framer\.website/framerusercontent\.com)/images/' + original_id + r'[^\s"<> ,]*', asset, source)

# Career logos in the template stand for unrelated companies.
for logo_id in ("THvEg4q9WjEWZVnQBhY4sQPIAxM", "mpRJYAxju8IIL55U9FH1mRtWk", "YHiUxSjJcZEFHgzZMEBhXI03Qjg", "Ad6zJmiPKpTTZTcxOh0cKxUezps"):
    source = re.sub(r'https://framerusercontent\.com/images/' + logo_id + r'\.svg[^\s"<> ,]*', 'assets/ao-monogram.svg', source)

project_tags = {
    "Project #1": {"AI Automation": "Shopify"},
    "Project #2": {"AI Automation": "COD", "Digital Marketing": "Meta Ads"},
    "Project #3": {"Web Design": "Reporting", "E-Commerce": "Automation"},
}
project_images = {"Project #1": "assets/project-ecommerce.png", "Project #2": "assets/project-cod.png", "Project #3": "assets/project-automation.png"}
for project_name, tags in project_tags.items():
    pattern = r'(<a\b[^>]*data-framer-name="' + re.escape(project_name) + r'"[^>]*>)(.*?)(</a>)'
    def retag(match):
        content = re.sub(r'(<div\b[^>]*data-framer-name="Image"[^>]*>.*?)(<img\b[^>]*>)',
                         lambda image: image.group(1) + replace_raster_images(image.group(2), project_images[project_name], circle=True),
                         match.group(2), flags=re.S)
        for old, new in tags.items():
            content = content.replace('>' + old + '</p>', '>' + new + '</p>')
        return match.group(1) + content + match.group(3)
    source = re.sub(pattern, retag, source, flags=re.S)

# Letter-by-letter rolling links belong to the Framer runtime. Replace them
# with plain static labels while retaining their original anchor positions.
source = re.sub(r'(<a\b[^>]*data-framer-name="Logotype"[^>]*>).*?(</a>)', r'\1<span class="cv-brand-mark"><img src="4k-ab-logo.png" alt="" width="64" height="64"></span>Abdessalam\2', source, flags=re.S)
source = re.sub(r'(<a\b[^>]*href="\./#blog"[^>]*>).*?(</a>)', r'\1Education <span aria-hidden="true">↓</span>\2', source, flags=re.S)

education_dates = iter(["2018–2019"] * 3 + ["2017"] * 3 + ["Since 2017"] * 3 + ["Ongoing"] * 3)
source = re.sub(r">Learning</p>", lambda match: ">" + next(education_dates, "Ongoing") + "</p>", source)

# Replace direct template links with real contact and CV links.
source = source.replace('mailto: hello@davewebsite.com', 'mailto:work@heyabdessalam.info')
source = source.replace('mailto:hello@davewebsite.com', 'mailto:work@heyabdessalam.info')
source = re.sub(r'href="https://www\.linkedin\.com/[^"]+"', 'href="mailto:work@heyabdessalam.info"', source)
source = re.sub(r'href="https://www\.facebook\.com/[^"]+"', 'href="abdessalam-cv-eng.pdf"', source)
source = re.sub(r'href="https://x\.com/[^"]+"', 'href="abdessalam-cv-fr.pdf"', source)
source = re.sub(r'href="https://(?:karta|astralab|realagent)\.framer\.website[^"]*"', 'href="abdessalam-cv-eng.pdf"', source)
source = re.sub(r'href="https://(?:www\.)?linkedin\.com[^"]*"', 'href="abdessalam-cv-eng.pdf"', source)

def fix_career_cv_link(match):
    link = match.group(0)
    return re.sub(r'href="[^"]+"', 'href="abdessalam-cv-eng.pdf"', link, count=1) if 'Download Full CV' in link else link
source = re.sub(r'<a\b[^>]*data-framer-name="(?:Black|Black phone)"[^>]*>.*?</a>', fix_career_cv_link, source, flags=re.S)

# Replace the template's repeated career placeholders with role-specific icons.
career_icons = ([('assets/claude.svg', 'Claude logo')] * 3 +
                [('assets/vscode.svg', 'VS Code logo')] * 3 +
                [('assets/network.svg', 'Network icon')] * 3 +
                [('assets/shopify.svg', 'Shopify logo')] * 3)
def add_career_icons(match):
    icons = iter(career_icons)
    body = match.group(2)
    assert body.count('src="assets/ao-monogram.svg"') == len(career_icons)
    def replace_icon(logo_match):
        asset, label = next(icons)
        return f'src="{asset}" alt="{label}"'
    body = re.sub(r'src="assets/ao-monogram\.svg" alt(?:="[^"]*")?', replace_icon, body)
    return match.group(1) + body + match.group(3)
source = re.sub(r'(<section\b[^>]*id="career"[^>]*>)(.*?)(</section>)', add_career_icons, source, count=1, flags=re.S)

for href, asset in [('mailto:work@heyabdessalam.info', 'assets/email.svg'),
                    ('abdessalam-cv-eng.pdf', 'assets/cv-en.svg'),
                    ('abdessalam-cv-fr.pdf', 'assets/cv-fr.svg')]:
    pattern = r'(<a\b[^>]*href="' + re.escape(href) + r'"[^>]*>(?:(?!</a>).)*?<div\b[^>]*data-framer-name="Socicon"[^>]*>)(.*?)(</div>)'
    icon_html = f'<img src="{asset}" alt="" aria-hidden="true" style="display:block;width:24px;height:24px;object-fit:contain">'
    source, count = re.subn(pattern, lambda m: m.group(1) + icon_html + m.group(3), source, count=1, flags=re.S)
    assert count == 1, f'Missing contact icon slot: {href}'

skills_html = """<div class="cv-details" id="skills">
  <div class="cv-details-heading"><span>From the CV</span><h3>Skills &amp; Tools</h3><p>Hands-on work across operations, growth, design and automation.</p></div>
  <div class="cv-details-grid">
    <div><h4>E-Commerce Operations</h4><p>Shopify, Cash-on-Delivery, dropshipping, supplier sourcing, inventory, fulfilment, customer service and returns.</p></div>
    <div><h4>Digital Marketing</h4><p>Facebook and Instagram Ads, media buying, audience testing, SEO, conversion optimisation and email marketing.</p></div>
    <div><h4>Web Design &amp; Development</h4><p>WordPress, Elementor, UI/UX, responsive websites, landing pages, HTML/CSS and AI-assisted development with VS Code.</p></div>
    <div><h4>AI &amp; Automation</h4><p>Sales and call-centre workflows, automated emails, Google Sheets formulas and dashboards, and custom scripts.</p></div>
    <div><h4>Design &amp; Business</h4><p>Canva, content creation, brand assets, business model design, process improvement and reporting.</p></div>
    <div><h4>Tools &amp; Languages</h4><p>Google Sheets, Microsoft Word and PDF workflows; macOS and Windows. Arabic: native. English: very good, working language. French: basic.</p></div>
  </div>
</div>"""
source = re.sub(r'(<section\b[^>]*id="about"[^>]*>)(.*?)(</section>)', lambda m: m.group(1) + m.group(2) + skills_html + m.group(3), source, count=1, flags=re.S)

experience_html = """<div class="cv-experience-details">
  <h3>Experience in Detail</h3>
  <article><div><h4>AI Automation &amp; Web Development Specialist</h4><span>Self-Employed · Casablanca · 2024 → Present</span></div><p>Build automation for sales, lead distribution, email, marketing and reporting. Develop websites and internal tools with AI-assisted development. Create automated Google Sheets workflows and dashboards.</p></article>
  <article><div><h4>Freelance Web Designer &amp; Developer</h4><span>Self-Employed · Remote · 2022 → Present</span></div><p>Design and develop WordPress and Elementor websites with a focus on UI/UX and on-page SEO. Create conversion-focused landing pages and digital assets using Canva and AI design tools.</p></article>
  <article><div><h4>COD E-Commerce Operator — Morocco &amp; Africa</h4><span>Self-Employed · Morocco · 2023 → 2024</span></div><p>Managed product sourcing, marketing, order processing and delivery coordination. Ran Meta ads and improved call-centre, order confirmation and returns workflows.</p></article>
  <article><div><h4>E-Commerce Store Owner — Dropshipping</h4><span>Self-Employed · Remote · 2019 → Present</span></div><p>Launched and managed nine stores across markets and product categories. Handled product research, suppliers, pricing, store operations and Meta advertising.</p></article>
  <article><div><h4>Online Seller — eBay &amp; Etsy</h4><span>Self-Employed · Remote · 2017 → 2019</span></div><p>Managed listings, prices, orders and customer transactions on eBay and Etsy. Coordinated sourcing and fulfilment between suppliers and international customers.</p></article>
</div>"""
source = re.sub(r'(<section\b[^>]*id="career"[^>]*>)(.*?)(</section>)', lambda m: m.group(1) + m.group(2) + experience_html + m.group(3), source, count=1, flags=re.S)

contact_html = """<div class="cv-contact-extra">
  <a href="tel:+212627144466">+212 627 144 466</a><span>Casablanca, Morocco</span>
  <a href="https://heyabdessalam.info" target="_blank" rel="noopener">heyabdessalam.info</a>
</div><div class="cv-downloads"><a href="abdessalam-cv-eng.pdf" download><img src="assets/cv-en.svg" alt="" aria-hidden="true">Download CV — English</a><a href="abdessalam-cv-fr.pdf" download><img src="assets/cv-fr.svg" alt="" aria-hidden="true">CV — Français</a></div>"""
source = re.sub(r'(<h4\b[^>]*>work@heyabdessalam\.info</h4>)', lambda m: m.group(1) + contact_html, source)

# Static rendering of the original animated export: show content immediately.
static_css = """<style id="cv-static-overrides">
@font-face { font-family:Orbitron; src:url('assets/orbitron-700.ttf') format('truetype'); font-style:normal; font-weight:700; font-display:swap; }
html { scroll-behavior: auto !important; }
html, body { overflow-x:clip; }
[style*="opacity:0.001"] { opacity: 1 !important; transform: none !important; }
[data-framer-name="Template CTA"], [data-framer-name="Purchase"] { display: none !important; }
a[data-framer-name="Logotype"] { display:inline-flex !important; align-items:center; gap:7px; font-family:Orbitron, Geist, Arial, sans-serif !important; font-size:20px !important; font-weight:700 !important; letter-spacing:.01em; text-transform:uppercase; color:#111 !important; text-decoration:none !important; white-space:nowrap; }
a[data-framer-name="Logotype"] .cv-brand-mark { width:52px; height:28px; flex:none; overflow:hidden; position:relative; display:block; }
a[data-framer-name="Logotype"] img { position:absolute; width:64px; height:64px; max-width:none; left:-5px; top:-16px; }
@media(max-width:390px){a[data-framer-name="Logotype"] { font-size:16px !important; gap:5px; } a[data-framer-name="Logotype"] .cv-brand-mark { width:46px; height:26px; } a[data-framer-name="Logotype"] img { width:58px; height:58px; top:-15px; }}
a[href="./#blog"] { font-family: Geist, Arial, sans-serif !important; font-size: 20px !important; font-weight: 600 !important; color: #111 !important; text-decoration: none !important; white-space: nowrap; }
a[href="./#blog"] span { margin-left: 7px; font-size: 17px; font-weight: 400; }
[data-framer-name="People"], #testimonials [data-framer-name="Ava3"], #testimonials [data-framer-name="Av1"], #testimonials [data-framer-name="stars"] { display: none !important; }
[data-framer-name="Sign"] { display: none !important; }
#home [data-framer-name="Ellipse bigger"] { animation:cv-ring-clockwise 72s linear infinite; }
#home [data-framer-name="Ellipse biggest"] { animation:cv-ring-counter 82s linear infinite; }
#home [data-framer-name="Av1"] { animation:cv-hero-face 5s ease-in-out infinite alternate; transform-origin:50% 70%; }
@keyframes cv-hero-face { from { transform:translateY(3px) rotate(-3deg) scale(1.04); } to { transform:translateY(-12px) rotate(3deg) scale(1.08); } }
@keyframes cv-ring-clockwise { from { transform:translateY(-50%) rotate(0deg); } to { transform:translateY(-50%) rotate(360deg); } }
@keyframes cv-ring-counter { from { transform:rotate(0deg); } to { transform:rotate(-360deg); } }
#career [data-framer-name^="Company #"].cv-career-reveal { opacity:0 !important; transform:translateY(34px) !important; transition:opacity .65s ease,transform .65s ease !important; }
#career [data-framer-name^="Company #"].cv-career-reveal.cv-visible { opacity:1 !important; transform:none !important; }
#testimonials ul { will-change:transform; }
#testimonials section[style*="opacity:0"] { opacity:1 !important; }
#testimonials li { flex-shrink:0; }
@media (prefers-reduced-motion: reduce) { #home [data-framer-name^="Ellipse"], #home [data-framer-name="Av1"] { animation:none !important; } #career [data-framer-name^="Company #"].cv-career-reveal { opacity:1 !important; transform:none !important; transition:none !important; } }
#about [data-framer-name="Open icon"] { display:none !important; }
#about .framer-iEy58, #about .framer-iEy58 * { -webkit-user-select:none !important; user-select:none !important; cursor:default !important; }
#projects [data-framer-name="Logo"] { display:none !important; }
#projects a[data-framer-name^="Project #"] [data-framer-name="Desktop"],
#projects a[data-framer-name^="Project #"] [data-framer-name="Phone"],
#projects a[data-framer-name^="Project #"] [data-framer-name="Image"] { border-radius:50% !important; overflow:hidden !important; }
#projects a[data-framer-name^="Project #"] [data-framer-name="Image"] > div,
#projects a[data-framer-name^="Project #"] [data-framer-name="Image"] img { border-radius:50% !important; object-fit:cover !important; }
#projects a[data-framer-name^="Project #"] { top:-105px; }
#projects a[data-framer-name^="Project #"] [data-framer-name="Ellipse-"] { animation:cv-project-ring 45s linear infinite; }
@keyframes cv-project-ring { from { transform:translate(-50%,-50%) rotate(0deg); } to { transform:translate(-50%,-50%) rotate(360deg); } }
#projects .framer-1hfa4bz-container { opacity:1 !important; transform:none !important; }
#projects .framer-1hfa4bz-container > section { opacity:1 !important; }
#projects .framer-1hfa4bz-container [data-framer-name="Variant 1"] { transform:none !important; opacity:1 !important; }
#projects .framer-1hfa4bz-container ul { width:max-content !important; min-width:100%; animation:cv-other-projects 34s linear infinite; }
#projects .framer-1hfa4bz-container li { flex:none !important; }
@keyframes cv-other-projects { to { transform:translateX(var(--cv-carousel-distance,-1828px)); } }
@media(min-width:810px) { #projects [data-framer-name="Small header"] { margin-top:-268px; } }
@media(max-width:809px) { #projects a[data-framer-name^="Project #"] { top:-40px; } #projects [data-framer-name="Project slider"] { margin-bottom:-112px; } }
@media(prefers-reduced-motion:reduce) { #projects a[data-framer-name^="Project #"] [data-framer-name="Ellipse-"], #projects .framer-1hfa4bz-container ul { animation:none !important; } }
[data-framer-name="Remove Me (Remix Button)"] { display: none !important; }
[data-framer-name="Created and Built"], [data-framer-name="404"] { display: none !important; }
.cv-details { width:min(100%,1200px); margin:68px auto 0; color:#17191c; }
.cv-details-heading span { font-size:13px; font-weight:600; text-transform:uppercase; letter-spacing:.12em; }
.cv-details-heading h3 { font-family:Geist,Arial,sans-serif; font-size:clamp(38px,5vw,68px); line-height:1.05; letter-spacing:-.05em; margin:14px 0; }
.cv-details-heading p { font-size:18px; margin:0 0 28px; }
.cv-details-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; }
.cv-details-grid>div { background:#fff; border-radius:18px; padding:28px; min-width:0; }
.cv-details-grid h4 { font-size:20px; line-height:1.2; margin:0 0 13px; }
.cv-details-grid p { font-size:16px; line-height:1.5; margin:0; }
.cv-experience-details { width:min(100% - 72px,1100px); margin:64px auto 0; color:#17191c; }
.cv-experience-details>h3 { font-size:clamp(28px,3vw,40px); letter-spacing:-.04em; margin:0 0 24px; }
.cv-experience-details article { display:grid; grid-template-columns:minmax(260px,1fr) 1.4fr; gap:28px; background:#fff; border-radius:12px; padding:25px 30px; margin:12px 0; }
.cv-experience-details h4 { font-size:19px; line-height:1.25; margin:0 0 7px; }
.cv-experience-details span { font-size:14px; color:#5c6268; }
.cv-experience-details p { font-size:16px; line-height:1.5; margin:0; }
.cv-contact-extra { display:flex; flex-wrap:wrap; gap:10px 22px; margin:18px 0; color:#fff; font-size:16px; }
.cv-contact-extra a { color:#fff; }
.cv-downloads { display:flex; flex-wrap:wrap; gap:10px; margin:18px 0 24px; }
.cv-downloads a { color:#111; background:#fff; border-radius:99px; padding:10px 17px; font-size:14px; text-decoration:none; font-weight:600; }
.cv-downloads a img { width:20px; height:20px; vertical-align:middle; margin-right:7px; }
.cv-language-menu[hidden] { display:none !important; }
.cv-language-menu { position:fixed; z-index:100001; width:240px; padding:14px; background:#fff; color:#17191c; border:1px solid #e5e8ed; border-radius:16px; box-shadow:0 16px 40px #0003; font-family:Geist,Arial,sans-serif; }
.cv-language-menu strong { display:block; margin:2px 8px 8px; font-size:14px; }
.cv-language-menu a { display:flex; align-items:center; gap:9px; padding:12px 10px; border-radius:9px; color:#17191c; text-decoration:none; font-size:15px; font-weight:600; }
.cv-language-menu a:hover,.cv-language-menu a:focus-visible { background:#f0f2f5; }
.cv-language-menu img { width:22px; height:22px; }
.framer-0AgRR[data-framer-name="Black"],.framer-0AgRR[data-framer-name="Black phone"],button.framer-7n9Qq { transition:transform .3s ease,box-shadow .3s ease,filter .3s ease; }
.framer-0AgRR[data-framer-name="Black"] [data-framer-name="Icon"],.framer-0AgRR[data-framer-name="Black phone"] [data-framer-name="Icon"],button.framer-7n9Qq [data-framer-name="Icon"] { transition:transform .35s cubic-bezier(.2,.8,.2,1); }
.framer-0AgRR[data-framer-name="Black"] [data-framer-name^="Arrow"],.framer-0AgRR[data-framer-name="Black phone"] [data-framer-name^="Arrow"],button.framer-7n9Qq [data-framer-name^="Arrow"] { transition:transform .35s ease,opacity .25s ease; }
.framer-0AgRR[data-framer-name="Black"] [data-framer-name="Arrow 2"],.framer-0AgRR[data-framer-name="Black phone"] [data-framer-name="Arrow 2"],button.framer-7n9Qq [data-framer-name="Arrow 2"] { opacity:0; }
.framer-0AgRR[data-framer-name="Black"]:is(:hover,:focus-visible),.framer-0AgRR[data-framer-name="Black phone"]:is(:hover,:focus-visible),button.framer-7n9Qq:is(:hover,:focus-visible) { transform:translateY(-2px); box-shadow:0 9px 20px #0002; filter:brightness(1.08); }
.framer-0AgRR[data-framer-name="Black"]:is(:hover,:focus-visible) [data-framer-name="Icon"],.framer-0AgRR[data-framer-name="Black phone"]:is(:hover,:focus-visible) [data-framer-name="Icon"],button.framer-7n9Qq:is(:hover,:focus-visible) [data-framer-name="Icon"] { transform:translateX(4px); }
.framer-0AgRR[data-framer-name="Black"]:is(:hover,:focus-visible) [data-framer-name="Arrow 1"],.framer-0AgRR[data-framer-name="Black phone"]:is(:hover,:focus-visible) [data-framer-name="Arrow 1"],button.framer-7n9Qq:is(:hover,:focus-visible) [data-framer-name="Arrow 1"] { transform:translateX(18px); opacity:0; }
.framer-0AgRR[data-framer-name="Black"]:is(:hover,:focus-visible) [data-framer-name="Arrow 2"],.framer-0AgRR[data-framer-name="Black phone"]:is(:hover,:focus-visible) [data-framer-name="Arrow 2"],button.framer-7n9Qq:is(:hover,:focus-visible) [data-framer-name="Arrow 2"] { transform:translateX(32px); opacity:1; }
@media(prefers-reduced-motion:reduce){.framer-0AgRR[data-framer-name="Black"],.framer-0AgRR[data-framer-name="Black phone"],button.framer-7n9Qq,.framer-0AgRR [data-framer-name="Icon"],button.framer-7n9Qq [data-framer-name="Icon"],.framer-0AgRR [data-framer-name^="Arrow"],button.framer-7n9Qq [data-framer-name^="Arrow"] { transition:none !important; transform:none !important; }}
@media(prefers-reduced-motion:reduce){.framer-0AgRR [data-framer-name="Arrow 1"],button.framer-7n9Qq [data-framer-name="Arrow 1"] { opacity:1 !important; }.framer-0AgRR [data-framer-name="Arrow 2"],button.framer-7n9Qq [data-framer-name="Arrow 2"] { opacity:0 !important; }}
.cv-mobile-panel { display:none; }
@media(max-width:809px){
  [data-framer-name="Menu mob"] [data-framer-name="Menu icon"] { width:44px !important; height:44px !important; min-height:44px; -webkit-user-select:none; user-select:none; -webkit-tap-highlight-color:transparent; }
  [data-framer-name="Menu mob"] [data-framer-name="Menu icon"] > div { width:36px !important; transition:transform .2s ease; }
  [data-framer-name="Menu mob"] [data-framer-name="Menu icon"][aria-expanded="true"] [data-framer-name="line 1"] { transform:translateY(5px) rotate(45deg) !important; }
  [data-framer-name="Menu mob"] [data-framer-name="Menu icon"][aria-expanded="true"] [data-framer-name="line 2"] { transform:translateY(-5px) rotate(-45deg) !important; }
  [data-framer-name="Menu mob"] [data-framer-name="Menu icon"]:focus { outline:none; }
  [data-framer-name="Menu mob"] [data-framer-name="Menu icon"]:focus-visible { outline:2px solid #17191c; outline-offset:2px; border-radius:4px; }
  .cv-mobile-panel.is-open { display:flex; flex-direction:column; position:fixed; z-index:99999; top:62px; left:0; right:0; max-height:calc(100dvh - 62px); overflow-y:auto; background:#fff; padding:18px 24px 26px; box-shadow:0 16px 24px #0002; }
  .cv-mobile-panel a { color:#17191c; text-decoration:none; font-size:19px; font-weight:600; padding:13px 2px; border-bottom:1px solid #e8eaed; }
  .cv-mobile-panel a:last-child { border:0; }
}
@media(max-width:809px){.cv-details { padding:0 20px; }.cv-details-grid { grid-template-columns:1fr; }.cv-experience-details { width:calc(100% - 40px); }.cv-experience-details article { grid-template-columns:1fr; gap:14px; padding:22px; }}
@media(max-width:809px){#about,#projects,#career,#skills,#blog,#contacts { scroll-margin-top:68px; }}
</style>"""
(ROOT / "styles.css").write_text(static_css.replace('<style id="cv-static-overrides">', '', 1).replace('</style>', '', 1).strip() + "\n")
viewport_guard = '''<style id="cv-viewport-guard">
html, body { width:100%; max-width:100%; overflow-x:clip !important; overscroll-behavior-x:none; }
body > div { max-width:100vw; overflow-x:clip; }
main[data-framer-name="Main"] { max-width:100vw; left:0 !important; transform:none !important; }
</style>'''
source = source.replace("</head>", '<link rel="stylesheet" href="styles.css?v=8">' + viewport_guard + '</head>', 1)
source = source.replace("Prolens | Personal website of an entrepreneur, investor, and business partner", "Abdessalam Ouaouane | E-Commerce & Digital Business Specialist")
source = source.replace("Entrepreneur, investor, and business partner focused on building scalable companies and long-term value. I work with founders and teams to turn ideas into successful ventures through strategy, execution, and hands-on experience.", "CV and portfolio of Abdessalam Ouaouane, e-commerce and digital business specialist based in Casablanca, Morocco.")
source = re.sub(r'<meta name="(?:generator|framer-search-index|framer-search-index-fallback)"[^>]*>', '', source)
source = re.sub(r'<link href="[^"]+" rel="icon"[^>]*>', '<link href="4k-ab-logo.png" rel="icon" type="image/png">', source)
source = re.sub(r'<link rel="apple-touch-icon"[^>]*>', '', source)
source = re.sub(r'<meta (?:property="og:image"|name="twitter:image")[^>]*>', '', source)
source = source.replace('content="summary_large_image"', 'content="summary"')
source = source.replace('https://prolens.framer.website/', 'https://heyabdessalam.info/')

# The Framer form requires the original site's backend. Use a local mailto
# handoff so the visible form has a working outcome on a static deployment.
source = source.replace("</body>", """<div class="cv-language-menu" id="cv-language-menu" role="group" aria-label="Download CV language" hidden>
  <strong>Download full CV</strong>
  <a href="abdessalam-cv-eng.pdf" download><img src="assets/cv-en.svg" alt="">English CV</a>
  <a href="abdessalam-cv-fr.pdf" download><img src="assets/cv-fr.svg" alt="">CV français</a>
</div><nav class="cv-mobile-panel" id="cv-mobile-panel" aria-label="Mobile navigation">
  <a href="#about">About</a><a href="#projects">Projects</a><a href="#career">Career</a>
  <a href="#skills">Skills</a><a href="#blog">Education</a><a href="#contacts">Contact</a>
  <a href="abdessalam-cv-eng.pdf">Download CV</a>
</nav><script>
document.querySelectorAll('[data-framer-name="Remove Me (Remix Button)"], [data-framer-name="Purchase"]').forEach(el => el.remove());
const cvLanguageMenu = document.getElementById('cv-language-menu');
const cvLanguageTriggers = [...document.querySelectorAll('#career a')].filter(link => link.textContent.includes('Download Full CV'));
let activeCvTrigger = null;
function closeCvLanguageMenu() {
  cvLanguageMenu.hidden = true;
  cvLanguageTriggers.forEach(link => link.setAttribute('aria-expanded', 'false'));
  activeCvTrigger = null;
}
cvLanguageTriggers.forEach(link => {
  link.setAttribute('aria-haspopup', 'true');
  link.setAttribute('aria-controls', 'cv-language-menu');
  link.setAttribute('aria-expanded', 'false');
  link.addEventListener('click', event => {
    event.preventDefault();
    if (activeCvTrigger === link && !cvLanguageMenu.hidden) { closeCvLanguageMenu(); return; }
    closeCvLanguageMenu();
    activeCvTrigger = link;
    cvLanguageMenu.hidden = false;
    const rect = link.getBoundingClientRect();
    const left = Math.max(12, Math.min(innerWidth - cvLanguageMenu.offsetWidth - 12, rect.left + (rect.width - cvLanguageMenu.offsetWidth) / 2));
    cvLanguageMenu.style.left = `${left}px`;
    cvLanguageMenu.style.top = `${Math.max(12, rect.top - cvLanguageMenu.offsetHeight - 10)}px`;
    link.setAttribute('aria-expanded', 'true');
  });
});
cvLanguageMenu.querySelectorAll('a').forEach(link => link.addEventListener('click', closeCvLanguageMenu));
document.addEventListener('click', event => { if (!cvLanguageMenu.hidden && !cvLanguageMenu.contains(event.target) && !cvLanguageTriggers.some(link => link.contains(event.target))) closeCvLanguageMenu(); });
document.addEventListener('keydown', event => { if (event.key === 'Escape' && !cvLanguageMenu.hidden) { const trigger = activeCvTrigger; closeCvLanguageMenu(); trigger?.focus(); } });
window.addEventListener('scroll', closeCvLanguageMenu, { passive:true });
window.addEventListener('resize', closeCvLanguageMenu);
document.querySelectorAll('#projects .framer-1hfa4bz-container ul').forEach(rail => {
  const cards = [...rail.children];
  if (!cards.length) return;
  const gap = parseFloat(getComputedStyle(rail).columnGap) || 0;
  const distance = cards.reduce((width, card) => width + (parseFloat(card.style.width) || card.offsetWidth) + gap, 0);
  cards.forEach(card => { const clone = card.cloneNode(true); clone.setAttribute('aria-hidden', 'true'); rail.appendChild(clone); });
  rail.style.setProperty('--cv-carousel-distance', `-${distance}px`);
});
function alignMobileProjectRings() {
  const mobile = matchMedia('(max-width:809px)').matches;
  document.querySelectorAll('#projects a[data-framer-name^="Project #"]').forEach(card => {
    const rings = [...card.querySelectorAll('[data-framer-name="Ellipse-"]')];
    if (!mobile) { rings.forEach(ring => { ring.style.top = ''; ring.style.left = ''; ring.style.bottom = ''; }); return; }
    const photo = [...card.querySelectorAll('[data-framer-name="Image"]')].find(image => image.getBoundingClientRect().width > 0);
    if (!photo) return;
    const imageRect = photo.getBoundingClientRect();
    const cardRect = card.getBoundingClientRect();
    rings.filter(ring => ring.getBoundingClientRect().width > 0).forEach(ring => {
      ring.style.top = `${imageRect.top + imageRect.height / 2 - cardRect.top}px`;
      ring.style.left = `${imageRect.left + imageRect.width / 2 - cardRect.left}px`;
      ring.style.bottom = 'auto';
    });
  });
}
alignMobileProjectRings();
window.addEventListener('load', alignMobileProjectRings);
window.addEventListener('resize', alignMobileProjectRings);
function keepPageCentered() {
  if (window.scrollX !== 0 || document.documentElement.scrollLeft !== 0) {
    window.scrollTo(0, window.scrollY);
    document.documentElement.scrollLeft = 0;
    document.body.scrollLeft = 0;
  }
}
window.addEventListener('pageshow', keepPageCentered);
window.addEventListener('scroll', keepPageCentered, { passive:true });
window.addEventListener('resize', keepPageCentered);
keepPageCentered();
const careerCards = [...document.querySelectorAll('#career [data-framer-name^="Company #"]')];
if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  careerCards.forEach(card => card.classList.add('cv-career-reveal'));
  const careerObserver = new IntersectionObserver(entries => entries.forEach(entry => {
    if (entry.isIntersecting) { entry.target.classList.add('cv-visible'); careerObserver.unobserve(entry.target); }
  }), { threshold:0.12, rootMargin:'0px 0px -6% 0px' });
  careerCards.forEach(card => careerObserver.observe(card));
}
document.querySelectorAll('#testimonials ul').forEach(rail => {
  const cards = [...rail.children];
  cards.forEach(card => { card.setAttribute('aria-hidden', 'false'); const clone = card.cloneNode(true); clone.setAttribute('aria-hidden', 'true'); clone.inert = true; rail.appendChild(clone); });
  let offset = 0, last = 0, paused = false;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  rail.addEventListener('mouseenter', () => paused = true);
  rail.addEventListener('mouseleave', () => paused = false);
  rail.addEventListener('focusin', () => paused = true);
  rail.addEventListener('focusout', () => paused = false);
  function moveReviews(time) {
    const distance = rail.children[cards.length]?.offsetLeft - rail.children[0]?.offsetLeft;
    if (last && distance > 0 && !paused && !reducedMotion.matches && document.visibilityState === 'visible') {
      offset = (offset + Math.min(time - last, 100) * 0.03) % distance;
      rail.style.transform = `translateX(${-offset}px)`;
    }
    last = time;
    requestAnimationFrame(moveReviews);
  }
  requestAnimationFrame(moveReviews);
});
const mobilePanel = document.getElementById('cv-mobile-panel');
const mobileMenuButtons = [...document.querySelectorAll('[data-framer-name="Menu mob"] [data-framer-name="Menu icon"]')];
function setMobileMenu(open) {
  mobilePanel.classList.toggle('is-open', open);
  mobileMenuButtons.forEach(icon => {
    icon.setAttribute('aria-expanded', String(open));
    icon.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
}
document.querySelectorAll('[data-framer-name="Menu mob"]').forEach(header => { header.removeAttribute('tabindex'); header.removeAttribute('data-highlight'); });
mobileMenuButtons.forEach(icon => {
  icon.removeAttribute('data-highlight');
  icon.setAttribute('role', 'button'); icon.setAttribute('aria-label', 'Open menu'); icon.setAttribute('aria-controls', 'cv-mobile-panel'); icon.setAttribute('aria-expanded', 'false');
  const toggle = () => setMobileMenu(!mobilePanel.classList.contains('is-open'));
  icon.addEventListener('click', toggle);
  icon.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); toggle(); } });
});
mobilePanel.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMobileMenu(false)));
document.addEventListener('keydown', event => { if (event.key === 'Escape') setMobileMenu(false); });
document.addEventListener('click', event => { if (mobilePanel.classList.contains('is-open') && !mobilePanel.contains(event.target) && !event.target.closest('[data-framer-name="Menu icon"]')) setMobileMenu(false); });
window.addEventListener('resize', () => { if (innerWidth > 809) setMobileMenu(false); });
document.querySelectorAll('form').forEach(form => form.addEventListener('submit', event => {
  event.preventDefault();
  const values = [...form.querySelectorAll('input, textarea')].map(field => `${field.placeholder || field.name}: ${field.value}`).join('\\n');
  location.href = 'mailto:work@heyabdessalam.info?subject=' + encodeURIComponent('Website enquiry') + '&body=' + encodeURIComponent(values);
}));
</script></body>""", 1)

(ROOT / "index.html").write_text(source)
print(f"Wrote index.html ({len(source):,} characters)")
