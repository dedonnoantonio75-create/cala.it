#!/usr/bin/env python3
"""
ING-343 — SEO/SXO optimization for cala.it
1. Rename cryptic image files to SEO-friendly names
2. Update all alt texts with keyword-rich descriptions
3. Improve meta descriptions with AI-search-friendly complete sentences
4. Add FAQPage JSON-LD structured data to faq pages
5. Add VideoObject JSON-LD to pages with YouTube embed
"""

import os
import re
import json
import shutil
from pathlib import Path

REPO    = Path(__file__).parent.parent
IMG_DIR = REPO / 'img'
CSS_SRC = REPO / 'css' / 'style.css'
CSS_MIN = REPO / 'css' / 'style.min.css'

# ── 1. Image rename mapping  (old_stem → new_stem, no extension) ─────────────

RENAME_MAP = {
    'E2-scaled':                 'vista-mare-adriatico-esclusiva-location-cala-dei-balcani-salento',
    'AND01841':                  'sposi-cerimonia-location-matrimoni-cala-dei-balcani-salento',
    'CAL_0407_1':                'giorno-speciale-matrimonio-cala-dei-balcani-santa-cesarea-terme',
    '0003-DJI_0036-scaled':      'panorama-costa-salentina-mare-adriatico-cala-dei-balcani',
    'DJI_0120-1024x768':         'campo-grano-azienda-agricola-la-brunitta-cala-dei-balcani-salento',
    'DJI_0248-copia_-1':         'vista-aerea-drone-torre-saracena-santa-cesarea-terme-salento',
    'DJI_0288-scaled':           'vista-drone-cala-dei-balcani-costa-santa-cesarea-terme-salento',
    'CAN_6759-Modifica-2':       'chef-alta-cucina-salentina-cala-dei-balcani-salento',
    'CAN_6764-Modifica-2':       'cucina-gourmet-ricevimento-matrimonio-cala-dei-balcani-salento',
    'CAN_6775-Modifica':         'ingredienti-freschi-cucina-salentina-cala-dei-balcani',
    'Sam-Megan-2865-scaled':     'sposi-matrimonio-internazionale-cala-dei-balcani-salento-puglia',
    'Sam-Megan-2865-scaled_1':   'sposi-internazionali-wedding-cala-dei-balcani-salento',
    'STI04416-768x512':          'cerimonia-nuziale-arco-floreale-terrazza-cala-dei-balcani-salento',
    '3-scaled':                  'veduta-location-cala-dei-balcani-santa-cesarea-terme-salento',
    '4-scaled':                  'terrazza-panoramica-matrimoni-mare-adriatico-cala-dei-balcani-salento',
    'Panoramica_senza-titolo-0026_web_1920':
                                 'panoramica-notturna-costa-salentina-cala-dei-balcani',
    'Panoramica_senza-titolo-135_web_1920-1024x683':
                                 'panoramica-mare-adriatico-cala-dei-balcani-santa-cesarea-terme',
    '133961716_10224484946421498_989410546601605502_n-1024x683':
                                 'galleria-matrimoni-cala-dei-balcani-salento-puglia',
}

# ── 2. Alt text map  (image stem → improved alt) ─────────────────────────────

