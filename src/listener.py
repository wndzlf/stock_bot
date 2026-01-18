import os
import time
import logging
from dotenv import load_dotenv
from src.telegram_bot import get_latest_telegram_reply, send_to_telegram
from src.post_tweet import post_to_x

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_listener(dry_run=False):
    """
    Polls Telegram for new messages and posts them to X.
    """
    logger.info("텔레그램 리스너를 시작합니다. 새로운 메시지를 기다리는 중...")
    last_update_id = None
    
    # Initialize last_update_id to skip old messages
    last_update_id, _ = get_latest_telegram_reply()
    
    while True:
        try:
            update_id, message_text = get_latest_telegram_reply(last_update_id)
            
            if update_id and message_text:
                last_update_id = update_id
                logger.info(f"새로운 메시지 수신: {message_text[:50]}...")
                
                if dry_run:
                    logger.info(f"[테스트 모드] X에 다음 내용을 포스팅했을 것입니다: {message_text}")
                    send_to_telegram(f"✅ 테스트 모드: X에 포스팅했을 내용입니다:\n{message_text}")
                else:
                    logger.info("X에 포스팅을 시작합니다.")
                    post_to_x(message_text)
                    send_to_telegram("🚀 X에 성공적으로 포스팅되었습니다!")
            
            # Polling interval
            time.sleep(5)
            
        except KeyboardInterrupt:
            logger.info("리스너를 종료합니다.")
            break
        except Exception as e:
            logger.error(f"리스너 오류 발생: {e}")
            time.sleep(10)

if __name__ == "__main__":
    import argparse
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Telegram to X Listener")
    parser.add_argument("--dry-run", action="store_true", help="Run without posting to X")
    args = parser.parse_args()
    
    start_listener(dry_run=args.dry_run)
