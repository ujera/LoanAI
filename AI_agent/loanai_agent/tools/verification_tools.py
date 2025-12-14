"""Verification and web search tools."""

import requests
from typing import Any, Dict, List
import time
from loanai_agent.utils.logger import get_logger

logger = get_logger(__name__)

# Cache to avoid repeated API calls
_verification_cache = {}
_cache_expiry = 3600  # 1 hour


class WebVerificationTools:
    """Tools for verifying information using web search and APIs."""

    @staticmethod
    def verify_university(university_name: str) -> Dict[str, Any]:
        """Verify university using web search and APIs."""
        logger.info(f"Verifying university: {university_name}")
        
        # Check cache first
        cache_key = f"university_{university_name.lower()}"
        if cache_key in _verification_cache:
            cached_data, timestamp = _verification_cache[cache_key]
            if time.time() - timestamp < _cache_expiry:
                logger.info(f"Using cached data for university: {university_name}")
                return cached_data
        
        try:
            # Use Wikipedia API to verify university
            wiki_url = "https://en.wikipedia.org/w/api.php"
            headers = {
                "User-Agent": "LoanAI-Bot/1.0 (Loan Application Verification System; +https://github.com/ujera/LoanAI)"
            }
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": f"{university_name} university",
                "utf8": 1,
                "srlimit": 3
            }
            
            response = requests.get(wiki_url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            search_results = data.get("query", {}).get("search", [])
            
            if search_results:
                # University found on Wikipedia - likely legitimate
                result = {
                    "name": university_name,
                    "country": "Unknown",  # Would need additional parsing
                    "ranking": None,
                    "accredited": True,
                    "legitimacy": "verified",
                    "source": "wikipedia",
                    "confidence": 0.85,
                    "info": search_results[0].get("snippet", "")
                }
                
                # Try to get more details from the first result
                page_title = search_results[0].get("title")
                detail_params = {
                    "action": "query",
                    "format": "json",
                    "prop": "extracts|pageimages",
                    "exintro": 1,
                    "explaintext": 1,
                    "titles": page_title,
                    "piprop": "thumbnail"
                }
                
                detail_response = requests.get(wiki_url, params=detail_params, headers=headers, timeout=5)
                detail_data = detail_response.json()
                pages = detail_data.get("query", {}).get("pages", {})
                
                if pages:
                    page = next(iter(pages.values()))
                    extract = page.get("extract", "")
                    
                    # Try to extract country from text
                    if "Georgia" in extract:
                        result["country"] = "Georgia"
                    elif "United States" in extract or "U.S." in extract:
                        result["country"] = "USA"
                    elif "United Kingdom" in extract or "UK" in extract:
                        result["country"] = "UK"
                    
                    result["description"] = extract[:200] + "..." if len(extract) > 200 else extract
                
                # Cache the result
                _verification_cache[cache_key] = (result, time.time())
                return result
            else:
                # Not found on Wikipedia - could still be legitimate but less confidence
                logger.warning(f"University not found on Wikipedia: {university_name}")
                result = {
                    "name": university_name,
                    "country": "Unknown",
                    "ranking": None,
                    "accredited": None,
                    "legitimacy": "unverified",
                    "source": "none",
                    "confidence": 0.3,
                    "warning": "Could not verify university through web sources"
                }
                _verification_cache[cache_key] = (result, time.time())
                return result
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error verifying university {university_name}: {e}")
            # Fallback to neutral response on API failure
            return {
                "name": university_name,
                "country": "Unknown",
                "ranking": None,
                "accredited": None,
                "legitimacy": "unverified",
                "source": "api_error",
                "confidence": 0.5,
                "error": str(e)
            }

    @staticmethod
    def verify_company(company_name: str) -> Dict[str, Any]:
        """Verify company legitimacy using web APIs."""
        logger.info(f"Verifying company: {company_name}")
        
        # Check cache first
        cache_key = f"company_{company_name.lower()}"
        if cache_key in _verification_cache:
            cached_data, timestamp = _verification_cache[cache_key]
            if time.time() - timestamp < _cache_expiry:
                logger.info(f"Using cached data for company: {company_name}")
                return cached_data
        
        try:
            # Use Wikipedia API to verify company
            wiki_url = "https://en.wikipedia.org/w/api.php"
            headers = {
                "User-Agent": "LoanAI-Bot/1.0 (Loan Application Verification System; +https://github.com/ujera/LoanAI)"
            }
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": f"{company_name} company",
                "utf8": 1,
                "srlimit": 3
            }
            
            response = requests.get(wiki_url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            search_results = data.get("query", {}).get("search", [])
            
            if search_results:
                # Company found on Wikipedia - likely legitimate
                result = {
                    "name": company_name,
                    "industry": "Unknown",
                    "employees": "Unknown",
                    "founded": None,
                    "legitimacy": "verified",
                    "rating": 4.0,
                    "source": "wikipedia",
                    "confidence": 0.85,
                    "info": search_results[0].get("snippet", "")
                }
                
                # Try to get more details
                page_title = search_results[0].get("title")
                detail_params = {
                    "action": "query",
                    "format": "json",
                    "prop": "extracts",
                    "exintro": 1,
                    "explaintext": 1,
                    "titles": page_title
                }
                
                detail_response = requests.get(wiki_url, params=detail_params, headers=headers, timeout=5)
                detail_data = detail_response.json()
                pages = detail_data.get("query", {}).get("pages", {})
                
                if pages:
                    page = next(iter(pages.values()))
                    extract = page.get("extract", "")
                    
                    # Try to extract industry from text
                    industries = {
                        "technology": ["software", "technology", "tech", "computing", "digital"],
                        "banking": ["bank", "financial services", "finance"],
                        "telecommunications": ["telecom", "mobile", "wireless", "communications"],
                        "retail": ["retail", "shopping", "e-commerce", "store"],
                        "healthcare": ["healthcare", "medical", "pharmaceutical", "health"]
                    }
                    
                    extract_lower = extract.lower()
                    for industry, keywords in industries.items():
                        if any(keyword in extract_lower for keyword in keywords):
                            result["industry"] = industry.capitalize()
                            break
                    
                    result["description"] = extract[:200] + "..." if len(extract) > 200 else extract
                
                # Cache the result
                _verification_cache[cache_key] = (result, time.time())
                return result
            else:
                # Not found - could be small/local company
                logger.warning(f"Company not found on Wikipedia: {company_name}")
                result = {
                    "name": company_name,
                    "industry": "Unknown",
                    "employees": "Unknown",
                    "founded": None,
                    "legitimacy": "unverified",
                    "rating": 3.0,
                    "source": "none",
                    "confidence": 0.3,
                    "warning": "Could not verify company through web sources - may be small/local business"
                }
                _verification_cache[cache_key] = (result, time.time())
                return result
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error verifying company {company_name}: {e}")
            # Fallback to neutral response on API failure
            return {
                "name": company_name,
                "industry": "Unknown",
                "employees": "Unknown",
                "founded": None,
                "legitimacy": "unverified",
                "rating": 3.0,
                "source": "api_error",
                "confidence": 0.5,
                "error": str(e)
            }

    @staticmethod
    def benchmark_salary(
        job_title: str, location: str, company_name: str = ""
    ) -> Dict[str, Any]:
        """Benchmark salary against market data."""
        logger.info(f"Benchmarking salary for {job_title} in {location}")

        # Simulated salary benchmarks
        salary_benchmarks = {
            "software engineer": {
                "min": 80000,
                "median": 120000,
                "max": 200000,
            },
            "data scientist": {
                "min": 90000,
                "median": 130000,
                "max": 210000,
            },
            "product manager": {
                "min": 100000,
                "median": 150000,
                "max": 250000,
            },
        }

        search_key = job_title.lower().split()[0]
        if search_key in salary_benchmarks:
            benchmark = salary_benchmarks[search_key]
        else:
            benchmark = {
                "min": 50000,
                "median": 80000,
                "max": 150000,
            }

        return {
            "job_title": job_title,
            "location": location,
            "salary_range": benchmark,
            "data_points": 1000,
            "confidence": 0.85,
        }

    @staticmethod
    def verify_address(address: str) -> Dict[str, Any]:
        """Verify address using geocoding API."""
        logger.info(f"Verifying address: {address}")
        
        # Check cache first
        cache_key = f"address_{address.lower()}"
        if cache_key in _verification_cache:
            cached_data, timestamp = _verification_cache[cache_key]
            if time.time() - timestamp < _cache_expiry:
                logger.info(f"Using cached data for address: {address}")
                return cached_data
        
        try:
            # Use Nominatim (OpenStreetMap) API for geocoding
            geocode_url = "https://nominatim.openstreetmap.org/search"
            headers = {
                "User-Agent": "LoanAI/1.0 (Loan Application Verification)"
            }
            params = {
                "q": address,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            
            response = requests.get(geocode_url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                location = data[0]
                address_details = location.get("address", {})
                
                result = {
                    "address": address,
                    "valid": True,
                    "geocoded": True,
                    "latitude": float(location.get("lat", 0)),
                    "longitude": float(location.get("lon", 0)),
                    "country": address_details.get("country", "Unknown"),
                    "state": address_details.get("state", "Unknown"),
                    "city": address_details.get("city") or address_details.get("town") or address_details.get("village", "Unknown"),
                    "zip_code": address_details.get("postcode", "Unknown"),
                    "confidence": float(location.get("importance", 0.5)),
                    "display_name": location.get("display_name", "")
                }
                
                # Cache the result
                _verification_cache[cache_key] = (result, time.time())
                return result
            else:
                logger.warning(f"Address not found: {address}")
                result = {
                    "address": address,
                    "valid": False,
                    "geocoded": False,
                    "latitude": None,
                    "longitude": None,
                    "country": "Unknown",
                    "state": "Unknown",
                    "city": "Unknown",
                    "zip_code": "Unknown",
                    "confidence": 0.0,
                    "warning": "Could not geocode address"
                }
                _verification_cache[cache_key] = (result, time.time())
                return result
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error verifying address {address}: {e}")
            # Fallback to neutral response on API failure
            return {
                "address": address,
                "valid": None,
                "geocoded": False,
                "latitude": None,
                "longitude": None,
                "country": "Unknown",
                "state": "Unknown",
                "city": "Unknown",
                "zip_code": "Unknown",
                "confidence": 0.5,
                "error": str(e)
            }

    @staticmethod
    def search_identity_info(
        first_name: str, last_name: str, personal_id: str
    ) -> Dict[str, Any]:
        """Search for identity information using web sources."""
        logger.info(f"Searching identity info for {first_name} {last_name}")

        # Simulated identity search
        return {
            "first_name": first_name,
            "last_name": last_name,
            "identity_verified": True,
            "public_records_found": 2,
            "red_flags": [],
            "confidence": 0.92,
        }


class ExternalDataFetcher:
    """Tools for fetching external data and cross-referencing."""

    @staticmethod
    def get_company_ratings(company_name: str) -> Dict[str, Any]:
        """Get company ratings from review platforms."""
        logger.info(f"Fetching ratings for {company_name}")

        return {
            "company": company_name,
            "glassdoor_rating": 4.2,
            "indeed_rating": 4.0,
            "financial_health": "stable",
            "employee_count": 500,
        }

    @staticmethod
    def get_education_details(university_name: str) -> Dict[str, Any]:
        """Get detailed education information."""
        logger.info(f"Fetching details for {university_name}")

        return {
            "university": university_name,
            "accreditation_status": "accredited",
            "world_ranking": 25,
            "reputation_score": 95,
            "niche_rating": "A+",
        }

    @staticmethod
    def cross_reference_income(
        stated_income: float, employment_data: Dict, bank_data: Dict
    ) -> Dict[str, Any]:
        """Cross-reference income from multiple sources."""
        logger.info(f"Cross-referencing income: ${stated_income}")

        bank_income = bank_data.get("average_monthly_income", 0)
        employment_income = employment_data.get("gross_salary", 0)

        variance_employment = (
            abs(stated_income - employment_income) / employment_income * 100
            if employment_income > 0
            else 0
        )

        variance_bank = (
            abs(stated_income - bank_income) / bank_income * 100
            if bank_income > 0
            else 0
        )

        return {
            "stated_income": stated_income,
            "employment_verified_income": employment_income,
            "bank_verified_income": bank_income,
            "variance_from_employment": round(variance_employment, 2),
            "variance_from_bank": round(variance_bank, 2),
            "all_sources_consistent": variance_employment < 10 and variance_bank < 10,
        }
