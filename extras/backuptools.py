from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from datetime import datetime
import getpass, os

load_dotenv()


if not os.environ.get("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = getpass.getpass("Tavily API key:\n")

search_tool = TavilySearch(max_results = 2)


FacebookAdsApi.init(
    access_token=os.getenv("META_ACCESS_TOKEN"),
    app_id=os.getenv("META_APP_ID"),
    app_secret=os.getenv("META_APP_SECRET")
)
account = AdAccount(os.getenv("META_AD_ACCOUNT_ID"))

CAMPAIGN_OBJECTIVE_MAP = {
    "Awareness": "REACH",
    "Conversions": "CONVERSIONS",
    "Traffic": "LINK_CLICKS",
    "App Installs": "APP_INSTALLS",
    "Lead Generation": "LEAD_GENERATION",
}
CTA_MAP = {
        "Learn More": "LEARN_MORE",
        "Shop Now": "SHOP_NOW",
        "Sign Up": "SIGN_UP",
        "Book Now": "BOOK_TRAVEL",
        "Download": "DOWNLOAD",
    }

@tool()
def make_campaign(campaign_name: str, campaign_goal: str) -> str:
    """
    Creates a Meta Ad campaign for the given brand and goal.
    
    Args:
        campaign_name: appropriate name for the ad campaign.
        campaign_goal: The campaign objective .

    Returns:
        The campaign ID of the newly created campaign.
    """
    campaign = account.create_campaign(params={
        'name': f"{campaign_name}",
        'objective': CAMPAIGN_OBJECTIVE_MAP.get(campaign_goal),  
        'status': 'PAUSED'
    })
    return campaign['id']


@tool
def make_ad_set(
    ad_set_name: str,
    campaign_id: str,
    daily_budget: float,
    start_date: datetime,
    end_date: datetime,
    age_min: int,
    age_max: int
) -> str:
    """
    Creates a Meta Ad Set under a given campaign.

    Args:
        ad_set_name: appropriate name for the ad set.
        campaign_id: The ID of the campaign to attach this Ad Set to.
        daily_budget: Daily budget in USD.
        start_date: Campaign start date (datetime).
        end_date: Campaign end date (datetime).
        age_min: Minimum age to set in targeting
        age_max: Maximum age to set in targeting

    Returns:
        The Ad Set ID of the newly created Ad Set.
    """
    ad_set = account.create_ad_set(params={
        'name': f"{ad_set_name}",
        'campaign_id': campaign_id,
        'daily_budget': int(daily_budget * 100),  # Meta uses cents
        'billing_event': 'IMPRESSIONS',
        'optimization_goal': 'LINK_CLICKS',
        'targeting': {
            'geo_locations': {'countries': ['US']},
            'age_min': age_min,
            'age_max': age_max,
        },
        'start_time': start_date.strftime('%Y-%m-%dT%H:%M:%S'),
        'end_time': end_date.strftime('%Y-%m-%dT%H:%M:%S'),
        'status': 'PAUSED',
    })
    return ad_set['id']


@tool
def make_ad_creative(
    ad_creative_name: str,
    page_id: str,
    ad_description: str,
    landing_page_url: str,
    ad_headline: str,
    call_to_action: str,
    image_path: str
) -> str:
    """
    Creates an ad creative with image, description, headline, and CTA.

    Args:
        ad_creative_name: appropriate name for the ad creative.
        page_id: The Facebook Page ID.
        ad_description: Description text for the ad.
        landing_page_url: URL to which the ad will link.
        ad_headline: The headline/caption of the ad.
        call_to_action: CTA type (e.g., 'LEARN_MORE', 'SHOP_NOW').
        image_path: Local file path of the image to upload.

    Returns:
        The ID of the created ad creative.
    """
    # Upload image to Meta Ads library
    image = account.create_ad_image(params={
        'filename': image_path
    })
    image_hash = image['hash']

    # Create ad creative
    creative = account.create_ad_creative(params={
        'name': f"{ad_creative_name}",
        'object_story_spec': {
            'page_id': page_id,
            'link_data': {
                'message': ad_description,
                'link': landing_page_url,
                'caption': ad_headline,
                'image_hash': image_hash,
                'call_to_action': {
                    'type': CTA_MAP.get(call_to_action, 'LEARN_MORE')
                }
            }
        }
    })

    return creative['id']

@tool
def make_ad(
    ad_name: str,
    ad_set_id: str,
    creative_id: str
) -> str:
    """
    Creates a Meta Ad using the given Ad Set and Creative.

    Args:
        ad_name: appropriate name for the ad.
        ad_set_id: ID of the Ad Set.
        creative_id: ID of the Ad Creative.

    Returns:
        The ID of the created Ad.
    """
    ad = account.create_ad(params={
        'name': f"{ad_name}",
        'adset_id': ad_set_id,
        'creative': {'creative_id': creative_id},
        'status': 'PAUSED'
    })
    return ad['id']