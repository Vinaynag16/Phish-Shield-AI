import re
from urllib.parse import urlparse

class URLExtractor:
    def __init__(self):
        # Suspicious keywords often found in phishing URLs
        self.suspicious_words = ['login', 'verify', 'update', 'secure', 'account', 'bank', 'ebayisapi', 'webscr']

    def extract_features(self, url):
        features = {}
        
        # Ensure url has a scheme for parsing
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        parsed = urlparse(url)
        hostname = parsed.netloc
        path = parsed.path

        # 1. URL Length
        features['url_length'] = len(url)
        
        # 2. Number of dots in hostname (e.g., mail.google.com.secure.com)
        features['dot_count'] = hostname.count('.')
        
        # 3. Presence of IP address instead of domain
        features['is_ip'] = 1 if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname) else 0
        
        # 4. Presence of '@' symbol (used to hide the real domain)
        features['has_at_symbol'] = 1 if '@' in url else 0
        
        # 5. Presence of '-' in domain (Phishers love hyphens)
        features['has_hyphen'] = 1 if '-' in hostname else 0
        
        # 6. Number of subdomains
        features['subdomain_count'] = len(hostname.split('.')) - 2 if len(hostname.split('.')) > 2 else 0

        # 7. Presence of suspicious keywords
        features['suspicious_keyword_count'] = sum(1 for word in self.suspicious_words if word in url.lower())

        # 8. Use of URL Shorteners (bit.ly, t.co, etc)
        shorteners = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs"
        features['is_shortened'] = 1 if re.search(shorteners, url) else 0

        # 9. Count of special characters
        features['special_char_count'] = sum(url.count(char) for char in ['?', '=', '&', '%', '!'])

        return features

# Test snippet
if __name__ == "__main__":
    extractor = URLExtractor()
    sample_url = "http://secure-login-verify-account.bit.ly/update?user=admin"
    print(f"Features for: {sample_url}")
    print(extractor.extract_features(sample_url))