ALT_MAP = {
    'logo': 'Logo Cala dei Balcani — location matrimoni di lusso Santa Cesarea Terme Salento Puglia',
    'logo-cala-dei-balcani-nuovo-ristorante-per-ricevimenti-santa-cesarea-terme-lecce-salento-puglia-italia-2-180x49':
        'Logo Cala dei Balcani — ristorante per matrimoni e ricevimenti Santa Cesarea Terme Salento Puglia',

    # Venue / location
    'cerimonia-civile-vista-mare-cala-dei-balcani-santa-cesarea-terme':
        'Cerimonia civile con arco floreale e vista sul mare Adriatico — location matrimoni Cala dei Balcani, Santa Cesarea Terme, Salento',
    'matrimonio-civile-cala-dei-balcani-santa-cesarea-terme-salento':
        'Matrimonio civile in riva al mare Adriatico a Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'santa-cesarea-terme-vista-aerea-accommodation-cala-dei-balcani':
        'Vista aerea di Santa Cesarea Terme sul mare Adriatico — accommodation vicino alla location matrimoni Cala dei Balcani, Salento',
    'cala-dei-balcani-location-matrimoni-wedding-salento-lecce-':
        'Location matrimoni Cala dei Balcani con vista sul mare Adriatico, Santa Cesarea Terme, Salento, Lecce, Puglia',
    'cala-dei-balcani-location-matrimoni-wedding-salento-santa-cesarea-terme-lecce-1':
        'Terrazza panoramica sul mare Adriatico — location matrimoni esclusiva Cala dei Balcani, Santa Cesarea Terme, Salento',
    'cala-dei-balcani-location-matrimoni-wedding-salento-santa-cesarea-terme-lecce-7-scaled':
        'Location matrimoni di lusso Cala dei Balcani con vista sul mare Adriatico, Santa Cesarea Terme, Salento, Puglia',
    'cala-dei-balcani-location-wedding-santa-cesarea-terme-lecce-salento-cerimonie-':
        'Cerimonie e ricevimenti nuziali all\'aperto a Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'cala-dei-balcani-matrimoni-santa-cesarea-terme-lecce-salento':
        'Matrimonio sul mare Adriatico a Cala dei Balcani — location esclusiva Santa Cesarea Terme, Salento',
    'location-per-matrimini-cala-dei-balcani-santa-cesare-terme-costa-adriatica-salentina-salento-lecce-puglia-italia-':
        'La location Cala dei Balcani sulla costa adriatica salentina, Santa Cesarea Terme, Lecce, Puglia, Italia',
    'la-location-per-i-matrimoni-di-cala-dei-balacani-di-santa-cesarea-terme-lecce-1':
        'Location matrimoni Cala dei Balcani — Torre Saracena, terrazze panoramiche e mare Adriatico, Santa Cesarea Terme',
    'la-location-per-i-matrimoni-di-cala-dei-balacani-di-santa-cesarea-terme-lecce-5-1024x768':
        'Vista della location matrimoni Cala dei Balcani da Santa Cesarea Terme, Salento, Lecce, Puglia',
    'cala-dei-balcani-salento-1-1024x683':
        'Panorama della costa del Salento con la location matrimoni Cala dei Balcani, Santa Cesarea Terme, Puglia',

    # Tower
    'cala-dei-balcani-la-torre-saracena-di-santa-cesarea-terme-lecce-salento':
        'Torre Saracena di Monte Saracino del XVI secolo a Cala dei Balcani, Santa Cesarea Terme, Salento, Lecce',
    'la-torre-di-cala-dei-balcani-santa-cesare-aterme-lecce-salento-2':
        'Torre Saracena di Monte Saracino del XVI secolo — Cala dei Balcani, Santa Cesarea Terme, Salento, Lecce',
    'la-torre-di-cala-dei-balcani-santa-cesare-aterme-lecce-salento-4-scaled':
        'Torre Saracena di Cala dei Balcani illuminata di notte — location matrimoni Santa Cesarea Terme, Salento',
    'la-torre-di-cala-dei-balcani-santa-cesare-aterme-lecce-salento-6':
        'Torre Saracena del XVI secolo con vista sul mare Adriatico — Cala dei Balcani, Santa Cesarea Terme, Salento',
    'la-torre-di-cala-dei-balcani-santa-cesare-aterme-lecce-salento-7':
        'La Torre Saracena di Monte Saracino e la costa salentina — Cala dei Balcani, Santa Cesarea Terme, Puglia',
    'la-torre-di-cala-dei-balcani-santa-cesare-aterme-lecce-salento-8':
        'Dettaglio della Torre Saracena — simbolo storico di Santa Cesarea Terme, Cala dei Balcani, Salento',
    'la-torre-di-cala-dei-balcani-santa-cesare-aterme-lecce-salento-9':
        'Vista della Torre Saracena dal mare Adriatico — Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'la-torre-di-cala-dei-balcani-santa-cesarea-terme-ristorante-per-matrimoni-e-ricevimenti-salento-lecce-puglia-italia-24-scaled':
        'Torre Saracena e sala ristorante per matrimoni Cala dei Balcani, Santa Cesarea Terme, Lecce, Salento',
    'la-torre-di-cala-dei-balcani-santa-cesarea-terme-ristorante-per-matrimoni-e-ricevimenti-salento-lecce-puglia-italia-40-scaled':
        'Terrazza con Torre Saracena per matrimoni di lusso — Cala dei Balcani, Santa Cesarea Terme, Salento',

    # Garden / terraces
    'giardino-cala-dei-balcani-ristorante-per-matrimoni-location-matrimonio-salento-lecce-29':
        'Giardino della Quercia di Cala dei Balcani per cerimonie all\'aperto, Santa Cesarea Terme, Salento, Lecce',
    'la-terrazza-di-cala-dei-balcani-ristorante-per-cerimonie-nuziali-santa-cesarea-gterme-lecce-salento-puglia-italia-1':
        'Terrazza verde per cerimonie nuziali con vista sul mare Adriatico — Cala dei Balcani, Santa Cesarea Terme, Salento',
    '1-terrazza-panoramica-cala-dei-balcani-ristoranti-per-matrimoni-santa-cesarea-terme-lecce-salento-puglia-italia-14-scaled':
        'Terrazza panoramica sul mare Adriatico per matrimoni di lusso — Cala dei Balcani, Santa Cesarea Terme, Salento',
    'terrazza-di-cala-dei-balcani-location-matrimoni-slaento-santa-cesarea-terme-lecce-16':
        'Terrazza di Cala dei Balcani con allestimento matrimonio — Santa Cesarea Terme, Salento, Lecce, Puglia',

    # Restaurant / halls
    'cala-dei-balcani-ristorante-per-matrimoni-santa-cesarea-terme-salento-lecce-puglia-1':
        'Ristorante per matrimoni Cala dei Balcani — ricevimenti nuziali con vista mare, Santa Cesarea Terme, Salento, Puglia',
    'cala-dei-balcani-ristorante-per-matrimoni-santa-cesarea-terme-salento-lecce-puglia-2':
        'Sala ristorante per matrimoni e ricevimenti a Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'cala-dei-balcani-ristorante-per-matrimoni-santa-cesarea-terme-salento-lecce-puglia-3':
        'Terrazza panoramica del ristorante per matrimoni Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'cala-dei-balcani-ristorante-per-matrimoni-santa-cesarea-terme-salento-lecce-puglia-4':
        'Sala allestita per ricevimento nuziale — Cala dei Balcani, Santa Cesarea Terme, Lecce, Salento',
    'cala-dei-balcani-ristorante-per-matrimoni-santa-cesarea-terme-salento-lecce-puglia-5':
        'Vista notturna della location matrimoni Cala dei Balcani sul mare Adriatico, Santa Cesarea Terme, Salento',
    'cala-dei-balcani-sala-interna-ristorante-per-ricevimenti-location-eventi-lecce-salento-':
        'Sala interna del ristorante Cala dei Balcani per ricevimenti nuziali, Lecce, Salento, Puglia',
    'cala-dei-balcani-ristorante-matrimoni-salento-lecce-santa-cesarea-terme-puglia-italia-7-768x512':
        'Dettaglio sala ristorante matrimoni Cala dei Balcani, Santa Cesarea Terme, Lecce, Salento, Puglia',

    # Cuisine
    'cucina-piatti-ristorazione-cala-dei-balcani-santa-cesarea-terme-lecce-salento-puglia-italia-1':
        'Alta cucina salentina per matrimoni e ricevimenti a Cala dei Balcani — piatti tipici della tradizione pugliese',
    'cucina-piatti-ristorazione-cala-dei-balcani-santa-cesarea-terme-lecce-salento-puglia-italia-2':
        'Antipasti tradizionali del Salento per banchetti nuziali a Cala dei Balcani, Santa Cesarea Terme, Puglia',
    'cucina-piatti-ristorazione-cala-dei-balcani-santa-cesarea-terme-lecce-salento-puglia-italia-3':
        'Secondi piatti di pesce adriatico per menu nozze — alta ristorazione Cala dei Balcani, Salento, Puglia',
    'cucina-piatti-ristorazione-cala-dei-balcani-santa-cesarea-terme-lecce-salento-puglia-italia-6':
        'Piatti della tradizione salentina per matrimoni di lusso a Cala dei Balcani, Puglia, Italia',
    'cucina-piatti-ristorazione-cala-dei-balcani-santa-cesarea-terme-lecce-salento-puglia-italia-7':
        'Alta gastronomia salentina per banchetti nuziali a Cala dei Balcani, Santa Cesarea Terme, Lecce, Salento',
    'primi-piatti-cala-dei-balcani':
        'Primi piatti della cucina salentina per matrimoni di lusso a Cala dei Balcani, Santa Cesarea Terme, Puglia',
    'Ricci-di-polpo-su-doppia-consistenza-di-caciocavallo-podolico-rotolini-di-peperoni-e-pomodorini':
        'Ricci di polpo su doppia consistenza di caciocavallo podolico — alta cucina salentina per matrimoni Cala dei Balcani',
    'Panciotti-di-melanzane-e-scamorza-con-filetti-di-pomodoro-di-bue-e-carpaccio-di-cernia':
        'Panciotti di melanzane e scamorza con filetti di pomodoro — cucina gourmet per nozze Cala dei Balcani, Salento',
    'Tagliolini-al-nero-di-seppia-su-foglia-di-tonno':
        'Tagliolini al nero di seppia su foglia di tonno — menu matrimonio gourmet Cala dei Balcani, Salento, Puglia',
    'Tortino-di-pesce-spada-con-soppressata-di-polpo-crema-di-pecorino-finocchio-marinato-e-chicchi-di-melagrana':
        'Tortino di pesce spada con soppressata di polpo — haute cuisine per banchetti nuziali Cala dei Balcani, Salento',
    'Darna-di-ombrina-con-cubo-di-carota-al-Roquefort-miele-e-noci':
        'Darna di ombrina con cubo di carota al Roquefort, miele e noci — menu esclusivo nozze Cala dei Balcani, Puglia',
    'Scaloppa-di-orata-su-insalata-liquida-di-bietola-rossa-cilindro-di-patata-in-olio-cottura-e-cicorelle':
        'Scaloppa di orata su insalata liquida di bietola rossa — alta cucina per matrimoni Cala dei Balcani, Salento',
    'Riso-Vialone-Nano-con-gamberetti-vongole-e-coriandoli-di-verdure-con-cialda-di-corallo':
        'Riso Vialone Nano con gamberetti e vongole — primo piatto matrimoni Cala dei Balcani, Santa Cesarea Terme',
    'Tagliatelle-di-seppia-e-patate-ratta':
        'Tagliatelle di seppia e patate ratta — eccellenza culinaria salentina per ricevimenti nuziali Cala dei Balcani',

    # Renamed cryptic → new alt
    'vista-mare-adriatico-esclusiva-location-cala-dei-balcani-salento':
        'Vista del mare Adriatico con esclusiva totale — location matrimoni Cala dei Balcani, Santa Cesarea Terme, Salento',
    'sposi-cerimonia-location-matrimoni-cala-dei-balcani-salento':
        'Sposi durante la cerimonia a Cala dei Balcani — location matrimoni esclusiva Santa Cesarea Terme, Salento',
    'giorno-speciale-matrimonio-cala-dei-balcani-santa-cesarea-terme':
        'Il giorno più bello: coppia di sposi a Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'panorama-costa-salentina-mare-adriatico-cala-dei-balcani':
        'Panorama della costa salentina e del mare Adriatico da Cala dei Balcani, Santa Cesarea Terme, Puglia',
    'campo-grano-azienda-agricola-la-brunitta-cala-dei-balcani-salento':
        'Campo di grano Senatore Cappelli dell\'Azienda Agricola La Brunitta di Cala dei Balcani, Salento, Puglia',
    'vista-aerea-drone-torre-saracena-santa-cesarea-terme-salento':
        'Vista aerea con drone della Torre Saracena e del mare Adriatico — Cala dei Balcani, Santa Cesarea Terme, Salento',
    'vista-drone-cala-dei-balcani-costa-santa-cesarea-terme-salento':
        'Vista drone della costa di Santa Cesarea Terme — location matrimoni Cala dei Balcani, Salento, Puglia',
    'chef-alta-cucina-salentina-cala-dei-balcani-salento':
        'Chef dell\'alta cucina salentina per matrimoni e ricevimenti a Cala dei Balcani, Santa Cesarea Terme, Salento',
    'cucina-gourmet-ricevimento-matrimonio-cala-dei-balcani-salento':
        'Cucina gourmet salentina per ricevimento nuziale a Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'ingredienti-freschi-cucina-salentina-cala-dei-balcani':
        'Ingredienti freschi del territorio per la cucina salentina d\'eccellenza di Cala dei Balcani, Santa Cesarea Terme',
    'sposi-matrimonio-internazionale-cala-dei-balcani-salento-puglia':
        'Sposi durante matrimonio internazionale a Cala dei Balcani — International Wedding in Salento, Puglia, Italy',
    'sposi-internazionali-wedding-cala-dei-balcani-salento':
        'Sposi internazionali al matrimonio a Cala dei Balcani — International & Cozy Wedding, Salento, Puglia',
    'cerimonia-nuziale-arco-floreale-terrazza-cala-dei-balcani-salento':
        'Cerimonia nuziale con arco floreale sulla terrazza panoramica di Cala dei Balcani, Santa Cesarea Terme, Salento',
    'veduta-location-cala-dei-balcani-santa-cesarea-terme-salento':
        'Veduta della location matrimoni Cala dei Balcani a Santa Cesarea Terme sul mare Adriatico, Salento, Puglia',
    'terrazza-panoramica-matrimoni-mare-adriatico-cala-dei-balcani-salento':
        'La terrazza panoramica di Cala dei Balcani per matrimoni di lusso con vista sul mare Adriatico, Santa Cesarea Terme',
    'panoramica-notturna-costa-salentina-cala-dei-balcani':
        'Panoramica notturna della costa salentina da Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'panoramica-mare-adriatico-cala-dei-balcani-santa-cesarea-terme':
        'Panoramica sul mare Adriatico da Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'galleria-matrimoni-cala-dei-balcani-salento-puglia':
        'Galleria di matrimoni a Cala dei Balcani — location esclusiva per nozze a Santa Cesarea Terme, Salento, Puglia',

    # Wedding
    'INTERNATIONAL-AND-COZY-WEDDING-cala-dei-balcani-santa-cesarea-terme-lecce-salento-puglia-italia-':
        'International and Cozy Wedding a Cala dei Balcani — matrimoni internazionali sul mare Adriatico, Salento, Puglia',
    'INTERNATIONAL-AND-COZY-WEDDING-cala-dei-balcani-santa-cesarea-terme-lecce-salento-puglia-italia-2':
        'Matrimonio internazionale intimo ed elegante a Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'wedding-location-santa-ceasrea-terme-salento-lecce-matrimoni-al-mare-puglia-9':
        'Sposi durante cerimonia con vista mare Adriatico — wedding location Cala dei Balcani, Santa Cesarea Terme, Salento',
    'sposi-cala-dei-balcani-santa-cesarea-terme-lecce-salento-puglia-italia--scaled':
        'Sposi felici dopo la cerimonia di matrimonio a Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'matrimonio-cala-dei-balcani-santa-cesarea-terme':
        'Schema degli spazi per matrimoni a Cala dei Balcani — mappa location Santa Cesarea Terme, Salento',
    'location-wedding-santa-cesarea-terme-salento-lecce-puglia-italia-2':
        'Location matrimoni Santa Cesarea Terme con vista mare Adriatico — Cala dei Balcani, Salento, Lecce, Puglia',
    'location-wedding-santa-cesarea-terme-salento-lecce-puglia-italia-5':
        'Sposi in un momento speciale alla location matrimoni Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'location-wedding-santa-cesarea-terme-salento-lecce-puglia-italia-7':
        'Vista del mare Adriatico dalla location matrimoni Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'location-wedding-santa-cesarea-terme-salento-lecce-puglia-italia-8':
        'Tramonto sul mare Adriatico dalla terrazza location matrimoni Cala dei Balcani, Santa Cesarea Terme, Salento',

    # Gallery
    'gallery-01': 'Vista panoramica sul mare Adriatico — location matrimoni Cala dei Balcani, Santa Cesarea Terme, Salento',
    'gallery-02': 'Location matrimoni Cala dei Balcani a Santa Cesarea Terme con vista sul mare Adriatico, Salento, Puglia',
    'gallery-03': 'Terrazza di Cala dei Balcani — spazio cerimonie e cocktail per matrimoni a Santa Cesarea Terme, Salento',
    'gallery-04': 'Allestimento sala ricevimenti matrimoni a Cala dei Balcani, Santa Cesarea Terme, Salento, Puglia',
    'gallery-05': 'Sposi sul terrazzo con vista mare Adriatico — matrimoni di lusso Cala dei Balcani, Santa Cesarea Terme',

    # History
    'la-storia-di-cala-dei-balcani-location-matrimoni-salento-santa-cesarea-terme-lecce-puglia-italia-1-1-scaled':
        'La storia di Cala dei Balcani: Maria Cristina Urso e la location matrimoni di lusso a Salento dal 2003',
    'la-storia-di-cala-dei-balcani-location-matrimoni-salento-santa-cesarea-terme-lecce-puglia-italia-5-1-scaled':
        'La famiglia Urso — custodi di Cala dei Balcani, location matrimoni esclusiva sul mare Adriatico, Salento',
    'la-storia-di-cala-dei-balcani-location-matrimoni-salento-santa-cesarea-terme-lecce-puglia-italia-7-scaled':
        'Maria Cristina Urso fondatrice di Cala dei Balcani, location matrimoni di lusso Santa Cesarea Terme, Salento',
    'la-storia-di-cala-dei-balcani-location-matrimoni-salento-santa-cesarea-terme-lecce-puglia-italia-9-scaled':
        'Cala dei Balcani: oltre 20 anni di matrimoni sul mare Adriatico del Salento — Santa Cesarea Terme, Puglia',
    'la-storia-di-cala-dei-balcani-location-matrimoni-salento-santa-cesarea-terme-lecce-puglia-italia-14-scaled':
        'Evento fotografico a Cala dei Balcani — location matrimoni Santa Cesarea Terme, Salento, Puglia',
    'la-storia-di-cala-dei-balcani-location-matrimoni-salento-santa-cesarea-terme-lecce-puglia-italia-18-1-scaled':
        'La famiglia Urso celebra i 20+ anni di Cala dei Balcani — location matrimoni dal 2003 a Santa Cesarea Terme, Salento',
    'la-storia-di-cala-dei-balcani-location-matrimoni-salento-santa-cesarea-terme-lecce-puglia-italia-18-scaled':
        'Panoramica di Cala dei Balcani con la famiglia Urso — 20+ anni di matrimoni sul mare Adriatico, Salento',

    # Farm
    'campo-di-grano-senatore-cappelli-mietitura-cala-dei-balcani':
        'Mietitura del grano Senatore Cappelli — Azienda Agricola La Brunitta di Cala dei Balcani, Salento, Puglia',

    # Rivivi
    'rivivi-il-tuo-si-del-tuo-giorno-speciale-in-cala-dei-balcani-ristorante-per-matrimoni-santa-cesarea-terme-lecce-salento-puglia-italia':
        'Rinnova le promesse e rivivi il tuo Sì a Cala dei Balcani — anniversario di matrimonio a Santa Cesarea Terme, Salento',

    # Accommodation
    '0003-DJI_0036-scaled':
        'Panorama della costa salentina e del mare Adriatico da Cala dei Balcani, Santa Cesarea Terme, Puglia',
}

