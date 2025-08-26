# tools/place_photo_tools.py

import os
import uuid
import logging
import asyncio

from dotenv import load_dotenv
import googlemaps
from googlemaps.exceptions import ApiError as GoogleMapsApiError

from tools.creative_backend_tools import bucket


logger = logging.getLogger(__name__)
load_dotenv()

# --- Google Maps Client Initialization ---
try:
    MAPS_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not MAPS_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable for Google Maps not set.")
    gmaps_client = googlemaps.Client(key=MAPS_API_KEY)
    logger.info("Initialized Google Maps client.")
except Exception as e:
    logger.error(f"Failed to initialize Google Maps client: {e}")
    raise

PLACE_PHOTOS_GCS_PREFIX = os.getenv("PLACE_PHOTOS_GCS_PREFIX", "place_photos/")


async def fetch_and_upload_place_photos(place_name: str, max_photos: int = 3) -> tuple[list[str], str]:
    """
    Finds a place, downloads multiple photos, uploads them to GCS, and returns a
    list of public HTTPS URLs and the place's display name.
    """
    logger.info(f"Tool processing request for place: '{place_name}'")
    loop = asyncio.get_event_loop()

    # --- 1. Geocode to find Place ID (Now non-blocking) ---
    geocode_result = await loop.run_in_executor(
        None, lambda: gmaps_client.geocode(place_name)
    )
    if not geocode_result or not geocode_result[0].get('place_id'):
        raise FileNotFoundError(f"Could not find a valid place or place_id for '{place_name}'.")

    place_id = geocode_result[0]['place_id']
    actual_place_name = geocode_result[0].get('formatted_address', place_name)
    logger.info(f"Found place_id '{place_id}' for '{actual_place_name}'.")

    # --- 2. Get Place Photo References (Now non-blocking) ---
    place_details = await loop.run_in_executor(
        None, lambda: gmaps_client.place(place_id=place_id, fields=['name', 'photo'])
    )
    if not (place_details and 'result' in place_details and 'photos' in place_details['result'] and place_details['result']['photos']):
        raise FileNotFoundError(f"No photos found for '{actual_place_name}' (place_id: {place_id}).")

    photo_references = place_details['result']['photos']

    async def upload_photo(photo_ref):
        try:
            current_loop = asyncio.get_event_loop()
            logger.info(f"Fetching photo data for ref: {photo_ref['photo_reference'][:20]}...")
            
            # --- Fetch photo data (Now non-blocking) ---
            photo_data_chunks = await current_loop.run_in_executor(
                None,
                lambda: gmaps_client.places_photo(
                    photo_reference=photo_ref['photo_reference'], max_width=800
                )
            )
            image_bytes = b"".join(photo_data_chunks)

            gcs_file_name = f"{PLACE_PHOTOS_GCS_PREFIX.strip('/')}/{uuid.uuid4()}.jpg"
            blob = bucket.blob(gcs_file_name)
            
            # --- Upload to GCS (Already correctly handled) ---
            await current_loop.run_in_executor(
                None, 
                lambda: blob.upload_from_string(image_bytes, content_type="image/jpeg")
            )

            public_url = f"https://storage.mtls.cloud.google.com/{bucket.name}/{gcs_file_name}"
            logger.info(f"Photo uploaded, public URL: {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"Failed to process photo ref {photo_ref['photo_reference'][:20]}: {e}")
            return None

    # --- Create and run all upload tasks concurrently ---
    tasks = [upload_photo(photo) for photo in photo_references[:max_photos]]
    results = await asyncio.gather(*tasks)
    
    public_urls = [url for url in results if url is not None]

    if not public_urls:
        raise ConnectionError(f"Failed to upload any photos for '{actual_place_name}'.")

    logger.info(f"Returning {len(public_urls)} public URLs for the frontend.")
    return public_urls, place_details['result'].get('name', actual_place_name)
