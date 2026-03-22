# Extraído de: LibroPQC/cap-08-certificados.md
def scan_urls(self, urls: List[str], max_workers: int = 5,
              depth: str = 'standard',
              discover_subdomains: bool = False,
              analysis_type: str = 'web_application') -> List[CertificateInfo]:
    """Escanear múltiples URLs en paralelo"""
    all_urls = []

    # Descubrimiento de subdominios si está habilitado
    if discover_subdomains:
        for url in urls:
            root_domain = self._extract_root_domain(url)
            discovered = self._discover_all_subdomains(root_domain, depth)
            for domain in discovered:
                all_urls.append(f"https://{domain}")
    else:
        all_urls = urls

    # Escaneo paralelo
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(self.scan_url, url, analysis_type): url
            for url in all_urls
        }
        for future in concurrent.futures.as_completed(future_to_url):
            try:
                results.append(future.result())
            except Exception as e:
                results.append(CertificateInfo(
                    url=future_to_url[future], is_valid=False,
                    error=str(e), ...
                ))

    self.results = results
    return results
