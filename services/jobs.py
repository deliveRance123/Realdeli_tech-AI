# -*- coding: utf-8 -*-
import logging
import aiohttp

logger = logging.getLogger(__name__)

# Free remote jobs endpoints
JOBICY_URL = "https://jobicy.com/api/v2/remote-jobs?count=10"
REMOTIVE_URL = "https://remotive.com/api/remote-jobs?limit=10"


async def fetch_remote_jobs(category: str = "all", limit: int = 5) -> list:
    """Fetch live remote jobs from free public APIs."""
    jobs = []
    
    # Try Jobicy API first
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(JOBICY_URL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    raw_jobs = data.get("jobs", [])
                    for j in raw_jobs:
                        title = j.get("jobTitle", "Remote Opportunity")
                        company = j.get("companyName", "Direct Employer")
                        cat = j.get("jobCategory", "Remote")
                        url = j.get("url", "https://jobicy.com")
                        geo = j.get("jobGeo", "Anywhere")
                        
                        # Filter by category keyword if specified
                        if category != "all":
                            combined = (title + " " + cat).lower()
                            if category.lower() not in combined:
                                continue

                        jobs.append({
                            "title": title,
                            "company": company,
                            "category": cat,
                            "url": url,
                            "location": geo,
                        })
                        if len(jobs) >= limit:
                            break
    except Exception as e:
        logger.error(f"Error fetching from Jobicy: {e}")

    # If Jobicy returned few results, try Remotive
    if len(jobs) < limit:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(REMOTIVE_URL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        raw_jobs = data.get("jobs", [])
                        for j in raw_jobs:
                            title = j.get("title", "Remote Opportunity")
                            company = j.get("company_name", "Direct Employer")
                            cat = j.get("category", "Tech")
                            url = j.get("url", "https://remotive.com")
                            
                            if category != "all":
                                combined = (title + " " + cat).lower()
                                if category.lower() not in combined:
                                    continue

                            jobs.append({
                                "title": title,
                                "company": company,
                                "category": cat,
                                "url": url,
                                "location": "Worldwide / Remote",
                            })
                            if len(jobs) >= limit:
                                break
        except Exception as e:
            logger.error(f"Error fetching from Remotive: {e}")

    return jobs[:limit]