# ── 3. Meta description updates (AI-search optimized) ────────────────────────

META_UPDATES = {
    # IT root
    'index.html': (
        "Cala dei Balcani — Location di Lusso per Matrimoni | Santa Cesarea Terme, Salento",
        "Se cerchi la migliore location per matrimoni vista mare in Salento, Cala dei Balcani a Santa Cesarea Terme (Via Roma 5, 73020 Lecce, Puglia) offre terrazze panoramiche sull'Adriatico, la storica Torre Saracena del XVI secolo, cucina salentina d'eccellenza e totale esclusiva. Cerimonie civili in location, capienza fino a 230 ospiti. La risposta a: dove sposarsi con vista mare in Puglia."
    ),
    'matrimoni.html': (
        "Matrimoni di Lusso in Puglia — Vista Mare | Cala dei Balcani, Santa Cesarea Terme, Salento",
        "Cala dei Balcani è la location esclusiva per matrimoni di lusso a Santa Cesarea Terme nel Salento: Torre Saracena del Cinquecento, terrazze panoramiche sul mare Adriatico, giardini mediterranei e totale esclusiva per il vostro giorno speciale in Puglia. Matrimoni civili, religiosi e unioni civili con cucina salentina d'eccellenza fino a 230 ospiti."
    ),
    'cucina.html': (
        "Cucina Salentina di Lusso per Matrimoni — Alta Gastronomia | Cala dei Balcani, Santa Cesarea Terme",
        "La cucina di Cala dei Balcani per matrimoni e ricevimenti nuziali in Salento: ingredienti a km zero dell'azienda agricola La Brunitta, pesce fresco dell'Adriatico e specialità pugliesi in chiave gourmet. Il miglior rapporto qualità-prezzo per banchetti di lusso a Santa Cesarea Terme, Lecce, Puglia. Menu personalizzati per ogni coppia."
    ),
    'il-luogo.html': (
        "Il Luogo — Santa Cesarea Terme sul Mare Adriatico | Cala dei Balcani, Salento, Puglia",
        "Cala dei Balcani si trova a Santa Cesarea Terme (Via Roma 5, 73020 Lecce), sulla costa più suggestiva del Salento meridionale, con terrazze panoramiche sul mare Adriatico e la Torre Saracena del Monte Saracino. La location ideale per chi cerca dove sposarsi con vista mare in Puglia o dove organizzare un ricevimento esclusivo in Salento."
    ),
    'la-torre.html': (
        "La Torre Saracena di Monte Saracino — Simbolo XVI Secolo | Cala dei Balcani, Santa Cesarea Terme",
        "La Torre Saracena di Monte Saracino a Cala dei Balcani è una delle torri costiere adriatiche più affascinanti del XVI secolo, oggi cornice unica per cerimonie e matrimoni a Santa Cesarea Terme, Salento. Chi cerca una location matrimoni con torre storica in Puglia o un luogo suggestivo sul mare Adriatico per le proprie nozze trova qui la risposta."
    ),
    'faq.html': (
        "FAQ Matrimoni Cala dei Balcani — Domande Frequenti | Santa Cesarea Terme, Salento, Puglia",
        "Tutte le risposte alle domande più frequenti su matrimoni e ricevimenti a Cala dei Balcani, Santa Cesarea Terme (Salento, Puglia): capienza (fino a 230 ospiti), esclusiva totale, cerimonia civile in location, parcheggio, accessibilità, menu, periodo migliore. Se ti chiedi come scegliere una location matrimoni vista mare in Salento, qui trovi tutto."
    ),
    'galleria.html': (
        "Galleria Fotografica — Matrimoni, Luoghi, Cucina | Cala dei Balcani, Salento",
        "Galleria fotografica di Cala dei Balcani: immagini di matrimoni di lusso, cerimonie civili, banchetti nuziali, Torre Saracena, terrazze panoramiche sul mare Adriatico e alta cucina salentina a Santa Cesarea Terme, Lecce, Puglia. Scopri perché Cala dei Balcani è la location matrimoni vista mare più scelta in Salento."
    ),
    'testimonianze.html': (
        "Testimonianze Sposi — Recensioni Autentiche | Cala dei Balcani, Santa Cesarea Terme, Salento",
        "Le parole delle coppie che hanno scelto Cala dei Balcani per il loro matrimonio: testimonianze autentiche su esperienze, cucina salentina, servizio e la magia del matrimonio vista mare Adriatico a Santa Cesarea Terme, Salento, Puglia. Leggi perché ci scelgono ogni anno sposi italiani e internazionali."
    ),
    'chi-siamo.html': (
        "Chi Siamo — La Famiglia Urso dal 2003 | Cala dei Balcani, Santa Cesarea Terme, Salento",
        "Cala dei Balcani è nata nel 2003 dalla visione di Maria Cristina Urso, custode di un luogo unico sulla costa salentina del mare Adriatico. Scopri la storia della famiglia che ogni anno accoglie coppie da tutto il mondo per matrimoni esclusivi a Santa Cesarea Terme, Lecce, Puglia. Una location autentica, non un semplice ristorante adattato."
    ),
    'salento.html': (
        "Salento — La Terra Perfetta per Matrimoni Vista Mare | Santa Cesarea Terme, Puglia, Italia",
        "Il Salento, terra di mare, storia e sole, è la cornice ideale per matrimoni da sogno in Puglia. Scopri perché Santa Cesarea Terme è tra le destinazioni matrimoni più richieste in Italia: mare Adriatico cristallino, paesaggi mozzafiato e la magia di Cala dei Balcani con la Torre Saracena. Ispirazione per chi cerca dove sposarsi in Puglia."
    ),
    'accommodation.html': (
        "Accommodation Vicino Cala dei Balcani — Hotel e B&B | Santa Cesarea Terme, Salento",
        "Strutture ricettive consigliate vicino a Cala dei Balcani a Santa Cesarea Terme: hotel, resort, B&B e appartamenti a pochi passi dalla location matrimoni. Dove alloggiare a Santa Cesarea Terme per un matrimonio o evento in Salento, Puglia. Guida completa all'accommodation per sposi e ospiti."
    ),
    'rivivi-il-tuo-si.html': (
        "Rivivi il Tuo Sì — Rinnova le Promesse a Cala dei Balcani | Salento, Puglia",
        "Rinnova le promesse di matrimonio e rivivi il tuo Sì a Cala dei Balcani, Santa Cesarea Terme — un evento speciale con tappeto rosso, cena di gala e brindisi sul mare Adriatico del Salento. Per gli anniversari e le coppie che vogliono rivivere la magia del loro giorno speciale in Puglia."
    ),
    'matrimoni-internazionali.html': (
        "Matrimoni Internazionali — International & Cozy Wedding | Cala dei Balcani, Salento, Italy",
        "Cala dei Balcani accoglie coppie internazionali per matrimoni intimi ed eleganti in Salento, Puglia, Italia. International & Cozy Weddings con staff multilingue, menu personalizzati e la magia della Torre Saracena sul mare Adriatico. La risposta per chi cerca a wedding venue in Italy with sea view o un lieu de mariage en Italie exclusif."
    ),
    # EN
    'en/index.html': (
        "Cala dei Balcani — Luxury Wedding Venue in Puglia | Salento, Adriatic Coast, Italy",
        "Looking for the best wedding venue in Puglia with sea views? Cala dei Balcani in Santa Cesarea Terme (Via Roma 5, 73020 Lecce, Salento, Puglia, Italy) offers panoramic Adriatic terraces, a 16th-century Saracen Tower, Salentine haute cuisine and exclusive use of the entire estate. Civil ceremonies, weddings and celebrations for up to 230 guests. The answer to: where to get married in Italy with sea view."
    ),
    'en/weddings.html': (
        "Weddings in Puglia — Luxury Adriatic Wedding Venue | Cala dei Balcani, Salento, Italy",
        "Cala dei Balcani is the premier exclusive wedding venue in Salento, Puglia, Italy: a 16th-century Saracen Tower, panoramic Adriatic terraces, Mediterranean gardens and full exclusive use for your dream wedding. Civil ceremonies, religious weddings and same-sex unions — up to 230 guests — with exceptional Salentine cuisine. The most requested wedding venue by sea in southern Italy."
    ),
    'en/cuisine.html': (
        "Salentine Cuisine for Weddings — Haute Gastronomy | Cala dei Balcani, Puglia, Italy",
        "The restaurant at Cala dei Balcani for wedding receptions in Salento: zero-km ingredients from the La Brunitta farm estate, fresh Adriatic seafood and Apulian specialities elevated to haute cuisine. The best value luxury wedding catering in Santa Cesarea Terme, Lecce, Puglia. Bespoke menus for every couple."
    ),
    'en/venue.html': (
        "The Venue — Santa Cesarea Terme on the Adriatic | Cala dei Balcani, Salento, Puglia",
        "Cala dei Balcani sits at Via Roma 5, 73020 Santa Cesarea Terme (Lecce, Salento, Puglia, Italy) — a clifftop estate on the Adriatic with panoramic terraces and the 16th-century Saracen Tower of Monte Saracino. The perfect answer for couples asking where to get married in Italy by the sea or looking for an exclusive wedding venue on the Adriatic coast."
    ),
    'en/faq.html': (
        "Wedding FAQ — Cala dei Balcani | Santa Cesarea Terme, Salento, Puglia, Italy",
        "All the answers to your questions about weddings and events at Cala dei Balcani, Santa Cesarea Terme (Salento, Puglia, Italy): capacity (up to 230 guests), exclusive use of the venue, civil ceremony on-site, parking, accessibility, menu options, best season. Everything you need to know before booking a wedding venue in Puglia with sea view."
    ),
    # FR
    'fr/index.html': (
        "Cala dei Balcani — Domaine de Mariage de Luxe | Salento, Pouilles, Italie",
        "Vous cherchez le meilleur lieu de mariage en Italie avec vue sur la mer ? Cala dei Balcani à Santa Cesarea Terme (Via Roma 5, 73020 Lecce, Salento, Pouilles) offre des terrasses panoramiques sur l'Adriatique, la Tour Sarrasine du XVIe siècle et une exclusivité totale pour votre mariage de rêve en Puglia. Cérémonies civiles, mariages et réceptions jusqu'à 230 convives."
    ),
    'fr/mariages.html': (
        "Mariages de Rêve en Puglia — Vue sur la Mer | Cala dei Balcani, Salento, Italie",
        "Cala dei Balcani est le domaine exclusif pour les mariages de luxe à Santa Cesarea Terme, Salento : Tour Sarrasine du XVIe siècle, terrasses panoramiques sur l'Adriatique, jardins méditerranéens et exclusivité totale. La réponse à : où se marier en Italie avec vue sur la mer ? Jusqu'à 230 invités, cuisine salentine d'exception."
    ),
    # DE
    'de/index.html': (
        "Cala dei Balcani — Luxus Hochzeitslocation | Salento, Apulien, Italien",
        "Suchen Sie die beste Hochzeitslocation in Italien mit Meeresblick? Cala dei Balcani in Santa Cesarea Terme (Via Roma 5, 73020 Lecce, Salento, Apulien) bietet Panoramaterrassen mit Blick auf die Adria, einen Sarazenturm aus dem 16. Jahrhundert und exklusive Nutzung der gesamten Anlage. Standesamtliche Trauungen, Hochzeiten und Feiern für bis zu 230 Gäste in Süditalien."
    ),
    'de/hochzeiten.html': (
        "Traumhochzeiten in Apulien — Hochzeitslocation am Meer | Cala dei Balcani, Salento",
        "Cala dei Balcani ist die exklusive Hochzeitslocation in Santa Cesarea Terme, Salento: Sarazenturm aus dem 16. Jahrhundert, Panoramaterrassen an der Adria, mediterrane Gärten und Alleinnutzung für Ihre Traumhochzeit in Apulien. Wo kann man in Italien am Meer heiraten? Hier ist die Antwort. Bis zu 230 Gäste, apulische Hochzeitsgastronomie."
    ),
    # ES
    'es/index.html': (
        "Cala dei Balcani — Lugar de Bodas de Lujo | Salento, Puglia, Italia",
        "¿Buscáis el mejor lugar de bodas en Italia con vistas al mar? Cala dei Balcani en Santa Cesarea Terme (Via Roma 5, 73020 Lecce, Salento, Puglia) ofrece terrazas panorámicas sobre el Adriático, la Torre Sarracena del siglo XVI y uso exclusivo de toda la finca para vuestra boda de ensueño en Puglia. Ceremonias civiles y bodas para hasta 230 invitados."
    ),
    'es/bodas.html': (
        "Bodas de Lujo en Puglia — Vistas al Mar Adriático | Cala dei Balcani, Salento, Italia",
        "Cala dei Balcani es el venue exclusivo para bodas de lujo en Santa Cesarea Terme, Salento: Torre Sarracena del siglo XVI, terrazas panorámicas sobre el Adriático, jardines mediterráneos y exclusividad total. La respuesta a: ¿dónde casarse en Italia con vistas al mar? Hasta 230 invitados, cocina salentina de alta calidad."
    ),
}

