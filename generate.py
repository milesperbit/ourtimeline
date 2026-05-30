from pathlib import Path
from datetime import datetime
from html import escape
from PIL import Image
from PIL.ExifTags import TAGS


BILD_ENDUNGEN = [".jpg", ".jpeg", ".png", ".webp"]


def aufnahmedatum_lesen(bildpfad):
    try:
        bild = Image.open(bildpfad)
        exif = bild.getexif()

        moegliche_felder = [
            "DateTimeOriginal",
            "DateTimeDigitized",
            "DateTime"
        ]

        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)

            if tag in moegliche_felder:
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")

    except Exception as fehler:
        print(f"Konnte EXIF-Datum nicht lesen für {bildpfad.name}: {fehler}")

    return datetime.fromtimestamp(bildpfad.stat().st_mtime)


def intro_lesen(jahresordner):
    intro_datei = jahresordner / "intro.txt"

    if not intro_datei.exists():
        return {
            "zeitraum": "",
            "text": ""
        }

    inhalt = intro_datei.read_text(encoding="utf-8").strip()
    zeilen = inhalt.splitlines()

    zeitraum = zeilen[0].strip() if len(zeilen) >= 1 else ""
    text = "\n".join(zeilen[1:]).strip() if len(zeilen) >= 2 else ""

    return {
        "zeitraum": zeitraum,
        "text": text
    }


def bildtext_lesen(bildpfad):
    textdatei = bildpfad.with_suffix(".txt")

    if textdatei.exists():
        return textdatei.read_text(encoding="utf-8").strip()

    return ""


def html_absatz(text):
    if not text:
        return ""

    zeilen = [escape(zeile.strip()) for zeile in text.splitlines() if zeile.strip()]
    return "".join(f"<p>{zeile}</p>" for zeile in zeilen)


def jahreszahl_aus_ordnername(ordner):
    return ordner.name.replace("jahr", "").strip()


