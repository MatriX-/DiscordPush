import aiohttp
from typing import Optional, List
import asyncio

async def send_pushover_notification(
    message: str,
    user_key: str,
    api_token: str,
    title: Optional[str] = None,
    priority: int = 0,
    sound: str = "pushover",
    image_urls: Optional[List[str]] = None
) -> None:
    """Send a notification via Pushover with optional image attachments.
    
    Args:
        message: The main notification message
        user_key: Pushover user key
        api_token: Pushover API token
        title: Optional title for the notification
        priority: Message priority (-2 to 2)
        sound: Notification sound to play
        image_urls: Optional list of image URLs to attach
    """
    async with aiohttp.ClientSession() as session:
        data = {
            "token": api_token,
            "user": user_key,
            "message": message,
            "priority": priority,
            "sound": sound
        }
        if title:
            data["title"] = title
            
        try:
            if image_urls:
                # Send a notification for each image
                for image_url in image_urls:
                    try:
                        # Download image
                        async with session.get(image_url) as image_response:
                            if image_response.status == 200:
                                image_data = await image_response.read()
                                
                                # Prepare form data with image
                                form = aiohttp.FormData()
                                for key, value in data.items():
                                    form.add_field(key, str(value))
                                form.add_field('attachment', image_data, 
                                             filename='image.jpg',
                                             content_type='image/jpeg')
                                
                                # Send notification with image
                                async with session.post(
                                    "https://api.pushover.net/1/messages.json",
                                    data=form
                                ) as response:
                                    if response.status != 200:
                                        error_text = await response.text()
                                        print(f"Error sending image notification: {error_text}")
                            else:
                                print(f"Failed to download image: {image_url}")
                    except Exception as e:
                        print(f"Error processing image {image_url}: {e}")
            else:
                # Send text-only notification
                async with session.post(
                    "https://api.pushover.net/1/messages.json",
                    data=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"Error sending notification: {error_text}")
        
        except Exception as e:
            print(f"Error sending notification: {e}") 