# ── 4. FAQPage JSON-LD for FAQ pages ─────────────────────────────────────────

# Detect FAQ questions in HTML and build FAQPage schema
FAQ_PAGES = [
    'faq.html',
    'en/faq.html',
    'fr/faq.html',
    'es/faq.html',
    'de/faq.html',
]

# ── Helper: minify CSS  ───────────────────────────────────────────────────────

def minify_css(src):
    out = re.sub(r'/\*[\s\S]*?\*/', '', src)
    out = re.sub(r'[ \t]+', ' ', out)
    out = re.sub(r' *([\{\};,>~+]) *', r'\1', out)
    out = re.sub(r'\n+', '', out)
    out = out.replace(';}', '}')
    return out.strip()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Rename cryptic image files
# ══════════════════════════════════════════════════════════════════════════════

print("=== 1/4  Renaming cryptic image files ===")

# Build reverse map: new_stem → old_stem (for reference)
rename_count  = 0
css_text      = CSS_SRC.read_text('utf-8')
css_changed   = False

for old_stem, new_stem in RENAME_MAP.items():
    for ext in ('.jpg', '.jpeg', '.png', '.webp'):
        old_path = IMG_DIR / (old_stem + ext)
        if not old_path.exists():
            continue
        new_path = IMG_DIR / (new_stem + ext)
        if new_path.exists():
            print(f"  SKIP {old_stem}{ext} → already exists")
            continue
        shutil.copy2(str(old_path), str(new_path))
        # Keep old file for backward compat (Netlify cache may still serve it)
        rename_count += 1
        print(f"  ✓ {old_stem}{ext} → {new_stem}{ext}")
        # Update CSS references
        if old_stem + ext in css_text:
            css_text = css_text.replace(old_stem + ext, new_stem + ext)
            css_changed = True

