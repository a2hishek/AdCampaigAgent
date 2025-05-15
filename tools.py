from langchain_core.tools import tool
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from datetime import datetime
import getpass, os

load_dotenv()

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



class GenerateCampaign(BaseModel):
    """Generates a Meta Ad Campaign"""
    campaign_name: str = Field(description="Name of the Campaign")
    campaign_goal: str = Field(description="Objective of the Campaign")


class GenerateAdSet(BaseModel):
    """Generates a Meta Ad Set under an Ad Campaign"""
    campaign_id: str = Field(description="A campaign id used to generate an ad set under the campaign")
    page_id: str = Field(description="The id of the page for which the campaign runs the ad")
    ad_set_name: str = Field(description="Name of the Ad set under the campaign")
    daily_budget: str = Field(description="Daily budget for the adset")

class GenerateAdCreative(BaseModel):
    """Generates a Meta Ad Creative under an Ad Set"""
    description: str = Field(description="A catchy one liner description for the ad")
    image_hash: str = Field(description="A hexadecimal string representing an uploaded image")
    creative_name: str = Field(description="A name for the ad creative that comes under the ad set")
    page_id: str = Field(description="The id of the page for which the campaign runs the ad")
    
class GenerateImageHash(BaseModel):
    """Uploads an image from given file path and creates an image hash"""
    image_path: str = Field(description="A path to the image used in ad creative")

class GenerateAd(BaseModel):
    """Generates a Meta Ad under an Ad set using the Ad creative."""
    ad_set_id: str = Field(description="Id of the Ad set under which the ad will run.")
    ad_name: str = Field(description="A name for the ad")
    creative_id: str = Field(description="Id of the Ad Creative that has the creative elements for the Ad.")


if not os.environ.get("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = getpass.getpass("Tavily API key:\n")

search_tool = TavilySearch(max_results = 2)


@tool("campaignGeneratorTool", args_schema=GenerateCampaign)
def make_campaign(campaign_name: str, campaign_goal: str) -> str:
   
    fields = [
        ]
    params = {
        'objective': CAMPAIGN_OBJECTIVE_MAP.get(campaign_goal),
        'status': 'PAUSED',
        'buying_type': 'AUCTION',
        'name': campaign_name,
    }
    campaign = account.create_campaign(
        fields=fields,
        params=params,
    )
    campaign_id = campaign['id']

    return {"campaign_id": campaign_id}
    

@tool("adsetGeneratorTool", args_schema=GenerateAdSet)
def make_ad_set(campaign_id, page_id, ad_set_name, daily_budget):
    fields = [
    ]
    params = {
        'status': 'PAUSED',
        'targeting': {'geo_locations': {'countries': ['US']}},
        'daily_budget': daily_budget,
        'billing_event': 'IMPRESSIONS',
        'bid_amount': '20',
        'campaign_id': campaign_id,
        'optimization_goal': 'PAGE_LIKES',
        'promoted_object': {'page_id': page_id},
        'name': ad_set_name,
    }

    ad_set = account.create_ad_set(
        fields=fields,
        params=params,
    )
    ad_set_id = ad_set.get_id()

    return {"ad_set_id": ad_set_id}

@tool("adCreativeGeneratorTool", args_schema=GenerateAdCreative)
def make_ad_creative(description, creative_name, page_id, image_hash):
    fields = [
]
    params = {
        'body': description,
        'image_hash': image_hash,
        'name': creative_name,
        'object_id': page_id,
        'title': 'My Page Like Ad',
    }
    creative = account.create_ad_creative(
        fields=fields,
        params=params,
    )
    creative_id = creative.get_id()

    return {"creative_id": creative_id}


@tool("imageGeneratorTool", args_schema=GenerateImageHash)
def make_ad_image(image_path):
    image = account.create_ad_image(params={
        'filename': image_path
    })
    image_hash = image['hash']

    return {"image_hash": image_hash}


@tool("adGeneratorTool", args_schema=GenerateAd)
def make_ad(ad_set_id, creative_id, ad_name):
    fields = [
    ]
    params = {
        'status': 'PAUSED',
        'adset_id': ad_set_id,
        'name': ad_name,
        'creative': {'creative_id': creative_id},
        'ad_format': 'DESKTOP_FEED_STANDARD',
    }
    ad = account.create_ad(
        fields=fields,
        params=params,
    )
    ad_id = ad.get_id()

    return {"ad_id": ad_id}