def timeline_generieren(jahresordner):
    jahr_nummer = jahreszahl_aus_ordnername(jahresordner)
    ausgabe_datei = Path(f"{jahresordner.name}.html")

    intro = intro_lesen(jahresordner)

    bilder = []

    for datei in jahresordner.iterdir():
        if datei.suffix.lower() in BILD_ENDUNGEN:
            datum = aufnahmedatum_lesen(datei)
            bilder.append({
                "pfad": datei.as_posix(),
                "datum": datum,
                "text": bildtext_lesen(datei)
            })

    bilder.sort(key=lambda x: x["datum"])

    html_karten = ""

    for bild in bilder:
        datum_text = bild["datum"].strftime("%d.%m.%Y")
        text_html = html_absatz(bild["text"])

        content_html = f"""
        <div class="card-content">
          <div class="date">{datum_text}</div>
          {f'<div class="memory-text">{text_html}</div>' if text_html else ''}
        </div>
        """

        html_karten += f"""
        <article class="moment">
          <div class="dot"></div>
          <div class="card">
            <img src="{bild['pfad']}" alt="Erinnerung">
            {content_html}
          </div>
        </article>
        """

    zeitraum_html = f"<h2>{escape(intro['zeitraum'])}</h2>" if intro["zeitraum"] else ""
    intro_text_html = html_absatz(intro["text"])

    html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Jahr {jahr_nummer}</title>

  <style>
    * {{
      box-sizing: border-box;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: linear-gradient(180deg, #17111f, #2a1735 46%, #0e0b16);
      color: white;
      min-height: 100vh;
      overflow-x: hidden;
    }}

    .back {{
      position: fixed;
      top: 14px;
      left: 14px;
      z-index: 10;
      color: white;
      background: rgba(255,255,255,.12);
      border: 1px solid rgba(255,255,255,.16);
      padding: 10px 14px;
      border-radius: 999px;
      text-decoration: none;
      font-weight: 700;
      backdrop-filter: blur(10px);
    }}

    .hero {{
      min-height: 20vh;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 80px 22px 32px;
      position: relative;
      overflow: hidden;
    }}

    .hero::before {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        radial-gradient(circle at 20% 20%, rgba(255,255,255,0.12) 0 1px, transparent 2px),
        radial-gradient(circle at 80% 30%, rgba(255,255,255,0.16) 0 1px, transparent 2px),
        radial-gradient(circle at 50% 70%, rgba(255,255,255,0.10) 0 1px, transparent 2px);
      background-size: 120px 120px, 180px 180px, 140px 140px;
      opacity: .75;
    }}

    .hero-content {{
      position: relative;
      z-index: 1;
      max-width: 760px;
    }}

    .eyebrow {{
      letter-spacing: .18em;
      text-transform: uppercase;
      color: #ffd6e7;
      font-size: .78rem;
      font-weight: 800;
      margin-bottom: 14px;
    }}

    h1 {{
      font-size: clamp(2.8rem, 12vw, 6rem);
      line-height: .92;
      margin: 0 0 24px;
    }}

    .hero h2 {{
      font-size: clamp(1.4rem, 5vw, 2.4rem);
      margin: 0 0 26px;
    }}

    .hero p {{
      font-size: clamp(1.05rem, 4vw, 1.45rem);
      line-height: 1.6;
      color: rgba(255,255,255,.82);
      margin: 0 auto 10px;
    }}

    .timeline {{
      width: min(980px, 100%);
      margin: 0 auto;
      padding: 40px 20px 80px;
      position: relative;
    }}

    .timeline::before {{
      content: "";
      position: absolute;
      top: 40px;
      bottom: 80px;
      left: 31px;
      width: 2px;
      background: linear-gradient(#ffd6e7, rgba(255,255,255,.08));
    }}

    .moment {{
      position: relative;
      display: grid;
      grid-template-columns: 32px 1fr;
      gap: 18px;
      margin-bottom: 28px;
      opacity: 0;
      transform: translateY(18px);
      transition: all .7s ease;
    }}

    .moment.visible {{
      opacity: 1;
      transform: translateY(0);
    }}

    .dot {{
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #ffd6e7;
      box-shadow: 0 0 0 7px rgba(255,214,231,.12), 0 0 28px rgba(255,214,231,.7);
      margin-top: 22px;
      z-index: 1;
    }}

    .card {{
      background: rgba(255,255,255,.09);
      border: 1px solid rgba(255,255,255,.14);
      border-radius: 24px;
      overflow: hidden;
      backdrop-filter: blur(10px);
      box-shadow: 0 24px 80px rgba(0,0,0,.24);
    }}

    .card img {{
      width: 100%;
      height: auto;
      display: block;
      background: rgba(255,255,255,.08);
    }}

    .card-content {{
      padding: 18px 20px 20px;
    }}

    .date {{
      color: #ffd6e7;
      font-weight: 800;
      font-size: .9rem;
      margin-bottom: 8px;
    }}

    .memory-text p {{
      margin: 0 0 10px;
      color: rgba(255,255,255,.84);
      line-height: 1.55;
      font-size: 1rem;
    }}

    .memory-text p:last-child {{
      margin-bottom: 0;
    }}

    @media (min-width: 760px) {{
      .timeline::before {{
        left: 50%;
        transform: translateX(-50%);
      }}

      .moment {{
        grid-template-columns: 1fr 32px 1fr;
        gap: 24px;
      }}

      .moment:nth-child(odd) .card {{
        grid-column: 1;
      }}

      .moment:nth-child(odd) .dot {{
        grid-column: 2;
      }}

      .moment:nth-child(even) .dot {{
        grid-column: 2;
      }}

      .moment:nth-child(even) .card {{
        grid-column: 3;
      }}

      .dot {{
        margin-left: 4px;
      }}
    }}
  </style>
</head>

<body>
  <a class="back" href="index.html">← Sternenkarte</a>

  <section class="hero">
    <div class="hero-content">
      <div class="eyebrow">Jahr {jahr_nummer}</div>
      {zeitraum_html}
      {intro_text_html}
    </div>
  </section>

  <main class="timeline">
    {html_karten}
  </main>

  <script>
    const moments = document.querySelectorAll(".moment");

    const observer = new IntersectionObserver((entries) => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{
          entry.target.classList.add("visible");
        }}
      }});
    }}, {{ threshold: 0.15 }});

    moments.forEach(moment => observer.observe(moment));
  </script>
</body>
</html>
"""

    ausgabe_datei.write_text(html, encoding="utf-8")
    print(f"Fertig: {ausgabe_datei} mit {len(bilder)} Bildern.")


jahresordner = sorted([
    ordner for ordner in Path(".").iterdir()
    if ordner.is_dir() and ordner.name.startswith("jahr")
])

if not jahresordner:
    print("Keine Jahresordner gefunden. Lege z. B. einen Ordner 'jahr1' an.")

for ordner in jahresordner:
    timeline_generieren(ordner)