if css_changed:
    CSS_SRC.write_text(css_text, 'utf-8')
    CSS_MIN.write_text(minify_css(css_text), 'utf-8')
    print(f"  CSS updated with renamed files")

print(f"  {rename_count} files copied to SEO-friendly names\n")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Update alt texts in all HTML files
# ══════════════════════════════════════════════════════════════════════════════

print("=== 2/4  Updating alt texts ===")

# Build a lookup by stem (no ext): stem → new alt
# Also include renamed stems
alt_lookup = dict(ALT_MAP)
for old_stem, new_stem in RENAME_MAP.items():
    if new_stem in alt_lookup:
        old_alt = alt_lookup.get(old_stem)
        if old_alt:
            alt_lookup[new_stem] = old_alt

HTML_FILES = sorted(REPO.rglob('*.html'))
alt_total = 0

def stem_of(src):
    """Extract filename stem from an img src path."""
    name = src.split('/')[-1]
    return os.path.splitext(name)[0]

def improve_alt(tag, alt_lookup):
    """
    Given an <img ...> tag, return a version with an improved alt attribute
    if the stem matches ALT_MAP.
    """
    src_m = re.search(r'\bsrc=["\']([^"\']+)["\']', tag)
    if not src_m:
        return tag, False
    src  = src_m.group(1)
    stem = stem_of(src)
    new_alt = alt_lookup.get(stem)
    if not new_alt:
        return tag, False
    # Replace existing alt=""
    if 'alt="' in tag or "alt='" in tag:
        new_tag = re.sub(r'\balt=["\'][^"\']*["\']', f'alt="{new_alt}"', tag)
    else:
        # Add alt before >
        new_tag = tag.rstrip('/>').rstrip() + f' alt="{new_alt}">'
    return new_tag, (new_tag != tag)

