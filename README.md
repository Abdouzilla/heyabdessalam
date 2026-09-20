# heyabdessalam

Abdessalam Ouaouane's online CV and portfolio.

Open `index.html` to view the site. It uses the saved Prolens Framer export in `prolens.framer.website/` as its layout and replaces the sample content with information from `abdessalam-cv-eng.pdf` and `abdessalam-cv-fr.pdf`.

Run `python3 build-from-prolens.py` after changing the content map in that file. It generates `index.html` and `styles.css`. The page is static and needs no build service. The English and French PDFs are linked from the page.

The project and education sections use locally stored illustrative images generated for this CV; they are not photographs of Abdessalam's actual projects or school. Some fonts and decorative assets in the saved export still load from Framer. The hero uses the supplied `heroface.png`; the header and favicon use `4k-ab-logo.png`. The contact form opens an email draft rather than posting to the template owner's Framer backend.

The hero and project image rings use the original template artwork. The achievements carousel reuses the template's review layout and continuous motion, but shows factual CV achievements because the PDFs contain no client testimonials. Career cards reveal as they enter the viewport. These animations stop when reduced motion is requested.

Career cards use local Claude and Shopify icons from Simple Icons, the VS Code logo from MicrosoftDocs, and a custom network icon. The email and CV language icons are local SVGs.

## Deploy on Vercel

Import `https://github.com/Abdouzilla/heyabdessalam` into Vercel. Use the repository root as the Root Directory and **Other** as the Framework Preset. The committed `index.html` is ready to serve; no build or install command is needed. `vercel.json` pins the output directory to the repository root.

After a content or style change, run `python3 build-from-prolens.py`, commit the updated `index.html` and `styles.css`, and push to `main`. The saved Framer editor and authentication pages are excluded from Git; only the original page and public assets required by the generator are included.
