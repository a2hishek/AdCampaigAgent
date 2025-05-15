def generate_campaign_prompt(
    brand_name,
    campaign_goal,
    daily_budget,
    start_date,
    end_date,
    page_id,
    brand_description,
    landing_page_url,
    call_to_action,
    image_path,
    age_min, age_max, tone, gender, interests
):
    return f"""
You are a campaign automation agent for Meta Ads.

Keep this user preferences in mind when creating creative elements:
 - Tone of the content: {tone}
 - Gender for which the ad content is created: {gender}
 - Interest of the target audience: {interests}
 - 

Using the provided inputs, generate a complete Facebook ad campaign by calling the tools in the following sequence:

1. Create a campaign using `make_campaign` with:
   - campaign_name = <Choose an appropriate name based on {brand_name} & {campaign_goal}>
   - campaign_goal = "{campaign_goal}"

2. Create an ad set using `make_ad_set` with:
   - ad_set_name = <Give an appropriate name to generate ad set>
   - campaign_id = <use campaign ID from step 1>
   - daily_budget = "{daily_budget}"
   - start_date = "{start_date.strftime('%Y-%m-%dT%H:%M:%S')}"
   - end_date = "{end_date.strftime('%Y-%m-%dT%H:%M:%S')}"
   - age_min = {age_min}
   - age_max = {age_max}

3. Create a creative using `make_ad_creative` with:
   - ad_creative_name = <Give an appropriate name to generate ad creative>
   - page_id = "{page_id}"
   - ad_description = <Give a good description for ad creative based on {brand_description}"
   - landing_page_url = "{landing_page_url}"
   - ad_headline = <Give a catchy headline {brand_name} & {brand_description}>
   - call_to_action = "{call_to_action}"
   - image_path = "{image_path}"

4. Finally, create an ad using `make_ad` with:
   - ad_name = <Give an appropriate name to generate ad>
   - ad_set_id = <use ad set ID from step 2>
   - creative_id = <use creative ID from step 3>

Make sure each step passes its output (like campaign_id, ad_set_id, creative_id) correctly to the next step.

Pause the ad after creation. Output the final ad ID at the end. 
Or Ask for valid credentials if not provided.
"""



def generate_campaign_prompt_dict(campaign_goal, brand_name, landing_page, daily_budget, start_date,
                                  end_date, call_to_action, product_name, brand_description, image_path,
                                   tone, image_style_prompt, age_min, age_max, gender, country, interests ):
    return {
        "campaign_goal": campaign_goal,
        "campaign_name": "suggest a campaign name",
        "landing_page": landing_page,
        "daily_budget": daily_budget,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "call_to_action": call_to_action,
        "product_name": product_name,
        "brand_description": brand_description,
        "image_path": image_path,
        "tone": tone,
        "image_style": image_style_prompt,
        "audience": {
            "age_min": age_min,
            "age_max": age_max,
            "gender": gender,
            "country": country,
            "interests": interests
        }
    }