for html_file in HTML_FILES:
    text = html_file.read_text('utf-8')
    orig = text
    counter = [0]  # mutable to allow capture in closure

    def replace_img_alt(m, _counter=counter):
        new_tag, did_change = improve_alt(m.group(0), alt_lookup)
        if did_change:
            _counter[0] += 1
        return new_tag

    text = re.sub(r'<img\b[^>]*>', replace_img_alt, text)
    changed = counter[0]

    # Also update src references from old → new for renamed files (in <picture><source srcset="...">)
    for old_stem, new_stem in RENAME_MAP.items():
        for ext in ('.jpg', '.jpeg', '.png', '.webp'):
            old_ref = old_stem + ext
            new_ref = new_stem + ext
            if old_ref in text:
                text = text.replace(old_ref, new_ref)

    if text != orig:
        html_file.write_text(text, 'utf-8')
        alt_total += changed
        print(f"  {html_file.relative_to(REPO)}: {changed} alt(s) updated")

print(f"  Total: {alt_total} alt attributes improved\n")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Update meta descriptions
# ══════════════════════════════════════════════════════════════════════════════

print("=== 3/4  Updating meta descriptions ===")
meta_count = 0

for rel_path, (new_title, new_desc) in META_UPDATES.items():
    html_file = REPO / rel_path
    if not html_file.exists():
        print(f"  SKIP {rel_path} (not found)")
        continue
    text = html_file.read_text('utf-8')
    orig = text

    # Update <title>
    text = re.sub(r'<title>[^<]*</title>', f'<title>{new_title}</title>', text, count=1)

    # Update meta name="description"
    text = re.sub(
        r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']*["\'][^>]*/?>',
        f'<meta name="description" content="{new_desc}">',
        text, count=1
    )
    # Also handle reversed attribute order
    text = re.sub(
        r'<meta\s+content=["\'][^"\']*["\']\s+name=["\']description["\'][^>]*/?>',
        f'<meta name="description" content="{new_desc}">',
        text, count=1
    )

    if text != orig:
        html_file.write_text(text, 'utf-8')
        meta_count += 1
        print(f"  {rel_path}")

