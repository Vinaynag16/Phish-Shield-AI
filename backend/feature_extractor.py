import re
from urllib.parse import urlparse

def get_url_features(url):
    features = {}
    
    # 1. Check for IP Address in URL
    ip_pattern = r"(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-5]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-5]|25[0-5])"
    features['has_ip'] = 1 if re.search(ip_pattern, url) else 0
    
    # 2. Check for "@" symbol
    features['has_at'] = 1 if "@" in url else 0
    
    # 3. URL Length (Phishing URLs > 54 chars are suspicious)
    features['is_long'] = 1 if len(url) >= 54 else 0
    
    # 4. URL Depth (Number of subdirectories)
    parsed_url = urlparse(url)
    path_segments = [s for s in parsed_url.path.split('/') if s]
    features['depth'] = len(path_segments)
    
    # 5. Redirection '//' (Check if '//' exists after the protocol)
    features['redirection'] = 1 if url.rfind('//') > 7 else 0
    
    # 6. Prefix/Suffix '-' (Phishers use hyphens to look legitimate like 'pay-pal.com')
    features['has_hyphen'] = 1 if '-' in parsed_url.netloc else 0
    
    # 7. Count dots in hostname (More than 3 is usually phishing/subdomain abuse)
    features['dot_count'] = parsed_url.netloc.count('.')

    return features

# --- TEST YOUR CODE ---
if __name__ == "__main__":
    test_link = "http://secure-login.paypal.com-update.verify@192.168.1.5/account/secure"
    results = get_url_features(test_link)
    
    print(f"Analyzing: {test_link}")
    for key, value in results.items():
        print(f"{key}: {value}")