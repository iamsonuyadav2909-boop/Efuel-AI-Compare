"""
Shared trusted-domain scoring logic for search providers (Tavily, Exa, future
Google CSE / SerpAPI providers). Centralized so every provider ranks sources
consistently, with Indian manufacturers/distributors prioritized.
"""

# Known trusted manufacturer / engineering domains for EV Charger & Solar components.
# Indian entities listed first as they are prioritized for this deployment.
TRUSTED_DOMAINS = [
    # India-focused manufacturers, distributors & marketplaces
    'havells.com', 'polycab.com', 'rrkabel.com', 'legrand.co.in', 'schneider-electric.co.in',
    'lntebg.com', 'larsentoubro.com', 'crompton.co.in', 'cgglobal.com', 'hpl.in',
    'indoasian.com', 'standardelectricals.com', 'anchor-electricals.com', 'panasonic.com',
    'exicom.in', 'luminousindia.com', 'servokon.com', 'vguard.in', 'orientelectric.com',
    'finolex.com', 'kei-ind.com', 'apar.com', 'waaree.com', 'tatapower.com',
    'adanisolar.com', 'vikramsolar.com', 'goldiengroup.com', 'utlsolar.co.in',
    'amaron.com', 'exide.com', 'indiamart.com', 'tradeindia.com',
    # Global manufacturers with strong India presence
    'schneider-electric.com', 'se.com', 'abb.com', 'siemens.com', 'siemens-energy.com',
    'eaton.com', 'legrand.com', 'legrand.us', 'chint.com', 'chintglobal.com',
    'mennekes.de', 'phoenixcontact.com', 'te.com', 'huawei.com', 'sungrowpower.com',
    'growatt.com', 'solaredge.com', 'fimer.com', 'socomec.com', 'delta-electronics.com',
    'victronenergy.com', 'sma.de', 'ge.com', 'generalelectric.com', 'rittal.com',
    'weidmuller.com', 'omron.com', 'wago.com', 'finder.com', 'hager.com', 'rst.co.in',
    'staubli.com', 'amphenol-industrial.com', 'tesla.com', 'delta.com.tw', 'vestas.com',
    'canadiansolar.com', 'jinkosolar.com', 'trinasolar.com', 'longi.com', 'meanwell.com',
]

INDIA_TRUSTED_SUFFIXES = ('.co.in', '.in')


def domain_trust_score(url: str) -> float:
    """Score a URL's trustworthiness for engineering procurement research (0-1)."""
    url_l = (url or '').lower()
    is_india_domain = any(
        url_l.split('/')[2].endswith(suf) if '://' in url_l and len(url_l.split('/')) > 2 else False
        for suf in INDIA_TRUSTED_SUFFIXES
    )
    for d in TRUSTED_DOMAINS:
        if d in url_l:
            return 0.98 if (d.endswith('.in') or '.co.in' in d) else 0.95
    if is_india_domain:
        return 0.85
    if any(k in url_l for k in ['datasheet', 'catalogue', 'catalog', 'spec', 'technical']):
        return 0.7
    if any(k in url_l for k in ['distributor', 'dealer', 'authorized']):
        return 0.6
    return 0.4