print(f"  {meta_count} pages updated\n")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Add FAQPage JSON-LD to faq pages
# ══════════════════════════════════════════════════════════════════════════════

print("=== 4/4  Adding FAQPage JSON-LD ===")
faq_count = 0

def extract_faq_qa(html_text):
    """Extract Q&A pairs from faq-box HTML structure."""
    pairs = []
    pattern = re.compile(
        r'class=["\']faq-box__q["\'][^>]*>(.*?)</(?:h\d|p)>.*?'
        r'class=["\']faq-box__a["\'][^>]*>(.*?)</(?:p|div)>',
        re.DOTALL | re.IGNORECASE
    )
    for m in pattern.finditer(html_text):
        q = re.sub(r'<[^>]+>', '', m.group(1)).replace('&egrave;', 'è').replace('&rsquo;', "'").replace('&eacute;', 'é').replace('&agrave;', 'à').replace('&mdash;', '—').replace('&nbsp;', ' ').strip()
        a = re.sub(r'<[^>]+>', '', m.group(2)).replace('&egrave;', 'è').replace('&rsquo;', "'").replace('&eacute;', 'é').replace('&agrave;', 'à').replace('&mdash;', '—').replace('&nbsp;', ' ').strip()
        if q and a:
            pairs.append({'@type': 'Question', 'name': q,
                          'acceptedAnswer': {'@type': 'Answer', 'text': a}})
    return pairs

FAQ_SCHEMA_SENTINEL = '"@type": "FAQPage"'

for rel_faq in FAQ_PAGES:
    faq_file = REPO / rel_faq
    if not faq_file.exists():
        continue
    text = faq_file.read_text('utf-8')
    if FAQ_SCHEMA_SENTINEL in text:
        print(f"  SKIP {rel_faq} (FAQPage already present)")
        continue

    pairs = extract_faq_qa(text)
    if not pairs:
        print(f"  SKIP {rel_faq} (no Q&A found)")
        continue

    schema = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': pairs
    }
    schema_tag = f'\n  <script type="application/ld+json">\n  {json.dumps(schema, ensure_ascii=False, indent=2)}\n  </script>'

    # Insert before </head>
    if '</head>' in text:
        text = text.replace('</head>', schema_tag + '\n</head>', 1)
        faq_file.write_text(text, 'utf-8')
        faq_count += 1
        print(f"  ✓ {rel_faq} — {len(pairs)} Q&A pairs")
    else:
        print(f"  WARN {rel_faq} — no </head> found")

print(f"  {faq_count} FAQ pages updated\n")
print("=== All done! ===")
