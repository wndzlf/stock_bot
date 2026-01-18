import logging
import time
import html

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_to_telegram(text: str):
    """
    Sends a message to the configured Telegram chat.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        logger.error("TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 .env에 설정되지 않았습니다.")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # Try sending with HTML first
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 400:
            logger.warning("HTML 파싱 오류 가능성. 일반 텍스트로 다시 시도합니다.")
            payload.pop("parse_mode")
            # Remove basic tags if sending as plain text to avoid showing <b> etc.
            payload["text"] = text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
            response = requests.post(url, json=payload, timeout=15)
            
        response.raise_for_status()
        logger.info("텔레그램 메시지 전송 성공")
        return True
    except Exception as e:
        logger.error(f"텔레그램 메시지 전송 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
             logger.error(f"상세 오류 내용: {e.response.text}")
        return False

def get_latest_telegram_reply(last_update_id=None):
    """
    Polls the Telegram API for new messages from the user.
    Returns the update_id and the text of the latest message.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        return None, None
        
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"offset": last_update_id + 1 if last_update_id else None, "timeout": 30}
    
    try:
        response = requests.get(url, params=params, timeout=35)
        response.raise_for_status()
        updates = response.json().get("result", [])
        
        if updates:
            # We take the most recent update
            latest_update = updates[-1]
            update_id = latest_update["update_id"]
            message_text = latest_update.get("message", {}).get("text")
            return update_id, message_text
    except Exception as e:
        logger.error(f"텔레그램 응답 가져오기 실패: {e}")
        
    return None, None

if __name__ == "__main__":
    # Test (requires env vars)
    from dotenv import load_dotenv
    load_dotenv()
    send_to_telegram("안녕하세요! HITL 봇 테스트 중입니다.")
